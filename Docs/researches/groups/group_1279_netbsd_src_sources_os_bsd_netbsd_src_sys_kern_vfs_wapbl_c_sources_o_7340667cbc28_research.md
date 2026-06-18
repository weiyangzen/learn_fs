# Group Research: group_1279_netbsd_src_sources_os_bsd_netbsd_src_sys_kern_vfs_wapbl_c_sources_o_7340667cbc28

Scope checked against `Docs/research_subset_a.md`: subset A includes the complete `sources/os/bsd/netbsd-src` tree. All 13 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_wapbl.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_wapbl.c

Read completely: 3480 lines.

Implements NetBSD's file-system independent write-ahead physical block logging layer, WAPBL. It manages per-mount journal state, transaction admission, metadata buffer capture, log record emission, stable-storage ordering, log truncation, replay discovery, and replay writes.

Core journal model:
- `struct wapbl` tracks the log vnode/device, physical log start, log/fs block shifts, circular log layout, head/tail offsets, transaction buffer accounting, committed-entry accounting, deallocation revocations, unlinked allocated inode tracking, and reusable journal I/O buffers.
- The on-disk log reserves two commit-header blocks, then uses a circular queue for block records, revocation records, and inode-list records.
- `wl_head` is advanced by `wapbl_flush()` as new records are appended; `wl_tail` is advanced by `wapbl_truncate()` when asynchronous metadata writes have completed.
- `head == tail == 0` means empty; `head == tail != 0` means full.

Initialization and teardown:
- `wapbl_start()` validates log geometry, maps the log vnode to a device block with `VOP_BMAP`, sizes in-memory transaction limits, initializes pools/hash tables/event counters, prepares commit headers, allocates journal I/O buffers, optionally preserves replay-discovered unlinked inodes, and writes an initial commit header.
- `wapbl_stop()` forces a flush, refuses to stop with persistent unlinked inodes unless forced, releases buffers and inode tracking, detaches event counters, and destroys locks/CVs.
- `wapbl_discard()` aborts in-memory journal state, invalidates pending locked buffers, clears inode/deallocation tracking, and detaches outstanding committed entries from the live journal.

Transaction path:
- `wapbl_begin()` may force a flush before admitting a reader transaction if buffered bytes, buffer count, computed transaction length, or deallocation count approaches limits.
- `wapbl_end()` asserts the transaction can fit in the usable log and drops the transaction reader lock.
- `wapbl_add_buf()`, `wapbl_remove_buf()`, and `wapbl_resize_buf()` maintain the current transaction's dirty metadata buffer list and byte/count totals.
- `wapbl_register_deallocation()` records block revocations; callers can force over-limit registration only for bounded paths.
- `wapbl_register_inode()` and `wapbl_unregister_inode()` track allocated-but-unlinked inodes so they can survive mount/log transitions.

Flush and ordering:
- `wapbl_flush()` takes the journal writer lock, invokes filesystem flush callbacks, computes transaction length, waits/truncates for space, writes block data records, revocation records, and inode records, then writes a commit header.
- After the commit header is stable, metadata buffers are issued asynchronously with `wapbl_biodone()` as completion handler.
- `wapbl_write_commit()` flushes buffered journal writes, optionally issues `DIOCCACHESYNC`, writes one of two alternating commit headers, flushes again unless FUA is used, and handles generation-zero/rollover by writing a duplicate commit.
- Disk cache behavior is controlled by sysctls for cache flush, verbose commits, DPO/FUA allowance, and journal I/O buffer count.
- `wapbl_buffered_write()` coalesces adjacent journal writes into reusable `MAXPHYS` buffers and tracks asynchronous completion.

Replay support:
- `wapbl_replay_start()` reads both commit headers, selects the newer generation, initializes replay state, builds a hash of final logged physical blocks, and records unlinked inode-list state.
- `wapbl_replay_process()` walks from tail to head, handling `WAPBL_WC_BLOCKS`, `WAPBL_WC_REVOCATIONS`, and `WAPBL_WC_INODES`.
- Block replay uses a hash keyed by filesystem block address; later block records replace earlier ones, and revocations remove blocks from replay.
- `wapbl_replay_write()` writes final logged blocks to the filesystem device.
- `wapbl_replay_can_read()` and `wapbl_replay_read()` let filesystems read blocks from the journal before full replay.

Concurrency and integration:
- Uses a rwlock for transaction readers versus flush/truncate writer operations, a mutex/CV for journal accounting, `bufcache_lock` around buffer queue transitions, and per-mount event counters.
- Integrates with `VOP_STRATEGY`, `VOP_IOCTL(DIOCGCACHE/DIOCCACHESYNC)`, `VOP_BMAP`, buffer cache I/O, module init/fini, sysctl, and filesystem-provided flush/abort callbacks.
- Kernel and non-kernel build paths share replay/log parsing helpers, with userspace allocation/assertion substitutes.

Risks and notes:
- Transaction sizing is conservative but still panics if a transaction exceeds usable log space.
- Several comments flag old assumptions or questionable behavior around circular offsets, VOP_BMAP freshness, inode-only flush skipping, and locking analysis.
- Any write or cache-flush error can permanently error the log until completion/truncation accounting clears or reports it.
- Correct crash consistency depends on strict ordering: journal records stable, commit header stable, then metadata writes.
- DPO/FUA use is disabled by default and gated behind both device cache flags and sysctl policy.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_wapbl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_xattr.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vfs_xattr.c

Read completely: 1306 lines.

Implements NetBSD VFS extended attribute syscall glue. It exposes both the BSD `extattr_*` API and Linux-compatible `xattr` API, converting file descriptors or paths into vnodes and routing operations through vnode extended-attribute operations.

Core helpers:
- `extattr_check_cred()` delegates per-attribute access checks to kauth with `genfs_can_extattr()` as filesystem-independent policy input.
- `vfs_stdextattrctl()` is the default unsupported mount operation and unlocks the optional vnode before returning `EOPNOTSUPP`.
- `extattr_set_vp()`, `extattr_get_vp()`, `extattr_delete_vp()`, and `extattr_list_vp()` lock the target vnode, build `uio` structures when data buffers are present, call `VOP_*EXTATTR`, set syscall return values, and emit ktrace records.

BSD API coverage:
- `sys_extattrctl()` passes mount-level attribute-control commands to `VFS_EXTATTRCTL`, optionally resolving both a controlling path and an attribute backing file.
- Implements fd, file, and symlink-preserving variants for set, get, delete, and list.
- Path variants use `NSM_FOLLOW_NOEMULROOT` for file operations and `NSM_NOFOLLOW_NOEMULROOT` for link operations.
- List operations use `EXTATTR_LIST_LENPREFIX` for the BSD API.

Linux-compatible API:
- `sys_setxattr`, `sys_lsetxattr`, and `sys_fsetxattr` support `XATTR_CREATE`/`XATTR_REPLACE` checks by probing existing attributes before setting.
- `sys_getxattr`, `sys_lgetxattr`, and `sys_fgetxattr` support size-query semantics when the user data pointer is NULL.
- `sys_listxattr`, `sys_llistxattr`, and `sys_flistxattr` concatenate user namespace attributes and system namespace attributes; `EPERM` while listing system attributes is ignored.
- `sys_removexattr`, `sys_lremovexattr`, and `sys_fremovexattr` delete attributes.
- `xattr_native()` maps `system.`, `security.`, and `trusted.` names to `EXTATTR_NAMESPACE_SYSTEM`; `user.` and unrecognized names map to `EXTATTR_NAMESPACE_USER`.
- `XATTR_ERRNO()` maps `EOPNOTSUPP` to Linux-style `ENOTSUP`.

Risks and notes:
- All vnode helpers use exclusive vnode locking even for reads/lists.
- `extattr_delete_vp()` falls back to `VOP_SETEXTATTR(..., NULL, ...)` if `VOP_DELETEEXTATTR` is unsupported.
- Linux list operations can underflow the remaining `size` if a filesystem reports more user-list bytes than the provided size; this relies on VOP list behavior to respect `uio_resid`.
- Namespace mapping is intentionally coarse: Linux `security.` and `trusted.` attributes share NetBSD's system namespace.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vfs_xattr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vnode_if.c -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vnode_if.c

Read completely: 2381 lines.

Generated vnode operation front-end wrappers. The file should not be edited directly; it is generated from `vnode_if.src` by `vnode_if.sh`.

Common wrapper behavior:
- Each `VOP_*` wrapper fills an operation-specific argument structure, calls `vop_pre()`, dispatches through `VCALL(vp, VOFFSET(...), &a)`, and calls `vop_post()`.
- `vop_pre()` takes the big kernel lock for non-`VV_MPSAFE` vnodes and starts filesystem transactions according to the generated `FST_*` mode.
- `vop_post()` ends filesystem transactions for normal/lazy modes and releases the big kernel lock when acquired.
- `VOP_LOCK()` and `VOP_UNLOCK()` have special fstrans handling to match lock acquisition/release semantics.
- Optional `VNODE_LOCKDEBUG` assertions check whether vnode arguments are expected to be unlocked, locked, or exclusively locked.

Vnode operation descriptors:
- Defines `vop_default_desc` and one `vnodeop_desc` per operation.
- Descriptor metadata includes operation offset, printable name, vnode argument offsets, optional output vnode pointer offset, credential offset, componentname offset, and WILLRELE/WILLPUT flags.
- The final `vfs_op_descs[]` table lists all descriptors with default first and NULL terminator.

Covered operations:
- File and directory operations include lookup, create, mknod, open, close, access/accessx, getattr/setattr, read/write, fallocate/fdiscard, fsync, seek, remove, link, rename, mkdir, rmdir, symlink, readdir, readlink, abortop, inactive, reclaim, bmap, strategy, pathconf, advlock, whiteout, getpages, and putpages.
- ACL wrappers cover get/set/check ACL.
- Extended attribute wrappers cover open/close/get/list/delete/set extended attributes.
- Polling, kqueue filter, revoke, mmap, ioctl, fcntl, print, and islocked wrappers are also generated.

Kqueue notification glue:
- Post hooks emit vnode knotes for create, mknod, setattr, ACL changes, link, mkdir, remove, rmdir, symlink, open, close, read, and write.
- Write and setattr hooks compare old size/offset to detect `NOTE_EXTEND`.
- Remove/rmdir special handling may hold the target vnode before the operation so notifications can still be delivered after filesystem code drops references.
- Close notifications suppress meaningless `NOTE_CLOSE` on already-dead/revoked vnodes.

Risks and notes:
- Correctness depends on the generator and `vnode_if.src`; local edits here are disposable.
- Generated lock assertions are diagnostic-only and not complete locking proof.
- The fstrans retry loop handles mount changes across transaction start, but each wrapper's selected `FST_*` mode must match operation semantics.
- Knote post hooks deliberately run after `vop_post()` to reduce time under the big kernel lock.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vnode_if.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vnode_if.sh -->
# File Research: sources/os/bsd/netbsd-src/sys/kern/vnode_if.sh

Read completely: 840 lines.

Generates NetBSD vnode operation front-end source and headers from `vnode_if.src`.

Generated outputs:
- `vnode_if.c`
- `../sys/vnode_if.h`
- `../rump/librump/rumpvfs/rumpvnode_if.c`
- `../rump/include/rump/rumpvnode_if.h`

Parser and input contract:
- Requires one source file argument.
- Extracts the source RCS ID from the first line and embeds both source/script IDs in generated warnings.
- Preprocesses input with `sed` to separate pointer stars from names and replace semicolons with spaces.
- An embedded awk parser recognizes operation blocks beginning with `vop_` and ending with `}`.
- Supports directives `VERSION`, `FSTRANS=`, `PRE=`, `POST=`, and `CONTEXT`.
- Supports argument annotations `LOCKED=EXCL`, `LOCKED=YES`, `LOCKED=NO`, `WILLRELE`, `WILLPUT`, and `WILLMAKE`.

Header generation:
- Emits descriptor offsets, operation argument structures, descriptor declarations, and function prototypes.
- Starts operation offsets at 1 so the default operation is offset 0.
- Emits `VNODE_OPS_COUNT` for kernel headers.
- Rump headers use portable type substitutions for selected kernel types.

C generation:
- Emits common kernel wrapper support for MPSAFE handling, fstrans handling, lockdebug assertions, and kqueue post hooks.
- Emits descriptor offset arrays and `struct vnodeop_desc` objects for each operation.
- Emits normal kernel wrappers that package arguments and call `VCALL`.
- Emits rump wrappers that call the kernel-facing `VOP_*` under `rump_schedule()`/`rump_unschedule()`.
- Emits `vfs_op_descs[]` for the normal kernel output.

Risks and notes:
- The generator relies on awk extensions and detects whether `toupper()` exists, otherwise shelling out to `tr`.
- The parser is whitespace-sensitive after custom sed preprocessing.
- Context fields are only accepted after `PRE` and `POST` handlers and must appear at the end of an argument structure.
- Rump type substitutions are explicitly described as a workaround for non-portable kernel types.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/kern/vnode_if.sh -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/Makefile -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/Makefile

Read completely: 81 lines.

Installs public kernel/userland headers from `sys/sys` into `/usr/include/sys`.

Key behavior:
- Sets `INCSDIR=/usr/include/sys`.
- `INCS` enumerates the exported system headers, including filesystem/VFS-relevant headers such as `acl.h`, `extattr.h`, `mount.h`, `uio.h`, `vnode.h`, `vnode_if.h`, `wapbl.h`, `wapbl_replay.h`, and `xattr.h`.
- `INCSYMLINKS` creates compatibility/convenience symlinks for selected headers such as `fcntl.h`, `poll.h`, hashing headers, std headers, `syslog.h`, and `termios.h`.
- Adds `../soundcard.h` as `${INCSDIR}/soundcard.h`.
- Provides generation rules for `namei` from `namei.src` via `gennameih.awk`, and `device_calls.h` from `../kern/device_calls` via `gendevcalls.awk`.
- Includes `<bsd.kinc.mk>` for kernel include installation mechanics.

Risks and notes:
- Header installation surface is explicit; missing a header from `INCS` prevents it from being installed for userland/kernel consumers.
- Generated headers depend on tool awk and source files in neighboring directories.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/Makefile -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/acct.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/acct.h

Read completely: 88 lines.

Defines NetBSD process accounting record ABI.

Key elements:
- `comp_t` is a 16-bit compact floating-point accounting type with a 3-bit base-8 exponent and 13-bit fraction.
- `struct acct` records command name, user/system/elapsed time, start time, uid/gid, average memory, I/O block count, controlling tty, and flags.
- Accounting time fields use `AHZ` granularity, defined as 64 units per second.
- Flags include `AFORK`, `ASU`, `ACOMPAT`, `ACORE`, and `AXSIG`, with `__ACCT_FLAG_BITS` for bit decoding.
- Kernel prototypes expose `acct_init()` and `acct_process()`.

Risks and notes:
- `struct acct` is a binary accounting-file ABI; changing fields or layout would affect accounting consumers.
- Compact time/accounting fields are lossy by design.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/acct.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/acl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/acl.h

Read completely: 440 lines.

Defines NetBSD ACL types, constants, kernel interfaces, private syscall interfaces, and userland ACL library prototypes for POSIX.1e and NFSv4 ACLs.

Core types and structures:
- Defines ACL scalar types: tags, permissions, entry types, flags, ACL type IDs, permsets, and flagsets.
- `ACL_MAX_ENTRIES` is 254 so the internal ACL structure fits one 4 KiB page.
- Kernel/private builds expose `struct oldacl_entry`, `struct oldacl`, `struct acl_entry`, `struct acl`, and libc's internal `struct acl_t_struct`.
- Non-private userland sees opaque `acl_t` and `acl_entry_t`.
- `struct oldacl` remains limited by `OLDACL_MAX_ENTRIES` for compatibility and POSIX.1e on-disk storage.

ACL constants:
- Defines POSIX.1e tags such as owner, named user, group, mask, other, and everyone.
- Defines NFSv4 entry types: allow, deny, audit, and alarm.
- Defines ACL type IDs for old access/default, current access/default, and NFSv4 ACLs.
- POSIX permission bits cover read/write/execute.
- NFSv4 permission bits cover data, named attributes, delete, ACL read/write, owner write, synchronize, and derived full/modify/read/write sets.
- Defines NFSv4 inheritance and audit flags.
- `ACL_UNDEFINED_ID` marks entries whose tag should not carry a uid/gid.

Kernel interfaces:
- Declares POSIX.1e mode/ACL conversion helpers, allocation/free helpers, NFSv4 mode sync/inheritance/triviality helpers, old/current ACL conversion helpers, and validation functions.
- Declares kernel ACL syscall helper entry points and vnode-level ACL helpers such as `vacl_set_acl`, `vacl_get_acl`, `vacl_aclcheck`, and `vacl_delete`.

User/private interfaces:
- `_ACL_PRIVATE` exposes raw `__acl_*` syscall wrappers and shared NFSv4 helpers used by libc.
- Public userland prototypes cover ACL creation, duplication, entry iteration, permission/flag mutation, text conversion, validation, file/fd/link get/set/delete calls, triviality checks, and ACL stripping.

Risks and notes:
- Increasing `ACL_MAX_ENTRIES` may require changing libc alignment assumptions.
- Changing `OLDACL_MAX_ENTRIES` would break pre-8.0 binary compatibility and POSIX.1e on-disk layout.
- Kernel code should use the VOP ACL type argument, not libc's internal ACL brand field.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/acl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/agpio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/agpio.h

Read completely: 150 lines.

Defines the AGP graphics aperture ioctl ABI.

Key elements:
- Fixes AGP GATT pages at 4096 bytes regardless of host page size.
- Provides AGP mode word extraction and insertion macros for request queue depth, ARQ size, calibration cycle, side-band addressing, AGP enable, 4G, fast writes, AGP 3 mode, and rate.
- Defines compatibility rate aliases for 1x/2x/4x.
- Defines ioctls for info, acquire, release, setup, allocate, deallocate, bind, and unbind.
- Disabled `#if 0` structs/ioctls show older reserve/protect region ideas.
- Public structs include `agp_version`, `agp_info`, `agp_setup`, `agp_allocate`, `agp_bind`, and `agp_unbind`.

Risks and notes:
- This is a user/kernel ioctl ABI; struct layout and ioctl numbers must remain stable.
- `AGP_MODE_SET_CAL` uses `__SHIFTIN((v), ~AGP_MODE_CAL)`, unlike the other setters that use the positive mask, which is a noteworthy macro risk.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/agpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/aio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/aio.h

Read completely: 233 lines.

Defines POSIX asynchronous I/O public structures and NetBSD kernel-private AIO service state.

Public ABI:
- Defines `AIO_CANCELED`, `AIO_NOTCANCELED`, and `AIO_ALLDONE` return states.
- Defines list I/O opcodes `LIO_NOP`, `LIO_WRITE`, `LIO_READ`.
- Defines list I/O modes `LIO_NOWAIT` and `LIO_WAIT`.
- `struct aiocb` contains file offset, userspace buffer, transfer length, fd, list opcode, request priority, sigevent, and kernel-maintained status fields `_state`, `_errno`, and `_retval`.

Kernel internals:
- Default limits are `AIO_LISTIO_MAX=512` and `AIO_MAX=AIO_LISTIO_MAX*16`.
- Defines operation flags for read/write/sync/dsync and job states none/work-in-progress/done.
- `struct aiowaitgroup` and `struct aiowaitgrouplk` manage suspend/list waiters and references.
- `struct aio_job` tracks one queued operation, its copied aiocb, originating process, file pointer, completion state, waitgroups, and list-I/O request pointer.
- `struct aiost_file_group`, `struct aiost`, and `struct aiosp` implement per-process servicing pools, worker thread lists, pending queues, hash lookup by user aiocb pointer, and per-file grouping.
- `struct aioproc` is per-process AIO state.
- Declares AIO pool, suspend, enqueue, conflict validation, error/return, and waitgroup helper functions.

Risks and notes:
- The public `aiocb` includes kernel status fields, so ABI consumers can observe layout.
- Kernel state is concurrency-heavy: jobs can be on queues, in worker threads, referenced by waitgroups, and found through aiocb pointer hashing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/aio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ansi.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ansi.h

Read completely: 76 lines.

Defines NetBSD's internal ANSI/base typedef substrate after including machine-specific `ansi.h`.

Key elements:
- Provides internal typedefs for core address, gid, IPv4 address/port, mode/access mode, offset, pid, socket family/length, uid, filesystem block/file counts, wide-character classification/translation handles, multibyte conversion state, and va_list.
- `__mbstate_t` is an opaque 128-byte union aligned by an `int64_t`.
- Exposes `_BSD_WCTRANS_T_`, `_BSD_WCTYPE_T_`, and `_BSD_MBSTATE_T_` macro aliases for public type plumbing.
- Uses `__builtin_va_list` except under lint, where `char *` is used.

Risks and notes:
- These typedefs underpin many public headers; changing widths affects ABI.
- The header deliberately uses internal names to support standards-visible typedef construction elsewhere.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ansi.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/aout_mids.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/aout_mids.h

Read completely: 80 lines.

Defines machine ID constants for legacy a.out binaries and kernel core files.

Key elements:
- Machine IDs are kept in numerical order and are expected to satisfy `0 < mid < 0x3ff`, except `MID_ZERO`.
- Includes legacy Sun, PC/i386, m68k, ns32532, sparc, pmax, vax, alpha, MIPS, ARM6, SH3/SH5, PowerPC, m88k, HPPA, x86_64, IA64, AArch64, OpenRISC, RISC-V, hp200/hp300, and HP-UX IDs.
- Notes these IDs are still used in kernel core files.

Risks and notes:
- This is compatibility namespace; reusing or renumbering values would affect a.out/core interpretation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/aout_mids.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/asan.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/asan.h

Read completely: 86 lines.

Defines the NetBSD kernel address sanitizer interface.

When `KASAN` is enabled:
- Includes required kernel type and bus headers.
- Defines compiler ABI shadow scale shift.
- Defines stack redzone marker values for left/mid/right redzones, use-after-return, and use-after-scope.
- Defines NetBSD redzone markers for generic, malloc, kmem, pool, and freed pool memory.
- Defines DMA marking types for linear, mbuf, uio, and raw DMA.
- Declares initialization, shadow mapping, softint, DMA sync/load, redzone sizing, and memory marking functions.

When `KASAN` is disabled:
- Exposes no-op macros for the same API so call sites compile away.

Risks and notes:
- Several constants are part of the compiler ABI and must match instrumentation expectations.
- The disabled path depends on `__nothing` semantics to remove side effects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/asan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ataio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ataio.h

Read completely: 56 lines.

Defines ATA command and ATA bus ioctl interfaces.

Key elements:
- `atareq_t` carries ATA command flags, command/features/sector/head/cylinder fields, user data buffer pointer and length, timeout, returned status, and error bits.
- Command flags indicate read, write, register read, and LBA addressing.
- Return statuses distinguish OK, timeout, command error, and device fault.
- `ATAIOCCOMMAND` is an `_IOWR('Q', 8, atareq_t)` ioctl for issuing ATA commands.
- ATA bus ioctls support scanning for devices, resetting the bus, and detaching a selected or wildcard device.

Risks and notes:
- This is a low-level user/kernel ioctl ABI exposing raw ATA command fields.
- Incorrect callers can request destructive device operations; validation is expected in ioctl handlers outside this header.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ataio.h -->