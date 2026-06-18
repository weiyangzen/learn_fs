# Group Research: group_490_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_p_d001afb5a09f

Scope checked against `Docs/research_subset_a.md`. All four listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prioctl.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prioctl.c

## Purpose

`prioctl.c` implements the legacy ioctl-based `/proc` control interface for illumos procfs. It translates old `PIOC*` commands into modern process-control operations, exposes old-format process/LWP status structures, implements old map/page-data readers, and handles 32-bit compatibility dispatch when `_SYSCALL32_IMPL` is enabled.

## Main Entry Points

- `prioctl()` is the vnode ioctl entry point. In 64-bit syscall builds it dispatches by caller data model to `prioctl32()` or `prioctl64()`.
- `prioctl64()` is the native ioctl implementation.
- `prioctl32()` mirrors the native implementation with ILP32 structure layouts, pointer narrowing, and `EOVERFLOW` checks for LP64 targets where old 32-bit structures cannot represent target state.
- `prctioctl()` handles contract-template proc nodes (`PR_TMPL`) for `CT_TSET` and `CT_TGET`.
- `oprgetstatus()` / `oprgetstatus32()` build old `prstatus_t` / `prstatus32_t`.
- `oprgetpsinfo()` / `oprgetpsinfo32()` build old `prpsinfo_t` / `prpsinfo32_t`.
- `oprgetmap()` / `oprgetmap32()` produce old `prmap` arrays.
- `oprpdsize*()` and `oprpdread*()` implement old page-data file sizing and reads.

## Ioctl Command Flow

The main ioctl handlers follow a consistent pattern:

1. Redirect old `/proc/<pid>` directory opens to the cached PID file if `pr_pidfile` is present.
2. Reject non-process/non-LWP nodes with `ENOTTY`.
3. Require `FWRITE` for logically mutating commands, as classified by `isprwrioctl()`.
4. Reject obsolete `PIOCSXREG` with `ENOTSUP`.
5. Copy user input and decide allocation sizes before acquiring proc locks.
6. Allocate buffers before `prlock()` to avoid sleeping allocation under `p_lock`.
7. Lock the target with `prlock(pnp, zdisp)`, allowing zombies only for selected information queries.
8. Choose a target LWP via `prchoose()` unless the command operates on process-wide state or stop/wait semantics.
9. Execute the command, usually unlocking before `copyout()` or file-descriptor assignment.
10. Free any temporary allocation and assert transient `xpnp` nodes were consumed or released.

## Command Categories

Supported commands include:

- Process and u-area snapshots: `PIOCGETPR`, `PIOCGETU`.
- Stop/run control: `PIOCSTOP`, `PIOCWSTOP`, `PIOCRUN`.
- LWP discovery and file opening: `PIOCLWPIDS`, `PIOCOPENLWP`.
- Page-data opening: `PIOCOPENPD`.
- Mapped object opening: `PIOCOPENM`.
- Signal tracing and delivery: `PIOCGTRACE`, `PIOCSTRACE`, `PIOCSSIG`, `PIOCKILL`, `PIOCUNKILL`.
- Priority/nice adjustment: `PIOCNICE`.
- Syscall tracing masks: `PIOCGENTRY`, `PIOCSENTRY`, `PIOCGEXIT`, `PIOCSEXIT`.
- Legacy proc flags: `PIOCSRLC`, `PIOCRRLC`, `PIOCSFORK`, `PIOCRFORK`, `PIOCSET`, `PIOCRESET`.
- Register access: `PIOCGREG`, `PIOCSREG`, `PIOCGFPREG`, `PIOCSFPREG`, `PIOCGXREGSIZE`, `PIOCGXREG`.
- Status and ps data: `PIOCSTATUS`, `PIOCLSTATUS`, `PIOCPSINFO`, `PIOCMAXSIG`, `PIOCACTION`.
- Signal hold/fault masks: `PIOCGHOLD`, `PIOCSHOLD`, `PIOCGFAULT`, `PIOCSFAULT`, `PIOCCFAULT`.
- Credentials and groups: `PIOCCRED`, `PIOCGROUPS`.
- Usage accounting: `PIOCUSAGE`, `PIOCLUSAGE`.
- Aux vector: `PIOCNAUXV`, `PIOCAUXV`.
- x86 LDT and SPARC register-window commands behind platform conditionals.

## Locking and Concurrency

This file relies heavily on procfs locking primitives from `prsubr.c`:

- `prlock()` holds `p_lock` and marks the target process `P_PR_LOCK`.
- `prunlock()` releases that state and may force killed processes runnable.
- Address-space operations drop `p_lock` before taking `AS_LOCK_*` to avoid lock-order deadlocks.
- Register operations drop `p_lock` while touching LWP stack/register state.
- Several dynamic array commands try `KM_NOSLEEP` while locked and restart after unlock if a sleeping allocation is required.

## ABI and Compatibility Notes

The file maintains two old ABIs: native old procfs structures and 32-bit old procfs structures. The 32-bit handler rejects operations against LP64 targets when addresses, register sets, aux vectors, page data, or status structures cannot be represented. Old map/page-data formats terminate map arrays with an all-zero record.

## Dependencies

This file depends on shared procfs helpers from `prsubr.c`, including `prchoose()`, `prgethold()`, `prgetaction*()`, `prnsegs()`, `pr_iol_*()`, `break_seg()`, `pr_getsegsize()`, `pr_getprot()`, usage converters, and process locking. It also delegates actual process control to wider procfs/kernel routines such as `pr_stop()`, `pr_wait_stop()`, `pr_setrun()`, `pr_setsig()`, `pr_kill()`, `pr_setentryexit()`, `pr_setfault()`, and register accessors.

## Important Edge Cases

- `PIOCWSTOP` refuses to wait on the current process/LWP to avoid deadlock.
- System processes and `kas` address-space users are treated as having no user address space.
- `PIOCOPENM` validates mapped objects are regular vnode-backed mappings and checks read access before returning an fd.
- Page-data readers retry if `page_exists()`/`SEGOP_INCORE()`-driven nondeterminism changes the computed output size while building the buffer.
- Zone visibility is sanitized for signal info and parent PID reporting when the examiner is in a non-global zone.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prioctl.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prsubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prsubr.c

## Purpose

`prsubr.c` is the core procfs support library. It supplies process/LWP selection, procfs vnode lifetime hooks, process locking, status/ps/usage formatting, memory-map and page-data generation, fdinfo generation, watchpoint bookkeeping, credential/privilege export, and 32-bit conversion helpers.

## Lifecycle and Notification

Key lifecycle hooks:

- `prnotify()` wakes waiters and pollers on procfs state changes.
- `prfree()` clears procfs process references when a process leaves the process table.
- `prexit()` marks traced process files as destroying and tears down watchpoints.
- `prlwpexit()` and `prlwpfree()` update LWP-specific procfs vnode state as LWPs exit or are reaped.
- `prexecstart()` blocks procfs operations during exec with `P_PR_EXEC`.
- `prexecend()` clears exec blocking and refreshes data model/TID metadata on open procfs nodes.
- `prrelvm()` removes watched areas/pages before address-space destruction.
- `prinvalidate()` invalidates sensitive procfs vnodes after set-id or unreadable exec events while preserving public information files.

## Process Locking

The central protocol is:

- `pr_p_lock()` takes `pr_pidlock`, finds the process through procfs common state, takes `p_lock`, waits for `P_PR_LOCK` to clear, then sets `P_PR_LOCK`.
- `prlock()` wraps `pr_p_lock()`, handles zombie/exiting/lwp-invalid cases, rejects invalidated nodes, and waits for in-progress execs.
- `prunmark()` clears `P_PR_LOCK` and wakes waiters.
- `prunlock()` calls `prunmark()` and drops `p_lock`; if the target was killed, it attempts to make it runnable.
- `prbarrier()` is used by process-owned paths to wait until procfs is no longer controlling the process.

This locking design prevents LWPs from disappearing while procfs inspects or controls them, and it establishes the lock ordering used by the rest of procfs.

## LWP Selection

`prchoose()` selects the representative LWP for process-wide operations. Its precedence is semantically important:

1. Agent LWP, if present.
2. On-processor LWP.
3. Runnable LWP.
4. Sleeping LWP.
5. Job-control stopped LWP.
6. Directed job-control stop.
7. Event-of-interest stop.
8. DTrace/requested stops.
9. Hold/suspended states.
10. Zombie fallback.

The function returns the chosen thread with its dispatcher lock held.

## Status and psinfo Generation

The file builds both modern and 32-bit status structures:

- `prgetstatus()` / `prgetstatus32()` fill process-wide `pstatus`.
- `prgetlwpstatus()` / `prgetlwpstatus32()` fill detailed LWP status, including stop reason, signal state, syscall args, rval/errno on syscall exit, fault info, registers, FP registers, and microstate time.
- `prgetpsinfo()` / `prgetpsinfo32()` fill `psinfo`.
- `prgetlwpsinfo()` / `prgetlwpsinfo32()` fill lightweight `lwpsinfo`.

It sanitizes zone-crossing signal info, maps kernel thread states to user-visible process states, exposes only selected process flags, and zeroes unrepresentable fields in 32-bit views.

## Memory Maps and Page Data

Memory-map support includes:

- `prnsegs()` counts visible map ranges, splitting segments by effective protection.
- `break_seg()` identifies the process heap segment.
- `prgetmap()` / `prgetmap32()` emit map entries with address, size, offset, protections, shared/noreserve/anon/break/stack/ISM/SHM flags, object names, and SysV SHM IDs.
- `prpdsize()` / `prpdsize32()` compute page-data file sizes.
- `prpdread()` / `prpdread32()` emit page-data headers and per-map page residency data.
- `prgetxmap()` / `prgetxmap32()` emit extended map entries including HAT page size plus RSS/anonymous/locked page counts.

The helper `pr_getsegsize()` trims segment sizes for regular files, ISM backing sizes, and `/dev/null`-style virtual reservations. `pr_getprot()` computes contiguous ranges of effective protection, handling per-page protections and `MAP_NORESERVE` materialization through the internal `prpagev_t` vector.

## Chained I/O Buffers

The `pr_iol_*()` helpers implement generic chained kernel buffers for variable-size procfs output:

- `pr_iol_initlist()` initializes a list with a bounded first buffer.
- `pr_iol_newbuf()` allocates space for one item and appends 64 KiB buffers as needed.
- `pr_iol_copyout_and_free()` copies the chain to user memory.
- `pr_iol_uiomove_and_free()` feeds the chain through a `uio_t`.
- `pr_iol_freelist()` releases without copying.

These helpers are shared by map, fdinfo, and other variable-output paths.

## FD Info

FD inspection support is built around:

- `pr_getf()` safely obtains a referenced `file_t` from another process while avoiding a procfs close-path lock inversion through bounded `mutex_tryenter()` retries.
- `pr_releasef()` drops that procfs-held file reference without always going through full close logic.
- `prgetfdinfosize()` computes `/proc/<pid>/fdinfo/<fd>` size, including misc trailers.
- `prgetfdinfo()` fills `prfdinfo_t` with offsets, stat attributes, lock info, peer credentials, paths, socket/TLI names, and socket options.

Socket/TLI helpers include `pristli()`, `prfdinfotlisockopt()`, and `prfdinfosockopt()`. Door pathname handling walks mounted namenodes.

## Usage Accounting

Usage helpers include:

- `estimate_msacct()` and `disable_msacct()`, now mostly compatibility shims because microstate accounting is effectively always available.
- `prgetusage()` for one LWP.
- `praddusage()` to aggregate one LWP into a process total.
- `prscaleusage()` to convert unscaled high-resolution accounting.
- `prcvtusage()` / `prcvtusage32()` to convert high-resolution internal usage to exported structures.

The accounting paths adjust for current dispatch-queue wait time and current microstate time, with bounded retries for timebase races.

## Watchpoints

Watchpoint state is split into watched areas and watched pages:

- `set_watched_area()` inserts or updates an AVL-sorted watched range, enabling watchpoints on all LWPs when the first watch appears.
- `clear_watched_area()` removes an exact watched range and disables watchpoints when the last one disappears.
- `pr_free_watchpoints()` frees process watched-area structures.
- `pr_free_watched_pages()` restores original protections and frees address-space watched-page state.
- `set_watched_page()` and `clear_watched_page()` maintain per-page read/write/exec watch counters and queue protection updates through `p_wprot`.
- `getwatchprot()` restores original protections when procfs map readers report pages affected by watchpoint protection changes.

## Credentials and Privileges

The file exports process security state through:

- `prgetcred()`
- `prgetsecflags()`
- `prgetprivsize()`
- `prgetpriv()`

These use credential locks where needed and rely on common privilege conversion routines.

## Compatibility Helpers

Under `_SYSCALL32_IMPL`, the file provides 32-bit status, psinfo, map, page-data, and xmap variants, plus structure conversion helpers `lwpsinfo_kto32()` and `psinfo_kto32()`. Pointer-sized fields that cannot be represented are either omitted, zeroed, or copied only for ILP32 targets.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prsubr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prusrio.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prusrio.c

## Purpose

`prusrio.c` implements `prusrio()`, the low-level helper for reading from or writing to a target process address space through procfs-style user I/O.

## Behavior

`prusrio(proc_t *p, enum uio_rw rw, struct uio *uiop, int old)` transfers `uiop->uio_resid` bytes starting at `uiop->uio_offset`.

For small transfers up to 64 bytes it uses a stack buffer. Larger transfers allocate one page of kernel memory. Transfers are split at page boundaries with:

- `len = MIN(uiop->uio_resid, PAGESIZE - (addr & PAGEOFFSET))`

For reads:

1. `uread()` copies from the target process into the kernel buffer.
2. `uiomove(..., UIO_READ, uiop)` copies from the kernel buffer to the caller.

For writes:

1. `uiomove(..., UIO_WRITE, uiop)` copies caller data into the kernel buffer.
2. `uwrite()` writes the buffer into the target process.
3. If `uwrite()` fails after `uiomove()`, the function backs up `uio_resid` and `uio_loffset` by the attempted length.

On SPARC, if the target is `curproc`, it flushes register windows to the stack before accessing user memory.

## Error Handling

`ENXIO` means the target page did not exist. The function maps this as follows:

- Reads: if some data was transferred, or if using new semantics (`old == 0`), return success; otherwise return `EIO`.
- Writes: if some data was transferred, return success; otherwise return `EIO`.

Unexpected `rw` values panic.

## Dependencies

This helper depends on `uread()`, `uwrite()`, `uiomove()`, `kmem_alloc()`, `kmem_free()`, and SPARC register-window flushing when applicable. It is intentionally page-boundary aware so partial failures have predictable procfs behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prusrio.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvfsops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvfsops.c

## Purpose

`prvfsops.c` implements the VFS/module layer for procfs. It registers the `proc` filesystem type, creates mount root nodes, handles mount/unmount/root/statvfs operations, and assigns per-mount pseudo-device identifiers.

## Module Registration

- `_init()` installs the filesystem module via `mod_install()`.
- `_info()` returns module information via `mod_info()`.
- There is deliberately no `_fini()`; the procfs module cannot be unloaded once loaded.

The `vfsdef_t` advertises the filesystem as `proc` with flags including protocol support, stats, extended IDs, and zone mount support.

## Initialization

`prinit()` is called by the VFS framework for the filesystem type. It:

- Computes `nproc_highbit`.
- Stores the procfs type ID.
- Registers VFS operations with `vfs_setfsops()`.
- Builds vnode operations with `vn_make_ops()`.
- Gets a unique major number with `getudev()`.
- Initializes mount and minor-number locks.

`prinitrootnode()` allocates and initializes a root `prnode_t` and vnode. The root vnode is a directory marked `VROOT`, `VNOCACHE`, `VNOMAP`, `VNOSWAP`, and `VNOMOUNT`, uses `prvnodeops`, and has procfs node type `PR_PROCDIR` with mode `0555`.

## Mount

`prmount()` enforces mount policy and mountpoint validity:

- Requires `secpolicy_fs_mount()`.
- Requires the mountpoint vnode to be a directory.
- In the global zone, verifies the mount path belongs to the global zone.
- Forces the VFS resource string to `"proc"`.
- Rejects busy non-overlay mountpoints.
- Allocates a procfs root `prnode_t`.
- Assigns filesystem type, root data, block size, and a unique pseudo-device minor number.
- Builds the VFS fsid.

Mount serialization is protected by `pr_mount_lock`; minor assignment is protected by `procfs_minor_lock`.

## Unmount

`prunmount()`:

- Requires `secpolicy_fs_unmount()`.
- Rejects forced unmounts with `ENOTSUP`.
- Fails with `EBUSY` if the root vnode is still referenced.
- Invalidates and frees the root vnode.
- Frees the root `prnode_t`.

## Root and Statvfs

`prroot()` returns a held reference to the procfs root vnode.

`prstatvfs()` fills `statvfs64` with pseudo-filesystem values:

- Block counts are zero.
- File count is based on configured process slots plus two.
- Free file counts are based on configured process slots minus current process count.
- fsid is derived from the procfs pseudo-device.
- base type and filesystem string are `/proc`.
- name maximum is fixed at 64.

## Dependencies

This file anchors procfs into the illumos VFS/module framework and depends on procfs vnode operations declared elsewhere through `prvnodeops` and `pr_vnodeops_template`. Its root nodes become the directory entry point for the rest of procfs.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/proc/prvfsops.c -->