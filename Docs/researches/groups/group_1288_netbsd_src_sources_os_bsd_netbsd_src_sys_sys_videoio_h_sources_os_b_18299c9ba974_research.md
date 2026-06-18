# Group Research: group_1288_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_videoio_h_sources_os_b_18299c9ba974

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/netbsd-src` tree. All 19 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/videoio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/videoio.h

Read completely: 3419 lines.

Defines NetBSD's public V4L2-compatible video ioctl ABI. The file is an imported/adapted `videodev2.h` style header with inlined `v4l2-common.h` and `v4l2-controls.h` content, plus NetBSD ioctl encodings and kernel compatibility pieces.

Core API surface:
- Selection targets and flags cover crop/compose rectangles, defaults, bounds, native size, and legacy subdevice aliases.
- Control IDs span user controls, MPEG/codec controls, camera controls, FM TX/RX, flash, JPEG, image source/processing, DV, RF tuner, and detection classes.
- Core enums define fields, buffer types, tuner types, memory models, colorspaces, transfer functions, YCbCr/HSV encodings, quantization, and priority.
- Structs model V4L2 capabilities, pixel formats, frame size/rate enumeration, timecode, JPEG compression, streaming buffer/plane state, framebuffers/windows, stream parameters, crop/selection, analog standards, DV timings/capabilities, inputs/outputs, controls, tuners/modulators, frequency bands, RDS, audio, MPEG encoder/decoder commands, VBI formats, multi-plane/SDR formats, events, debug chip/register access, and buffer creation.

Format and ioctl coverage:
- Defines a large FOURCC catalog for RGB, greyscale, YUV packed/planar/multiplanar, Bayer, HSV, compressed, vendor-specific, SDR, and touch formats.
- Defines analog TV standard bitmasks and useful combined PAL/NTSC/SECAM/ATSC macros.
- Defines DV timing helpers for blanking/frame dimensions and packed BT.656/BT.1120 timing structs.
- `VIDIOC_*` ioctl constants cover capability query, format negotiation, buffer allocation/queue/dequeue/streaming, standards, inputs/outputs, controls, tuners, crop/selection, ext controls, frame enumeration, encoder/decoder commands, event subscription/dequeue, DV timings, frequency bands, debug register/chip info, and private ioctl range.
- Kernel-only compatibility defines `struct v4l2_buffer50` and `VIDIOC_QUERYBUF50`/`QBUF50`/`DQBUF50` for old timeval layout handling.

Integration notes:
- Uses NetBSD `sys/ioccom.h` `_IO*` macros while preserving Linux/V4L2 structure layouts and numeric constants as much as practical.
- Contains user-pointer fields marked with a local no-op `__user` when not otherwise defined.
- Includes `_KERNEL` conditional time compatibility for old timeval layouts.

Risks and notes:
- This is ABI material: structure packing, integer widths, pointer fields, and ioctl numbers must remain stable for userland and driver compatibility.
- The header intentionally mixes Linux-origin V4L2 semantics with NetBSD types; updates need careful cross-checking against both V4L2 upstream and NetBSD compat handling.
- Several APIs are explicitly deprecated or experimental but remain present for compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/videoio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vmem.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vmem.h

Read completely: 102 lines.

Public interface for NetBSD's `vmem(9)` resource allocator. It declares the opaque `vmem_t` arena type, address/size/flag typedefs, global kernel arenas, import/release callback types, allocation/free routines, diagnostics, and sizing helpers.

Core API:
- Arena creation supports fixed-size import (`vmem_create`) and extended import (`vmem_xcreate`) callbacks, plus parent arenas and quantum/import-size parameters.
- Allocation APIs include normal allocation/free, constrained allocation (`vmem_xalloc`), fixed-address allocation (`vmem_xalloc_addr`), constrained free, free-all, and adding spans.
- Diagnostics include rehash start, `vmem_whatis`, `vmem_print`, and `vmem_printall`.
- Flags distinguish sleep behavior, instant/best fit, bootstrap/populating modes, large/extended import, and private tags.

Integration notes:
- Exposes `kmem_arena`, `kmem_meta_arena`, and `kmem_va_arena` for kernel allocation layers.
- Usable outside `_KERNEL` with `<stdbool.h>` for standalone/test builds.

Risks and notes:
- Callers must pass matching address/size pairs back to the correct arena; the API is low-level and trusts the caller.
- `VM_SLEEP` versus `VM_NOSLEEP` controls blocking behavior and is important in interrupt or lock-sensitive paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vmem.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vmem_impl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vmem_impl.h

Read completely: 159 lines.

Private data structures for the `vmem` allocator implementation. It defines arenas, boundary tags, freelist/hash/list heads, optional quantum-cache backing, and internal initialization helpers.

Core structures:
- `struct vmem` holds locks/CV, flags, import/release functions, free boundary-tag pool, segment list, power-of-two freelists, busy-tag hash table, quantum parameters, arena size/in-use accounting, name, all-arena linkage, and optional qcache state.
- `struct vmem_btag` represents spans/free/busy extents with segment-list linkage, freelist or hash-list linkage, start, size, type, and flags.
- Boundary tag types distinguish dynamic/static spans, free extents, and busy extents.

Kernel versus standalone:
- Kernel builds enable `QCACHE`, include pools, and use `kmutex_t`/`kcondvar_t`.
- Non-kernel builds use libc/assert/errno headers and compile lock/CV declarations away.

Risks and notes:
- Boundary-tag accounting is central to correctness; corrupt tag type/list membership would affect allocator state globally.
- `VMEM_EST_BTCOUNT` documents the expected metadata pressure: roughly two tags per allocation plus two per span.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vmem_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vmmeter.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vmmeter.h

Read completely: 56 lines.

Defines the legacy `struct vmtotal` snapshot of systemwide VM/process totals computed periodically, historically used by VM statistics interfaces.

Fields covered:
- Runnable, disk-wait, page-wait, and sleeping-in-core process counts.
- Total and active virtual memory.
- Total and active real memory.
- Shared virtual/real memory totals and active shared counts.
- Free memory pages.

Risks and notes:
- This is an ABI-style statistics structure with fixed-width signed fields; consumers should treat values as periodic snapshots, not live counters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vmmeter.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vnode.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vnode.h

Read completely: 683 lines.

Central public kernel vnode contract for NetBSD VFS. It defines vnode types/tags, the public `struct vnode`, vnode attribute and permission models, VOP dispatch metadata, vnode operation vector descriptors, and exported vnode/VFS helper APIs.

Core vnode model:
- `enum vtype` covers regular files, directories, devices, symlinks, sockets, FIFOs, bad vnodes, and no-type.
- `enum vtagtype` identifies filesystem family for external tools, including UFS, NFS, LFS, tmpfs, puffs, zfs, nilfs, v7fs, chfs, autofs, and others.
- `struct vnode` contains the UVM object, file size/write size, synchronization state, use/write/hold counts, clean/dirty buffer lists, mount/op-vector references, type/tag/data, vnode kqueue state, and type-specific union data for mountpoints, sockets, devices, FIFOs, or read-ahead context.
- Field comments document lock ownership: vnode interlock, buffer cache lock, UVM object lock, vnode lock, exec lock, filesystem locking, and mount/vnode-list locks.

Flags and attributes:
- `VV_*` flags cover root/system/tty/mapped/MPSAFE state.
- `VI_*` flags cover text/executable/write mappings, resident pages, syncer list membership, and dead-check needs.
- `VU_DIROP` is an underlying-filesystem flag used by LFS directory operations.
- `struct vattr` holds type, mode, ownership, fsid, fileid, size, block size, timestamps, generation, flags, rdev, disk bytes, file revision, and operation flags.
- Kernel `ioflag` bits express sync/direct/journal/append/node-locked/ext-attr behavior and access pattern advice.
- VFS access bits include traditional read/write/exec plus NFSv4-style ACL permissions and derived permission groups.

Dispatch and helper API:
- `struct vnodeop_desc`, `vnodeopv_entry_desc`, and `vnodeopv_desc` describe generated VOP operation offsets, names, vnode argument offsets, returned vnode pointer offsets, credential/componentname offsets, and willrele/willput flags.
- `VCALL`, `VOCALL`, `VDESC`, and `VOFFSET` are the low-level VOP dispatch macros.
- Includes generated `<sys/vnode_if.h>` in kernel builds.
- Declares public vnode lifecycle/cache/sync helpers such as `vref`, `vrele`, `vput`, `vn_lock`, `vgone`, `vflush`, `vinvalbuf`, `vcache_get`, `vcache_new`, `vcache_rekey_*`, `vn_open`, `vn_rdwr`, `vn_readdir`, `vn_stat`, `vn_extattr_*`, and vnode/device helpers.
- Provides vnode kqueue interest helpers `VN_KEVENT_INTEREST` and `VN_KNOTE`.

Risks and notes:
- Lock annotations are part of the contract; VFS and filesystem code must follow them to avoid vnode/buffer/VM races.
- `v_tag` is explicitly for external programs and should not drive kernel behavior.
- VOP descriptor metadata must match generated wrappers and filesystem operation vectors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vnode_if.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vnode_if.h

Read completely: 631 lines.

Generated vnode operation interface header. It is generated from `vnode_if.src` by `vnode_if.sh` and should not be edited directly.

Core contents:
- Declares `vop_default_desc`, one descriptor offset macro per operation, one operation-specific argument structure per VOP, the external descriptor object, and the wrapper prototype.
- `VNODE_OPS_COUNT` is 55.
- Includes non-kernel `<stdbool.h>` compatibility and forward declarations for `struct buf`.

Operation coverage:
- I/O and metadata: `BWRITE`, `OPEN`, `CLOSE`, `READ`, `WRITE`, `FALLOCATE`, `FDISCARD`, `IOCTL`, `FCNTL`, `FSYNC`, `SEEK`, `GETATTR`, `SETATTR`.
- Namespace operations: `PARSEPATH`, `LOOKUP`, `CREATE`, `MKNOD`, `REMOVE`, `LINK`, `RENAME`, `MKDIR`, `RMDIR`, `SYMLINK`, `READDIR`, `READLINK`, `ABORTOP`, `WHITEOUT`.
- Lifecycle and locking: `INACTIVE`, `RECLAIM`, `LOCK`, `UNLOCK`, `ISLOCKED`, `REVOKE`, `PRINT`.
- VM/block integration: `BMAP`, `STRATEGY`, `GETPAGES`, `PUTPAGES`, `MMAP`.
- Policy and event operations: `ACCESS`, `ACCESSX`, `POLL`, `KQFILTER`, `PATHCONF`, `ADVLOCK`.
- ACL and extended attributes: `GETACL`, `SETACL`, `ACLCHECK`, `OPENEXTATTR`, `CLOSEEXTATTR`, `GETEXTATTR`, `LISTEXTATTR`, `DELETEEXTATTR`, `SETEXTATTR`.

Risks and notes:
- This header is part of the generated VOP ABI inside the kernel; descriptor offsets and arg structs must stay synchronized with generated `vnode_if.c` and filesystem operation vectors.
- Several arg structs have version suffixes (`_v2`, `_v3`) reflecting interface evolution while preserving generated names/descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vnode_if.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vnode_impl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/vnode_impl.h

Read completely: 162 lines.

Private vnode implementation header for kernel/kmemuser builds. It wraps the public `struct vnode` in `struct vnode_impl` with cache, LRU, syncer, namecache, state, and lock metadata used by the vnode subsystem.

Core structures:
- `enum vnode_state` models vnode-cache lifecycle: active, marker, loading, loaded, blocked, reclaiming, and reclaimed.
- `struct vcache_key` keys vnodes by mount plus filesystem-provided key bytes.
- `struct vnode_impl` embeds `struct vnode`, vnode-cache key, private `vnode_klist`, LRU/syncer/hash/mount-list linkages, state, namecache tree/list and cached credentials/mode, vnode lock, and namecache locks.
- Conversion macros map between public vnode pointers and implementation objects.

APIs:
- Diagnostic state assertions via `_vstate_assert`, `VSTATE_ASSERT`, and `VSTATE_ASSERT_UNLOCKED`.
- Internal helpers for state names, marker allocation/free/testing, anonymizing cache keys, acquiring cached vnodes, try-acquire, and draining vnodes.
- Declares the `vfs` SDT provider.

Risks and notes:
- Lock annotations document separate vnode-cache, drain, interlock, namecache, mount-list, and syncer locks; ordering matters for deadlock avoidance.
- Marker vnodes are stable special cases and must not be treated like normal filesystem-backed vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/vnode_impl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wait.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/wait.h

Read completely: 217 lines.

Defines process wait status encoding, wait option bits, compatibility `union wait`, and userland wait-family prototypes.

Status model:
- `WIFSTOPPED`, `WIFCONTINUED`, `WSTOPSIG`, `WIFSIGNALED`, `WTERMSIG`, `WIFEXITED`, and `WEXITSTATUS` decode the integer wait status.
- NetBSD/XOpen/kernel-visible additions include `WCOREFLAG`, `WCOREDUMP`, `W_EXITCODE`, `W_STOPCODE`, and `W_CONTCODE`.
- `_WCONTINUED` uses `0xffffU`; stopped status uses low 7 bits equal to `0177`.

Options:
- POSIX options include `WNOHANG`, `WSTOPPED`/`WUNTRACED`, `WCONTINUED`, `WEXITED`, and `WNOWAIT`.
- NetBSD options include `WALTSIG`, `WALLSIG`, `WTRAPPED`, and `WNOZOMBIE`.
- Linux clone compatibility aliases map `__WCLONE` and `__WALL` to NetBSD alternate/all-signal options.
- Kernel option masks define selectable and all valid options.

Compatibility/user API:
- `WAIT_ANY` and `WAIT_MYPGRP` expose special pid values.
- Deprecated `union wait` maps status bits with endian-specific bitfields.
- Userland prototypes expose `wait`, `waitpid`, `waitid`, and NetBSD/XOpen `wait3`, `wait4`, `wait6` with symbol renames for older ABI variants.

Risks and notes:
- The file is ABI-sensitive: bit layout differs by endian for deprecated `union wait`, while macro decoding uses integer status.
- Feature-test macros control which legacy or extension names are visible.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wait.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wapbl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/wapbl.h

Read completely: 278 lines.

Public/private header for NetBSD write-ahead physical block logging (WAPBL). It declares the kernel transaction API, replay API, debug hooks, in-kernel transaction entry structure, deallocation records, and the internal replay state when `WAPBL_INTERNAL` is defined.

Kernel transaction API:
- `wapbl_start` attaches a journal to a mount/log vnode with geometry, replay state, and filesystem flush callbacks.
- `wapbl_stop` tears down logging; `wapbl_discard` drops current in-memory transaction state.
- `wapbl_begin`/`wapbl_end` bracket recursive per-thread transactions.
- `wapbl_add_buf`, `wapbl_remove_buf`, and `wapbl_resize_buf` manage metadata buffers captured by the current transaction.
- `wapbl_flush` commits completed transactions and starts asynchronous metadata writes.
- `wapbl_register_inode`/`unregister_inode` track allocated but unlinked inodes for replay cleanup.
- `wapbl_register_deallocation`/`unregister_deallocation` record block revocations.
- Assertion, print/dump, and `wapbl_biodone` hooks support debugging and buffer I/O completion.

Structures and helpers:
- `struct wapbl_entry` tracks one committed transaction's journal pointer, queue entry, unsynced buffer count, reclaimable bytes, and error state.
- `struct wapbl_dealloc` records revoked block address/length.
- `wapbl_vptomp` maps regular or block vnodes to a mount, using `spec_node_getmountedfs` for block devices.
- `wapbl_vphaswapbl` tests whether a vnode's mount has WAPBL enabled.

Replay API:
- Opaque `struct wapbl_replay` is exposed unless internal details are requested.
- `wapbl_replay_start`, `stop`, `free`, `write`, `can_read`, and `read` manage journal replay and read-through from journaled blocks.
- Internal replay state tracks log/device vnodes, block shifts, circular offsets, generation, scratch buffer, block hash, and pending inode list.

Risks and notes:
- Correctness depends on filesystems registering all metadata buffers, deallocations, and unlinked allocated inodes while inside WAPBL transactions.
- Debug macros compile away unless WAPBL debug printing is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wapbl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wapbl_replay.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/wapbl_replay.h

Read completely: 150 lines.

Defines the on-disk WAPBL journal record layout used by replay. This is the persistent ABI for WAPBL headers, block lists, revocations, and unlinked inode lists.

Journal layout:
- A journal header precedes a circular data region.
- `wc_head` and `wc_tail` are byte offsets from the start of the journal header; both zero means empty, equal nonzero means full.
- Records are tagged with a 32-bit type and length and padded to log device block boundaries.

Record types:
- `WAPBL_WC_HEADER` (`"WABL"`) identifies `struct wapbl_wc_header`.
- `WAPBL_WC_BLOCKS` and `WAPBL_WC_REVOCATIONS` share `struct wapbl_wc_blocklist`.
- `WAPBL_WC_INODES` uses `struct wapbl_wc_inodelist`.

Structures:
- `struct wapbl_wc_header` stores checksum, generation, fsid, timestamp, version, log/fs block shifts, circular head/tail/off/size, and spare payload.
- `struct wapbl_wc_blocklist` stores count plus variable-length block descriptors with disk address and length; block records are followed by logged block data, while revocation records carry no data.
- `struct wapbl_wc_inodelist` stores variable-length inode number/mode pairs and a clear flag to supersede previous inode lists.

Risks and notes:
- Replay safety depends on handling revocations before stale logged data can overwrite blocks reallocated as data.
- Variable-length trailing arrays and on-disk padding require careful length validation when parsing damaged journals.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wapbl_replay.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wchan.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/wchan.h

Read completely: 37 lines.

Defines `wchan_t` as `volatile const void *`, the typed wait-channel identifier used by sleep/wakeup-style kernel synchronization interfaces.

Risks and notes:
- The volatile-qualified opaque pointer expresses identity only; callers should not dereference wait channels.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wchan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wdog.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/wdog.h

Read completely: 109 lines.

Defines the user/kernel ioctl ABI for manipulating watchdog timers.

Core API:
- `WDOG_NAMESIZE` matches device `dv_xname` size.
- `struct wdog_mode` names a watchdog and carries mode plus period in seconds.
- `WDOGIOC_GMODE`, `SMODE`, `WHICH`, `TICKLE`, `GTICKLER`, and `GWDOGS` get/set modes, report the active watchdog, tickle user-tickle watchdogs, report last tickler PID, and enumerate watchdog names.
- `struct wdog_conf` points to a name buffer and count for enumeration.

Modes and features:
- Modes distinguish disarmed, kernel tickle, user tickle, and external tickle.
- Feature bit `WDOG_FEATURE_ALARM` requests audible alarm on expiry.
- `WDOG_PERIOD_DEFAULT` requests a default period; `WDOG_PERIOD_TO_TICKS` converts seconds to `hz` ticks.

Risks and notes:
- `WDOGIOC_GWDOGS` relies on caller-provided buffer sizing of `count * WDOG_NAMESIZE`.
- Only `UTICKLE` mode is tickled by the `TICKLE` ioctl according to the comments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/wdog.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/workqueue.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/workqueue.h

Read completely: 61 lines.

Declares NetBSD's lightweight workqueue API for deferring small work items to thread context.

Core API:
- `struct work` is intentionally tiny so it can be embedded in other structures.
- `struct workqueue` is opaque.
- `workqueue_create` creates a queue with name, callback, callback argument, priority, IPL, and flags.
- `workqueue_destroy`, `workqueue_wait`, and `workqueue_enqueue` manage queue lifetime, wait for a work item, and enqueue work optionally targeted at a CPU.

Flags:
- `WQ_MPSAFE` marks callbacks as MP-safe.
- `WQ_PERCPU` requests per-CPU behavior.
- `WQ_FPU` indicates callbacks may use the FPU.

Risks and notes:
- Because `struct work` contains only a dummy pointer, callers must provide storage/lifetime discipline and avoid enqueueing the same work item unsafely.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/workqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/xattr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/xattr.h

Read completely: 81 lines.

Defines Linux-compatible extended attribute user API declarations layered over NetBSD's extended attribute support, limited by comment to the user namespace for these calls.

Core definitions:
- `XATTR_NAME_MAX` maps to `KERNEL_NAME_MAX`, matching `EXTATTR_MAXNAMELEN` and Linux's 255-byte name maximum.
- `XATTR_SIZE_MAX` is 65536 but explicitly not enforced by NetBSD.
- `XATTR_CREATE` and `XATTR_REPLACE` select create-only or replace-only set semantics.

Userland API:
- Declares path, lpath, and fd variants for set, get, list, and remove: `setxattr`, `lsetxattr`, `fsetxattr`, `getxattr`, `lgetxattr`, `fgetxattr`, `listxattr`, `llistxattr`, `flistxattr`, `removexattr`, `lremovexattr`, and `fremovexattr`.

Risks and notes:
- The Linux-compatible size maximum is advisory in this header; actual filesystem/VFS behavior may differ.
- Declarations are hidden in `_KERNEL` builds.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/xattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/xcall.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/xcall.h

Read completely: 62 lines.

Kernel-only interface for cross-calls, NetBSD's mechanism to invoke functions on other CPUs and wait for completion.

Core API:
- `xcfunc_t` is a two-argument callback.
- `XC_HIGHPRI` and `XC_HIGHPRI_IPL(ipl)` request high-priority cross-calls with encoded IPL.
- CPU bring-up/IPI hooks include `xc_init_cpu`, `xc_send_ipi`, `xc_ipi_handler`, and `xc__highpri_intr`.
- `xc_broadcast` sends to all CPUs, `xc_unicast` sends to one CPU, and both return a ticket waited on by `xc_wait`.
- `xc_barrier` provides a cross-CPU synchronization barrier.
- `xc_encode_ipl` converts IPL into cross-call flags.

Risks and notes:
- Only visible to `_KERNEL`; callbacks must be safe for the requested priority/IPL context.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/xcall.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/Makefile

Read completely: 7 lines.

Kernel include makefile for the UFS-related subtree. It lists `ffs`, `lfs`, `mfs`, `ufs`, and `ext2fs` as subdirectories, sets `INCSDIR` to `/usr/include/ufs`, and includes `<bsd.kinc.mk>`.

Risks and notes:
- This is build-system metadata; changing `SUBDIR` or `INCSDIR` affects which UFS-family headers are installed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs.h

Read completely: 757 lines.

Main kernel header for CHFS, NetBSD's flash-oriented filesystem. It defines mount state, eraseblock/node reference structures, vnode-cache structures, fragment/read-inode helpers, allocation constants, inline flash operation wrappers, and prototypes for the CHFS implementation files.

Core model:
- CHFS pads node lengths to 4-byte boundaries and stores node state in the low two bits of node-reference offsets.
- Vnode cache states track unchecked, checking, present, absent, GC, reading, and clearing states.
- Eraseblock states distinguish free, clean, partially dirty, and all-dirty blocks.
- Node error constants identify bad magic, CRC, and name CRC conditions.

In-memory structures:
- `struct chfs_node_ref` points to on-media nodes by logical eraseblock number and offset; refs are allocated in blocks with sentinel values for empty and linked ref blocks.
- `node_next` walks ref blocks, following `REF_LINK_TO_NEXT` and stopping at `REF_EMPTY_NODE`.
- `struct chfs_dirent` is the in-memory directory entry with node ref, version, target vnode number, name hash, type, name length, and flexible name storage.
- Temporary data-node and read-inode structs support reconstruction of inode fragment trees from scanned media.
- `struct chfs_full_dnode` and `struct chfs_node_frag` represent full data nodes and fragments in rb trees.
- `struct chfs_vnode_cache` links vnode, data-node, and dirent refs, stores version/link/parent/state metadata, and holds scan-time dirent lists.
- `struct chfs_eraseblock` tracks logical eraseblock number, queue membership, unchecked/used/dirty/free/wasted sizes, node-ref bounds, and GC cursor.
- `struct chfs_mount` owns the mount pointer, eraseblock handler, version counters, vnode-cache hash, eraseblock array and queues, global size counters, reserved-block thresholds, GC thread state, write buffer state, pools, locks, and filesystem block constants.

Queues and allocation policy:
- Eraseblocks move through free, clean, dirty, very-dirty, erasable-pending-wbuf, and erase-pending queues.
- Allocation modes distinguish normal writes, deletion, and GC.
- Reserved block fields and dirty-space triggers drive ENOSPC/GC behavior.

Declared implementation surface:
- Build/scan/nodeops/malloc/readinode/erase/GC/VFS/vnops/vnode/vnode-cache/wbuf/write/subr functions are declared here.
- Vnode operation vectors `chfs_vnodeop_p`, `chfs_specop_p`, and `chfs_fifoop_p` are exported.
- Inline helpers wrap EBH map/unmap/read/write and log errors.
- `CHFS_PAGES_MAX` reserves 4 MiB worth of pages before allowing CHFS page use.
- `CHFS_ITIMES`, `IMPLIES`, and `IFF` provide small local helper macros.

Risks and notes:
- Several comments flag incomplete or uncertain design points, including old `void *p` placement, bad-block checks, and TODOs around moving declarations.
- Lock-order comments require mountfields before vnode-cache, size, or write-buffer locks.
- Node-reference pointer tagging in low offset bits requires all real offsets to be accessed through `CHFS_GET_OFS`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_args.h -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_args.h

Read completely: 44 lines.

Mount argument header for CHFS.

Core definitions:
- `CHFS_ARGS_VERSION` is 1.
- `struct chfs_args` carries `fspec` and `fl_index`, the index of the flash device in the flash layer.

Risks and notes:
- This is a mount ABI structure; changes require compatibility handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_args.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_build.c -->
# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_build.c

Read completely: 371 lines.

Builds CHFS's in-memory filesystem representation during mount. It computes GC/reservation thresholds, scans eraseblocks, constructs vnode-cache link counts from scanned directory entries, removes unlinked vnode subtrees, frees scan-only dirents, and initializes the write-buffer offset.

Trigger setup:
- `chfs_calc_trigger_levels` reserves two blocks for deletions.
- Write reservation is deletion reservation plus about 2% of flash size, plus 100 bytes per physical eraseblock, rounded to eraseblock size.
- GC trigger, GC merge, very-dirty trigger, and dirty-space ENOSPC thresholds are derived from eraseblock and flash sizes.

Link reconstruction:
- `chfs_build_set_vnodecache_nlink` walks a vnode cache's `scan_dirents`.
- Missing child vnode caches cause the dirent node to be marked obsolete and removed.
- Directory child links set `pvno` and ensure at least one link, while duplicate directory parents are reported as hard links.
- Both child and parent link counts are incremented for live entries.

Unlinked removal:
- `chfs_build_remove_unlinked_vnode` requires `chm_lock_mountfields`.
- It marks all data nodes, dirent nodes, and vnode nodes obsolete, resets each node-ref list back to the vnode-cache sentinel, and clears non-root vnode state to unchecked.
- Scan dirents are removed; child link counts are decremented, and newly linkless children are queued for cascading removal.

Mount build pass:
- `chfs_build_filesystem` runs under `chm_lock_mountfields`.
- Step 1 marks scanning, initializes each eraseblock, skips unmapped LEBs into the free queue, scans mapped eraseblocks, and queues them as free, clean, selected nextblock, closed dirty, or erase-pending depending on scan classification.
- Step 2 marks building and walks every vnode-cache bucket to compute parent/link relationships from scan dirents.
- Step 3 removes vnode caches with zero link count, then drains the cascading unlinked dirent queue.
- Final cleanup frees all remaining scan dirents, removes `vno == 0` refs, marks directory child vnode caches present, asserts scan lists empty, and initializes `chm_wbuf_ofs` from the chosen nextblock or `0xffffffff`.

Risks and notes:
- The file has TODO comments for bad-block handling during erase/write/read and uncertainty about unlinked-list insertion order.
- In the final cleanup path, `notregvc = chfs_vnode_cache_get(...)` is dereferenced without a null check for directory entries with nonzero `vno`.
- Some unknown scan states fall through the default case without changing `err`, so scan error propagation depends on scan return conventions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs_build.c -->