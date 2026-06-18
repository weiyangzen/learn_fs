# Group Research: group_318_dragonflybsd_sources_os_bsd_dragonflybsd_sys_sys_tree_h_sources_os_b_e68774becc96

Scope: `Docs/research_subset_a.md`; all listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tree.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/tree.h

## Summary
Generic intrusive splay-tree and red-black-tree macro framework used throughout DragonFly BSD kernel and user-visible code.

## Main Responsibilities
- Defines `SPLAY_HEAD`, `SPLAY_ENTRY`, generated prototypes, generated insert/remove/find/next/min/max routines, and traversal macros.
- Defines `RB_HEAD`, `RB_ENTRY`, generated red-black insert/remove/find/scan/next/prev/min/max routines, and traversal macros.
- Adds DragonFly-specific red-black scan tracking through `rbh_inprog` so scanned nodes can be deleted while a scan is active.
- Provides extended red-black lookup generators for exact numeric keys, relative numeric lookups, ranged lookups, and custom comparator lookups.

## Important Behavior
Splay operations move accessed nodes toward the root and mutate the tree on lookup. Red-black operations preserve parent/color metadata and support optional `RB_AUGMENT()` hooks during rotations and parent updates. Kernel builds use `rb_spin_lock()`/`rb_spin_unlock()` around scan-info manipulation; non-kernel builds compile scan locking away.

## Risks
This is macro-generated container code with intrusive node fields, so comparator consistency, field names, and duplicate-key handling are entirely caller-controlled. `RB_INIT()` clears root and in-progress scan state but does not initialize the embedded spinlock, so callers must use a valid initialization pattern for kernel scan locking.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tty.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/tty.h

## Summary
Defines DragonFly BSD tty core structures, tty/clist state flags, buffering constants, sleep-address helpers, and kernel tty API prototypes.

## Main Responsibilities
- Defines `struct clist` as a linear character queue with count, max count, head offset, and data buffer.
- Defines kernel-visible `struct tty`, including raw/canonical/output queues, pgrp/session ownership, kqueue state, termios state, watermarks, callbacks, and reference tracking.
- Declares tty state flags such as open/carrier/busy/input blocked/output stopped/zombie/snoop/registered.
- Declares kernel helpers for clists, termios setup, tty read/write/open/close/ioctl, session cleanup, sleeps, wakeups, and registration.

## Important Behavior
The tty object combines device-driver callbacks (`t_oproc`, `t_stop`, `t_param`, `t_unhold`) with line discipline and queueing state. Sleep-channel macros intentionally use distinct addresses inside the tty object to avoid aliasing wakeups.

## Risks
The structure is a shared kernel ABI surface for tty drivers and line disciplines. Many state bits encode historical behavior, and incorrect locking or queue watermark handling can break blocking I/O, pty operation, or terminal session semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/tty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ttycom.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ttycom.h

## Summary
User/kernel tty ioctl ABI definitions.

## Main Responsibilities
- Defines `struct winsize`.
- Defines modem-control bits and tty ioctl numbers for termios, line discipline, pgrp/session, pty packet mode, window size, break/DTR, draining, timestamps, and console/control tty behavior.
- Defines tty line discipline numbers.

## Important Behavior
The ioctl numbers preserve old BSD tty ABI allocation, including compatibility gaps. Pty packet-mode constants encode control events such as flush, stop/start, ioctl changes, and flow-control mode changes.

## Risks
This is a stable ABI header. Renumbering or changing structure layout would break userland utilities, pty consumers, terminal emulators, and compatibility layers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ttycom.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ttydefaults.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ttydefaults.h

## Summary
System-wide default terminal mode and control-character definitions.

## Main Responsibilities
- Defines default input/output/local/control flags and default speed.
- Defines canonical default control characters through `CTRL()`.
- Optionally emits `static const cc_t ttydefchars[]` when `TTYDEFCHARS` is defined.
- Uses a static assertion to ensure the optional default control-character table matches `NCCS`.

## Important Behavior
`TTYDEF_LFLAG` defaults to canonical, signal, extended processing, and echo-related flags. Disabled control characters use `0xff` to avoid depending directly on `_POSIX_VDISABLE`.

## Risks
The optional table is included by macro side effect and then undefines `TTYDEFCHARS`. Consumers must include termios definitions consistently or the default table will not match the active control-character ordering.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ttydefaults.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/types.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/types.h

## Summary
Core DragonFly BSD scalar type definitions shared by kernel and userland.

## Main Responsibilities
- Defines BSD/System V compatibility aliases under visibility gates.
- Defines file, device, ID, time, size, socket, filesystem-count, disk-address, and fixed-point types.
- Defines kernel-only `cdev_t` and `uoff_t`.
- Provides userland `major`, `minor`, and `makedev` macros for `dev_t`.
- Pulls in fd-set/timeval, pthread, stdint, and kernel integer/machine types as appropriate.

## Important Behavior
Several typedefs are guarded by `_FOO_T_DECLARED` macros to coordinate with other public headers. Userland sees `dev_t` as a 32-bit value and kernel code uses `struct cdev *` via `cdev_t`.

## Risks
This header is highly order-sensitive because many other headers depend on the declaration guards. Device-number macros intentionally preserve DragonFly’s cookie-style minor encoding rather than a simple index split.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ucontext.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ucontext.h

## Summary
Userland ucontext API declaration wrapper.

## Main Responsibilities
- Includes machine-independent `_ucontext` definitions.
- Declares `getcontext`, `setcontext`, `makecontext`, and `swapcontext` under BSD or older POSIX visibility.
- Declares DragonFly BSD quick context helpers under BSD visibility.

## Important Behavior
The POSIX context functions are hidden for POSIX.1-2008 and newer unless BSD visibility is enabled, matching their obsolescent status.

## Risks
Context switching APIs are ABI- and architecture-sensitive. The quick variants are nonstandard DragonFly extensions and should not be assumed portable.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ucontext.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ucred.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/ucred.h

## Summary
Kernel credential structure and external credential representation.

## Main Responsibilities
- Defines `struct ucred` with effective/real/saved IDs, groups, uid resource pointers, prison pointer, and system capability restrictions.
- Places `cr_ref` in its own cache-aligned subobject to reduce cacheline ping-pong.
- Defines `NOCRED`, `FSCRED`, and `cr_gid`.
- Defines stable external `struct xucred` and `XUCRED_VERSION`.
- Declares kernel credential allocation, duplication, reference, conversion, and group-membership helpers.

## Important Behavior
The comment explicitly warns against inspecting `cr_uid` directly for superuser checks; privilege decisions should use `priv(9)`.

## Risks
Credential lifetime is reference-counted and shared. Incorrect direct mutation or privilege checks can produce security bugs, and `xucred` layout is externally visible.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/ucred.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/udev.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/udev.h

## Summary
DragonFly udev event/ioctl ABI and kernel helper declarations.

## Main Responsibilities
- Declares kernel helpers to set/delete device property dictionary keys and emit attach/detach events.
- Defines `UDEVPROP` and `UDEVWAIT` ioctls.
- Defines event types, property update/remove keys, filter types, and default udevd listen socket path.
- Defines `struct udev_event` carrying an event type and property dictionary.

## Important Behavior
Kernel builds include queue/conf support and expose `cdev_t`-based helper APIs; userland builds include proplib for `prop_dictionary_t`.

## Risks
The socket path is hard-coded as `/tmp/udevd.socket`. The header’s userland-facing structures depend on proplib types, so consumers must preserve the expected include/visibility environment.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/udev.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/uio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/uio.h

## Summary
Scatter/gather I/O public declarations and kernel uio helper API.

## Main Responsibilities
- Includes `struct iovec` definitions.
- Defines `off_t` and `ssize_t` as needed under visibility guards.
- For kernel structures, includes `struct uio` and declares `UIO_MAXIOV` and `UIO_SMALLIOV`.
- Declares kernel copy/move helpers for uio, buffers, physical pages, and iovec copyin/free.
- Declares userland `readv`, `writev`, `preadv`, and `pwritev`.

## Important Behavior
Kernel code may allocate iovec arrays only when the caller exceeds the small stack-backed threshold. `iovec_free()` frees only when the allocated vector differs from the supplied stack vector.

## Risks
`UIO_MAXIOV` is a hard ABI/resource limit. Incorrect residual/count handling in users of these APIs can corrupt I/O accounting or copy beyond intended ranges.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/uio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/un.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/un.h

## Summary
UNIX-domain socket address and kernel protocol declarations.

## Main Responsibilities
- Defines `sa_family_t` if needed.
- Defines `struct sockaddr_un` with 104-byte path storage.
- Defines BSD-visible `LOCAL_PEERCRED`.
- Declares kernel UNIX-domain socket request/control and rights-passing helpers.
- Defines userland `SUN_LEN()` under BSD visibility.

## Important Behavior
`sockaddr_un.sun_len` includes the terminating null in the initialized length convention. Kernel declarations cover control-message disposal/externalization and peer socket connection.

## Risks
Path storage is fixed-size and historically constrained. `SUN_LEN()` depends on a null-terminated `sun_path`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/un.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/unistd.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/unistd.h

## Summary
Kernel-shared POSIX/BSD option, access, seek, pathconf, rfork, and extended-exit constants.

## Main Responsibilities
- Defines POSIX feature-option values and `_POSIX_VERSION`.
- Defines access-mode constants and seek whence values, including BSD `SEEK_DATA` and `SEEK_HOLE`.
- Defines `_PC_*` pathconf names for POSIX, BSD ACL/capability options, and minimum hole size.
- Defines BSD `rfork()` flags and extended-exit bit encoding.

## Important Behavior
The comments distinguish unsupported features (`-1`), conditionally discoverable features (`0`), and implemented versioned features. Saved IDs are deliberately not advertised despite partial implementation notes.

## Risks
These constants are ABI-visible and must stay aligned with libc, syscall implementations, `<fcntl.h>`, and `<stdio.h>`.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/unistd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/unpcb.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/unpcb.h

## Summary
Protocol control block definitions for UNIX-domain sockets.

## Main Responsibilities
- Defines `struct unpcb` links between sockets, connected peers, referencing sockets, bound address, peer credentials, file-passing state, vnodes, and generation count.
- Defines peer-credential state flags and private implementation flags.
- Defines `struct xunpcb` for diagnostic/export use when socket internals are available.

## Important Behavior
A socket can both reference another socket and be referenced by multiple sockets, so `unp_conn`, `unp_refs`, and `unp_reflink` are separate. Peer credentials may be true peer credentials or cached listen-time credentials depending on flags.

## Risks
The header notes `xunpcb` depends on `<sys/socketvar.h>`. GC and rights-passing fields are delicate because UNIX sockets can carry file references inside control messages.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/unpcb.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/upmap.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/upmap.h

## Summary
Defines mapped per-thread, per-process, and per-CPU kernel/user shared metadata pages.

## Main Responsibilities
- Defines map sizes, versions, element headers, element-length encodings, and element type IDs.
- Defines `/dev/lpmap` thread map fields including signal-blocking coordination and thread title.
- Defines `/dev/upmap` process map fields including runtime ticks, fork ID, pid, vfork indicator, and process title.
- Defines `/dev/kpmap` per-CPU read-only fields including uptime/realtime timespecs, TSC frequency, tick frequency, and fast gettimeofday flag.

## Important Behavior
The header repeatedly warns that absolute field locations can change; userland should scan headers for the desired type and cache only after version validation. `blockallsigs` uses low bits as a nesting count and bit 31 as a pending-signal indicator.

## Risks
This is a shared-memory ABI with explicit atomicity and memory-order expectations. Incorrect userland reads of `sys_kpmap` timestamps can observe torn or stale values unless the documented `upticks` protocol is followed.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/upmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/usched.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/usched.h

## Summary
Userland scheduler control constants and kernel scheduler interface structures.

## Main Responsibilities
- Defines `struct usched`, a scheduler operations table for process acquisition/release, runqueue placement, clock accounting, priority recalculation, fork/exit heuristics, load updates, CPU mask changes, yielding, and CPU migration.
- Defines per-LWP scheduler data union for BSD4 and DragonFly scheduler state.
- Defines scheduler control flags and `usched_set()` operation numbers.
- Declares kernel scheduler instances and scheduler initialization/control functions.

## Important Behavior
The union reserves padding for future expansion and provides scheduler-specific fields while keeping storage embedded in LWP state.

## Risks
Scheduler implementations rely on exact semantics of callbacks and embedded fields. Adding fields or reinterpreting union members can break existing scheduler code and userland `usched_set()` callers.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/usched.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/usched_dfly.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/usched_dfly.h

## Summary
DragonFly scheduler priority, runqueue, and per-CPU scheduler data definitions.

## Main Responsibilities
- Defines priority bands, runqueue counts, priority-per-queue math, nice/estcpu scaling, and estcpu limits.
- Maps generic LWP scheduler data fields to DragonFly-specific names.
- Provides `lptouload()` for estimated per-LWP scheduler load.
- Defines `struct usched_dfly_pcpu` with spinlock, helper thread, queues, queue bitmaps, run count, CPU identity, CPU mask, and topology node.
- Defines per-CPU mask reflection flags.

## Important Behavior
The scheduler uses 32 queues per class, with four priority levels per queue. `uload` is long-sized specifically to avoid overflow on very large process counts.

## Risks
This header assumes access to `struct lwp`, process nice values, cpumasks, and globaldata. Queue bitmap and priority math must remain synchronized with scheduler implementation code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/usched_dfly.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/user.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/user.h

## Summary
Userland compatibility header for programs that need kernel process information structures.

## Main Responsibilities
- Rejects inclusion from kernel builds.
- Forces `_KERNEL_STRUCTURES` so userland sees kernel-structure layouts.
- Includes types, errno, time, resource, credential, iovec/uio, process, lock, VM, pmap, resourcevar, signalvar, PCB, and kinfo definitions.

## Important Behavior
The header explicitly calls itself a hack for user programs that need `kinfo_proc` and related kernel structures.

## Risks
Including this header exposes userland to kernel layout churn and broad transitive dependencies. It should be treated as a compatibility/debugging interface, not a stable high-level API.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/user.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/utsname.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/utsname.h

## Summary
Defines `struct utsname` and `uname()` ABI.

## Main Responsibilities
- Defines `SYS_NMLN` as 32.
- Defines fixed-size fields for system name, node name, release, version, and machine.
- Declares userland `uname()` or kernel global `utsname`.

## Important Behavior
All strings are fixed-width 32-byte fields.

## Risks
The small fixed field size is ABI-visible and can truncate modern version or node strings.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/utsname.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/uuid.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/uuid.h

## Summary
DCE-style UUID structure and kernel/user UUID helper declarations.

## Main Responsibilities
- Defines `struct uuid` with time, clock sequence, and six-byte node fields.
- Defines kernel `uuid_t`, comparison/classification, formatting, parsing, and endian encode/decode helpers.
- Declares userland `uuidgen()`.

## Important Behavior
The structure matches DCE 1.1 source representation rather than an opaque byte array. Kernel helpers distinguish byte-order encoding and decoding.

## Risks
Endian conversion mistakes can produce stable but wrong UUID values across disk/network formats.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/uuid.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/varsym.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/varsym.h

## Summary
Variant symlink data structures and kernel APIs.

## Main Responsibilities
- Defines `struct varsym`, `struct varsyment`, and `struct varsymset`.
- Defines variable levels for process, user, system, and internal prison scope.
- Defines scope masks and maximum name/data/set sizes.
- Declares kernel lookup, creation/replacement, reference drop, set init/clean, and symlink replacement helpers.

## Important Behavior
Variant symlink sets are TAILQ-backed and protected by a lock. Shared variable objects carry a reference count.

## Risks
Substitution length limits are fixed. Incorrect scope-mask handling could leak or hide per-user/process variant symlink values.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/varsym.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vfs_quota.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vfs_quota.h

## Summary
VFS quota control and write-admission declarations.

## Main Responsibilities
- Declares mount quota init/done helpers.
- Declares `vquotactl()` property-list control entry point.
- Exposes `vfs_quota_enabled`.
- Declares vnode-to-mount helper for kernel structures.
- Declares `vq_write_ok()` for uid/gid/delta write checks.

## Important Behavior
The interface uses proplib `plistref` for quota control data and attaches quota lifecycle to `struct mount`.

## Risks
Quota enforcement depends on callers checking write deltas consistently. Missing calls around metadata or delayed allocation paths could bypass accounting.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vfs_quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vfscache.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vfscache.h

## Summary
VFS cache-facing vnode type, tag, and attribute definitions.

## Main Responsibilities
- Defines vnode types such as regular, directory, block/char device, symlink, socket, FIFO, database, and internal.
- Defines external vnode tag identifiers for filesystem families, including HAMMER, HAMMER2, devfs, tmpfs, autofs, and FUSE.
- Defines full `struct vattr` and lightweight `struct vattr_lite`.
- Defines vattr operation flags for null utimes, exclusive create, and UUID validity.

## Important Behavior
`VNOVAL` semantics are described externally in `vnode.h`, but `vattr` fields here are the primary VOP getattr/setattr payload. `vattr_lite` is explicitly tied to fast-path getattr and futimes code.

## Risks
Kernel code must not use `vtagtype` for behavior decisions; comments say tags are for external tools. Any `vattr_lite` layout changes must be synchronized with fast-path users named in the comments.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vfscache.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vfsops.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vfsops.h

## Summary
Defines DragonFly BSD vnode operation argument structures, VOP operation vectors, wrapper prototypes, descriptors, and convenience macros.

## Main Responsibilities
- Defines per-operation argument structures for old path-based VOPs, file operations, metadata operations, VM/page operations, ACL/extattr operations, mount control, allocation, and namecache-based new VOPs.
- Defines `struct vop_ops`, the per-mount vnode operation vector.
- Declares wrapper functions `vop_*()` and lower-level `*_ap()` forwarding entry points.
- Declares descriptor symbols consumed by generated/compiled vnode operation vectors.
- Defines `VOP_*` convenience macros for common kernel call sites.

## Important Behavior
The file strongly requires callers to use wrapper helpers instead of direct vector calls so future/message-based VFS dispatch and cache/journal hooks can interpose. New namecache VOPs use `struct nchandle` as the operational basis, while old VOPs are deprecated and intended only for compatibility glue.

## Risks
This is a central VFS ABI. A visible issue in this file is the `VOP_FDATASYNC` macro expanding through `VOP_FDATASYNC_FP(*(vp)->v_ops, vp, waitfor, flags, NULL)`, which does not match the `VOP_FDATASYNC_FP(vp, waitfor, flags, fp)` macro shape and appears typo-prone. Operation signatures and descriptor offsets must stay exactly synchronized with generated VOP code.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vfsops.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vkernel.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vkernel.h

## Summary
Virtual-kernel process/LWP structures and virtual page-table entry definitions.

## Main Responsibilities
- Defines kernel-only vkernel LWP saved trap/ext frames, active vmspace entry, and small vmspace-entry cache.
- Defines vkernel process state with vmspace red-black tree, token, refs, and virtual CR3.
- Defines `struct vmspace_entry` and deleted-reference flag.
- Declares vkernel inheritance, exit, LWP exit, and trap hooks.
- Defines user/kernel `vpte_t` layout constants and VPTE flag bits.

## Important Behavior
Virtual kernels manage multiple VM spaces inside one process. The VPTE layout varies by `LONG_BIT`, with a four-layer page-table warning and 64-bit `vpte_t` expectation.

## Risks
The RB tree and cache references are lifecycle-sensitive. VPTE frame masks and page-bit math must match architecture page-table expectations or virtual-kernel memory translation breaks.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vkernel.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vmmeter.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vmmeter.h

## Summary
Virtual memory and system activity statistics structures.

## Main Responsibilities
- Defines `struct vmmeter` counters for switches, traps, syscalls, interrupts, VM faults, paging, forks, execs, VM collisions, forwarded interrupts, TLB shootdowns, and lock/wakeup collisions.
- Defines `struct vmstats` for page-size/count, free/reserved thresholds, paging targets, DMA page accounting, and page queue counts.
- Defines `struct vmtotal` five-second systemwide totals.
- Provides optional `PGINPROF` instrumentation arrays.
- Declares kernel rollup functions.

## Important Behavior
The comments state per-CPU `vmmeter` counters roll up into global statistics, while `vmstats` separates mostly fixed data from frequently changing values for cache behavior.

## Risks
Statistics are partly approximate and moving-target oriented. Consumers should not treat all fields as exact instantaneous truth, especially during per-CPU rollup.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vmmeter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vmspace.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vmspace.h

## Summary
User-mode virtualized VM-space control API.

## Main Responsibilities
- Defines control and trap reason constants.
- Declares create/destroy/control operations for separate VM contexts.
- Declares mmap/munmap/mcontrol and positional read/write APIs for managed vmspaces.

## Important Behavior
The header describes support for user-mode DragonFly kernels or similar applications to create and execute code in separate VM contexts.

## Risks
The API exposes low-level VM manipulation to user mode. Callers must correctly handle trapframes/ext frames and memory-control semantics.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vmspace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vnioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vnioctl.h

## Summary
Ioctl ABI for vnode-backed disk pseudo-devices.

## Main Responsibilities
- Defines default config path `/etc/vntab`.
- Defines attach/detach structure `struct vn_ioctl`.
- Defines query structure `struct vn_user` for file-backed and swap-backed vnode disk devices.
- Defines attach/detach, global/unit option, and get-info ioctl numbers.
- Defines debug, clustering, and swap-reservation option flags.

## Important Behavior
`vn_user` uses unions to represent either file-backed device/inode data or swap-backed size/sector-size data, with macros naming the active fields.

## Risks
The comment flags possible jail path disclosure through `vnu_file`. Userland and driver code must agree which union member is meaningful for the current backing mode.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vnioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vnode.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/vnode.h

## Summary
Core vnode structure, vnode flags, I/O flags, vnode lifecycle APIs, and default VOP helper declarations.

## Main Responsibilities
- Defines `struct vnode`, including vnode lock/token/spinlock, I/O tracking, open/write counts, mount and ops vector, mount lists, buffer trees, type/tag, special unions, file size/object, namecache list, reference counts, poll info, resident image pointer, passthrough mount pointer, and last-write timestamp.
- Defines vnode flags, vnode state values, reference-count high bits, vmntvnodescan flags, and I/O flags.
- Defines permission mode bits and `VNOVAL`.
- Declares vnode allocation, lookup/open/read/write/stat/strategy/sync/reclaim/recycle/reference/lock APIs.
- Declares default VOP implementations and compatibility new-VOP helpers.

## Important Behavior
The comments describe the vnode as the center of file activity and document which fields require `v_token`, `v_spin`, or normal vnode locking. `v_ops` is double-indirect so a mount can swap active operation vectors dynamically, e.g. for journaling.

## Risks
This is one of the highest-risk shared kernel structures in the group. Reference counts encode termination/finalization bits, several fields have distinct locking rules, and buffer-tree/namecache/poll fields must be accessed with the correct token or spinlock.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/wait.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/wait.h

## Summary
Wait status macros, wait option flags, idtype definitions, and wait-family declarations.

## Main Responsibilities
- Defines status interpretation macros such as `WIFEXITED`, `WIFSIGNALED`, `WEXITSTATUS`, and BSD `WCOREDUMP`.
- Defines wait option flags including no-hang, stopped, continued, nowait, exited, trapped, and DragonFly/Linux clone support.
- Defines `WAIT_ANY`, `WAIT_MYPGRP`, `id_t`, and Solaris-style `idtype_t`.
- Declares userland wait APIs: `wait`, `waitpid`, `waitid`, `wait3`, `wait4`, and BSD `wait6`.

## Important Behavior
`WIFCONTINUED(x)` is hard-coded to status value `19`, documented as `SIGCONT`. `idtype_t` numeric values are intentionally synchronized with Solaris values.

## Risks
Wait status encoding is ABI-visible. The Solaris-compatible idtype list includes entities without exact DragonFly counterparts, so implementation support must be checked per call.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/wait.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/wdog.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/wdog.h

## Summary
Watchdog kernel registration structure and user ioctl constant.

## Main Responsibilities
- Defines watchdog callback type.
- Defines `struct watchdog` with public driver fields and internal period/list fields.
- Declares kernel register/unregister/disable helpers.
- Defines `WDIOCRESET` ioctl and default period.

## Important Behavior
Drivers provide a max period and callback argument, while the framework manages current period and list linkage internally.

## Risks
The structure warns internal fields should not be touched. Incorrect period handling can disable or misprogram watchdog hardware.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/wdog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/xdiskioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/xdiskioctl.h

## Summary
Minimal ioctl ABI for xdisk attach/detach.

## Main Responsibilities
- Defines `struct xdisk_attach_ioctl` with file descriptor and reserved fields.
- Defines `XDISKIOCATTACH` and `XDISKIOCDETACH`.

## Important Behavior
The reserved array leaves room for ABI extension without changing the ioctl payload size immediately.

## Risks
The attach API passes a raw file descriptor, so kernel-side implementation must validate descriptor type, lifetime, and permissions.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/xdiskioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/xio.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/sys/xio.h

## Summary
Kernel page-list data representation for I/O and mapping operations.

## Main Responsibilities
- Defines `struct xio` with page list, page count, byte offset, byte count, flags, error, and internal page-pointer storage sized from `MAXPHYS`.
- Defines read/write/VM-linear flags.
- Declares initialization, release, uio-copy, user/kernel copy-in/out helpers.
- Provides inline remaining-byte and KVA-offset helpers.

## Important Behavior
XIO represents a byte range over pages but does not track in-progress I/O. Copy routines do not mutate the XIO; callers track offsets.

## Risks
Offsets are relative to the represented dataset, not the first page. Confusing `uoffset`, `xio_offset`, and KVA offset can copy the wrong byte range.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/sys/xio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/Makefile

## Summary
Top-level makefile for DragonFly BSD VFS modules.

## Main Responsibilities
- Lists VFS module subdirectories including fifofs, msdosfs, nfs, procfs, hpfs, ntfs, smbfs, isofs, mfs, udf, nullfs, hammer, tmpfs, autofs, ext2fs, fuse, and hammer2.
- Leaves `SUBDIR_ORDERED` empty to allow concurrent building.
- Includes `bsd.subdir.mk`.

## Risks
Build inclusion is controlled by this subdirectory list. Adding a VFS module elsewhere without updating this makefile can omit it from module builds.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/Makefile -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/Makefile

## Summary
Kernel module makefile for autofs.

## Main Responsibilities
- Sets `KMOD=autofs`.
- Builds `autofs.c`, `autofs_vfsops.c`, and `autofs_vnops.c`.
- Includes `bsd.kmod.mk`.

## Risks
The module depends on `autofs_vnops.c` even though that file is outside this grouped prompt; research of `autofs.c` and `autofs_vfsops.c` needs that context for node and VOP behavior.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.c

## Summary
Implements the autofs control device, automount daemon request queue, trigger retry/cache logic, and shared autofs node tree helpers.

## Main Responsibilities
- Defines `M_AUTOFS`, autofs request/node objcaches, `/dev/autofs` dev ops, global softc, sysctls/tunables, and interruptible signal set.
- Implements RB comparison/generation for autofs node children.
- Implements daemon-ignore detection based on process group of the process using `/dev/autofs`.
- Builds full autofs paths from node ancestry and mountpoint.
- Creates, shares, waits for, times out, retries, and completes automount daemon requests.
- Implements `AUTOFSREQUEST` and `AUTOFSDONE` ioctls.
- Enforces single opener for the autofs device.

## Important Behavior
Trigger requests are keyed by mount/path/key and shared by concurrent waiters. A timeout task marks requests done with `ETIMEDOUT` and wildcard support enabled. Successful requests cache the node for `vfs.autofs.cache` seconds, but failures are deliberately not negatively cached so users can retry immediately.

## Risks
Only one automount daemon instance can open the device; the code relies on stored process group to avoid recursively triggering autofs from automountd descendants. Request taskqueue cancellation/draining occurs while temporarily dropping and reacquiring the softc lock, making refcount/list discipline important.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.h

## Summary
Shared autofs kernel structures, macros, globals, and internal function declarations.

## Main Responsibilities
- Defines root inode and conversion macros for mount and vnode private data.
- Declares autofs caches, softc, dev ops, vnode ops, and debug variable.
- Defines debug/warning print macros.
- Defines `struct autofs_node` for tree nodes, vnode association, cache/wildcard state, callout, retry count, and ctime.
- Defines `struct autofs_mount` for root node, lock, map/mount/options/prefix strings, and inode allocator.
- Defines `struct autofs_request` for daemon queue entries and timeout task.
- Defines `struct autofs_softc` for device, condition variable, lock, request queue, opener state, daemon process group, and request ID allocator.
- Declares trigger/cache/path/flush/node/vnode helpers and RB prototypes.

## Important Behavior
Autofs nodes are organized as RB trees under each parent and are separate from vnode lifetime; `autofs_reclaim()` clears the vnode pointer but nodes are freed by explicit node deletion.

## Risks
The structures mix mount-level locks, node-level vnode locks, condition variables, callouts, and reference-counted request objects. Lock ordering must remain consistent between VOP paths, triggers, and unmount.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_ioctl.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_ioctl.h

## Summary
User/kernel ioctl ABI for the autofs daemon protocol.

## Main Responsibilities
- Defines control path `/dev/autofs`.
- Defines `struct autofs_daemon_request` containing request ID, map name, full path, prefix, key, and mount options.
- Defines `struct autofs_daemon_done` containing request ID, wildcard flag, error, and reserved fields.
- Defines `AUTOFSREQUEST` and `AUTOFSDONE` ioctl numbers.

## Important Behavior
`AUTOFSREQUEST` lets automountd fetch a pending request. `AUTOFSDONE` completes that request and tells the kernel whether wildcard entries may exist, controlling negative caching behavior.

## Risks
All strings are fixed `MAXPATHLEN` buffers. The daemon and kernel must preserve request IDs exactly or completions return `ESRCH` and waiters may time out.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_ioctl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_mount.h -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_mount.h

## Summary
Mount argument ABI for autofs.

## Main Responsibilities
- Defines `struct autofs_mount_info` with user pointers for map source, master options, and master prefix.

## Important Behavior
`autofs_mount()` copies this structure from userland and then copies each pointed-to string separately.

## Risks
The structure contains userland pointers, not embedded strings. Kernel mount code must use `copyin`/`copyinstr` carefully and handle partial failures.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vfsops.c -->
# File Research: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vfsops.c

## Summary
Implements autofs VFS lifecycle operations: module init/uninit, mount, unmount, root lookup, and statfs/statvfs.

## Main Responsibilities
- Initializes global autofs softc, request/node objcaches, condition variable, mutex, and `/dev/autofs` device node.
- Refuses module uninit while the control device is open and destroys device/caches/softc on unload.
- Mounts autofs by copying mount arguments, allocating `struct autofs_mount`, creating the root autofs node, assigning a fsid, and installing vnode ops.
- Handles mount updates by flushing autofs cache state.
- Unmounts by flushing vnodes, completing outstanding requests for that mount with `ENXIO`, deleting all autofs nodes, and freeing mount state.
- Returns a synthetic directory root vnode and zero-capacity statfs/statvfs values.
- Registers the filesystem as synthetic and MPSAFE.

## Important Behavior
Unmount loops until no outstanding request references the mount remain, broadcasting completion and sleeping between checks. Because autofs does not support `rmdir`, unmount force-deletes nested indirect-map nodes bottom-up after vnodes are gone.

## Risks
`autofs_uninit()` frees `autofs_softc` after dropping internal resources and comments note a race with open. Unmount safety depends on preventing new triggerings after `vflush()` and correctly completing all outstanding requests for the mount.
<!-- END FILE RESEARCH: sources/os/bsd/dragonflybsd/sys/vfs/autofs/autofs_vfsops.c -->