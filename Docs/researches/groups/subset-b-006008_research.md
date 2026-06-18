# subset-b-006008 Research

Grouped source research for io_uring zero-copy receive support and Linux IPC namespace, System V IPC, and POSIX mqueue implementation files. Each source file has its own marker-delimited section for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/zcrx.c -->
# sources/distributed-fs/ceph-client/io_uring/zcrx.c

## Purpose

`sources/distributed-fs/ceph-client/io_uring/zcrx.c` implements io_uring zero-copy receive support. It lets privileged users register a receive queue backed by user memory or a dma-buf, bind that queue to a network RX queue through the page-pool memory-provider API, deliver received buffer slices through extended CQEs, and reclaim buffers through a userspace refill ring. The source was read as a complete 1615-line file.

## Important APIs, Types, and Functions

The exported entry points are `io_register_zcrx()`, `io_unregister_zcrx()`, `io_terminate_zcrx()`, `io_zcrx_ctrl()`, `io_zcrx_get_region()`, and `io_zcrx_recv()`. Internal lifecycle helpers include `io_import_umem()`, `io_import_dmabuf()`, `io_import_area()`, `io_zcrx_create_area()`, `zcrx_register_netdev()`, `io_allocate_rbuf_ring()`, `io_zcrx_ifq_free()`, and `zcrx_unregister()`.

The page-pool integration is the `memory_provider_ops io_uring_pp_zc_ops` table: `io_pp_zc_alloc_netmems()` refills the driver page pool from returned userspace buffers or the area freelist, `io_pp_zc_release_netmem()` returns provider buffers to the freelist, `io_pp_zc_init()` validates page-pool parameters, `io_pp_uninstall()` detaches the provider, and `io_pp_nl_fill()` reports netlink attributes.

Receive-side helpers are `io_zcrx_queue_cqe()`, `io_zcrx_recv_frag()`, `io_zcrx_copy_chunk()`, `io_zcrx_recv_skb()`, and `io_zcrx_tcp_recvmsg()`. Control operations include `zcrx_flush_rq()` for force-returning userspace-held buffers and `zcrx_export()`/`import_zcrx()` for sharing a ZCRX queue through an anonymous inode fd.

## Control Flow

Registration requires `CAP_NET_ADMIN`, `IORING_SETUP_DEFER_TASKRUN`, and either `IORING_SETUP_CQE32` or `IORING_SETUP_CQE_MIXED`. `io_register_zcrx()` copies the userspace registration, preallocates an xarray id, creates the mapped refill region, imports the memory area, optionally opens a netdev RX queue with this file's page-pool provider, publishes the `io_zcrx_ifq`, and copies negotiated offsets, ids, and buffer sizes back to userspace.

Memory import validates reserved fields, page alignment, size ranges, and flags. Anonymous user memory is pinned with `io_pin_pages()`, converted to an sg table, optionally DMA-mapped, and charged against io_uring memory accounting. Dma-buf import attaches to the RX device, maps for `DMA_FROM_DEVICE`, and verifies the mapped DMA length matches the requested length. Area creation slices imported memory into power-of-two `net_iov` entries, initializes per-buffer user reference counters, and seeds the freelist.

The network datapath asks the page pool for provider memory. The fast refill path parses userspace RQEs, decrements the userspace reference for the named `net_iov`, tests the page-pool refcount, and returns only buffers owned by the requesting page pool. The slow path allocates unused `net_iov`s from the freelist. Receive CQEs contain the original request user data, result length, `IORING_CQE_F_MORE`, optional `IORING_CQE_F_32`, and a ZCRX offset encoding area id plus buffer offset. TCP is the only supported protocol path, via `tcp_read_sock()`.

## State and Persistence Behavior

State is in `io_zcrx_ifq`, `io_zcrx_area`, `io_zcrx_mem`, and the mapped `zcrx_rq`. It is per-io_uring-context and held in `ctx->zcrx_ctxs`. The state persists until explicit unregister, io_uring termination, imported-fd close, or page-pool/netdev uninstall. No file-backed data is persisted; pinned pages, dma-buf attachments, DMA mappings, xarray ids, region mappings, netdev references, device references, uid/mm accounting, and page-pool references are all runtime resources.

User references (`area->user_refs`) and page-pool refs jointly protect buffers exposed to userspace. `io_zcrx_scrub()` reclaims buffers still counted as userspace-held during unregister. `io_terminate_zcrx()` first marks and unregisters userspace-facing queue ownership; `io_unregister_zcrx()` later erases xarray entries and drops final references.

## Dependencies and Integration Points

This file integrates io_uring resource registration, mapped regions, deferred CQE allocation, network `page_pool`, netdev RX queue memory-provider installation, DMA mapping APIs, dma-buf, TCP receive internals, RPS flow recording, and netlink queue diagnostics. It depends on UAPI structures from `linux/io_uring.h`, local io_uring helpers from `io_uring.h`, `memmap.h`, `kbuf.h`, and `rsrc.h`, and the data contracts declared in `zcrx.h`.

## Risks and Edge Cases

The main risks are lifetime and ownership races across io_uring, userspace, page pools, and netdev teardown. Incorrect user-ref or page-pool-ref transitions can lead to buffer reuse while userspace still reads it, leaked buffers, or stale DMA ownership. The code also has sharp validation requirements around power-of-two buffer sizes, page alignment, dma-buf lengths, xarray publication, RQE offset parsing, and mixed/CQE32 CQE layout. Dma-buf areas are not kernel-readable, so skb head data and non-provider fragments can only be copied when the area came from pinned pages.

## Test Signals

Useful tests include registration failure coverage for missing capabilities, wrong io_uring setup flags, bad reserved fields, invalid RX queue ids, bad region sizes, non-power-of-two buffer sizes, and unsupported dma-buf configurations. Datapath tests should cover TCP receive with provider frags, copied skb head data, fallback copies, RQE refill, RQ flush, multishot CQE behavior, queue export/import, netdev uninstall, unregister while buffers are held by userspace, dma-sync-required devices, and memory-accounting cleanup after all failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/zcrx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/zcrx.h -->
# sources/distributed-fs/ceph-client/io_uring/zcrx.h

## Purpose

`sources/distributed-fs/ceph-client/io_uring/zcrx.h` declares the in-kernel state and public io_uring entry points for zero-copy receive. It is the local contract shared by io_uring receive code, registration code, and the ZCRX implementation. The source was read as a complete 121-line file.

## Important APIs, Types, and Functions

`struct io_zcrx_mem` tracks imported memory: size, dma-buf vs pinned-pages mode, page arrays, sg tables, accounted pages, dma-buf attachment, and dma-buf object. `struct io_zcrx_area` owns the `net_iov_area`, back-pointer to `io_zcrx_ifq`, per-buffer user refs, freelist, area id, mapping state, and imported memory. `struct zcrx_rq` describes the userspace refill ring and cached head. `struct io_zcrx_ifq` is the registered interface queue with area pointer, user/mm accounting, refill ring, RX queue id, device/netdev references, refcounts, provider lock, and mapped region.

When `CONFIG_IO_URING_ZCRX` is enabled, the header declares `io_zcrx_ctrl()`, `io_register_zcrx()`, `io_unregister_zcrx()`, `io_terminate_zcrx()`, `io_zcrx_recv()`, and `io_zcrx_get_region()`. When disabled, those helpers return `-EOPNOTSUPP` or `NULL` and unregister/terminate become no-ops. `io_recvzc()` and `io_recvzc_prep()` are always declared for the higher-level receive operation.

## Control Flow

The header has no executable control flow beyond disabled-feature inline stubs. It establishes that enabled builds use the real registration/control/receive implementation, while disabled builds compile callers without special-case preprocessor logic.

## State and Persistence Behavior

The structures describe runtime state only. Lifetimes are reference-counted through `io_zcrx_ifq.refs` and `user_refs`, and are tied to io_uring context lifetime, exported fd lifetime, netdev page-pool ownership, and user-visible buffer ownership. No persistent storage is declared here.

## Dependencies and Integration Points

Includes show the integration surface: `linux/io_uring_types.h`, `linux/dma-buf.h`, sockets, page-pool types, and net-device tracker support. The constants `ZCRX_SUPPORTED_REG_FLAGS` and `ZCRX_FEATURES` bind this implementation to UAPI flags such as import, nodev registration, and RX page-size feature reporting.

## Risks and Edge Cases

The header is a state-layout contract inside io_uring. Field changes can break assumptions in the implementation about cacheline placement, page-pool callbacks, mmap region lookup, and lifetime cleanup. The disabled stubs must stay behaviorally aligned with callers so unsupported kernels return clean errors instead of partially enabling recvzc paths.

## Test Signals

Build tests should cover both `CONFIG_IO_URING_ZCRX=y` and disabled configurations. Static checks should verify all declared enabled symbols are implemented and that disabled stubs satisfy callers. Runtime tests should confirm unsupported builds return `-EOPNOTSUPP` for registration, control, and receive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/io_uring/zcrx.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/Makefile -->
# sources/distributed-fs/ceph-client/ipc/Makefile

## Purpose

`sources/distributed-fs/ceph-client/ipc/Makefile` selects Linux IPC objects for the kernel build. It maps configuration symbols to System V IPC, POSIX mqueue, IPC namespace, sysctl, and compatibility support. The source was read as a complete 12-line file.

## Important APIs, Types, and Functions

There are no C APIs. Build rules add `compat.o` for `CONFIG_SYSVIPC_COMPAT`; `util.o`, `msgutil.o`, `msg.o`, `sem.o`, `shm.o`, and `syscall.o` for `CONFIG_SYSVIPC`; `ipc_sysctl.o` for `CONFIG_SYSVIPC_SYSCTL`; `mqueue.o` and `msgutil.o` for `CONFIG_POSIX_MQUEUE`; `namespace.o` for `CONFIG_IPC_NS`; and `mq_sysctl.o` for `CONFIG_POSIX_MQUEUE_SYSCTL`.

## Control Flow

Build-time flow is controlled by Kconfig. `msgutil.o` is deliberately shared by System V IPC and POSIX mqueue because it provides common message allocation/copy/free helpers and `init_ipc_ns`/`mq_lock` support for configurations that may compile only one IPC family.

## State and Persistence Behavior

The Makefile owns no runtime state. It determines which object files define IPC namespace state, sysctl registration, message helpers, and syscall entry points.

## Dependencies and Integration Points

This file integrates Kconfig with the IPC source directory. It must remain consistent with exported helpers across `msg.c`, `sem.c`, `shm.c`, `mqueue.c`, `namespace.c`, `ipc_sysctl.c`, and `mq_sysctl.c`.

## Risks and Edge Cases

The main risk is missing shared objects under unusual config combinations, especially `msgutil.o` when POSIX mqueue is enabled without full SysV IPC, or compatibility objects when old multiplexed syscall paths are enabled. Incorrect object selection can appear as link failures or, worse, missing namespace/sysctl initialization in a valid config.

## Test Signals

Build matrix coverage should include SysV IPC only, POSIX mqueue only, both together, IPC namespaces enabled and disabled, sysctl variants, compat syscall variants, and all-disabled configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/compat.c -->
# sources/distributed-fs/ceph-client/ipc/compat.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/compat.c` converts 32-bit compatibility IPC permission structures to and from native kernel `ipc64_perm` structures. The source was read as a complete 82-line file.

## Important APIs, Types, and Functions

`get_compat_ipc64_perm()` and `get_compat_ipc_perm()` copy compat permission structures from userspace into `struct ipc64_perm`, preserving uid, gid, and mode. `to_compat_ipc64_perm()` fills the modern compat layout with key, uid/gid, creator uid/gid, mode, and sequence. `to_compat_ipc_perm()` fills the old compat layout and uses `SET_UID()`/`SET_GID()` conversions for legacy narrow uid/gid fields.

## Control Flow

All functions are small conversion helpers. The `get_*` functions first `copy_from_user()` into a stack local and return `-EFAULT` on bad user memory. The `to_*` functions populate caller-provided kernel-side compat structs before the caller copies them to userspace.

## State and Persistence Behavior

No state is stored. These helpers translate syscall arguments/results for message, semaphore, and shared-memory `IPC_SET`/`IPC_STAT` compatibility paths.

## Dependencies and Integration Points

The file depends on compat ABI definitions, highuid conversion helpers, user-copy APIs, and IPC utility declarations. It is called from compat implementations in `msg.c`, `sem.c`, and `shm.c`, and indirectly from the old compat `sys_ipc` multiplexer.

## Risks and Edge Cases

The compatibility ABI is sensitive to structure layout, uid/gid width, and time/sequence field placement. Bad copies must never partially update live permissions. Old ABI conversion can truncate ids, so tests need to distinguish legacy behavior from IPC_64 behavior.

## Test Signals

Compat syscall tests should exercise `IPC_SET` and `IPC_STAT`/`*_STAT` for msg, sem, and shm using both old and IPC_64 command versions, invalid user pointers, high uid/gid values, and 32-bit userlands on 64-bit kernels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/compat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/ipc_sysctl.c -->
# sources/distributed-fs/ceph-client/ipc/ipc_sysctl.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/ipc_sysctl.c` registers per-IPC-namespace sysctls for System V shared memory, messages, semaphores, and checkpoint/restore next-id controls. It also supports the `ipcmni_extend` early boot parameter. The source was read as a complete 334-line file.

## Important APIs, Types, and Functions

Handlers include `proc_ipc_dointvec_minmax_orphans()` for `shm_rmid_forced`, `proc_ipc_auto_msgmni()` for the legacy no-op `auto_msgmni`, and `proc_ipc_sem_dointvec()` for validating semaphore tunables through `sem_check_semmni()`. The exported setup/teardown functions are `setup_ipc_sysctls()` and `retire_ipc_sysctls()`. Global limits are `ipc_mni`, `ipc_mni_shift`, and `ipc_min_cycle`, modified by `ipc_mni_extend()`.

## Control Flow

`setup_ipc_sysctls()` initializes `ns->ipc_set`, duplicates the static `ipc_sysctls` table, rewrites every `.data` pointer from `init_ipc_ns` storage to the target namespace storage, and registers the table under `kernel`. `retire_ipc_sysctls()` unregisters and frees the duplicated table. `ipc_sysctl_init()` registers sysctls for `init_ipc_ns` at device init time.

## State and Persistence Behavior

Sysctl values live in `struct ipc_namespace`: shared memory limits and forced removal flag, message queue limits, semaphore control array, and optional next-id fields. Writes persist for the namespace lifetime. Enabling `shm_rmid_forced` can immediately destroy orphaned shared-memory segments through `shm_destroy_orphaned()`.

## Dependencies and Integration Points

This file integrates the sysctl core, IPC namespace ownership, user namespace uid/gid mapping, checkpoint/restore privilege checks, and SysV IPC subsystems. Permission callbacks make sysctls appear owned by root in the owning user namespace and give checkpoint/restore-capable tasks write access to next-id fields when configured.

## Risks and Edge Cases

Pointer rewriting must be exhaustive; a stale pointer to `init_ipc_ns` would make one namespace mutate another. Semaphore sysctl writes must roll back invalid `semmni` changes. `shm_rmid_forced` has destructive side effects, so handler ordering matters. Permission calculations are namespace-sensitive and must not accidentally grant host-level access from another user namespace.

## Test Signals

Tests should create IPC namespaces, read/write `/proc/sys/kernel/{shmmax,shmall,shmmni,shm_rmid_forced,msgmax,msgmni,msgmnb,sem}`, verify isolation between namespaces, validate invalid `sem` writes roll back, exercise `shm_rmid_forced` orphan cleanup, and boot with `ipcmni_extend` to confirm extended id limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/ipc_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/mq_sysctl.c -->
# sources/distributed-fs/ceph-client/ipc/mq_sysctl.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/mq_sysctl.c` registers per-IPC-namespace sysctls for POSIX message queue defaults and limits under `fs/mqueue`. The source was read as a complete 167-line file.

## Important APIs, Types, and Functions

The sysctl table exposes `queues_max`, `msg_max`, `msgsize_max`, `msg_default`, and `msgsize_default`. `setup_mq_sysctls()` duplicates and registers the table for a namespace. `retire_mq_sysctls()` unregisters it. Permission helpers `mq_set_ownership()` and `mq_permissions()` map ownership and access checks through the namespace's user namespace.

## Control Flow

Setup initializes `ns->mq_set`, clones `mq_sysctls`, rewrites each table entry from `init_ipc_ns` fields to the target namespace fields, and registers under `fs/mqueue`. On failure it frees the clone and retires the sysctl set. Teardown unregisters, retires the set, and frees the cloned table.

## State and Persistence Behavior

Values are stored in `ipc_namespace` fields and persist for the namespace lifetime. They control future POSIX mqueue creation, default queue attributes, and non-privileged limits; existing queues keep their inode-local attributes.

## Dependencies and Integration Points

This file integrates `mqueue.c`, IPC namespaces, sysctl, user namespaces, and capability policy. The min/max handlers enforce hard message-count and message-size bounds through `MIN_MSGMAX`, `HARD_MSGMAX`, `MIN_MSGSIZEMAX`, and `HARD_MSGSIZEMAX`.

## Risks and Edge Cases

As with SysV IPC sysctls, pointer rewriting must be correct for namespace isolation. Limit writes can affect resource-exhaustion behavior for later queue creation. Permission handling must reflect root/group in the namespace rather than global root assumptions.

## Test Signals

Tests should verify per-namespace isolation of `/proc/sys/fs/mqueue/*`, min/max rejection for message counts and sizes, creation behavior before and after default changes, and permission behavior from nested user namespaces.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/mq_sysctl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/mqueue.c -->
# sources/distributed-fs/ceph-client/ipc/mqueue.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/mqueue.c` implements Linux POSIX message queues as a filesystem named `mqueue`. It handles queue inode creation, priority-ordered message storage, blocking send/receive, timed operations, notification, polling, namespace mount setup, per-user accounting, and compat/time32 syscall variants. The source was read as a complete 1680-line file.

## Important APIs, Types, and Functions

Core state is `struct mqueue_inode_info`, which embeds a VFS inode, queue lock, wait queue, priority rb-tree, queue attributes, notification state, accounting `ucounts`, two wait queues for send and receive, and memory-size tracking. `struct posix_msg_tree_node` stores messages for one priority. `struct ext_wait_queue` represents a sleeping sender or receiver and uses `STATE_NONE`/`STATE_READY` with release/acquire barriers.

Important functions include `mqueue_get_inode()`, `mqueue_create_attr()`, `mqueue_evict_inode()`, `do_mq_open()`, `do_mq_timedsend()`, `do_mq_timedreceive()`, `do_mq_notify()`, `do_mq_getsetattr()`, `mq_init_ns()`, `mq_clear_sbinfo()`, and `init_mqueue_fs()`. File operations support read-only queue status text, poll, flush notification cleanup, and normal VFS lookup/create/unlink semantics.

## Control Flow

`init_mqueue_fs()` creates the inode cache, registers init namespace sysctls, registers the filesystem, initializes `mq_lock`, and creates the initial namespace mount. Each IPC namespace gets an internal `mqueue` mount via `mq_init_ns()`. `mq_open` resolves a queue name under that mount, optionally creates an inode with validated attributes and accounting, then opens it as a file descriptor.

Messages are inserted into an rb-tree keyed by priority, with the rightmost node holding the highest priority. Send allocates/copies a `msg_msg`, validates priority, fd type, write access, and message length, then either directly hands the message to a waiting receiver, inserts it into the tree, or sleeps on the send wait list when full. Receive validates fd/read access and buffer size, then either removes the highest-priority message, sleeps on the receive wait list, or returns `-EAGAIN` for nonblocking empty queues. Pipelined send/receive bypasses the tree when a peer is already sleeping.

## State and Persistence Behavior

Queue state persists as long as the mqueue inode exists or open references keep it alive. Messages are kernel memory allocated by `load_msg()` and freed on receive or inode eviction. Queue counts, qsize, attributes, notification owner, and waiters are inode-local. Namespace state tracks mount, queue count, limits, defaults, and sysctls. Per-user `RLIMIT_MSGQUEUE` accounting is charged at queue creation for worst-case queue memory and released in eviction.

## Dependencies and Integration Points

This file integrates VFS, fs_context, namespace mounts, `simple_*` directory helpers, SysV message allocation helpers from `msgutil.c`, audit hooks, signal delivery, netlink notification for `SIGEV_THREAD`, user namespace accounting, `RLIMIT_MSGQUEUE`, poll, hrtimer absolute timeouts, and compat/time32 syscall layers.

## Risks and Edge Cases

Blocking send/receive has intentional lockless return paths; `STATE_READY`, `smp_store_release()`, `smp_acquire__after_ctrl_dep()`, and `wake_q_add_safe()` are critical to avoid stale message pointers or task use-after-free. Queue creation accounting assumes worst-case memory; overflow checks and capability exceptions must remain exact. Notification state must be removed on close/unregister and must not signal after exec-id changes. The rb-tree must stay consistent with `mq_curmsgs` and qsize even when allocation of a new priority node fails.

## Test Signals

Tests should cover queue creation limits, `RLIMIT_MSGQUEUE`, namespace mounts, priority ordering, blocking and nonblocking send/receive, absolute timeout behavior, signal interruption, poll readiness, unlink with open descriptors, notification registration/removal for `SIGEV_NONE`, `SIGEV_SIGNAL`, and `SIGEV_THREAD`, compat attributes, time32 syscalls, and stress with concurrent senders/receivers across many priorities.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/mqueue.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/msg.c -->
# sources/distributed-fs/ceph-client/ipc/msg.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/msg.c` implements System V message queues: queue creation, removal, control operations, blocking send/receive, message selection by type, permission/security checks, namespace initialization, proc reporting, and compat syscall support. The source was read as a complete 1376-line file.

## Important APIs, Types, and Functions

`struct msg_queue` stores IPC permissions, timestamps, byte/message counts, byte limit, sender/receiver pids, queued messages, and sleeping receiver/sender lists. `struct msg_receiver` tracks a blocked `msgrcv()` selection and destination constraints. `struct msg_sender` tracks a blocked `msgsnd()` waiting for queue space.

Public syscall helpers are `ksys_msgget()`, `ksys_msgsnd()`, `ksys_msgrcv()`, and the `msgctl` syscall path through `ksys_msgctl()`. Core helpers include `newque()`, `freeque()`, `msgctl_down()`, `msgctl_info()`, `msgctl_stat()`, `do_msgsnd()`, `pipelined_send()`, `convert_mode()`, `find_msg()`, and `do_msgrcv()`. Namespace hooks are `msg_init_ns()`, `msg_exit_ns()`, and `msg_init()`.

## Control Flow

`msgget` delegates to `ipcget()` with `newque()` for creation and LSM association for existing queues. `msgsnd` copies the user message via `load_msg()`, validates type and size, locks the target queue under RCU, checks write permission and LSM policy, waits if the queue is full unless `IPC_NOWAIT`, then either directly hands the message to a matching sleeping receiver or appends it to `q_messages`.

`msgrcv` converts the requested type and flags into a search mode: first message, exact type, not-equal type, lowest type less-or-equal, or `MSG_COPY` ordinal lookup. It scans the queue with LSM receive checks, unlinks and accounts a matching message unless `MSG_COPY` is used, or sleeps as a `msg_receiver`. A sender can complete a sleeping receiver with a release-store to `r_msg`, allowing the receiver to return without relocking when safe.

`msgctl` handles info/stat commands, permission updates, queue-byte limit changes, and removal. `IPC_RMID` expunges receivers, wakes senders with `-EIDRM`, removes the queue id, and frees all queued messages and pid references.

## State and Persistence Behavior

Message queue objects live in `ns->ids[IPC_MSG_IDS]` and persist until `IPC_RMID` or namespace teardown. Queued bytes and headers are mirrored in per-namespace percpu counters for `MSG_INFO`. Timestamps and last-pid fields are updated on send, receive, and control changes. Message payloads are allocated in segmented kernel memory and freed after receive, copy failure cleanup, queue removal, or namespace exit.

## Dependencies and Integration Points

The file integrates generic SysV IPC id/key management from `util.h`, LSM hooks (`security_msg_queue_*`), audit, percpu counters, RCU/id locks, pid namespaces for proc output, compat permission conversion, and shared message allocation/copy helpers from `msgutil.c`.

## Risks and Edge Cases

The lockless receiver wake path depends on the documented `MSG_BARRIER` ordering and `wake_q_add_safe()`. Queue-full logic uses both byte count and message count against `q_qbytes`, preserving historical semantics. `MSG_COPY` is only valid with checkpoint/restore support, `IPC_NOWAIT`, and without `MSG_EXCEPT`. Type conversion must handle `LONG_MIN`. Permission changes can make sleeping receivers invalid and must expunge them with `-EAGAIN`.

## Test Signals

Tests should cover create/find semantics, `IPC_CREAT|IPC_EXCL`, permission denial, queue full blocking and wakeup order, direct sender-to-receiver handoff, message type selection modes, `MSG_NOERROR`, `MSG_COPY`, `IPC_STAT`/`MSG_STAT_ANY`, `IPC_SET` byte-limit changes, `IPC_RMID` with blocked tasks, namespace isolation, proc output, and compat send/receive/control paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/msg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/msgutil.c -->
# sources/distributed-fs/ceph-client/ipc/msgutil.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/msgutil.c` provides shared message payload allocation, user copy, duplication, and free helpers for System V message queues and POSIX mqueues. It also defines `init_ipc_ns` and `mq_lock` for build configurations where only one IPC family is enabled. The source was read as a complete 192-line file.

## Important APIs, Types, and Functions

`DEFINE_SPINLOCK(mq_lock)` protects mqueue namespace/mount teardown races. `struct ipc_namespace init_ipc_ns` seeds the initial IPC namespace. Message storage uses a head `struct msg_msg` followed by optional `struct msg_msgseg` continuation pages. `init_msg_buckets()` creates bucketed allocations for message heads. `load_msg()` allocates and copies user payload into segmented kernel memory, `store_msg()` copies it back to userspace, `copy_msg()` supports checkpoint/restore message copying, and `free_msg()` releases LSM state plus all segments.

## Control Flow

`alloc_msg()` allocates enough head storage for `DATALEN_MSG` and chains additional `msg_msgseg` allocations for larger payloads. `load_msg()` copies each segment from userspace and then calls `security_msg_msg_alloc()`. `store_msg()` walks the same segmentation layout in the opposite direction. `free_msg()` calls `security_msg_msg_free()` and frees the head and all segments with reschedule points for long chains.

## State and Persistence Behavior

Message payloads persist only while held by a queue, a blocked sender/receiver handoff, or a temporary copy operation. The global bucket allocator persists after `subsys_initcall`. `init_ipc_ns` persists for the kernel lifetime.

## Dependencies and Integration Points

This file integrates slab bucket allocation, LSM message hooks, user-copy APIs, IPC namespace initialization, namespace tree/proc namespace headers, and both `msg.c` and `mqueue.c`.

## Risks and Edge Cases

Segment accounting must match the payload length exactly across allocation, copy-in, copy-out, and free. Failure after partial allocation or partial user copy must release all segments. `copy_msg()` is gated by checkpoint/restore; callers must handle `-ENOSYS` when unsupported. The shared `init_ipc_ns` definition must be available for config combinations selected by the Makefile.

## Test Signals

Tests should cover zero-length, small, page-sized, and multi-page messages; copy_from_user/copy_to_user faults at different segment boundaries; LSM allocation failure; checkpoint/restore `MSG_COPY`; and kmemleak or fault-injection runs for partial allocation cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/msgutil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/namespace.c -->
# sources/distributed-fs/ceph-client/ipc/namespace.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/namespace.c` implements IPC namespace creation, reference management, teardown, proc namespace operations, and generic cleanup of per-namespace IPC objects. The source was read as a complete 257-line file.

## Important APIs, Types, and Functions

`copy_ipcs()` clones or references an IPC namespace depending on `CLONE_NEWIPC`. `create_ipc_ns()` allocates and initializes a new namespace. `free_ipcs()` walks an `ipc_ids` table and calls a type-specific free function. `put_ipc_ns()` drops namespace references and schedules asynchronous teardown. Proc namespace operations are `ipcns_get()`, `ipcns_put()`, `ipcns_install()`, and `ipcns_owner()`, exposed through `ipcns_operations`.

## Control Flow

Namespace creation charges `UCOUNT_IPC_NAMESPACES`, allocates `struct ipc_namespace`, initializes common namespace state, assigns namespace tree id and user namespace, creates the mqueue mount, registers mqueue and SysV IPC sysctls, initializes message, semaphore, and shared-memory namespaces, then adds the namespace to the namespace tree. Failure unwinds in reverse order.

Namespace put is asynchronous. When the last reference is dropped under `mq_lock`, `mq_clear_sbinfo()` prevents new VFS lookups from taking namespace references, the namespace is removed from the tree, and work is queued. `free_ipc()` marks mqueue mounts short-term, waits for an RCU grace period, then calls `free_ipc_ns()` to free mqueues, semaphores, messages, shm, sysctls, ucounts, user namespace, common namespace state, and memory.

## State and Persistence Behavior

The IPC namespace owns SysV IPC id tables, mqueue mount and limits, sysctl registrations, user namespace reference, ucounts charge, namespace tree id, and teardown list linkage. State persists until reference count reaches zero and asynchronous cleanup completes.

## Dependencies and Integration Points

This file integrates user namespaces and ucounts, mount/VFS lifetime rules for mqueuefs, sysctl setup/retire helpers, SysV IPC subsystem init/exit functions, RCU, namespace tree registration, `nsproxy`, and `/proc/<pid>/ns/ipc` operations.

## Risks and Edge Cases

The critical race is between last-task namespace exit and another mount namespace accessing the mqueue superblock. `mq_lock`, `mq_clear_sbinfo()`, and the RCU-delayed free path are designed to close that race. Namespace creation must unwind partial initialization precisely. `ipcns_install()` must require `CAP_SYS_ADMIN` in both the target namespace owner and caller credential user namespace.

## Test Signals

Tests should cover `unshare(CLONE_NEWIPC)`, `setns()` permission checks, mqueue mount access after namespace exit, namespace limit exhaustion and delayed free retry, cleanup of live msg/sem/shm objects on namespace exit, and proc namespace owner/reference behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/namespace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/sem.c -->
# sources/distributed-fs/ceph-client/ipc/sem.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/sem.c` implements System V semaphore sets, including `semget`, `semctl`, `semop`, timed waits, SEM_UNDO, namespace initialization/teardown, wakeup ordering, proc reporting, and compat/time32 syscall support. The source was read as a complete 2484-line file.

## Important APIs, Types, and Functions

`struct sem` stores one semaphore value, last-modifier pid, per-semaphore lock, pending alter/const wait queues, and replicated operation time. `struct sem_array` stores IPC permissions, set-wide timestamps, global pending queues, undo-list linkage, number of semaphores, complex-operation counters, global-lock mode, and the flexible array of semaphores. `struct sem_queue` represents one blocked semop. `struct sem_undo` and `struct sem_undo_list` implement SEM_UNDO state.

Major functions include `sem_init_ns()`, `sem_exit_ns()`, `newary()`, `freeary()`, `ksys_semget()`, `ksys_semctl()`, `semctl_main()`, `semctl_setval()`, `semctl_down()`, `__do_semtimedop()`, `do_semtimedop()`, `copy_semundo()`, and `exit_sem()`. Concurrency helpers include `sem_lock()`, `complexmode_enter()`, `complexmode_tryleave()`, `merge_queues()`, `unmerge_queues()`, `perform_atomic_semop()`, `update_queue()`, and `do_smart_update()`.

## Control Flow

`semget` uses generic `ipcget()` with `newary()` to allocate a semaphore set, initialize all per-semaphore queues/locks, charge `ns->used_sems`, and publish an id. `semctl` handles info/stat commands, permission updates, removal, get/set value operations, and bulk get/set. `SETVAL` and `SETALL` clear related undo adjustments and run smart wakeups because blocked operations may now complete.

`semop` copies user `sembuf` operations, validates counts and semaphore indexes, optionally allocates an undo entry, checks permissions and LSM policy, and attempts atomic execution. Nonblocking success updates values, SEM_UNDO adjustments, pids, operation time, and pending waiters. If an operation would block, it is inserted into either per-semaphore queues for simple operations or global queues for complex operations, then sleeps with timeout/signal handling. Wakers complete blocked operations while holding the relevant semaphore locks and store final status before waking the task.

## State and Persistence Behavior

Semaphore sets persist in `ns->ids[IPC_SEM_IDS]` until `IPC_RMID` or namespace exit. Semaphore values, pids, timestamps, pending queues, and undo lists are runtime kernel state. SEM_UNDO entries persist per task or shared task group when `CLONE_SYSVSEM` is used; `exit_sem()` applies bounded adjustments and frees undo objects on final reference. Namespace tunables control maximum set size, total semaphores, operations per call, and number of sets.

## Dependencies and Integration Points

This file integrates SysV IPC id/key utilities, LSM hooks, audit, RCU, wake queues, hrtimer timeouts, pid and user namespaces, proc sysvipc output, sysctl validation through `sem_check_semmni()`, clone/exit task hooks, and compat/time32 syscall layers.

## Risks and Edge Cases

The file has high concurrency risk. Correctness depends on the documented barriers for `use_global_lock` and `queue.status`, lock ordering between set locks and per-semaphore locks, and active wakeup semantics. FIFO behavior requires careful queue merging when complex operations appear. SEM_UNDO must handle id reuse, `IPC_RMID` races, duplicate semops in one transaction, undo range limits, and exit-time clamping to `0..SEMVMX`.

## Test Signals

Tests should cover simple and multi-op semop success/failure, wait-for-zero, FIFO wake order, timeout and signal interruption, `IPC_NOWAIT`, duplicate operations on the same semaphore, `SEM_UNDO` across fork/clone/exit, `IPC_RMID` with sleepers, `SETVAL`/`SETALL` wakeups and undo clearing, sysctl limit changes, proc output, namespace isolation, compat semctl, and time32 semtimedop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/sem.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/shm.c -->
# sources/distributed-fs/ceph-client/ipc/shm.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/shm.c` implements System V shared memory: segment creation, control, attach/detach, VMA wrappers, forced orphan cleanup, namespace initialization/teardown, locking/unlocking, proc reporting, and compat syscall support. The source was read as a complete 1880-line file.

## Important APIs, Types, and Functions

`struct shmid_kernel` stores IPC permissions, backing file, attach count, size, timestamps, creator/last pids, mlock accounting, creator task, creator-list linkage, and namespace pointer. `struct shm_file_data` wraps the real shmem/hugetlb file with shmid, namespace, file, and original vm ops. Public helpers include `ksys_shmget()`, `ksys_shmctl()`, `do_shmat()`, `ksys_shmdt()`, `shm_destroy_orphaned()`, `exit_shm()`, `shm_init_ns()`, `shm_exit_ns()`, and `shm_init()`.

## Control Flow

`shmget` delegates to `ipcget()` with `newseg()` for creation. `newseg()` validates size and namespace page limits, allocates `shmid_kernel`, runs LSM allocation, creates either a hugetlb file or shmem file, initializes metadata, publishes an IPC id, links the segment to the creator task, sets the backing inode number to the shmid, and updates namespace total pages.

`shmctl` dispatches info/stat, permission update, removal, and lock/unlock operations. `IPC_RMID` marks attached segments `SHM_DEST` and hides their key or destroys unattached segments immediately. `SHM_LOCK`/`SHM_UNLOCK` enforce capability/owner and memlock rules, call shmem locking helpers, and track the charging `ucounts`.

`do_shmat()` validates address/alignment/remap flags, derives protections and access mode, checks permissions and LSM policy, increments attach count, creates an outer file clone whose ops point to this file, and maps the real backing file through `do_mmap()`. The wrapper VMA ops forward faults and NUMA policy to the underlying mapping while maintaining SysV attach timestamps and counts. `shmdt` finds all VMA fragments belonging to the segment and unmaps them.

## State and Persistence Behavior

Segments persist in `ns->ids[IPC_SHM_IDS]` until `IPC_RMID`, namespace teardown, or forced orphan cleanup. Backing storage lives in shmem or hugetlbfs files and can remain mapped after `IPC_RMID` until the last attach closes. `shm_nattch`, `shm_atim`, `shm_dtim`, `shm_ctim`, creator/last pids, `SHM_DEST`, `SHM_LOCKED`, namespace total pages, and creator lists are runtime state. `shm_rmid_forced` changes cleanup policy for orphaned creator lists.

## Dependencies and Integration Points

This file integrates generic SysV IPC id management, shmem, hugetlb, VFS file cloning, mmap and VMA operations, mempolicy hooks, LSM and audit, pid/user namespaces, namespace tree init, sysctl orphan cleanup, rlimits/ucounts for mlock, proc sysvipc output, and compat control/attach paths.

## Risks and Edge Cases

Attach/detach lifetime is the central risk. The wrapper file can outlive IPC id removal, so `__shm_open()` checks both id and backing file to detect id reuse. `do_shmat()` increments `shm_nattch` before mapping and must decrement on all failures. `shmdt` must unmap fragmented VMAs without detaching unrelated segments. Forced orphan removal and creator-list cleanup race with task exit, namespace teardown, and `IPC_RMID`, requiring `task_lock`, `mq_lock`-style namespace refs, RCU, and id rwsem coordination.

## Test Signals

Tests should cover shmem and hugetlb creation, size/limit failures, `SHM_NORESERVE`, attach at fixed/rounded addresses, `SHM_REMAP`, read-only and exec attaches, detach of fragmented mappings, `IPC_RMID` while attached, `shm_rmid_forced`, creator task exit, `SHM_LOCK`/`SHM_UNLOCK` permissions and memlock behavior, namespace isolation, proc RSS/swap reporting, and compat `shmctl`/`shmat`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/shm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/syscall.c -->
# sources/distributed-fs/ceph-client/ipc/syscall.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/syscall.c` implements the legacy `sys_ipc` multiplexed System V IPC syscall and old compat multiplexer variants for architectures that still request them. The source was read as a complete 211-line file.

## Important APIs, Types, and Functions

`ksys_ipc()` decodes the high-word IPC version and low-word operation, then dispatches to semaphore, message, and shared-memory helpers. `SYSCALL_DEFINE6(ipc)` exposes that path when `__ARCH_WANT_SYS_IPC` is set. Under compat support, `compat_ksys_ipc()` and `COMPAT_SYSCALL_DEFINE6(ipc)` do equivalent decoding for `CONFIG_ARCH_WANT_OLD_COMPAT_IPC`. `struct compat_ipc_kludge` mirrors the old message-receive kludge layout.

## Control Flow

The multiplexer switches on operations such as `SEMOP`, `SEMTIMEDOP`, `SEMGET`, `SEMCTL`, `MSGSND`, `MSGRCV`, `MSGGET`, `MSGCTL`, `SHMAT`, `SHMDT`, `SHMGET`, and `SHMCTL`. Older `MSGRCV` and `SHMAT` ABIs use kludge structs or out-parameters; newer variants pass direct pointers and values. Time handling dispatches to native timespec or compat old-timespec helpers depending on configuration.

## State and Persistence Behavior

This file owns no IPC objects. It only translates the old syscall ABI into calls that mutate message queues, semaphores, or shared-memory segments in the current IPC namespace.

## Dependencies and Integration Points

It integrates architecture syscall selection, SysV IPC helper functions from `msg.c`, `sem.c`, and `shm.c`, version parsing conventions, compat pointer conversion, old 32-bit time support, and shared-memory alignment constants such as `SHMLBA`/`COMPAT_SHMLBA`.

## Risks and Edge Cases

The risk is ABI compatibility. The multiplexer must preserve historical argument packing, including `SEMCTL` reading an indirect argument, old `MSGRCV` kludge handling, `SHMAT` returning an address through `third`, and rejecting unsupported version-1 `SHMAT`. Compat paths must reject negative ids/sizes where required and avoid truncating returned attach addresses incorrectly.

## Test Signals

Tests should run old `ipc()` syscall variants where supported for all SysV IPC families, including old and new `MSGRCV`, indirect `SEMCTL`, `SHMAT` out-address storage, invalid operation numbers, unsupported time configurations, and compat 32-bit userland behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/ipc/syscall.c -->
