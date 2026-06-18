# Group Research: group_432_freebsd_src_sources_os_bsd_freebsd_src_sys_kern_uipc_mqueue_c_source_0807ae9f80bd

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mqueue.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_mqueue.c

## Purpose
Implements FreeBSD POSIX message queues and the synthetic `mqueuefs` filesystem view. Queues can be accessed through `kmq_*` syscalls without mounting the filesystem, while mounted `mqueuefs` exposes queue names as regular-looking vnode entries whose reads report queue statistics.

## Main Elements
- `mqfs_node`, `mqfs_info`, and `mqfs_vdata`: in-kernel namespace tree, vnode attachments, reference counts, file numbers, ownership/mode metadata, timestamps, and jail-root visibility tags.
- `struct mqueue`: queue state including limits, current messages, total queued bytes, priority-ordered message list, sender/receiver wait counters, select/kqueue state, and optional `mq_notify()` registration.
- `mqfs_init()` / `mqfs_uninit()`: create UMA zones, initialize the single global namespace root, add `.` and `..`, register process-exit cleanup, publish POSIX feature config, and register jail OSD cleanup.
- VFS/vnode operations: mount/unmount/root/statfs, vnode allocation/recycling, lookup/create/remove, inactive/reclaim, access/getattr/setattr, read, and readdir.
- Queue operations: `mqueue_alloc()`, `mqueue_free()`, `mqueue_send()`, `_mqueue_send()`, `mqueue_receive()`, `_mqueue_recv()`, and message copyin/copyout helpers.
- Syscall entry points: `kern_kmq_open()`, `sys_kmq_open()`, `sys_kmq_unlink()`, `kern_kmq_setattr()`, send/receive timed wrappers, and notify wrappers.
- Descriptor operations: `mqueueops` supports poll, kqueue, stat, close/fdclose, chmod/chown, `kinfo_file`, and descriptor passing.
- Notification support: per-process `mqueue_notifier` list, `mq_proc_exit()` cleanup, `SIGEV_SIGNAL`/`SIGEV_THREAD_ID`/`SIGEV_NONE` validation, and one-shot notification delivery.
- `COMPAT_FREEBSD32` wrappers translate `mq_attr`, `timespec`, and `sigevent` layouts and register 32-bit syscall helpers.

## Dependencies And Integration
Integrates VFS, vnode cache, file descriptors, Capsicum rights (`cap_read_rights`, `cap_write_rights`, `cap_event_rights`), audit, jails, process exit eventhandlers, POSIX.1b feature reporting, UMA, taskqueue vnode recycle, select, kqueue, signals, and syscall helper registration. The namespace is global but filters lookup/readdir by jail root.

## Risk Notes
Correctness depends on lock partitioning between the global `mqfs_data.mi_lock` namespace lock and per-queue `mq_mutex`. Queue deletion unlinks names but open descriptors keep node/queue references alive. `mq_notify()` races are handled by rechecking the fd under `FILEDESC_SLOCK` and using per-process notifier cleanup, but signal queue ownership and descriptor reuse remain subtle. Timeout logic uses absolute timespecs and converts to ticks in retry loops; invalid nanoseconds are rejected after an initial nonblocking attempt, matching the file's current behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_mqueue.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_sem.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_sem.c

## Purpose
Implements POSIX kernel semaphores for FreeBSD, including named semaphore lookup by path, anonymous semaphore descriptors, semaphore wait/post/getvalue/destroy syscalls, descriptor metadata operations, MAC hooks, and 32-bit compatibility wrappers.

## Main Elements
- `struct ksem_mapping`: hash dictionary entry mapping a full jail-rooted path and FNV hash to a referenced `struct ksem`.
- Global state: `ksem_dictionary`, `ksem_dict_lock`, `ksem_count_lock`, `sem_lock`, active count `nsems`, and unload guard `ksem_dead`.
- `ksem_ops`: file operation table for semaphore descriptors; read/write/ioctl/poll/kqueue/truncate are invalid, while stat, close, chmod, chown, kinfo, comparison, and descriptor passing are supported.
- Object lifetime: `ksem_alloc()`, `ksem_hold()`, and `ksem_drop()` allocate semaphore state, initialize condition variables and MAC labels, enforce POSIX semaphore count limits, and free on last reference.
- Dictionary operations: `ksem_lookup()`, `ksem_insert()`, and `ksem_remove()` implement named semaphore creation/open/unlink with permission and MAC checks.
- Creation path: `ksem_create()` handles file descriptor allocation, early semid copyout, anonymous vs named objects, jail path prefixing, `O_CREAT`/`O_EXCL`, mode masking, and reference transfer into `finit()`.
- Syscalls: `ksem_init`, `ksem_open`, `ksem_unlink`, `ksem_close`, `ksem_post`, `ksem_wait`, `ksem_timedwait`, `ksem_trywait`, `ksem_getvalue`, and `ksem_destroy`.
- Wait implementation: `kern_sem_wait()` handles trywait, interruptible indefinite waits, absolute timed waits, wait counters, value decrement, and MAC wait checks under `sem_lock`.
- Module setup: registers POSIX.1b semaphore feature values, syscall helpers, 32-bit syscall helpers, hash table, and locks; unload is rejected while semaphores remain active.

## Dependencies And Integration
Uses the file descriptor layer, Capsicum semaphore rights (`CAP_SEM_POST`, `CAP_SEM_WAIT`, `CAP_SEM_GETVALUE`), POSIX.1b configuration, FNV hashing, jail-root path rewriting, MAC framework hooks, condition variables, audit, resource counters, and syscall helper registration.

## Risk Notes
The implementation uses one global `sem_lock` for semaphore value/waiter/metadata operations, so behavior is simple but contended. `ksem_create()` copies the descriptor id to user memory before final object creation to simplify rollback, so later errors must close/drop the provisional fd correctly. Named semaphore unlink removes the dictionary reference while open descriptors continue holding object references. Anonymous semaphores can only be destroyed through `ksem_destroy()` and reject `ksem_close()`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_sem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_shm.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_shm.c

## Purpose
Implements POSIX shared memory objects for FreeBSD, backed by VM objects and exposed as file descriptors. It supports `shm_open2()`, legacy `shm_open()`, unlink, rename/exchange, anonymous objects, largepage objects, sealing, file-like read/write/truncate/fallocate/fspacectl operations, mmap integration, and kernel mappings.

## Main Elements
- `struct shm_mapping`: named-object dictionary entries mapping full jail-rooted paths and FNV hashes to referenced `struct shmfd` objects.
- `shm_ops`: file operation table for shared memory descriptors, including read/write, truncate, ioctl, stat, close, chmod/chown, seek, mmap, seals, fallocate, space deallocation, sendfile, kinfo, comparison, and descriptor passing.
- VM I/O: `uiomove_object_page()` and `uiomove_object()` move data between uio and VM object pages; sparse reads can return `zero_region` without instantiating pages.
- Pager hooks: custom swap pager callbacks track resident/swap-backed page accounting in `shm_pages`; physical pager callbacks implement largepage populate/haspage/destructor behavior and largepage counters.
- Truncation: `shm_dotruncate_locked()`, `shm_dotruncate_largepage()`, `shm_dotruncate_cookie()`, and `shm_dotruncate()` enforce grow/shrink seals, kernel mapping constraints, swap reservation, page invalidation, and largepage alignment/allocation policy.
- Object lifecycle: `shm_alloc()`, `shm_hold()`, `shm_drop()`, and `shm_access()` allocate swap or physical pager objects, initialize timestamps/rangelocks/MAC labels, assign synthetic inode numbers, and release VM backing on last reference.
- Namespace operations: `shm_lookup()`, `shm_insert()`, `shm_remove()`, `shm_doremove()`, `shm_remove_prison()`, and `shm_get_path()` manage names, jail cleanup, and object path introspection.
- Open/unlink/rename: `kern_shm_open2()` handles flags, anonymous objects, supplied in-kernel shmfds, `O_CREAT`/`O_EXCL`/`O_TRUNC`, initial sealing policy, largepage selection, Capsicum rejection for named opens in capability mode, and descriptor creation. `sys_shm_rename()` implements no-replace and exchange semantics.
- Mapping paths: `shm_mmap()` computes max protections, write-count handling for writable shared mappings, atime updates, MAC checks, and normal or largepage mapping. `shm_mmap_large()` performs alignment, address selection, MAP_FIXED/MAP_EXCL handling, and direct VM map insertion for physical largepage objects.
- File-like helpers: `shm_read()`, `shm_write()`, `shm_seek()`, `shm_ioctl()`, `shm_stat()`, `shm_chmod()`, `shm_chown()`, `shm_fallocate()`, `shm_fspacectl()`, and `shm_deallocate()`.
- Seals and observability: `shm_add_seals()`, `shm_get_seals()`, `shm_fill_kinfo()`, `sysctl_posix_shm_list`, and `kern_shm_open()`/`sys_shm_open2()` wrappers.

## Dependencies And Integration
Connects file descriptors, Capsicum, audit, jail path rewriting, MAC hooks, VM pager/object/page APIs, swap reservation and per-credential accounting, rangelocks, resource limits, kernel maps, sysctls, `kinfo_file`, FNV hash dictionaries, and largepage/physical memory allocation. `vm_mmap.c` supplies complementary mapping behavior referenced by the file header.

## Risk Notes
This file is a concurrency and VM boundary. Rangelocks serialize read/write/truncate/fallocate/seal-sensitive ranges, while VM object locks protect backing pages and pager metadata. Write seals must reject future writable mappings and fail if existing writable mappings remain. Largepage shm objects are intentionally more restrictive: they require configured page size, aligned sizes/offsets, no private mappings, and currently do not support shrink/free of unmanaged pages. Rename temporarily holds objects while removing and reinserting names to preserve references across rollback and exchange cases.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_shm.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_sockbuf.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/uipc_sockbuf.c

## Purpose
Implements FreeBSD socket buffer primitives: mbuf accounting, readiness tracking, wakeups, buffer reservation, append/compress helpers, record/address/control insertion, front-drop/cut operations, send-pointer helpers, and exported socket-buffer status. It is the common low-level machinery used by socket receive and send paths.

## Main Elements
- Global tuning: `sb_max`, `sb_max_adj`, `sb_efficiency`, and sysctls for maximum socket buffer size and mbuf waste factor.
- Accounting helpers: `sballoc()`, `sbfree()`, and KTLS-specific `sballoc_ktls_rx()` / `sbfree_ktls_rx()` update byte counts, mbuf memory counts, control bytes, ready bytes, first-not-ready pointer, TLS counts, and send pointer cache.
- Readiness model: `sbready()` marks `M_NOTREADY` mbufs or ext-page subranges ready, advances `sb_acc` only when the first blocking mbuf becomes ready, and calls `sbready_compress()` to coalesce newly ready data.
- Wakeups and half-close: `socantsendmore*()`, `socantrcvmore*()`, `soroverflow*()`, `sbwait()`, `sowakeup()`, `sorwakeup_locked()`, and `sowwakeup_locked()` integrate select, kqueue, upcalls, AIO, SIGIO, socket splicing, and KTLS receive checks.
- Buffer reservation: `soreserve()`, `sbreserve_locked_limit()`, `sbreserve_locked()`, `sbunreserve_locked()`, `sbsetopt()`, `sbrelease*()`, and `sbdestroy()` enforce `RLIMIT_SBSIZE`, high/low water marks, autosize flags, and reserved mbuf budget.
- Append paths: `sbappend_locked()`, `sbappend()`, `sbappendstream_locked()`, `sbappendstream()`, `sbappendrecord_locked()`, `sbappendrecord()`, `sbappendaddr*()`, and `sbappendcontrol*()` maintain record chains with `m_nextpkt` and mbuf chains with `m_next`.
- Compression: `sbcompress()` drops empty mbufs, coalesces small writable mbufs where safe, handles `M_EOR`, preserves record and tail invariants, and avoids coalescing not-ready/TLS-session data. `sbcompress_ktls_rx()` appends encrypted TLS RX data to the separate TLS chain.
- Debug invariants: optional `sblastrecordchk()`, `sblastmbufchk()`, and `sbcheck()` validate `sb_lastrecord`, `sb_mbtail`, accounting totals, not-ready placement, and TLS detached data counts.
- Drop/cut helpers: `sbflush*()`, `sbcut_internal()`, `sbdrop*()`, `sbcut_locked()`, and `sbdroprecord*()` remove bytes or records while preserving accounting and special handling for externally referenced not-ready mbufs.
- Send helpers and ancillary data: `sbsndptr_noadv()`, `sbsndptr_adv()`, `sbsndmbuf()`, `sbcreatecontrol()`, and `sbtoxsockbuf()`.

## Dependencies And Integration
Depends on mbuf internals, socket locks, select/kqueue, AIO callback integration, KTLS when enabled, resource accounting, socket upcalls, socket splice dispatch, sysctls, and protocol-level send/receive assumptions. The file is a shared substrate for stream and record-oriented protocols.

## Risk Notes
The central invariant is that `sb_mb`/`sb_lastrecord` describe records while `sb_mbtail` describes the final mbuf in the final record; many helpers panic under debug if this drifts. `M_NOTREADY` complicates accounting because `sb_ccc` includes queued bytes but `sb_acc` only includes visible ready bytes. `sbcut_internal()` must not free externally referenced not-ready mbufs and has special paths for KTLS detached/decryption queues. Wakeup functions intentionally unlock the sockbuf and may call into other subsystems, so callers rely on the documented lock-release behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/uipc_sockbuf.c -->