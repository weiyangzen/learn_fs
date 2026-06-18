# Group Research: group_1896_xnu_sources_os_darwin_xnu_bsd_vfs_vfs_utfconvdata_h_sources_os_darw_28f1e240d8c0

## Scope

This grouped report covers four files from `sources/os/darwin/xnu/bsd/vfs` in subset A (`sources/os/darwin/xnu`): Unicode conversion data, vnode file operations, extended attribute/default named-stream support, and generated vnode operation descriptors. Each listed source file was read completely.

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_utfconvdata.h -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_utfconvdata.h

## Purpose

`vfs_utfconvdata.h` is a generated/static Unicode data header used by XNU VFS UTF conversion code. It contains no executable logic; it supplies compact lookup tables derived from Core Foundation Unicode decomposition, precomposition, and non-base/combining-character data.

The file exists so kernel filename conversion/normalization code can perform Unicode canonical decomposition, canonical composition, and combining-character classification without depending on Core Foundation at runtime.

## Data Provided

- `__CFUniCharDecompositionTable[]`: `u_int16_t` pairs mapping precomposed BMP code points to packed decomposition-table positions or flags.
- `__UniCharDecompositionTableLength`: computed element-pair count for the decomposition table.
- `__CFUniCharMultipleDecompositionTable[]`: ordered `u_int16_t` sequences used for decompositions that expand into multiple code units, including Latin diacritics, Greek, Cyrillic, Arabic, Indic scripts, Tibetan, Kana voiced/semi-voiced forms, Hebrew presentation forms, and others.
- `__CFUniCharDecomposableBitmap[]`: bitmap/index data for fast checks that a code point is decomposable before doing table lookup.
- `__CFUniCharPrecompSourceTable[]`: `u_int32_t` records keyed by combining marks, carrying packed offsets/counts into destination precomposition tables.
- `__CFUniCharPrecompositionTableLength`: computed pair count for precomposition source records.
- `__CFUniCharBMPPrecompDestinationTable[]`: base-code-point plus precomposed-result pairs for BMP canonical composition.
- `__CFUniCharCombiningBitmap[]`: bitmap/index data identifying combining characters/non-base characters.
- `__CFUniCharCombiningPropertyBitmap[]`: compact combining-class/property table used to order or classify non-base marks.

## Control Flow

There is no control flow in this file. Consumers include it and interpret the table formats. The only computations are compile-time `sizeof(...)` length constants.

## State and Invariants

- The table layout is positional and tightly coupled to the UTF conversion implementation that consumes it. Reordering entries or changing element widths changes semantics.
- `u_int16_t` tables assume BMP-oriented code unit representation for these normalization tables; packed values such as high-bit-prefixed entries are meaningful to the consumer.
- Length constants divide by pair widths, so callers likely iterate by logical mapping records, not raw element count.
- The header has no include guard because it is data intended for direct inclusion in one implementation context rather than a public multi-include interface.

## Dependencies

The file depends only on kernel integer typedefs (`u_int8_t`, `u_int16_t`, `u_int32_t`) being available before inclusion. Its comments identify Core Foundation source headers as the data origin: `CFUniCharDecompData.h`, `CFUniCharPrecompData.h`, and `CFUniCharNonBaseData.h`.

## Risks and Edge Cases

- Unicode correctness depends on the consuming code and this generated data staying in sync. Updating one without the other can silently corrupt filename normalization.
- The data appears static and versioned by the source snapshot, not by an explicit Unicode version marker in the file.
- Because it is mostly numeric data, review must focus on table shape, lengths, and generator provenance rather than individual value semantics.
- Any accidental formatter, sort, or line-wrap change that alters values would be hard to catch without normalization regression tests.

## Research Notes

The entire 1,697-line file was read. No per-file output was generated separately in this pass.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_utfconvdata.h -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_vnops.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_vnops.c

## Purpose

`vfs_vnops.c` implements the file-table-facing vnode operations for Darwin/XNU: open/create with authorization, close, read/write dispatch, stat translation, ioctl/select, pathconf, kqueue vnode filters, and a small internal `vniodesc` API for kernel code to read regular-file vnodes through a persistent descriptor.

It bridges BSD file descriptors and VFS/VNOP interfaces, layering policy checks, file offset serialization, retry handling, compatibility behavior, and event notification around filesystem-provided VNOPs.

## APIs and Entry Points

- Fileops registration: `vnops` with `.fo_read`, `.fo_write`, `.fo_ioctl`, `.fo_select`, `.fo_close`, and `.fo_kqfilter`.
- Open path: `vn_open()`, `vn_open_modflags()`, `vn_open_auth()`, `vn_open_auth_do_create()`, `vn_open_auth_finish()`.
- Close path: `vn_close()`, `vn_closefile()`.
- I/O helpers: `vn_rdwr()`, `vn_rdwr_64()`, `vn_read_common()`, `vn_read()`, `vn_write()`, `vn_read_swapfile()`.
- Offset locking: `vn_offset_lock()`, `vn_offset_unlock()`.
- Attributes and metadata: `vn_stat()`, `vn_stat_noauth()`, `vn_pathconf()`, `vnode_isauthfs()`.
- Device/control dispatch: `vn_ioctl()`, `vn_select()`.
- Kqueue: `vn_kqfilter()`, `filt_vndetach()`, `filt_vnode()`, `filt_vntouch()`, `filt_vnprocess()`, `filt_vnode_common()`, `vnode_readable_data_count()`, `vnode_writable_space_count()`.
- Kernel descriptor API: `vnio_openfd()`, `vnio_close()`, `vnio_read()`, `vnio_vnode()`.

## Control Flow

`vn_open()` and `vn_open_modflags()` prepare a `vnode_attr` and delegate to `vn_open_auth()`. `vn_open_auth()` chooses between create and lookup modes, rewrites namei flags for open semantics, handles `O_NOFOLLOW_ANY`, `O_RESOLVE_BENEATH`, `O_UNIQUE`, named resource forks, data-protection flags, compound open/create VNOPs, and fallback `VNOP_OPEN()`. It updates caller-visible flags: clearing `O_CREAT` when an existing file is opened and clearing `O_TRUNC` when create/compound open already handled truncation.

Create handling uses `vn_open_auth_do_create()`. It authorizes create when compound operations will not do so internally, calls `vn_create()`, recognizes `EKEEPLOOKING` for compound lookup continuation, updates vnode identity for new nodes, drops parent iocounts, and emits create FSEvents when configured.

Open completion calls `vnode_ref_ext()`, MAC open notification, and `kauth_authorize_fileop()`. Error paths close already-opened vnodes, recycle failed shadow streams, drop iocounts, and retry selected races (`ENOENT` after create lookup, `EREDRIVEOPEN`, or reference failure) with bounded retry/yield behavior.

`vn_close()` handles named stream shadow flushes, special-device reference-drop ordering, HFS last-writer fsync behavior, `VNOP_CLOSE()`, content-modified FSEvents, and final vnode reference release.

`vn_rdwr_64()` builds a one-iovec `uio`, performs optional MAC checks, then dispatches to `VNOP_READ()`/`VNOP_WRITE()` or returns zero-filled data for swap-file reads. The file-table `vn_read()` and `vn_write()` paths serialize shared file offsets unless `FOF_OFFSET` is supplied, acquire vnode iocounts from the file reference, apply syscall I/O flags, and update offsets from actual residuals.

`vn_write()` enforces `RLIMIT_FSIZE`, clips writes that would exceed `INT64_MAX` or file-size limits, sends `SIGXFSZ` when no byte can be written, maps fd flags to `IO_*` flags, updates NFS UBC credentials after successful writes, and breaks parent directory leases when file metadata changes.

`vn_stat()` authorizes read attributes/security, then `vn_stat_noauth()` fetches vnode attributes and translates them into `stat` or `stat64`, including type bits, times, allocation blocks, optional file security data, and privileged handling for generation numbers.

`vn_ioctl()` handles generic `FIONREAD`, `FIONBIO`, `FIOASYNC`, `FIODTYPE`, rejects user attempts at `DKIOCSETBLOCKSIZE` and `FSIOC_AUTH_FS`, blocks selected tty revoke ioctls, and otherwise dispatches special files to `VNOP_IOCTL()`.

`vn_kqfilter()` attaches vnode knotes for regular files, FIFOs, and selected character devices, holding the vnode across the knote lifetime and asking filesystems to monitor begin/end events through `VNOP_MONITOR()`. Filter callbacks compute readability/writability, report revoke as EOF/oneshot, and support touch/process paths that detect recycled vnodes by vid.

## State and Invariants

- File offsets are protected by `FG_OFF_LOCKED`/`FG_OFF_LOCKWANT` in `fg_lflags`; regular-file reads/writes keep offset locking longer than non-regular or swap vnodes.
- Open state tracks `did_create`, `did_open`, `need_vnop_open`, `batched`, and `ref_failed`; these determine whether to call `VNOP_CLOSE()` and whether retry is legal.
- `ndp->ni_dvp` must be cleared/dropped before open proceeds past lookup/create; the code panics if it reaches post-lookup with an uncleared parent vnode.
- Compound open support uses `EKEEPLOOKING` plus `NAMEI_CONTLOOKUP` as an explicit continuation protocol with consistency panics for impossible states.
- For special device vnodes, `vnode_rele_ext()` happens before `VNOP_CLOSE()` so device close code can observe use-count state.
- Kqueue filters hold a vnode reference separate from transient iocounts and guard stale detach/process paths with vnode IDs.

## Dependencies

This file depends on XNU VFS/vnode internals, namei, fileglob/fileproc, UBC, MACF, kauth, FSEvents, kqueue, specfs, fifofs, device switch tables, resource limits, signal delivery, data-protection IOCTLs, and filesystem VNOPs such as `VNOP_COMPOUND_OPEN`, `VNOP_OPEN`, `VNOP_CLOSE`, `VNOP_READ`, `VNOP_WRITE`, `VNOP_IOCTL`, `VNOP_SELECT`, `VNOP_ADVLOCK`, `VNOP_PATHCONF`, and `VNOP_MONITOR`.

It also interacts with named-stream/resource-fork support implemented in `vfs_xattr.c`, notably `vnode_flushnamedstream()` and shadow-stream flags.

## Risks and Edge Cases

- Open/create is race-heavy: create races, unlink races, NFS/tty redrive races, compound-open continuation, and vnode reference failures all share cleanup logic.
- `FEXEC` opens retry with `FREAD` for filesystems that reject execute-only opens, which is compatibility-sensitive.
- `O_NOFOLLOW_ANY` cannot be combined with `O_NOFOLLOW`; path-resolution flags are translated into namei flags and must remain consistent with namei semantics.
- Offset clipping for reads/writes around `INT64_MAX` and `RLIMIT_FSIZE` must preserve correct residuals or userspace sees incorrect short I/O behavior.
- Swap-file reads intentionally synthesize zeroes unless encryption-skip flags change the path.
- Kqueue detach/touch/process paths must handle recycled vnodes without leaking vnode holds or using stale pointers.
- The ioctl path deliberately denies some operations from userspace even if a filesystem/device VNOP might accept them.

## Research Notes

The entire 2,392-line file was read. No per-file output was generated separately in this pass.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_xattr.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_xattr.c

## Purpose

`vfs_xattr.c` implements Darwin VFS extended attribute wrappers and default fallback support. It mediates native filesystem xattr VNOPs through security/name validation, supports named streams/resource forks, manages shadow stream files for filesystems without native named streams, and uses AppleDouble sidecar files plus `doubleagentd` for default non-native extended attributes when `CONFIG_APPLEDOUBLE` is enabled.

## APIs and Entry Points

- Public xattr wrappers: `vn_getxattr()`, `vn_setxattr()`, `vn_removexattr()`, `vn_listxattr()`.
- Name helpers: `xattr_validatename()`, `xattr_protected()`.
- Named stream APIs: `vnode_setasnamedstream()`, `vnode_getnamedstream()`, `vnode_makenamedstream()`, `vnode_removenamedstream()`, `vnode_relenamedstream()`, `vnode_flushnamedstream()`, `vnode_verifynamedstream()`.
- Shadow-stream internals: `vnode_setasnamedstream_internal()`, `getshadowfile()`, `default_getnamedstream()`, `default_makenamedstream()`, `default_removenamedstream()`, `is_shadow_dir_valid()`, `get_shadow_dir()`.
- AppleDouble fallback wrappers: `default_getxattr()`, `default_setxattr()`, `default_removexattr()`, `default_listxattr()`.
- DoubleAgent integration: `get_doubleagentd_port()`, `default_getxattr_doubleagent()`, `default_setxattr_doubleagent()`, `default_listxattr_doubleagent()`, `default_removexattr_doubleagent()`.
- Sidecar file helpers: `open_xattrfile()`, `close_xattrfile()`, `remove_xattrfile()`, `make_xattrfile_port()`.

## Control Flow

The public `vn_*xattr()` functions first reject unsupported vnodes and named-stream vnodes where direct xattr calls are invalid. User-originated operations validate UTF-8 names, run MACF checks when configured, and authorize the appropriate `KAUTH_VNODE_*_EXTATTRIBUTES` right. Resource fork xattrs are special: they may use nonzero `uio` offsets, while other attributes reject nonzero offsets.

Each public operation first calls the filesystem native VNOP. On `ENOTSUP`, unless `XATTR_NODEFAULT` is set, the code falls back to default AppleDouble support. Under `DUAL_EAS`, selected `EJUSTRETURN` paths coordinate between native and AppleDouble copies so `XATTR_CREATE`/`XATTR_REPLACE` semantics remain consistent across both backing stores. Successful set/remove operations notify MACF and update multilabel state when needed.

Named streams prefer native filesystem support when `MNTK_NAMED_STREAMS` is set; otherwise only `com.apple.ResourceFork` is implemented by shadow files under `/private/var/run`. Shadow names include kernel-address-permuted vnode identity pieces and `v_id`; shadow directories include `shadow_sequence`. Created stream vnodes are tagged with `VISNAMEDSTREAM`, optionally `VISSHADOW`, linked back to the data vnode as a named-stream parent, and inherit the dyld shared cache flag when relevant.

`getshadowfile()` creates or locates the per-vnode shadow file, copies metadata from the original file when creating it, checks for existing resource fork xattr data, and handles races with existing files or shadow directory removal. `default_getnamedstream()` makes the creator populate the shadow file from the AppleDouble/resource-fork xattr while other callers wait for initialization on the vnode parent channel. `vnode_flushnamedstream()` copies shadow-file data back into the resource fork on close and removes the old resource-fork xattr first because there is no truncate-xattr operation.

`get_shadow_dir()` looks up `/private/var/run`, validates an existing shadow directory, removes invalid entries, and creates a hidden root-owned directory if needed. Validation requires a directory, root ownership, no writable group/other bits, same filesystem as `/private/var/run`, no directory hard links, and no ACLs.

When `CONFIG_APPLEDOUBLE` is enabled, fallback xattr operations get a send right to `doubleagentd`, open or create the AppleDouble `._` sidecar, convert a fileglob to a fileport, drop the vnode iocount before the userspace upcall, call DoubleAgent MIG routines to locate/list/allocate/remove attribute storage, reacquire an iocount, and perform VNOP reads/writes at the offsets DoubleAgent returns.

`open_xattrfile()` finds the sidecar name (`._.` for root directories, otherwise `._<basename>`), blocks sidecar files from having sidecar attributes themselves, uses `DONOTAUTH` because authorization was already performed on the primary vnode, optionally creates the sidecar with inherited ownership/mode, checks owner match, opens and references it, wraps it in a fileglob, and applies advisory locks. `remove_xattrfile()` resolves the sidecar path and removes only if lookup returns the same vnode, avoiding deletion of a raced replacement.

## State and Invariants

- Xattr names must be nonempty valid UTF-8. `xattr_protected()` identifies `com.apple.system.*` attributes as protected by name prefix.
- `XATTR_NOSECURITY` marks trusted kernel paths that bypass user MAC/kauth checks.
- Non-resource-fork xattrs must use zero `uio` offset; resource forks can be read/written with offsets.
- Shadow stream files must be accessed with kernel context to avoid chroot-dependent views of `/private/var/run`.
- Shadow initialization uses `VISNAMEDSTREAM` and `VISSHADOW` flags as readiness/failure signals; waiters sleep on `svp->v_parent`.
- AppleDouble data structures are big-endian/Motorola-aligned and include fixed Finder Info and resource-fork entries plus an attribute header area.
- DoubleAgent fileports are move-send in MIG calls, so the kernel does not retain the send right after the call.
- AppleDouble sidecars are locked shared for reads/lists and exclusive for set/remove layout changes.

## Dependencies

This file depends on XNU VFS/vnode internals, xattr constants, UTF-8 validation, MACF, kauth, namei, vnode identity helpers, VNOP xattr/named-stream operations, AppleDouble constants, fileglob/fileport machinery, Mach host special ports, `doubleagentd` MIG interfaces, and kernel allocation/uio APIs.

It is closely coupled to `vfs_vnops.c` for named stream close/flush behavior and to VFS authorization in `vfs_subr.c`.

## Risks and Edge Cases

- Native and default xattr stores can both exist under `DUAL_EAS`; create/replace/remove semantics depend on carefully probing both stores.
- Shadow streams deliberately create hidden kernel-managed files in `/private/var/run`; directory validation is security-critical.
- Shadow initialization races are subtle: failed creators must mark/wake waiters so another thread can retry.
- Resource fork flushing removes and rewrites the xattr because there is no truncate primitive, so partial-copy failures can affect resource fork persistence.
- The AppleDouble fallback drops vnode iocounts before upcalling to `doubleagentd`; all paths must reacquire and handle vnode identity loss.
- `open_xattrfile()` uses `DONOTAUTH` and relies on prior authorization on the primary vnode, so callers must not expose it as a standalone sidecar access primitive.
- Sidecar removal uses path reconstruction and same-vnode verification to avoid deleting a raced replacement, but failure leaves sidecar cleanup best-effort.
- With `CONFIG_APPLEDOUBLE` disabled, default xattr routines return `ENOTSUP`, changing behavior for filesystems without native xattr support.

## Research Notes

The entire 2,527-line file was read. No per-file output was generated separately in this pass.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vfs_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vnode_if.c -->
# File Research: sources/os/darwin/xnu/bsd/vfs/vnode_if.c

## Purpose

`vnode_if.c` is generated by `vnode_if.sh` from vnode interface definitions. It defines the `struct vnodeop_desc` metadata records for all VNOP operations and publishes the global `vfs_op_descs[]` descriptor array used by XNU VFS operation registration/dispatch code.

It does not implement filesystem behavior. It describes operation names, vnode argument offsets, returned vnode-pointer offsets, component-name/context offsets, and release semantics for the generic vnode operation layer.

## Descriptors and Entry Points

- Default and special descriptors: `vnop_default_desc`, `vnop_strategy_desc`, `vnop_bwrite_desc`, `vnop_verify_desc`.
- Lookup/create/open descriptors: `vnop_lookup_desc`, `vnop_compound_open_desc`, `vnop_create_desc`, `vnop_whiteout_desc`, `vnop_mknod_desc`, `vnop_open_desc`, `vnop_close_desc`.
- Access/attribute/I/O descriptors: `vnop_access_desc`, `vnop_getattr_desc`, `vnop_setattr_desc`, `vnop_read_desc`, `vnop_write_desc`, `vnop_ioctl_desc`, `vnop_select_desc`, `vnop_fsync_desc`.
- Namespace mutation descriptors: `vnop_remove_desc`, `vnop_compound_remove_desc`, `vnop_link_desc`, `vnop_rename_desc`, `vnop_renamex_desc`, `vnop_compound_rename_desc`, `vnop_mkdir_desc`, `vnop_compound_mkdir_desc`, `vnop_rmdir_desc`, `vnop_compound_rmdir_desc`, `vnop_symlink_desc`.
- Directory and lifecycle descriptors: `vnop_readdir_desc`, `vnop_readdirattr_desc`, `vnop_getattrlistbulk_desc`, `vnop_readlink_desc`, `vnop_inactive_desc`, `vnop_reclaim_desc`, `vnop_pathconf_desc`, `vnop_advlock_desc`.
- VM/block/search/copy descriptors: `vnop_allocate_desc`, `vnop_pagein_desc`, `vnop_pageout_desc`, `vnop_searchfs_desc`, `vnop_copyfile_desc`, `vnop_clonefile_desc`, `vnop_blktooff_desc`, `vnop_offtoblk_desc`, `vnop_blockmap_desc`, `vnop_monitor_desc`.
- Xattr descriptors: `vnop_getxattr_desc`, `vnop_setxattr_desc`, `vnop_removexattr_desc`, `vnop_listxattr_desc`.
- Named stream descriptors: `vnop_getnamedstream_desc`, `vnop_makenamedstream_desc`, `vnop_removenamedstream_desc`, enabled under `NAMEDSTREAMS` or marked `VDESC_DISABLED` otherwise.
- Exported descriptor list: `vfs_op_descs[]`, with `vnop_default_desc` first, followed by special cases and all operation descriptors, terminated by `NULL`.

## Control Flow

There is no runtime control flow beyond static initialization. The file builds arrays of vnode-argument offsets using `VOPARG_OFFSETOF(...)` and then initializes one descriptor per VNOP. VFS registration code elsewhere uses `vfs_op_descs[]` to assign operation offsets and interpret argument structures during dispatch/wrapping.

## State and Invariants

- `vnop_default_desc` must remain first in `vfs_op_descs[]`.
- Each `*_vp_offsets[]` array ends with `VDESC_NO_OFFSET`.
- `vdesc_vpp_offset` marks returned vnode-pointer arguments where relevant.
- `vdesc_componentname_offset` and `vdesc_context_offset` allow generic VFS code to find name/context fields without operation-specific knowledge.
- `VDESC_VP*_WILLRELE` and `VDESC_VPP_WILLRELE` flags encode ownership/release expectations for operations such as create, remove, rename, mkdir, symlink, copyfile, and clonefile.
- Named-stream symbols exist regardless of `NAMEDSTREAMS`; when disabled, their descriptors are present but flagged `VDESC_DISABLED`.

## Dependencies

The generated file depends on `sys/mount_internal.h`, `sys/vm.h`, and `sys/vnode_internal.h` for vnode operation argument structures, `struct vnodeop_desc`, descriptor flags, and `VOPARG_OFFSETOF`.

It must remain synchronized with the vnode operation declarations/macros generated from the same interface source; otherwise descriptor offsets and operation wrappers can disagree.

## Risks and Edge Cases

- Manual edits are fragile and explicitly warned against by the file header; regeneration can overwrite local changes.
- Incorrect offset metadata can cause generic VFS code to inspect or release the wrong vnode argument.
- Release flags are part of lifetime correctness. A wrong `VDESC_VP*_WILLRELE` or `VDESC_VPP_WILLRELE` annotation can produce leaks, premature releases, or stale references.
- Descriptor ordering matters to operation registration, especially the default descriptor and special-case descriptors.
- Conditional named-stream descriptors must still export valid symbols when the feature is disabled.

## Research Notes

The entire 1,290-line file was read. No per-file output was generated separately in this pass.
<!-- END FILE RESEARCH: sources/os/darwin/xnu/bsd/vfs/vnode_if.c -->