# Group Research: group_471_illumos_gate_sources_os_illumos_illumos_gate_usr_src_uts_common_fs_d_bd081e56f63e

Scope: `Docs/research_subset_a.md`

Files researched completely:
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_sys.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_vnops.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fd/fdops.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fdbuffer.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fem.c`
- `sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifosubr.c`

Note: the referenced internal group report path was absent in the working tree, so this report is based on the subset scope and complete source reads.

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_sys.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_sys.c

## Purpose
Implements the illumos door system-call layer and kernel door interfaces. Doors are an RPC-like IPC mechanism where clients invoke server threads through door descriptors or kernel-held door handles. This file owns door syscall dispatch, creation/revocation, argument/result transfer, descriptor translation, server-thread shuttle scheduling, unref notifications, process exit/fork cleanup, and exported kernel interfaces such as `door_ki_create()`, `door_ki_upcall()`, and `door_ki_lookup()`.

## Main Responsibilities
- Registers the `doors` syscall module and optional 32-bit syscall entry.
- Creates synthetic door vnodes/files and tracks them in per-process door lists.
- Implements `door_call()` client invocation and `door_return()` server reply/wait loop.
- Moves data and descriptors between client/server address spaces using small-buffer copy or direct page copy.
- Handles user server pools, private door binding, cancellation, revocation, unref delivery, and process lifecycle cleanup.
- Provides kernel consumers with door handles, upcalls, parameter APIs, and reference management.

## Key Data and Limits
- `door_max_arg`: threshold for kernel-buffer copy versus direct page-copy transfer.
- `door_max_upcall_reply`: caps kernel door-upcall reply allocation.
- `door_max_desc`: caps descriptors passed per call/return.
- `door_knob`: global door mutex protecting door state, server pools, active counts, and unref lists.
- `door_node_t`: door object behind VDOOR vnodes, with target process, callback, flags, per-door private server pool, active call count, and limits.
- Per-thread `door_data_t` contains client/server substructures used while the thread is in a door call or server wait.

## System Call Dispatch
`doorfs()` switches on subcodes:
- `DOOR_CALL`
- `DOOR_RETURN`
- legacy `DOOR_RETURN_OLD`
- `DOOR_CREATE`
- `DOOR_REVOKE`
- `DOOR_INFO`
- `DOOR_BIND`
- `DOOR_UNBIND`
- `DOOR_UNREFSYS`
- `DOOR_UCRED`
- `DOOR_GETPARAM`
- `DOOR_SETPARAM`

The 32-bit path `doorfs32()` mirrors this and explicitly casts 32-bit pointer-sized arguments to avoid sign-extension problems.

## Door Creation and Lookup
`door_create()` validates attributes, calls `door_create_common()`, then marks the returned fd close-on-exec.

`door_create_common()`:
- Allocates `door_node_t` and a vnode.
- Initializes server process, callback, cookie, flags, descriptor/data limits.
- Installs `door_vnodeops`, marks vnode as `VDOOR`, attaches dummy `door_vfs`.
- Inserts the door into the server process list under `door_knob`.
- Allocates a `file_t` and optionally fd.
- Cleans up list/vnode/node on `falloc()` failure.

`door_lookup()` validates that an fd resolves, through `VOP_REALVP()` if needed, to a `VDOOR` vnode. Callers must `releasef()`.

## Invocation Flow
`door_call()`:
- Copies in `door_arg_t` or 32-bit equivalent.
- Looks up the door, takes a vnode hold, and drops the fd reference.
- Checks door validity and per-door data/descriptor limits.
- Handles kernel door servers directly in caller context when `door_target == &p0`.
- For user servers, obtains an available server thread via `door_get_server()`.
- Transfers args to the server through `door_args()`.
- Sets caller/server linkage, increments `door_active`, resumes the server by shuttle.
- Handles interrupted waits, SIGCANCEL delivery unless `DOOR_NO_CANCEL`, server exit, and late result races.
- Copies returned data/descriptors to user buffers or overflow mappings.
- Cleans up overflow mappings, descriptor arrays, file references, temporary buffers, kernel-server destructors, and vnode holds.

Important invariants:
- Client and server thread state is protected by `door_knob`.
- `DOOR_T_HOLD()` prevents a peer thread from exiting while data is copied.
- `door_active` delays unref delivery until in-flight calls finish.

## Server Return Flow
`door_return()`:
- Records the server stack base/size.
- If there is a caller, transfers results through `door_results()`.
- Places the server back in its pool with `door_release_server()`.
- Wakes the caller or switches back to wait for a new invocation.
- On a new call, invokes `door_server_dispatch()` to lay out and copy arguments on the server stack.
- Handles /proc stops, signals, cancellation, and server exit.

`door_server_dispatch()`:
- Computes stack layout with `door_layout()`.
- Inserts descriptors into the server process, copies descriptors/data onto the stack, and optionally emits `door_info_t` for private empty pools.
- Writes `door_results` or `door_results32`.
- Calls architecture helper `door_finish_dispatch()`.

`door_layout()` carefully checks overflow, stack alignment, descriptor/data/info/result placement, and recorded stack-size bounds.

## Data and Descriptor Transfer
- `door_args()` copies user client args to a user server. Small data uses a kernel buffer; larger data copies directly page-by-page into the server stack with `door_copy()`.
- `door_results()` copies server results back to the caller, handles upcall reply limits, overflow mapping, direct copy, and descriptor translation.
- `door_overflow()` maps a new anonymous region in the caller address space when the original result buffer is too small.
- `door_copy()` locks the destination user page, maps it into kernel space, and uses `copyin_nowatch()` from the current address space.

Descriptor helpers:
- `door_insert()` allocates an fd in the current process for a returned `file_t` and fills `door_desc_t` attributes.
- `door_translate_in()` converts user fds to kernel door handles for kernel servers.
- `door_translate_out()` converts kernel descriptors/handles into held `file_t` references for user delivery.
- `door_fd_close()`, `door_fd_rele()`, `door_release_fds()`, and `door_fp_close()` centralize cleanup of descriptor/file ownership.

## Server Pools and Binding
`door_get_server()` scans a door-private pool or process-wide pool for a server thread sleeping on `SOBJ_SHUTTLE`; if unavailable, waits interruptibly on the pool CV. It removes the selected server from the pool and marks it runnable/onproc.

`door_release_server()` returns a server to its pool and signals waiters.

`door_bind()` binds the current LWP to a private door pool and increments the door-bound thread count through `door_bind_thread()` in `door_vnops.c`.

`door_unbind()` reverses binding or clears invalid inherited binding state.

## Revocation, Exit, Fork, and Unref
- `door_revoke()` marks a current-process door revoked, wakes server waiters, drops the fd using `closeandsetf()`.
- `door_revoke_all()` marks all current-process doors revoked before thread termination.
- `door_exit()` clears process door/unref lists during final process exit.
- `door_slam()` handles current thread exit during active door work, waking a caller with `DOOR_EXIT` and implicitly unbinding private doors.
- `door_fork()` marks inherited private bindings invalid in `forkall()` children.
- `door_deliver_unref()` queues unreferenced-door notifications and holds the vnode while queued.
- `door_unref()` and `door_unref_kernel()` drain per-process or process-0 unref queues and deliver user/kernel callbacks.

## Parameter and Info APIs
- `door_setparam()` / `door_getparam()` and kernel variants control/read max descriptors, min data, and max data.
- `door_check_limits()` enforces per-door limits, with unref upcall exception for data minimum.
- `door_info()` / `door_info_common()` fill `door_info_t`, including `DOOR_LOCAL`, uniquifier, attributes, and inferred `DOOR_IS_UNREF`.
- `door_ucred()` returns caller credentials to a server, using upcall credentials when present.

## Kernel Interfaces
Exports:
- `door_ki_create()`
- `door_ki_upcall()`
- `door_ki_upcall_limited()`
- `door_ki_hold()`
- `door_ki_rele()`
- `door_ki_open()`
- `door_ki_info()`
- `door_ki_lookup()`
- `door_ki_setparam()`
- `door_ki_getparam()`

These adapt kernel `door_handle_t` values to `file_t *`, preserve references, and invoke the same core upcall/parameter/info machinery.

## Integration Points
- Door vnode operations from `door_vnops.c`.
- VFS/vnode/file table routines: `vn_alloc`, `vn_setops`, `falloc`, `getf`, `releasef`, `closef`, `closeandsetf`.
- Scheduler/thread shuttle routines: `shuttle_resume`, `shuttle_swtch`, `shuttle_sleep`.
- VM/address-space APIs: `as_pagelock`, `as_map`, `as_unmap`, `hat_kpm_mapin`, `ppmapin`.
- /proc and signal machinery: `prstop`, `ISSIG`, `sigtoproc`, `schedctl_cancel_pending`.
- Credential conversion via `cred2ucred()`.

## Risks and Subtle Areas
- Reference ownership is complex: fd refs, file refs, vnode refs, descriptor release flags, and door handles must match every success/error path.
- `door_knob` lock ordering is critical; many helpers assert it is held or not held.
- Interrupt/cancel/server-exit paths are race-sensitive and use peer holds to avoid exit during copy.
- Stack layout arithmetic must avoid wraparound and preserve ABI alignment.
- Overflow result mappings must be unmapped on error to avoid user address leaks.
- Kernel-server destructor callbacks must run exactly once after returned data handling.

## Testing/Validation Signals
Useful coverage would include:
- User door call/return with small and large data.
- Descriptor passing with and without `DOOR_RELEASE`.
- 32-bit client compatibility.
- Private door binding/unbinding.
- Revocation while clients wait.
- Client interruption and `DOOR_NO_CANCEL`.
- Unref notification delivery for single and multi-unref modes.
- Kernel `door_ki_*` creation/upcall/open/info/param paths.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_sys.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_vnops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_vnops.c

## Purpose
Defines vnode operations for synthetic door vnodes. These operations make door descriptors behave like VFS objects while delegating most door behavior to `door_sys.c`.

## Vnode Operations
`door_vnodeops_template` provides:
- `OPEN`: `door_open`
- `CLOSE`: `door_close`
- `GETATTR`: `door_getattr`
- `ACCESS`: `door_access`
- `INACTIVE`: `door_inactive`
- `REALVP`: `door_realvp`
- Unsupported/error operations for lock, poll, pathconf, dispose, secattr, and share locks.

## Key Functions
`door_open()`:
- Enforces labeled-system MAC policy.
- Allows cross-zone clients only when the server is in the global zone; otherwise client and server zones must match.
- Ignores invalid doors by returning success, preserving legacy open behavior.

`door_close()`:
- Handles unref notification scheduling when this is the last file-structure reference and vnode count indicates no other files reference it.
- If the door has active invocations, sets `DOOR_DELAY`; otherwise calls `door_deliver_unref()`.
- Asserts process-exit cleanup revoked current-process doors before `closeall()`.

`door_getattr()`:
- Fills synthetic attributes: type from vnode, mode `0777`, uid/gid `0`, size `0`, zero timestamps, `doordev` fsid/rdev, and nlink from vnode refcount.

`door_inactive()`:
- Defers freeing while private bound server threads remain.
- If still listed on a target process, removes the door under `door_knob`.
- Invalidates and frees vnode and `door_node_t`.

`door_bind_thread()` / `door_unbind_thread()`:
- Track private-server bindings with `door_bound_threads` under `v_lock`, without changing vnode refcount.
- `door_unbind_thread()` triggers inactive processing when the last bound thread releases an otherwise unreferenced vnode.

`door_access()`:
- Grants all access.

`door_realvp()`:
- Returns the door vnode itself.

## Integration Points
- Shares `door_knob` with `door_sys.c`.
- Calls `door_deliver_unref()` and `door_list_delete()` implemented in the syscall layer.
- Uses `VTOD()`/`DTOV()` door vnode/node conversions.
- Exports `door_bind_thread()` and `door_unbind_thread()` for private door binding.

## Risks and Subtle Areas
- `door_bound_threads` deliberately does not use `VN_HOLD()`; inactive logic must cooperate with this separate count.
- `door_close()` unref delivery depends on `count == 2` and `vp->v_count == 1`, which is tied to file/vnode lifetime semantics.
- Zone check dereferences `door_target` only after validating the door under `door_knob`.

## Testing/Validation Signals
- Open a door across zones on labeled systems.
- Close last refs with `DOOR_UNREF` while no invocations are active.
- Close last refs while invocations are active and verify delayed unref.
- Bind/unbind private server threads and verify inactive cleanup occurs only after final unbind.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/doorfs/door_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fd/fdops.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fd/fdops.c

## Purpose
Implements the `/dev/fd` pseudo-filesystem. It exposes per-process file descriptor numbers as character-device vnodes under a mounted directory.

## Main Responsibilities
- Registers and initializes the `fd` filesystem module.
- Provides VFS mount/unmount/root/statvfs operations.
- Provides vnode operations for directory reads/lookups and synthetic descriptor vnodes.
- Generates entries based on the current process file table and `RLIMIT_NOFILE`.

## Core Constants and State
- `FDROOTINO`: inode number for root directory.
- `fdtoi(n)`: maps fd number to synthetic inode number.
- `FDSDSIZE`, `FDNSIZE`: directory-entry sizing/name limits.
- `fdfstype`, `fdfsmaj`, `fdfsmin`, `fdrmaj`: filesystem and device numbering.
- `fd_minor_lock`: serializes pseudo-device minor allocation.

## Vnode Operations
`fd_vnodeops_template` includes:
- `fdopen()`: marks non-directory vnodes `VDUP`, allowing open to duplicate the referenced fd semantics.
- `fdclose()`: no-op.
- `fdread()`: legacy directory-format read for the root directory.
- `fdgetattr()`: synthetic stat data for root or fd entries.
- `fdaccess()`: permits all access.
- `fdlookup()`: maps `"."`, `".."`, or numeric names to vnodes.
- `fdcreate()`: treats create as lookup for numeric fd entries.
- `fdreaddir()`: emits `dirent64` records.
- `fdinactive()`: releases and frees transient vnodes.

Unsupported operations include frlock, poll, dispose.

## Directory Enumeration
Both `fdread()` and `fdreaddir()` compute entry count from:
- `P_FINFO(curproc)->fi_nfiles`
- enforced `RLIMIT_NOFILE`

Entries include `"."`, `".."`, then numeric names from `0` to allowed max minus one. These are not filtered for currently open descriptors; `/dev/fd/N` lookup creates a vnode for numeric `N`, and later open behavior resolves duplication elsewhere in the kernel path.

`fdreaddir()` advances offsets in fixed `FDSDSIZE` increments even though returned `dirent64` record lengths vary.

## Vnode Creation
`fdget()`:
- Parses component name as decimal digits only.
- Allocates a transient `VCHR` vnode.
- Uses fd vnode ops, `VNOMAP`, and `makedevice(fdrmaj, n)`.
- Does not validate that fd `n` is open at lookup time.

## VFS Operations
`fdmount()`:
- Requires mount privilege and directory mount point.
- Enforces non-overlay busy checks.
- Sets resource name to `"fd"`.
- Allocates the root vnode, assigns unique pseudo-device minor, sets fsid and block size.

`fdunmount()`:
- Requires unmount privilege.
- Rejects forced unmount.
- Refuses if root vnode has extra refs, otherwise releases it.

`fdroot()`:
- Returns a held root vnode.

`fdstatvfs()`:
- Reports zero block capacity, synthetic file count, name max, basetype, flags, fsid, and `/dev/fd` strings.

`fdinit()`:
- Installs VFS ops and vnode ops.
- Gets unique device majors for filesystem and descriptor nodes.
- Initializes minor lock.

## Module Registration
Defines mount options defaulting to read-write and ignore support, then registers as filesystem `"fd"` with `VSW_HASPROTO | VSW_ZMOUNT`.

## Integration Points
- VFS operation registration via `vfs_setfsops()`.
- Vnode operation creation via `vn_make_ops()`.
- Resource controls via `rctl_enforced_value()`.
- File table sizing via `P_FINFO(curproc)`.
- Device number helpers `getudev()`, `makedevice()`, `vfs_make_fsid()`.

## Risks and Subtle Areas
- Directory listings are based on allowed descriptor range, not open descriptors, which can surprise consumers but matches `/dev/fd` semantics.
- `fdget()` accepts arbitrary numeric values without range or open checks.
- Root vnode lifetime is simple but unmount depends on `v_count` being exactly manageable.
- `fdread()` uses old fixed-size directory records; `fdreaddir()` uses modern `dirent64`.

## Testing/Validation Signals
- Mount/unmount `/dev/fd` with/without overlay and busy root refs.
- `readdir()` under different `RLIMIT_NOFILE` values.
- Lookup numeric and nonnumeric names.
- Open non-directory fd vnode and verify duplication behavior through broader `/dev/fd` stack.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fd/fdops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fdbuffer.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fdbuffer.c

## Purpose
Implements `fdbuffer_t`, a filesystem/direct-I/O helper abstraction that wraps either page lists or user virtual-address buffers and tracks cloned `buf_t` I/O, holes, async completion, errors, and final byte accounting.

## Main Responsibilities
- Create fdbuffers for page I/O or virtual-address I/O.
- Build cloned buf structures for subrange I/O.
- Track outstanding async I/O count and completion callbacks.
- Account attempted/completed/residual bytes.
- Record and optionally zero sparse holes.
- Free parent pageio/physical buf resources.

## Allocation and Initialization
`fdb_init()` creates `fdb_cache`.

`fdb_cache_constructor()` / destructor initialize/destroy `fd_mutex`.

`fdb_prepare()` resets reusable fields: holes, callbacks, parent buffer, residual, I/O count, dispatch count, and error state.

Creation:
- `fdb_page_create(page_t *pp, size_t len, int flags)` creates an `FDB_PAGEIO` buffer.
- `fdb_addr_create(caddr_t addr, size_t len, int flags, page_t **pplist, proc_t *procp)` creates an `FDB_VADDR` buffer.

Both require read or write mode.

## I/O Setup
`fdb_iosetup()`:
- Validates direction against fdb state and enforces sync/async consistency.
- Marks sync or async mode and increments `fd_iodispatch`.
- Creates a parent buf once:
  - `pageio_setup()` for page I/O.
  - allocated `buf_t` with `bioinit()`, `B_BUSY | B_PHYS`, optional `B_SHADOW` for virtual-address I/O.
- Clones a subrange with `bioclone()`.
- Stores the `fdbuffer_t` in `bp->b_forw`.
- Sets `B_ASYNC` and callback to `fdb_iodone()` for async I/O.

## Completion
`fdb_iodone(buf_t *bp)`:
- Maps out remapped buffers.
- Decrements outstanding dispatch count.
- Records error and residual bytes.
- Adds completed/attempted byte count.
- If no more dispatches and final state is `FDB_ERROR` or `FDB_DONE`, invokes callback for async or immediate-callback mode.
- For `FDB_ICALLBACK`, callback can fire per buffer.
- Frees cloned buf with `freerbuf()`.

`fdb_ioerrdone()`:
- Marks an async fdb done or errored without a buf completion.
- If no outstanding dispatches remain, invokes callback.

`fdb_get_iolen()`:
- Returns `fd_iocount - fd_resid`, requiring no outstanding dispatches.

`fdb_get_error()` returns the stored error.

## Hole Handling
`fdb_add_hole()`:
- Inserts a hole descriptor in ascending offset order.
- Adds hole length to `fd_iocount` so holes count toward accounted I/O range.
- Requires `off < fd_len`.

`fdb_get_holes()`:
- If `FDB_ZEROHOLE`, zeros holes before returning the list.

`fdb_zero_holes()`:
- For `FDB_PAGEIO`, walks page list and calls `pagezero()` for hole ranges.
- For `FDB_VADDR`, calls `bzero()` on buffer ranges.
- Frees hole records as it processes them.
- Panics for unknown fdb type.

## Freeing
`fdb_free()`:
- Zeroes holes if requested.
- Frees remaining hole records.
- Calls `pageio_done()` for pageio parent buffers or frees virtual-address parent buf.
- Returns fdb object to cache.
- Asserts no outstanding dispatch remains.

## Integration Points
- Kernel buffer cache: `buf_t`, `bioclone()`, `freerbuf()`, `bioinit()`.
- Page I/O: `pageio_setup()`, `pageio_done()`, `pagezero()`, page list traversal.
- VM/physical I/O: `B_PHYS`, `B_SHADOW`, process pointer, shadow page lists.
- Completion callbacks through `fdb_iodone_t`.

## Risks and Subtle Areas
- Async state machine depends on `fd_iodispatch`, `FDB_DONE`, `FDB_ERROR`, `FDB_ASYNC`, and `FDB_ICALLBACK` combinations.
- `fdb_zero_holes()` page offset logic has an in-code warning about offset interpretation; callers must pass buffer-relative holes consistently.
- Parent buf is created once using the first requested len/flags; later clones reuse it.
- `fdb_add_hole()` updates `fd_iocount`, so holes are counted as accounted I/O even without a device request.
- Callback can receive either a completing `buf_t *` or `NULL` depending on path.

## Testing/Validation Signals
- Sync and async page I/O subrange clones.
- Virtual-address I/O with and without shadow page list.
- Hole insertion ordering and zeroing for page and virtual buffers.
- Error completion with residual accounting.
- Immediate callback versus final callback behavior.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fdbuffer.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fem.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fem.c

## Purpose
Implements FEM/FSEM, the illumos vnode and VFS operation interposition framework. It lets kernel components install monitor operation vectors on individual vnodes or VFS instances, so operations pass through a stack of monitors before reaching the original filesystem operations.

## Main Responsibilities
- Define vnode monitor (`fem_t`) and VFS monitor (`fsem_t`) operation vector layouts.
- Build head operation vectors that intercept every vnode/VFS op.
- Provide `vnext_*()` and `vfsnext_*()` APIs for monitors to call the next operation below them.
- Manage per-object monitor stacks with copy-on-update semantics and refcounts.
- Install, uninstall, query, and replace base vnode/VFS operations under interposition.
- Initialize guard vectors that panic on stack corruption/underrun.

## Core Structures and Concepts
- `fem_type_info`: per-type head node, guard node, and error function.
- `fem_head`: per-vnode/per-vfs object containing a mutex and current `fem_list`.
- `fem_list`: refcounted stack of `fem_node` entries.
- `fem_node`: either base ops (`fn_available == NULL`) or a monitor with ops plus opaque `fn_available` argument and optional hold/release callbacks.
- Stack bottom is a guard node; above it is the original base ops; monitors are pushed above that.
- `FEM_HEAD(FEMTYPE_VNODE)` and `FEM_HEAD(FEMTYPE_VFS)` are the installed head ops that intercept object calls.

## Operation Vector Definitions
`fem_opdef` maps all vnode operation names to offsets in `fem_t`.
`fsem_opdef` maps VFS operation names to offsets in `fsem_t`.

Guard ops:
- `fem_guard_ops` routes all vnode monitor calls to `fem_err()`.
- `fsem_guard_ops` routes all VFS monitor calls to `fsem_err()`.

Both panic if reached, indicating stack corruption.

## Dispatch Machinery
`vsop_find()` and `vfsop_find()` walk downward from a current stack node:
- If a base node is reached, select the original vnode/VFS operation and pass the base object.
- If a monitor node has the requested method, select it and pass the fem/fsem argument handle.
- Otherwise continue down.

Debug builds route through `_op_find()` using explicit offsets.

## Head Operations
`vhead_*()` functions cover the full vnode op surface: open, close, read, write, ioctl, setfl, getattr, setattr, access, lookup, create, remove, link, rename, mkdir, rmdir, readdir, symlink, readlink, fsync, inactive, fid, rwlock/rwunlock, seek, cmp, frlock, space, realvp, getpage/putpage, map/addmap/delmap, poll, dump, pathconf, pageio, dumpctl, dispose, secattr, shrlock, vnevent, reqzcbuf, retzcbuf.

`fshead_*()` functions cover VFS ops: mount, unmount, root, statvfs, sync, syncfs, vget, mountroot, freevfs, vnstate.

Each head function:
- Locks the object FEM head.
- If no stack exists, calls the current base op directly.
- Otherwise increments stack refcount, unlocks, initializes `femarg_t`/`fsemarg_t` at top-of-stack, finds a matching top operation, invokes it, then releases the stack.

## Next Operations
`vnext_*()` and `vfsnext_*()` are exported to monitor implementations. They:
- Decrement `fa_fnode` to move below the current monitor.
- Use `vsop_find()`/`vfsop_find()` to find the next monitor or base op.
- Assert valid function and target object.
- Invoke with the same logical operation arguments.

These are the canonical way for interposition modules to continue the operation chain.

## Stack Lifetime and Concurrency
`fem_lock()` / `fem_unlock()` protect a `fem_head`.
`fem_addref()` / `fem_delref()` use atomics for list lifetime.
`fem_get()` safely obtains a referenced current list.
`fem_release()` decrements the list refcount and, when zero, calls monitor argument release callbacks from top down before freeing the list.

This permits operations already in flight to continue on an old list while install/uninstall creates or swaps a new list.

## List Creation and Mutation
`new_femhead()` atomically installs a new head with CAS, preserving lock-free unaugmented fast paths.

`femlist_create()` allocates an uninitialized list with a placeholder guard.
`femlist_construct()` creates a list containing guard plus original base ops.
`fem_dup_list()` clones an existing stack and calls hold callbacks on cloned monitor arguments.

`fem_push_node()`:
- Validates monitor ops and opaque argument.
- Creates a head/list as needed.
- Expands stack capacity by cloning when full.
- Installs the head ops in the object’s `v_op`/`vfs_op` on first monitor push.
- Enforces install policy:
  - `FORCE`: always push.
  - `OPUNIQ`: reject if same ops vector already exists.
  - `OPARGUNIQ`: reject if same ops vector and opaque argument already exist.
- Appends the new node at top-of-stack.

`fem_remove_node()`:
- Finds a matching monitor by ops and optional data pointer.
- If list is idle, removes in place.
- If busy, clones list, removes from clone, and swaps current head.
- Restores base ops and clears list when the last monitor is removed.
- Calls release callbacks for removed monitor arguments.

## Public FEM API
Vnode interposition:
- `fem_create()`: builds a monitor vector from an operation template.
- `fem_install()`: pushes a monitor onto a vnode.
- `fem_is_installed()`: scans for a monitor/argument pair.
- `fem_uninstall()`: removes a monitor.
- `fem_setvnops()`: changes base vnode ops even when interposed.
- `fem_getvnops()`: returns base vnode ops under interposition.

VFS interposition:
- `fsem_create()`
- `fsem_install()`
- `fsem_is_installed()`
- `fsem_uninstall()`
- `fsem_setvfsops()`
- `fsem_getvfsops()`

VFS APIs require `vfs_implp` to be initialized.

## Initialization
`fem_init()`:
- Initializes null guard metadata.
- Creates vnode head ops via `vn_make_ops("fem-head", ...)`.
- Creates vnode guard monitor via `fem_create("fem-guard", ...)`.
- Creates VFS head ops via `vfs_makefsops(...)`.
- Creates VFS guard monitor via `fsem_create("fem-guard", ...)`.

## Integration Points
- Vnode/VFS operation registration: `vn_make_ops()`, `vfs_makefsops()`, `fs_build_vector()`.
- Core vnode fields: `v_op`, `v_femhead`.
- Core VFS fields: `vfs_op`, `vfs_femhead`, `vfs_implp`.
- Atomic and memory ordering primitives: `atomic_cas_ptr()`, `membar_consumer()`, `atomic_inc_32()`, `atomic_dec_32_nv()`.

## Risks and Subtle Areas
- Head functions are repetitive and must exactly match operation signatures; a mismatch corrupts call frames.
- Install/uninstall copy-on-update relies on correct refcount handling and hold/release callback symmetry.
- Removing the last monitor must restore base ops and free the list without disrupting in-flight callers.
- `fem_setvnops()` and `fsem_setvfsops()` must update base ops inside the stack when interposition is active.
- Guard ops panic intentionally; reaching them means stack underrun or corruption.
- `fem_push_node()` first monitor install changes object ops to head ops, so unaugmented objects stay fast until needed.

## Testing/Validation Signals
- Install one and multiple vnode monitors; verify call order and `vnext_*()` continuation.
- Install duplicate monitors under `FORCE`, `OPUNIQ`, and `OPARGUNIQ`.
- Uninstall while operations are in flight.
- Replace base vnode/VFS ops while a monitor is installed.
- VFS monitor install/uninstall on initialized and uninitialized VFS objects.
- Coverage across void-return operations as well as int-return operations.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifosubr.c -->
# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifosubr.c

## Purpose
Provides support routines and module initialization for FIFOFS, including fifonode/pipe allocation, FIFO shadow vnode management, STREAMS open coordination, connld handling, fast FIFO mode transitions, and reader/writer wakeups.

## Main Responsibilities
- Register and initialize the `fifofs` filesystem module.
- Create kmem caches for named FIFO nodes and anonymous pipe pairs.
- Maintain a hash table mapping real FIFO vnodes to FIFOFS shadow vnodes.
- Allocate and initialize pipe endpoint vnodes.
- Coordinate STREAMS open/close serialization for FIFOs and pipes.
- Handle `connld` by creating and passing a new pipe endpoint.
- Manage FIFO fast-mode buffering and transition to STREAMS mode.
- Wake blocked readers/writers and trigger poll/SIGPOLL notifications.

## Core State
- `fifoalloc[FIFO_HASHSZ]`: hash table of real vnode to fifonode shadows.
- `fifodev`, `fifovfsp`, `fifofstype`: synthetic FIFOFS device/VFS metadata.
- `ftable_lock`: protects FIFO shadow hash table.
- `fino_lock`: protects anonymous pipe inode counter.
- `fnode_cache`: cache for single-fnode FIFO data.
- `pipe_cache`: cache for two-fnode pipe data.
- `fifolock_t`: shared lock/CVs and synchronization state for one FIFO or pipe pair.

## Constructors and Destructors
`fnode_constructor()`:
- Initializes shared fifolock and every embedded fifonode.
- Allocates a vnode for each fnode.
- Initializes counters, destination pointer, stream state, pid/cred fields, wait CV, vnode ops/type/data/flags.
- Handles partial allocation failure by calling destructor.

`fnode_destructor()`:
- Asserts clean state.
- Destroys CVs, invalidates/frees vnodes, destroys shared lock/CV.

`pipe_constructor()`:
- Uses `fnode_constructor()` for two fnodes.
- Sets both vnodes to global FIFOFS VFS/device.
- Cross-links destinations between the two pipe ends.

`pipe_destructor()`:
- Debug-checks VFS/device fields and delegates to `fnode_destructor()`.

`fifo_reinit_vp()`:
- Reinitializes a cached vnode for reuse and restores VFIFO type plus `VNOMAP | VNOSWAP`.

## Initialization
`fifoinit()`:
- Installs empty VFS ops and vnode ops.
- Allocates unique pseudo-device number.
- Creates global FIFOFS VFS via `fs_vfsp_global()`.
- Initializes locks and caches.
- Applies debug high-water tuning to STREAMS module info.

Module `_init()` installs the filesystem module; `_info()` returns module info.

## Shadow FIFO Vnodes
`fifovp(vnode_t *vp, cred_t *crp)`:
- Allocates a speculative fnode.
- Resolves `VOP_REALVP()` so layered aliases share the same communication endpoint.
- Initializes counts, flags, timestamps from real vnode attributes.
- Holds real vnode before acquiring `ftable_lock`.
- If an existing shadow is found, drops the speculative allocation and returns the held existing shadow vnode.
- Otherwise reinitializes the new FIFO vnode, holds underlying VFS, copies VFS/rdev/root flag, inserts into hash table, and returns it.

`fifoinsert()`, `fifofind()`, and `fiforemove()` manage the hash table. `fifofind()` holds the found FIFO vnode before returning it.

## Pipe Creation and IDs
`makepipe()`:
- Allocates a two-fnode pipe object.
- Sets both ends reader/writer counts to one.
- Marks flags `ISPIPE` plus optional `FIFOFAST`.
- Initializes timestamps.
- Reinitializes both vnodes and restores global FIFOFS VFS/device.

`fifogetid()` returns a unique anonymous pipe inode number under `fino_lock`.

## STREAMS Open Coordination
`fifo_stropen()`:
- Serializes open using `FIFOOPEN` and the shared `flk_ocsync` open/close sync flag.
- Waits if another open is in progress.
- Rejects opens on a pipe end that is closing under namefs.
- Calls `stropen()` with the FIFO lock dropped to avoid module side effects under lock.
- On first open with `dotwist`, uses `strmate()` to connect stream queues.
- Increments `fn_open`, sets `FIFOISOPEN`, clears stale `FIFOCLOSE` when writers return, and wakes waiters.
- If `FIFOCONNLD` is set, delegates special reopen/new-pipe logic to `fifo_connld()` while preserving close synchronization with a fake open.

`fifo_cleanup()`:
- Used when open is interrupted.
- Cleans locks/shares for current process and decrements reader/writer counts.

## Connld Handling
`fifo_connld()`:
- Creates a new pipe with `makepipe()`.
- Allocates a file structure for one endpoint.
- Opens both stream heads and mates them.
- Marks the returned endpoint `FIFOOPEN`.
- Marks original destination as `FIFOSEND` and verifies it is still open.
- Tags sender credentials/pid on the passed pipe descriptor.
- Sends the file pointer over the old stream using `do_sendfp()`.
- Waits until the receiver consumes the fd or a close/signal occurs.
- On success, replaces caller’s vnode with the new endpoint and closes the temporary file structure.
- On failure, closes/free/releases all temporary pipe/file state.

## Fast FIFO Mode
`fifo_fastflush()`:
- Frees queued fast-mode message data, resets byte count, and wakes writers.

`fifo_fastoff()`:
- Waits while this FIFO or paired pipe endpoint has `FIFOSTAYFAST`.
- If still fast, calls `fifo_fastturnoff()` on this endpoint and pipe peer if needed.

`fifo_fastturnoff()`:
- Moves any fast-mode queued message into the STREAMS read queue with `put()`.
- Reissues poll wakeups so STREAMS sees pending read/write readiness.
- Clears `FIFOFAST`, `FIFOWANTW`, and `FIFOWANTR`.
- Wakes waiters.

`fifo_vfastoff()` is a vnode wrapper around `fifo_fastoff()`.

## Wakeup Helpers
`fifo_wakewriter()`:
- Wakes writers sleeping below high-water mark.
- Sends poll and signal notifications for write readiness.
- Clears writer wait/high-water/poll flags.

`fifo_wakereader()`:
- Wakes readers waiting for data.
- Sends poll and signal notifications for input/read-normal readiness.
- Clears reader wait/poll flags.

## Integration Points
- Vnode/VFS ops from FIFOFS vnode implementation (`fifo_vnodeops_template` external).
- STREAMS: `stropen()`, `strmate()`, `strpollwakeup()`, `str_sendsig()`, `do_sendfp()`, queue `put()`.
- VFS/vnode lifecycle: `vn_alloc()`, `vn_reinit()`, `vn_exists()`, `vn_invalid()`, `vn_free()`, `VN_HOLD()`, `VN_RELE()`, `VFS_HOLD()`.
- Credentials and process IDs for connld descriptor passing.
- Namefs/layering via `VOP_REALVP()`.

## Risks and Subtle Areas
- FIFO open/close synchronization depends on `FIFOOPEN`, `flk_ocsync`, and wait CVs; incorrect ordering can race with `stropen()` or close hangups.
- `fifo_connld()` has many staged resources: two vnodes, a file pointer, stream opens, `FIFOSEND`, credentials, and vnode replacement.
- Fast-mode transition must preserve queued data ordering while moving messages into STREAMS.
- Shadow FIFO hash table relies on real vnode identity; layered filesystems require `VOP_REALVP()` for correctness.
- Cached vnode reuse requires `fifo_reinit_vp()` to restore expected vnode type/flags after prior lifecycle.

## Testing/Validation Signals
- Named FIFO open races and interrupted opens.
- Anonymous pipe creation and bidirectional stream mating.
- FIFO vnode shadow reuse through lofs/namefs aliases.
- `connld` open with receiver success, receiver close, signal interruption, and send failure.
- Fast FIFO read/write path followed by `putmsg/getmsg` transition to STREAMS mode.
- Poll/SIGPOLL behavior for reader and writer wakeups.
<!-- END FILE RESEARCH: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/fifofs/fifosubr.c -->