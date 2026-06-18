<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/Makefile -->
# sources/distributed-fs/ceph-client/net/core/Makefile

## Purpose
This kbuild file defines the object composition for the Linux networking core under `net/core`. It selects always-built core networking objects, conditionally includes feature-specific modules based on `CONFIG_*` symbols, and ensures foundational facilities such as sockets, skbuffs, datagram helpers, device registration, rtnetlink, XDP, GRO/GSO, flow offload, page pool, BPF socket maps, and diagnostic/debug helpers are linked into the kernel or module build as configured.

## Important APIs, Types, and Functions
The file does not define C APIs directly; its interface is kbuild object selection. Key always-built objects include `sock.o`, `skbuff.o`, `datagram.o`, `stream.o`, `scm.o`, `net_namespace.o`, `flow_dissector.o`, `dev.o`, `dst.o`, `rtnetlink.o`, `filter.o`, `sock_diag.o`, `xdp.o`, `gro.o`, `gso.o`, `net-sysfs.o`, `hotdata.o`, and queue/config helpers. Conditional objects expose feature APIs when their configs are enabled, for example `page_pool.o`, `netpoll.o`, `fib_rules.o`, `drop_monitor.o`, `timestamping.o`, `lwt_bpf.o`, `sock_map.o`, `bpf_sk_storage.o`, and debug/fault-injection objects.

## Control Flow
Kbuild evaluates `obj-y` and `obj-$(CONFIG_...)` assignments during kernel build generation. Objects listed in `obj-y` are linked unconditionally for this directory. Objects listed under a config symbol are included only when that symbol evaluates to built-in or module as appropriate. The ordering matters because it influences link order and therefore initcall ordering and symbol resolution within the core networking subsystem.

## State and Persistence
There is no runtime state in the Makefile itself. Its persistent effect is the compiled networking-core artifact: enabling or disabling config symbols changes which code paths, exported symbols, sysctls, procfs files, BPF helpers, debug hooks, and test objects exist in the resulting kernel.

## Dependencies and Integration Points
The Makefile depends on kernel kbuild semantics and Kconfig symbols such as `CONFIG_BPF_SYSCALL`, `CONFIG_PAGE_POOL`, `CONFIG_PROC_FS`, `CONFIG_NETPOLL`, `CONFIG_LWTUNNEL_BPF`, `CONFIG_NET_DEVMEM`, and `CONFIG_DEBUG_NET`. It integrates the two researched C files directly: `datagram.o` is part of the always-built networking core, while `bpf_sk_storage.o` is included when `CONFIG_BPF_SYSCALL` is enabled. Downstream protocols and drivers depend on the exported functions and subsystems made available by these objects.

## Risks
The primary risks are build- and integration-level. Accidentally moving a common object behind a config gate can break protocols that assume exported networking helpers are always present. Adding objects in the wrong order can affect init sequencing. Gating BPF, devmem, procfs, tracing, or debug files under the wrong symbol can produce missing symbols or dead code. Because this file controls a dense subsystem, small changes can have broad build-matrix impact.

## Test Signals
Useful signals include allmodconfig/allnoconfig/defconfig builds, targeted builds with `CONFIG_BPF_SYSCALL`, `CONFIG_PAGE_POOL`, `CONFIG_NET_DEVMEM`, and debug/test options toggled, link-time missing-symbol checks, and boot smoke tests that exercise sockets, netdevice registration, BPF socket storage, datagram receive paths, and rtnetlink/sysfs/procfs exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/bpf_sk_storage.c -->
# sources/distributed-fs/ceph-client/net/core/bpf_sk_storage.c

## Purpose
This file implements BPF socket-local storage maps for `struct sock` owners. It lets BPF programs and userspace map operations attach per-socket values, clone selected values to accepted sockets, charge storage against socket memory accounting, destroy storage with socket lifetime, expose stored values through socket diagnostics, and iterate storage entries through the BPF iterator framework.

## Important APIs, Types, and Functions
The storage backend is built on generic BPF local-storage infrastructure via `bpf_local_storage`, `bpf_local_storage_map`, `bpf_local_storage_elem`, and `bpf_local_storage_data`. `DEFINE_BPF_STORAGE_CACHE(sk_cache)` creates the allocator/cache binding used by socket storage maps.

Core lookup and lifetime helpers are `bpf_sk_storage_lookup()`, `bpf_sk_storage_del()`, `bpf_sk_storage_free()`, `bpf_sk_storage_map_alloc()`, and `bpf_sk_storage_map_free()`. Userspace fd-keyed map operations are `bpf_fd_sk_storage_lookup_elem()`, `bpf_fd_sk_storage_update_elem()`, and `bpf_fd_sk_storage_delete_elem()`, all using `sockfd_lookup()` to translate an integer fd key into a socket.

Socket cloning is handled by `bpf_sk_storage_clone()` and `bpf_sk_storage_clone_elem()`. Only maps with `BPF_F_CLONE` are copied, and values containing `BPF_SPIN_LOCK` use `copy_map_value_locked()` rather than the plain `copy_map_value()`.

The BPF helper entry points are `bpf_sk_storage_get`, `bpf_sk_storage_delete`, and tracing-safe wrappers `bpf_sk_storage_get_tracing` and `bpf_sk_storage_delete_tracing`. Their verifier-facing metadata lives in `bpf_sk_storage_get_proto`, `bpf_sk_storage_get_cg_sock_proto`, `bpf_sk_storage_delete_proto`, `bpf_sk_storage_get_tracing_proto`, and `bpf_sk_storage_delete_tracing_proto`. `bpf_sk_storage_tracing_allowed()` rejects recursive tracing of `bpf_sk_storage*` helpers and disallows incompatible attach types.

`sk_storage_map_ops` is the map implementation contract. It wires allocation, free, lookup, update, delete, BTF checks, owner pointer access, memory usage, and socket-memory charge/uncharge hooks. `bpf_sk_storage_charge()` and `bpf_sk_storage_uncharge()` account against `sk->sk_omem_alloc` with `sock_net(sk)->core.sysctl_optmem_max`.

Diagnostics use `struct bpf_sk_storage_diag`, `bpf_sk_storage_diag_alloc()`, `bpf_sk_storage_diag_free()`, `bpf_sk_storage_diag_put()`, `bpf_sk_storage_diag_put_all()`, `diag_get()`, and `nla_value_size()` to parse requested map fds and serialize map id/value pairs into nested sock-diag netlink attributes.

BPF iteration uses `struct bpf_iter_seq_sk_storage_map_info`, `struct bpf_iter__bpf_sk_storage_map`, `bpf_sk_storage_map_seq_find_next()`, seq-file callbacks, `bpf_iter_attach_map()`, `bpf_iter_detach_map()`, `bpf_sk_storage_map_reg_info`, and the `late_initcall()` registration of target `bpf_sk_storage_map`.

## Control Flow
Map creation flows through `sk_storage_map_ops.map_alloc` into generic local-storage map allocation. Userspace map operations receive an fd key, look up the socket, perform local-storage lookup/update/delete, and drop the socket fd reference. BPF helper lookup requires an RCU BPF read-side critical section, a non-null full socket, and valid flags; on `BPF_SK_STORAGE_GET_F_CREATE` it takes a temporary socket reference with `refcount_inc_not_zero()`, inserts via `bpf_local_storage_update()`, then releases the reference.

Socket destruction calls `bpf_sk_storage_free()`, which reads `sk->sk_bpf_storage` under `rcu_read_lock_dont_migrate()`, destroys all local storage, and uncharges accumulated storage bytes from `sk_omem_alloc`. Accepted-socket cloning starts by clearing `newsk->sk_bpf_storage`, iterates the parent storage list under RCU, skips maps without `BPF_F_CLONE`, pins each map with `bpf_map_inc_not_zero()`, allocates/copies a new element, and links it either into newly allocated storage or into the already-created storage for the new socket.

Sock-diag allocation first checks `bpf_capable()`, counts requested nested map-fd attributes, allocates a flexible `struct bpf_sk_storage_diag`, resolves each map fd, verifies `BPF_MAP_TYPE_SK_STORAGE`, rejects duplicates, and stores map references. Diagnostic output either dumps all storage entries or selected maps, builds a nested attribute group, copies values with lock-aware map copy helpers, initializes hidden map-value fields, and continues calculating the needed size even if the skb is too small.

Iterator attach resolves and pins a sk-storage map fd, verifies map type and max read/write access, then seq iteration walks map buckets under RCU. The iterator preserves bucket and skip position, skips elements whose local storage has disappeared, passes `sk` and `value` to the attached BPF iterator program, and releases the RCU read lock in the seq stop callback.

## State and Persistence
Persistent state is per-socket storage linked from `sk->sk_bpf_storage`, per-map bucket lists in the generic local-storage map, map references held by diagnostics and iterators, and socket memory accounting in `sk->sk_omem_alloc`. Values live as long as the map and socket-local element survive, are destroyed during socket teardown or map cleanup, and may be cloned to child sockets when map flags request it. No on-disk state is used.

## Dependencies and Integration Points
This file depends on BPF map and verifier infrastructure, BTF metadata, generic BPF local storage, RCU, socket lifetime and memory accounting, sockfd lookup, netlink attributes, sock_diag uapi definitions, seq_file, and BPF iterator registration. It integrates with socket destruction (`__sk_destruct()` callers), socket cloning/accept paths, BPF helpers available to networking/cgroup/tracing programs, user-visible `BPF_MAP_TYPE_SK_STORAGE` syscalls, and inet/sock diagnostic dumps.

## Risks
Lifetime and concurrency are the main risks. Helpers must not attach storage to a socket whose refcount has reached zero, and diagnostic/iterator paths must tolerate maps or socket storage disappearing under RCU. Memory charging must remain paired with uncharging, including clone failures. Value copying must honor embedded BPF spin locks. Tracing wrappers avoid hardirq/NMI contexts and recursive helper tracing; relaxing those checks could introduce unsafe allocations or recursion. Netlink serialization must not expose uninitialized map value padding and must report correct needed size on `-EMSGSIZE`.

## Test Signals
Strong coverage would include BPF selftests for create/lookup/update/delete through helpers and fd-based map syscalls, socket close cleanup, optmem-limit failures, clone behavior with and without `BPF_F_CLONE`, values containing `struct bpf_spin_lock`, tracing attach-type rejection, hardirq/NMI rejection for tracing wrappers, sock_diag dumps for all and selected maps, duplicate/invalid map-fd diagnostic requests, iterator traversal while sockets/maps are concurrently removed, and leak/accounting checks for `sk_omem_alloc`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/bpf_sk_storage.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/datagram.c -->
# sources/distributed-fs/ceph-client/net/core/datagram.c

## Purpose
This file provides generic networking-core helpers for datagram-style socket receive, peek, copy, checksum, zerocopy scatter-gather construction, and poll behavior. It centralizes common logic used by protocols such as UDP, raw sockets, packet sockets, Appletalk/IPX-style datagram users, and sequenced-packet sockets that share skb receive-queue semantics.

## Important APIs, Types, and Functions
Receive-side helpers include `connection_based()`, `receiver_wake_function()`, `__skb_wait_for_more_packets()`, `skb_set_peeked()`, `__skb_try_recv_from_queue()`, `__skb_try_recv_datagram()`, `__skb_recv_datagram()`, `skb_recv_datagram()`, `skb_free_datagram()`, `__sk_queue_drop_skb()`, and `skb_kill_datagram()`. These operate on `struct sock`, `struct sk_buff_head`, and `struct sk_buff`, handling `MSG_PEEK`, offsets, blocking waits, socket errors, shutdown, and busy polling.

Copy helpers are centered on `__skb_datagram_iter()`, which walks skb head data, page frags, and nested frag skbs into an `iov_iter`. Public wrappers include `skb_copy_datagram_iter()`, `skb_copy_and_crc32c_datagram_iter()` under `CONFIG_NET_CRC32C`, `skb_copy_datagram_from_iter()`, `skb_copy_datagram_from_iter_full()`, and checksum-aware `skb_copy_and_csum_datagram_msg()`.

Zerocopy send construction is handled by `zerocopy_fill_skb_from_iter()`, `zerocopy_fill_skb_from_devmem()`, `__zerocopy_sg_from_iter()`, and `zerocopy_sg_from_iter()`. These pin or reference pages/netmem from user iterators or devmem dma-buf bindings and append them as skb fragments while updating skb length, data length, truesize, and socket write memory accounting.

Poll APIs are `datagram_poll_queue()` and `datagram_poll()`, returning `__poll_t` masks for errors, receive readiness, shutdown/hangup, connection state, and write availability.

## Control Flow
`__skb_recv_datagram()` computes the receive timeout from socket flags, repeatedly calls `__skb_try_recv_datagram()`, and sleeps in `__skb_wait_for_more_packets()` while the queue has not advanced and the timeout allows. `__skb_try_recv_datagram()` first reports pending socket errors, locks the queue, delegates selection to `__skb_try_recv_from_queue()`, unlocks, optionally busy-polls if the queue did not advance, and returns `-EAGAIN` when no skb is ready.

`__skb_try_recv_from_queue()` walks the skb queue. For normal receives it unlinks the first eligible skb. For `MSG_PEEK`, it may maintain a byte offset across already-peeked skbs, clones shared zero-length skbs before setting `skb->peeked`, increments the skb user count, and leaves the skb queued. `__sk_queue_drop_skb()` and `skb_kill_datagram()` handle the follow-up case where a peeked skb needs to be removed if it is still queued.

`__skb_datagram_iter()` copies out in three stages: linear skb head, page fragments, then nested frag-list skbs recursively. It uses callback indirection so plain copy, CRC32C update, and checksum update can share traversal. On short copy or malformed length it reverts the iterator to its starting position and returns `-EFAULT` unless the caller allows a nonfault short copy at end of iterator.

`skb_copy_datagram_from_iter()` mirrors the traversal in the opposite direction, copying from an iterator into linear data, page frags, and nested fragments. The `_full` variant saves and restores iterator state on failure. `skb_copy_and_csum_datagram_msg()` either validates the existing checksum before plain copy when the destination is short, or copies and computes the checksum in one pass, reverting the iterator if the checksum fails.

Zerocopy filling first copies any linear head bytes when needed, then gathers pages from the iterator or resolves devmem offsets from a dma-buf binding. It coalesces adjacent compound-page fragments where possible, enforces `MAX_SKB_FRAGS`, advances the iterator, and charges the resulting truesize either to stream socket write memory or to the skb socket write allocation.

`datagram_poll_queue()` registers the caller in the socket wait queue, reports errors and error queue state, maps receive shutdown to readable/RDHUP events, reports custom receive-queue non-emptiness, handles connection-based close/SYN_SENT state, and reports writability via `sock_writeable()` or sets async nospace.

## State and Persistence
The file manipulates transient socket receive queues, skb reference counts, skb `peeked` state, queue links, iterator positions, checksum accumulators, skb fragment arrays, skb length/truesize fields, and socket memory counters. It does not persist state beyond socket/skb lifetime, but its helpers are responsible for preserving invariants across blocking waits, peeking, iterator rollback, zerocopy page references, and socket shutdown transitions.

## Dependencies and Integration Points
Dependencies include core socket APIs, skbuff internals, wait queues, poll/epoll flags, busy-poll support, iov_iter, checksum and CRC helpers, page-frag mapping, highmem local mapping, tracepoint `trace_skb_copy_datagram_iovec`, netdevice checksum fault reporting, and optional devmem dma-buf support from `devmem.h`. Exported symbols integrate with protocol receive paths, protocol send paths that build skb frags from userspace, and generic socket file poll operations.

## Risks
Important risks include races between `MSG_PEEK` and consuming reads, incorrect skb refcounting or queue unlinking, sleeping/waiting with stale queue-position observations, iterator rollback bugs after partial copies, checksum validation paths that copy data before detecting failure, zerocopy page reference leaks, `MAX_SKB_FRAGS` overflow, incorrect truesize/socket memory charging, and poll readiness mismatches for protocols using custom receive queues. Devmem support adds risk around interpreting user iterator addresses as dma-buf offsets and rejecting unsupported iterator types.

## Test Signals
Useful tests include UDP/raw/packet socket receive with blocking, nonblocking, timeout, shutdown, and signal interruption; `MSG_PEEK` with offsets, zero-length skbs, shared skbs, and concurrent consume; fault-injected iov_iter short copies verifying iterator restoration; checksum and CRC32C copy validation; send zerocopy with many fragments, adjacent fragment coalescing, and `MAX_SKB_FRAGS` boundary; devmem-backed iterator success and rejection cases; busy-poll smoke tests; and epoll/poll readiness for error queues, shutdown, hangup, connection-based sockets, and custom receive queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/core/datagram.c -->
