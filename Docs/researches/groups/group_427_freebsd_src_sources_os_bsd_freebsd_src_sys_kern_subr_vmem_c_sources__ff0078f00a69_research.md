# Group Research: FreeBSD kernel support files in subset A

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All six listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_vmem.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_vmem.c

## Purpose

Implements FreeBSD's `vmem(9)` resource arena allocator. It manages arbitrary address/resource ranges with boundary tags, size-class free lists, busy-tag hashing, optional import/release callbacks, small allocation quantum caches, and kernel debugger/diagnostic inspection.

## Main responsibilities

- Represents arenas with `struct vmem`, protected by an arena mutex/condvar.
- Represents ranges with `struct vmem_btag` boundary tags, typed as span, static span, free, busy, or next-fit cursor.
- Allocates/free resources through:
  - `vmem_alloc()`
  - `vmem_xalloc()`
  - `vmem_free()`
  - `vmem_xfree()`
  - `vmem_add()`
- Supports constrained allocation by alignment, phase, non-crossing boundary, min/max address, and fit strategy.
- Supports `M_BESTFIT`, `M_FIRSTFIT`, and `M_NEXTFIT`.
- Supports resource growth/shrink via `vmem_set_import()` and release callbacks.
- Tracks allocated tags in a hash table and periodically resizes it.
- Provides DDB commands and diagnostic consistency checking.

## Key data structures

- `struct vmem`
  - `vm_seglist`: ordered segment/boundary-tag list.
  - `vm_freelist[VMEM_MAXORDER]`: size-class free lists.
  - `vm_hashlist`: hash table for busy allocations, initially `vm_hash0`.
  - `vm_freetags`: per-arena reserve of unused boundary tags.
  - `vm_cursor`: next-fit cursor.
  - import/release/reclaim hooks and arena accounting.
- `struct vmem_btag`
  - start, size, type.
  - list linkage reused for free-list or busy-hash membership.
- Kernel-only `struct qcache`
  - UMA zone cache for small fixed-size resource allocations.

## Important control flow

- `vmem_init()` initializes locks, lists, hash table, cursor, quantum settings, optional initial static span, and inserts the arena into the global arena list.
- `bt_fill()` ensures enough preallocated boundary tags exist before operations that may split/import ranges.
- `vmem_xalloc()` rounds size to arena quantum, validates constraints, scans size-class free lists, clips a matching free tag, and records it as busy.
- `vmem_xalloc_nextfit()` scans from `vm_cursor`, coalesces around the cursor, and advances the cursor after successful allocation.
- `vmem_import()` asks the backing importer for more range, over-allocating for alignment when needed, then inserts the imported span.
- `vmem_xfree()` finds the busy tag by start address, marks it free, coalesces adjacent free tags, and may release an entire imported span back to the backing provider.
- `vmem_periodic()` walks all arenas to resize busy-tag hash tables, optionally run diagnostics, and wake waiters.

## Kernel integration

- Boot-time arenas include `kernel_arena`, `buffer_arena`, and `transient_arena`, plus `memguard_arena` under `DEBUG_MEMGUARD`.
- Boundary tags are allocated from UMA zone `vmem_bt_zone`.
- On platforms without `UMA_USE_DMAP`, `vmem_bt_alloc()` uses kernel arena address space and backing memory carefully to avoid allocator recursion.
- Small allocations can use UMA zcaches through `qc_init()`, `qc_import()`, and `qc_release()`.

## Filesystem/storage relevance

`vmem` is a foundational kernel resource allocator used by VM, kernel address-space, buffer, and device subsystems. Filesystem paths depend on these arenas indirectly for buffers, KVA-backed I/O, and kernel memory/resource management. The file is not a filesystem implementation, but it is part of the allocation substrate VFS and storage code rely on.

## Edge cases and safeguards

- Allocation constraints are asserted heavily with `MPASS`.
- Waiting allocations panic if they still fail after wait/reclaim/import paths.
- `bt_save()`/`bt_restore()` hide reserved tags while dropping the arena lock.
- Resource zero is avoided in quantum caches because UMA uses `0` as allocation failure.
- `vmem_try_release()` only releases whole imported spans.
- Diagnostic `vmem_check_sanity()` detects corrupt, overlapping, or invalid tags.

## Research notes

This file is mainly allocator infrastructure. For future source-tree-aligned indexing, classify it under kernel memory/resource management with cross-links to VM, buffer cache, and kernel address-space allocation rather than VFS semantics directly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_vmem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_witness.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_witness.c

## Purpose

Implements FreeBSD's WITNESS lock-order verifier. It tracks lock classes, lock acquisition order, held-lock stacks, and known lock-order relationships to detect deadlock-prone lock order reversals, invalid recursion, invalid upgrades/downgrades, sleeping with locks held, and other locking contract violations.

## Main responsibilities

- Enrolls named lock types into `struct witness` records.
- Tracks lock instances held by threads or CPUs.
- Maintains a relationship matrix describing parent/child and ancestor/descendant lock ordering.
- Records lock-order establishment stack traces.
- Detects duplicate lock acquisition and lock-order reversals.
- Provides warnings, panics, debugger entry, sysctls, and DDB commands.
- Encodes static order rules for major kernel subsystems.

## Key data structures

- `struct witness`
  - One per named lock type.
  - Stores name, class, matrix index, refcount, last acquire site, graph counters, and reversal flags.
- `struct lock_instance`
  - Per held lock: lock pointer, source file/line, exclusive/shared state, recursion count, no-release flag, sleepable state.
- `struct lock_list_entry`
  - Chunked list for locks held by a thread or CPU.
- `w_rmatrix`
  - Relationship matrix with parent/child, ancestor/descendant, reversal, hardcoded-order, and known-order bits.
- `struct witness_lock_order_data`
  - Hash-table entry storing stack trace for a direct lock order.
- Static `order_lists`
  - Hardcoded lock order chains for sx locks, mutexes, sockets, routing, multicast, UNIX sockets, UDP/TCP, BPF, NFS, VM, VFS/namecache, ZFS, spin locks, and leaf locks.
- `blessed_list`
  - Known tolerated pairs such as `dirhash`/`bufwait`, `ufs`/`bufwait`, and `tarfs`/`bufwait`.

## Important control flow

- `witness_startup_count()` computes early boot memory needed for witness objects and matrix storage.
- `witness_startup()` initializes WITNESS, preloads static order lists, enrolls pending locks, initializes hash tables, and enables runtime checking.
- `witness_init()` validates lock flags against lock class capabilities and enrolls or defers lock witness setup.
- `witness_checkorder()` is the core verifier:
  - Rejects sleep-lock acquisition while in critical/spin context.
  - Checks recursive shared/exclusive mismatches.
  - Validates interlock expectations.
  - Checks recently held and all held locks against the lock graph.
  - Records new orders and reports reversals with stack traces.
- `witness_lock()` records a lock as held.
- `witness_unlock()` validates unlock mode, handles recursion, rejects forbidden release, and removes the instance.
- `witness_upgrade()` and `witness_downgrade()` enforce upgradable sleep-lock semantics.
- `adopt()` and `itismychild()` add direct lock-order edges and propagate transitive ancestor/descendant relationships.
- `witness_warn()` reports locks held at unsafe sleep/blocking points.
- `witness_assert()` and `witness_is_owned()` support lock assertion checks.

## Debug and observability

- Sysctls under `debug.witness`:
  - `watch`
  - `kdb`
  - `trace`
  - `skipspin`
  - `output_channel`
  - `fullgraph`
  - `badstacks`
- DDB commands:
  - `show locks`
  - `show alllocks`
  - `show witness`
  - `show badstacks`
- Verbose graph reporting walks lock chains and prints stack traces for known order paths.

## Filesystem/storage relevance

This file is central to safe VFS and filesystem locking. The hardcoded order lists explicitly include VFS, namecache, vnode interlock, mount mutex, UFS/tarfs blessed buffer-lock interactions, VM object/page locks, and ZFS lock names. It does not implement file I/O, but it guards correctness of filesystem and VM lock ordering.

## Edge cases and safeguards

- WITNESS disables itself on witness object or lock-list exhaustion.
- Spin-lock tracking is optional via `witness_skipspin`.
- Graph generation counters help sysctl reporting restart if the lock graph changes.
- Some checks are done lockless first for performance, then repeated under `w_mtx`.
- The matrix has consistency checks for paradoxical ancestor/descendant states.
- `witness_watch = -1` permanently disables WITNESS until reboot.

## Research notes

Classify this as kernel lock verification infrastructure. For filesystem research, its most important sections are the hardcoded VFS/namecache/VM/ZFS order lists, blessed filesystem-buffer lock pairs, and public assertion/warning APIs used by lock primitives.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/subr_witness.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_capability.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_capability.c

## Purpose

Implements FreeBSD Capsicum capability mode and file-descriptor capability rights enforcement syscalls. It provides process sandbox entry/query and descriptor rights limiting/querying for general rights, ioctl command subsets, and fcntl command subsets.

## Main responsibilities

- Enter/query Capsicum capability mode:
  - `sys_cap_enter()`
  - `sys_cap_getmode()`
- Check descriptor rights:
  - `cap_check()`
  - `cap_check_failed_notcapable()`
- Convert mmap rights to VM protection:
  - `cap_rights_to_vmprot()`
- Limit and query file descriptor rights:
  - `kern_cap_rights_limit()`
  - `sys_cap_rights_limit()`
  - `sys___cap_rights_get()`
- Limit and query ioctl command rights:
  - `cap_ioctl_check()`
  - `kern_cap_ioctls_limit()`
  - `sys_cap_ioctls_limit()`
  - `sys_cap_ioctls_get()`
- Limit and query fcntl command rights:
  - `cap_fcntl_check_fde()`
  - `cap_fcntl_check()`
  - `sys_cap_fcntls_limit()`
  - `sys_cap_fcntls_get()`

## Compile-time modes

- With `CAPABILITY_MODE`, process credentials can be marked with `CRED_FLAG_CAPMODE`.
- Without `CAPABILITY_MODE`, cap mode syscalls return `ENOSYS`.
- With `CAPABILITIES`, descriptor rights limiting and checking is active.
- Without `CAPABILITIES`, capability descriptor syscalls return `ENOSYS`.

## Important control flow

- `sys_cap_enter()` creates/copies credentials, sets `CRED_FLAG_CAPMODE`, swaps process credentials under `PROC_LOCK`, and frees the old credential.
- `_cap_check()` verifies requested rights are contained in held rights and optionally emits ktrace capability-failure records.
- `kern_cap_rights_limit()` requires the requested rights to be a subset of current rights, updates `fde_rights`, clears ioctl/fcntl filters if the corresponding general right is removed, and uses `seqc_write_begin/end`.
- `sys_cap_rights_limit()` copies in versioned rights safely, validates version and rights shape, normalizes old version bits, audits, and delegates to the kernel helper.
- `sys___cap_rights_get()` copies current rights out, rejecting old-version requests if unknown higher-version rights are present.
- `kern_cap_ioctls_limit()` replaces an fd's allowed ioctl list only if it is a subset of the old list.
- `sys_cap_ioctls_get()` returns either a copied command list or `CAP_IOCTLS_ALL`.
- `sys_cap_fcntls_limit()` restricts fcntl rights by subset only.

## Filesystem/storage relevance

Capsicum controls what file descriptors may do. This affects VFS and filesystem operations by gating read, write, mmap, ioctl, fcntl, truncate, event polling, and similar descriptor operations at the fd layer. Filesystem code typically sees already-authorized operations, while this file enforces descriptor delegation boundaries.

## Edge cases and safeguards

- Capability rights can only be reduced, not expanded.
- ioctl list length is capped by `IOCTLS_MAX_COUNT`.
- Versioned rights copyin checks detect races or malformed user rights.
- Descriptor updates occur under filedesc locks and seqc write sections.
- Capability failure tracing integrates with ktrace.
- `trap_enotcap` sysctl controls SIGTRAP delivery behavior for `ECAPMODE`/`ENOTCAPABLE`.

## Research notes

Classify as security/sandbox descriptor-rights infrastructure. It is important context for syscall files such as `sys_generic.c`, which calls `fget_*()` with specific capability rights for read/write/ioctl/poll paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_capability.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_eventfd.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_eventfd.c

## Purpose

Implements FreeBSD's `eventfd` file type: a passable kernel file object containing a 64-bit event counter with read, write, poll, kqueue, stat, close, and kinfo support.

## Main responsibilities

- Create an eventfd-backed `struct file` via `eventfd_create_file()`.
- Provide reference management through `eventfd_get()` and `eventfd_put()`.
- Provide signaling through `eventfd_signal()`.
- Implement file operations:
  - `eventfd_read()`
  - `eventfd_write()`
  - `eventfd_ioctl()`
  - `eventfd_poll()`
  - `eventfd_kqfilter()`
  - `eventfd_stat()`
  - `eventfd_close()`
  - `eventfd_fill_kinfo()`

## Key data structures

- `struct eventfd`
  - `efd_count`: 64-bit counter.
  - `efd_flags`: creation flags such as `EFD_NONBLOCK` and `EFD_SEMAPHORE`.
  - `efd_sel`: `select`/`poll`/kqueue notification state.
  - `efd_lock`: mutex protecting state.
  - `efd_refcount`: lifetime management.
- `eventfdops`
  - File operation vector for `DTYPE_EVENTFD`.
- `eventfd_rfiltops` and `eventfd_wfiltops`
  - kqueue filters for readability and writability.

## Important control flow

- `eventfd_create_file()` allocates and initializes the object, maps nonblocking flags to file flags, and calls `finit()`.
- `eventfd_read()` blocks until count is nonzero unless nonblocking. It either returns/decrements `1` in semaphore mode or returns the full count and resets it to zero.
- `eventfd_write()` copies in a 64-bit count, rejects `UINT64_MAX`, blocks if adding would overflow the allowed counter range, and wakes waiters after adding.
- `eventfd_signal()` increments by one unless already saturated at `UINT64_MAX`, then wakes waiters.
- `eventfd_poll()` reports readable when count is nonzero and writable when count is below `UINT64_MAX - 1`.
- kqueue filters expose read data as current count and write data as remaining writable capacity.
- `eventfd_put()` drains selection state, destroys knote list and mutex, then frees when refcount reaches zero.

## Filesystem/storage relevance

This is not a filesystem implementation, but it is a special descriptor type that participates in the same descriptor, poll/select, kqueue, and process file table infrastructure as regular files. It is also exposed through `sys_generic.c` via `SPECIALFD_EVENTFD`.

## Edge cases and safeguards

- Static assertions require `EFD_CLOEXEC == O_CLOEXEC` and `EFD_NONBLOCK == O_NONBLOCK`.
- Reads/writes require at least `sizeof(eventfd_t)` bytes.
- Write of `UINT64_MAX` is invalid.
- Nonblocking write rollback restores `uio_resid` before returning `EAGAIN`.
- `FIONBIO` and `FIOASYNC` are accepted as no-op ioctls.
- `eventfd_stat()` reports FIFO-like mode.

## Research notes

Classify as kernel special-file descriptor implementation. Cross-reference with `sys_generic.c` `kern_specialfd()` and polling/select support.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_eventfd.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_generic.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_generic.c

## Purpose

Implements many generic FreeBSD file-descriptor syscalls and helpers: read/write families, truncate, ioctl, space allocation/deallocation, special file descriptor creation, select/pselect, poll/ppoll, selinfo wakeups, `kcmp`, and extended-error reporting.

## Main responsibilities

- Generic read paths:
  - `sys_read()`, `sys_pread()`, `sys_readv()`, `sys_preadv()`
  - `kern_readv()`, `kern_pread()`, `kern_preadv()`
  - `dofileread()`
- Generic write paths:
  - `sys_write()`, `sys_pwrite()`, `sys_writev()`, `sys_pwritev()`
  - `kern_writev()`, `kern_pwrite()`, `kern_pwritev()`
  - `dofilewrite()`
- File sizing and allocation:
  - `kern_ftruncate()`
  - `kern_posix_fallocate()`
  - `kern_fspacectl()`
- Ioctl:
  - `sys_ioctl()`
  - `kern_ioctl()`
- Special descriptors:
  - `kern_specialfd()`
  - `sys___specialfd()`
- Event wait APIs:
  - `kern_select()`, `sys_select()`, `sys_pselect()`
  - `kern_poll()`, `kern_poll_kfds()`, `sys_poll()`, `sys_ppoll()`
  - select/poll registration and wakeup helpers.
- Utility:
  - `kern_posix_error()`
  - `kern_kcmp()`, `file_kcmp_generic()`
  - extended error setup/copyout/debug printing.

## Key data structures

- `struct seltd`
  - Per-thread select/poll tracking, condition variable, pending/rescan flags, and reusable `selfd` slots.
- `struct selfd`
  - A registration linking one thread wait to one `selinfo`.
- `M_IOCTLOPS`, `M_SELECT`, `M_IOV`, `M_SELFD`
  - Allocation types for ioctl buffers, select buffers, iovecs, and select fd registrations.

## Important read/write behavior

- Single-buffer syscalls construct a one-element `uio`; vector syscalls use `copyinuio()`.
- `fget_read()`/`fget_write()` enforce fd validity and Capsicum rights.
- Positioned I/O requires `DFLAG_SEEKABLE`, except negative offsets are allowed only for character vnodes.
- `dofileread()` and `dofilewrite()` set `uio_rw`, `uio_offset`, and `uio_td`, call fileops, handle short transfers interrupted by restartable errors, emit ktrace records, and set `td_retval[0]`.
- `dofilewrite()` sends `SIGPIPE` on `EPIPE` for non-socket file types.

## Ioctl behavior

- `sys_ioctl()` validates the encoded ioctl direction/size, uses a stack buffer for small payloads, copies data in/out, and delegates to `kern_ioctl()`.
- `kern_ioctl()` handles descriptor close-on-exec operations directly, enforces Capsicum ioctl command rights, holds the file, validates read/write mode, handles `FIONBIO`/`FIOASYNC` file flag synchronization, and otherwise calls `fo_ioctl()`.

## Space-management behavior

- `kern_ftruncate()` requires nonnegative length and writable descriptor.
- `kern_posix_fallocate()` checks offset/length/wrap, requires seekable writable file, and calls `fo_fallocate()`.
- `kern_fspacectl()` currently supports `SPACECTL_DEALLOC`, validates ranges/flags, requires seekable writable file, calls `fo_fspacectl()`, and suppresses restart errors after partial progress.

## Select/poll behavior

- `kern_select()` copies input fd sets, handles ABI fd-bit width and endian conversion, validates high bits beyond open fds, computes timeout, initializes per-thread select state, scans descriptors, sleeps, rescans pending selfd registrations, clears registrations, and copies output fd sets.
- `selscan()` registers interest through `selrecord()` after preallocating selfd entries.
- `selrescan()` rechecks only descriptors whose `selinfo` woke the thread.
- `kern_poll()` copies user pollfd arrays into stack or heap buffers, delegates to `kern_poll_kfds()`, then copies `revents` out.
- `pollscan()` and `pollrescan()` mirror the select logic for pollfd arrays.
- `doselwakeup()` removes waiters from a `selinfo`, marks their `seltd` pending, wakes condition variables, and clears `sf_si` with release semantics.
- `seldrain()` uses wakeup logic to drain waiters during object teardown.

## Special descriptor integration

- `kern_specialfd()` creates eventfd and inotify descriptors through type-specific helpers, then installs the file descriptor.
- `sys___specialfd()` validates ABI struct sizes and flags before delegating.
- This file directly connects `sys_eventfd.c` into the generic syscall surface.

## Extended errors and comparison

- `kern_kcmp()` compares file objects, file tables, signal handlers, or vmspaces between processes after permission checks.
- `exterr_set()`, `exterr_copyout()`, and `sys_exterrctl()` manage optional user-visible extended errno metadata.
- `kern_posix_error()` converts internal errno returns to POSIX-style positive return values for `posix_*` syscalls.

## Filesystem/storage relevance

This is a central VFS syscall front end. It does not implement specific filesystems, but it routes read/write/truncate/ioctl/fallocate/deallocate/select/poll requests into file operations (`fo_read`, `fo_write`, `fo_truncate`, `fo_ioctl`, `fo_fallocate`, `fo_fspacectl`, `fo_poll`). Filesystem behavior appears behind these fileops, so this file defines syscall-level validation, capability checks, offset semantics, signal behavior, ktrace/audit hooks, and readiness waiting semantics.

## Edge cases and safeguards

- I/O sizes are capped by `IOSIZE_MAX`; LP64 has sysctls to clamp to `INT_MAX`.
- `select_check_badfd()` preserves historical `EBADF` behavior for bits set beyond open descriptors.
- Poll array length is bounded by `kern_poll_maxfds()`.
- `select`/`poll` convert `ERESTART` to `EINTR` and `EWOULDBLOCK` to success timeout.
- Selection registration uses preallocated `selfd` entries to avoid allocation after fileops have begun polling.
- Wakeup/free races are handled with selinfo locking and atomic load/store ordering around `sf_si`.

## Research notes

Classify this as generic fd syscall and event-wait infrastructure. It is one of the highest-value syscall boundary files for filesystem behavior because it defines how user I/O requests become VFS/fileops calls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_generic.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_getrandom.c -->
# File Research: sources/os/bsd/freebsd-src/sys/kern/sys_getrandom.c

## Purpose

Implements the `getrandom(2)` syscall wrapper over FreeBSD `random(4)` output using a `uio` and Linux-compatible flag handling.

## Main responsibilities

- Validate `getrandom` flags and buffer length.
- Translate `GRND_INSECURE` into nonblocking behavior.
- Build a user-space read `uio`.
- Call `read_random_uio()`.
- Return the number of bytes copied in `td_retval[0]`.

## Important behavior

- Valid flags are `GRND_NONBLOCK`, `GRND_RANDOM`, and `GRND_INSECURE`.
- Unknown flags return `EINVAL`.
- `buflen > IOSIZE_MAX` returns `EINVAL`.
- Zero-length requests return success with `td_retval[0] = 0`.
- `GRND_RANDOM` is accepted but not specially differentiated here.
- `GRND_INSECURE` is intentionally treated as `GRND_NONBLOCK` rather than returning pre-seeding random output.
- The file asserts `EWOULDBLOCK == EAGAIN` for Linux API compatibility naming.

## Security rationale

The comments explicitly reject producing insecure pre-seeding kernel random output, even for Linux-compatible `GRND_INSECURE`, because doing so could leak entropy about the initial seed and provide low-entropy bytes from a security-oriented API. Returning `EAGAIN` under nonblocking conditions is preferred.

## Filesystem/storage relevance

This file is not filesystem-specific. It is generic syscall infrastructure and shares the same syscall/uio/copyout style seen in file I/O paths. It matters to subset A mostly as adjacent kernel syscall plumbing, not as VFS behavior.

## Research notes

Classify as random syscall wrapper. Cross-reference with `sys_generic.c` for similar `uio` construction and `IOSIZE_MAX` validation patterns.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/kern/sys_getrandom.c -->