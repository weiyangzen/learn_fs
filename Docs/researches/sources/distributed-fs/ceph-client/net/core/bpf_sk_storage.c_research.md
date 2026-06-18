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
