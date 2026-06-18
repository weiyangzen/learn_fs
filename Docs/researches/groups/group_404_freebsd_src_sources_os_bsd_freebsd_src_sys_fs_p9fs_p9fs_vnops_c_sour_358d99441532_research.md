# Group Research: group_404_freebsd_src_sources_os_bsd_freebsd_src_sys_fs_p9fs_p9fs_vnops_c_sour_358d99441532

Scope: `Docs/research_subset_a.md` includes `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vnops.c

## Purpose

Implements FreeBSD vnode operations for the 9P filesystem client. It translates VFS operations into 9P client requests, maintains p9fs node/fid state, updates vnode attributes and pager size, and connects path lookup, creation, I/O, directory iteration, removal, rename, links, symlinks, and VM paging to the lower `p9_client_*` protocol layer.

## Main Entry Points

The exported VOP vector `p9fs_vnops` registers handlers for lookup, open/close, access, getattr/setattr, create/mknod/mkdir, read/write, remove/rmdir, readdir, strategy, symlink, rename, link, readlink, putpages, inactive, reclaim, delayed setsize, and pathconf.

Node lifetime is handled by:
- `p9fs_cleanup()`: removes a vnode from the hash/session lists, purges namecache entries, destroys the VM object, removes all fids, and destroys the `p9fs_node`.
- `p9fs_reclaim()`: calls cleanup on vnode reclaim.
- `p9fs_inactive()`: recycles nodes marked `P9FS_NODE_DELETED`.

Lookup and creation:
- `p9fs_lookup()` walks the server with `p9_client_walk()`, validates cached vnodes against returned qids and fresh attrs, enforces read-only/delete/rename and sticky-directory rules, and calls `p9fs_vget_common()` for new vnode materialization.
- `create_common()` clones the parent fid, sends `p9_client_file_create()`, walks back to the new child, creates the vnode, and retains the create-open fid as a `VOFID` when appropriate.
- `p9fs_create()`, `p9fs_mkdir()`, and `p9fs_mknod()` are thin mode translators around `create_common()`.

Attributes and permissions:
- `p9fs_reload_stats_dotl()` and `p9fs_stat_vnode_dotl()` fetch 9P2000.L attrs, update inode fields, vnode type, qid version, modification flag, and pager size.
- `p9fs_getattr_dotl()` exports inode fields as `struct vattr`.
- `p9fs_setattr_dotl()` implements chmod/chown/truncate/time changes, builds `p9_iattr_dotl`, calls `p9_client_setattr()`, and rolls back size on failed truncation.
- `p9fs_access()` combines read-only filesystem checks with `vaccess()`.

I/O:
- `p9fs_open()` finds or clones a fid, sends `p9_client_open()`, tracks `v_opens`, creates a vnode object for regular files, and caches open fids per credential/mode.
- `p9fs_close()` decrements open fid counts; final clunk happens during node cleanup.
- `p9fs_read()` and `p9fs_write()` obtain an open fid, use a UMA I/O buffer, loop over `p9_client_read()`/`p9_client_write()`, and move data through `uio`.
- `p9fs_strategy()` and `p9fs_doio()` service buffer-cache I/O through synthetic `uio` structures.
- `p9fs_putpages()` maps dirty VM pages into a pbuf and writes them synchronously via `VOP_WRITE()`.

Directory and namespace operations:
- `p9fs_readdir()` reads 9P directory data with `p9_client_readdir()`, parses `struct p9_dirent`, and emits FreeBSD `struct dirent`.
- `remove_common()`, `p9fs_remove()`, and `p9fs_rmdir()` call `p9_client_unlink()`, remove non-open fids, purge caches, remove from vnode hash, and mark deleted.
- `p9fs_symlink()`, `p9fs_link()`, `p9fs_readlink()`, and `p9fs_rename()` map VFS namespace operations to 9P symlink, hardlink, readlink, and renameat helpers.
- `p9fs_pathconf()` returns `_PC_NAME_MAX` from `p9_client_statfs()` when available and conservative path/symlink limits otherwise.

## Integration Points

This file depends on `p9fs_get_fid()`, `p9fs_fid_add()`, `p9fs_fid_remove_all()`, `p9fs_vget_common()`, `p9fs_destroy_node()`, and lower `p9_client_*` request helpers. It owns the VFS-facing half of p9fs and cooperates with mount/session code through `struct p9fs_session`, vnode hash membership, and the session node list.

## Risks and Review Notes

Name lookup temporarily null-terminates `cn_nameptr`; all paths restore the saved byte, so error exits around that pattern are important review targets.

Open fid reuse is credential/mode sensitive and deliberately retains create-open fids to avoid failing later opens on newly created `000` files.

`p9fs_write()` moves data from the user `uio` before all server writes complete; if the server accepts only a partial inner write, the user-visible `uio` offset can advance farther than the actual server offset. This is worth targeted write-shortening tests.

Several size updates derive from current `uio` state after loops. Truncate/write/page-write behavior should be tested around partial writes, EOF extension, and concurrent server-side file changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.c

## Purpose

Defines the FreeBSD `procfs` pseudofs instance and registers the process-oriented file hierarchy under `/proc`. It supplies shared attribute and visibility callbacks plus simple filler callbacks for `curproc`, `self`, and executable path links.

## Main Entry Points

`procfs_init()` builds the tree:
- root links: `curproc`, `self`.
- process directory: `pid`, marked `PFS_PROCDEP`.
- per-process files: `cmdline`, `dbregs`, `etype`, `fpregs`, `map`, `mem`, `note`, `notepg`, `regs`, `rlimit`, `status`, `osrel`.
- per-process links: `file`, `exe`.

`procfs_doprocfile()` returns the process binary path using `proc_get_binpath()`.

`procfs_docurproc()` emits the current process pid.

`procfs_attr_all_rx()`, `procfs_attr_rw()`, and `procfs_attr_w()` wrap `procfs_attr()` to set fixed file modes. For setuid/setgid-exec processes, non-process-directory entries are hidden by setting mode `0`.

`procfs_notsystem()` hides entries for `P_SYSTEM` processes.

`procfs_candebug()` exposes entries only for non-system processes that pass `p_candebug()`.

`procfs_uninit()` has no explicit cleanup because pseudofs garbage-collects the constructed tree.

## Integration Points

The file uses the `PSEUDOFS(procfs, 1, VFCF_JAIL)` macro from pseudofs to register VFS operations and module dependency. Most content handlers are implemented in the sibling `procfs_*.c` files and declared by `procfs.h`.

## Risks and Review Notes

Visibility and permission behavior relies on callers honoring pseudofs callback locking rules: attribute and visibility callbacks expect the target process lock held. Debug-sensitive nodes use both `procfs_candebug()` at lookup/visibility time and deeper checks in their file handlers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.h

## Purpose

Declares the kernel-only procfs filler, attribute, and visibility callback prototypes shared by `procfs.c` and per-file procfs implementations.

## Interface

Declared filler callbacks:
- `procfs_docurproc()`
- `procfs_doosrel()`
- `procfs_doproccmdline()`
- `procfs_doprocdbregs()`
- `procfs_doprocfile()`
- `procfs_doprocfpregs()`
- `procfs_doprocmap()`
- `procfs_doprocmem()`
- `procfs_doprocnote()`
- `procfs_doprocregs()`
- `procfs_doprocrlimit()`
- `procfs_doprocstatus()`
- `procfs_doproctype()`

Declared attribute callbacks:
- `procfs_attr_w()`
- `procfs_attr_rw()`
- `procfs_attr_all_rx()`

Declared visibility callbacks:
- `procfs_notsystem()`
- `procfs_candebug()`

## Integration Points

This header depends on pseudofs callback macros such as `PFS_FILL_ARGS`, `PFS_ATTR_ARGS`, and `PFS_VIS_ARGS`, so it is included after pseudofs declarations by implementation files.

## Risks and Review Notes

The header is intentionally minimal and kernel-guarded. ABI/API coupling is mostly by callback signature; any pseudofs callback signature change would require coordinated updates here and in all procfs content files.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_dbregs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_dbregs.c

## Purpose

Implements `/proc/<pid>/dbregs`, exposing target-process debug registers through procfs raw read/write.

## Main Entry Point

`procfs_doprocdbregs()`:
- ignores nonzero offsets by returning success with no data.
- locks the target process and verifies `p_candebug()`.
- selects the first thread in the process.
- under `COMPAT_FREEBSD32`, wraps 32-bit callers to 32-bit debug register access only when the target process is also ILP32; otherwise returns `EINVAL`.
- reads debug registers with `proc_read_dbregs()` or `proc_read_dbregs32()`.
- copies the register buffer through `uiomove_frombuf()`.
- on write, requires the process to be stopped via `P_SHOULDSTOP(p)` before calling `proc_write_dbregs()` or `proc_write_dbregs32()`.

## Integration Points

Registered by `procfs.c` as `dbregs` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

Reads do not require the target to be stopped, while writes do. The code unlocks the process around `uiomove_frombuf()` and relocks afterward, so stopped/debuggability state can change between read-copy and write-back; the write path rechecks stopped state but not `p_candebug()` after relock.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_dbregs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_fpregs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_fpregs.c

## Purpose

Implements `/proc/<pid>/fpregs`, exposing target-process floating-point register state through procfs raw read/write.

## Main Entry Point

`procfs_doprocfpregs()`:
- ignores nonzero offsets.
- locks the target process and requires `p_candebug()` success.
- requires the target process to be stopped with `P_SHOULDSTOP(p)` for both reads and writes.
- uses the first thread in the process.
- supports `COMPAT_FREEBSD32` by selecting `struct fpreg32` and `proc_read_fpregs32()`/`proc_write_fpregs32()` when caller and target are both ILP32.
- copies register data through `uiomove_frombuf()`.
- writes register data back only if the target is still stopped after the copy phase.

## Integration Points

Registered by `procfs.c` as `fpregs` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

The process lock is dropped during `uiomove_frombuf()`. The code rechecks stopped state before write-back, which is critical because the process can resume while the copy is in progress.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_fpregs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_map.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_map.c

## Purpose

Implements `/proc/<pid>/map`, a text representation of the target process VM map including address ranges, resident/private page counts, object metadata, protection bits, COW flags, backing type/path, and charged credential information.

## Main Entry Point

`procfs_doprocmap()`:
- requires `p_candebug()` and read-only access.
- rejects 32-bit callers reading a 64-bit target under `COMPAT_FREEBSD32`.
- obtains a referenced `vmspace`, locks the VM map for reading, and iterates non-submap entries.
- locks VM objects along backing chains to gather object type, vnode path, resident counts, flags, reference count, and shadow count.
- temporarily drops the VM map lock while formatting each entry and resolving vnode full paths.
- re-locks the map and uses the timestamp to recover if the map changed while unlocked.
- emits one line per mapping with start/end, residency, object pointer unless hidden for 32-bit wrapping, protection string, object counts/flags, COW/needs-copy state, type, path, charge marker, and charged uid.

## Integration Points

Registered by `procfs.c` as `map` with `PFS_RD` and `procfs_notsystem`. It uses VM internals, `vn_fullpath()`, `vmspace_acquire_ref()`, `kern_proc_vmmap_resident()`, and `vm_object_kvme_type()`.

## Risks and Review Notes

The function intentionally cannot provide an atomic full-map snapshot; it formats while dropping the map lock and compensates with map timestamps. Large maps can overflow the sbuf and terminate early, matching the file comment’s expectation that readers may need larger buffers.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_map.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_mem.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_mem.c

## Purpose

Implements `/proc/<pid>/mem`, allowing raw reads and writes of target process memory through procfs.

## Main Entry Point

`procfs_doprocmem()`:
- returns immediately for zero-length I/O.
- locks the target process and checks `p_candebug()`.
- delegates actual memory transfer to `proc_rwmem(p, uio)` when permitted.

## Integration Points

Registered by `procfs.c` as `mem` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

Security is concentrated in `p_candebug()` and `proc_rwmem()`. The procfs layer itself does not add range policy beyond the caller’s `uio`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_mem.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_note.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_note.c

## Purpose

Provides the handler for `/proc/<pid>/note` and `/proc/<pid>/notepg`.

## Main Entry Point

`procfs_doprocnote()` trims and finishes the sbuf, then returns `EOPNOTSUPP`.

## Integration Points

Registered by `procfs.c` as write-only `note` and `notepg` entries with `procfs_attr_w` and `procfs_candebug`.

## Risks and Review Notes

The file is a stub: writes are accepted into the pseudofs buffer but no signal/notification action is implemented. Consumers expecting historical procfs note semantics receive `EOPNOTSUPP`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_note.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_osrel.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_osrel.c

## Purpose

Implements `/proc/<pid>/osrel`, exposing and allowing updates to a process’s ABI OS release value.

## Main Entry Point

`procfs_doosrel()`:
- rejects calls without a `uio`.
- on read, emits `p->p_osrel` followed by newline.
- on write, trims and finishes the sbuf, parses only decimal digits, detects integer wrap by checking monotonic accumulation, and stores the parsed value in `p->p_osrel`.

## Integration Points

Registered by `procfs.c` as `osrel` with `PFS_RDWR`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

The parser accepts only unsigned decimal text after trimming and does not accept whitespace or signs. Write access is gated by procfs debug permission rather than by a file-local privilege check.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_osrel.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_regs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_regs.c

## Purpose

Implements `/proc/<pid>/regs`, exposing target-process general register state through procfs raw read/write.

## Main Entry Point

`procfs_doprocregs()`:
- ignores nonzero offsets.
- requires `p_candebug()` success.
- requires `P_SHOULDSTOP(p)` for register read and write.
- selects the first thread in the process.
- supports `COMPAT_FREEBSD32` with `struct reg32` and 32-bit read/write routines when caller and target are both ILP32.
- copies register state through `uiomove_frombuf()`.
- writes back the register state only if the target remains stopped.

## Integration Points

Registered by `procfs.c` as `regs` with `PFS_RDWR | PFS_RAW`, `procfs_attr_rw`, and `procfs_candebug`.

## Risks and Review Notes

The stopped-state requirement prevents racing active execution. Like the fpregs handler, the process lock is dropped for the user I/O copy and stopped state is rechecked before write-back.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_regs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_rlimit.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_rlimit.c

## Purpose

Implements `/proc/<pid>/rlimit`, a read-only text view of process resource limits.

## Main Entry Point

`procfs_doprocrlimit()`:
- obtains a private reference to the process limit structure with `lim_hold()`.
- iterates all `RLIM_NLIMITS` entries.
- emits `rlimit_ident[i]`, current limit, and maximum limit per line.
- represents `RLIM_INFINITY` as `-1`.
- releases the limit reference with `lim_free()`.

A static assertion ensures `rlimit_ident[]` remains aligned with `RLIM_NLIMITS`.

## Integration Points

Registered by `procfs.c` as `rlimit` with `PFS_RD`.

## Risks and Review Notes

The private limit reference avoids holding the process lock while formatting. Output compatibility depends on `resource.h` maintaining `_RLIMIT_IDENT` names in the expected order.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_rlimit.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_status.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_status.c

## Purpose

Implements `/proc/<pid>/status` and `/proc/<pid>/cmdline`.

## Main Entry Points

`procfs_doprocstatus()` emits a single status line containing:
- escaped command name.
- pid, parent pid, process group, session id.
- controlling tty and session flags.
- process start time, user CPU time, system CPU time.
- first thread wait message.
- effective/real uid and gid plus supplementary groups.
- jail/prison name or `-`.

It locks the process, session, first thread, and process stats as needed while gathering fields.

`procfs_doproccmdline()`:
- returns cached `p_args` contents when present and visible to the caller.
- returns an empty result for system processes.
- otherwise calls `proc_getargv()` to read argv from process memory.
- deliberately avoids falling back to `p_comm` if argv is unavailable.

## Integration Points

Registered by `procfs.c` as `status` and `cmdline`, both read-only.

## Risks and Review Notes

`status` produces historical procfs formatting, including comma-separated group data and escaped command bytes. `cmdline` follows Linux-like zero-length behavior when argv is unavailable, which callers must distinguish from an error-free empty command line.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_status.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_type.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_type.c

## Purpose

Implements `/proc/<pid>/etype`, exposing the target process executable/sysent ABI name.

## Main Entry Point

`procfs_doproctype()` prints `p->p_sysent->sv_name` when available, otherwise `Not Available`, followed by newline.

## Integration Points

Registered by `procfs.c` as read-only `etype`.

## Risks and Review Notes

This is a simple formatter. The output depends on `p_sysent` being present and named for the process ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/procfs/procfs_type.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.c

## Purpose

Implements the core pseudofs framework: node allocation, tree construction, destruction, mount/unmount/root/statfs operations, filesystem initialization, and module lifecycle.

## Main Entry Points

Node construction:
- `pfs_alloc_node_flags()` allocates a variable-length `struct pfs_node`, initializes its mutex, name, type, and owning `pfs_info`.
- `pfs_add_node()` attaches a node to a parent directory, rejects duplicate names, allocates file numbers, propagates `PFS_PROCDEP`, and appends to the child list.
- `pfs_fixup_dir_flags()` adds synthetic `.` and `..` nodes.
- `pfs_create_dir()`, `pfs_create_file()`, and `pfs_create_link()` create public directory, regular-file, and symlink nodes with callbacks and flags.
- `pfs_find_node()` finds a child by name.

Node destruction:
- `pfs_destroy()` detaches a node, recursively destroys children, purges associated vnodes, invokes optional destroy callbacks, frees the file number, destroys the mutex, and frees storage.

VFS operations:
- `pfs_mount()` initializes mount flags, fsid, statfs defaults, and `mnt_data`.
- `pfs_cmount()` delegates compatibility mounts to `kernel_mount()`.
- `pfs_unmount()` flushes vnodes with optional force.
- `pfs_root()` obtains the root vnode through the pseudofs vnode cache.
- `pfs_statfs()` is a no-op because `mp->mnt_stat` is already populated.

Lifecycle:
- `pfs_init()` initializes fileno allocation, creates root, adds `.`/`..`, and calls the consumer filesystem’s init callback.
- `pfs_uninit()` destroys the root tree, uninitializes fileno allocation, then calls the consumer uninit callback.
- `pfs_modevent()` loads/unloads the shared vnode cache for the pseudofs module.

## Integration Points

Consumers use the public construction APIs and `PSEUDOFS()` macro from `pseudofs.h`. `procfs` is one such consumer. Vnode realization is delegated to `pseudofs_vncache.c` and operation dispatch to `pseudofs_vnops.c`.

## Risks and Review Notes

The node tree is mostly immutable after filesystem initialization; child list manipulation uses node mutexes but some invariant checks are explicitly not fully locked. Dynamic consumers must be careful with parent-before-child lock ordering documented in `pseudofs.h`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.h

## Purpose

Defines the public pseudofs API, callback types, node/instance structures, flags, limits, and the `PSEUDOFS()` registration macro used by procfs-like synthetic filesystems.

## Main Interface

Types:
- `pfs_type_t`: root, directory, `.`/`..`, file, symlink, and process-directory node kinds.
- `struct pfs_info`: filesystem instance name, init/uninit callbacks, root node, mutex, and file-number allocator.
- `struct pfs_node`: immutable node identity/callback fields plus mutex-protected data, file number, parent/children/sibling pointers, and name.

Flags:
- `PFS_RD`, `PFS_WR`, `PFS_RDWR`: readable/writeable file semantics.
- `PFS_RAWRD`, `PFS_RAWWR`, `PFS_RAW`: raw `uio` handlers instead of sbuf text buffering.
- `PFS_PROCDEP`: process-dependent nodes.
- `PFS_NOWAIT`: nonblocking allocation option.
- `PFS_AUTODRAIN`: streaming sbuf reads.

Callback contracts:
- fill callbacks are called with proc held but unlocked.
- attr, visibility, ioctl, getextattr, and close callbacks document process-lock expectations through their macros/comments.

Public functions include mount/root/statfs/init/uninit, node creation, lookup, purge, and destroy.

`PSEUDOFS(name, version, flags)` creates per-filesystem `pfs_info`, mount/init/uninit wrappers, VFS ops, `VFS_SET`, module version, and pseudofs module dependency.

## Integration Points

Used by `procfs` and other synthetic filesystems to define hierarchy and behavior without writing their own VFS/vnode core.

## Risks and Review Notes

The callback locking contract is central: callers and implementers must agree on whether `struct proc` is locked, held, or unlocked. `struct pfs_node` comments define lock ownership for fields and require parent-before-child locking to avoid deadlocks.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_fileno.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_fileno.c

## Purpose

Manages pseudofs file number allocation for synthetic nodes.

## Main Entry Points

`pfs_fileno_init()` initializes the `pfs_info` mutex and creates an `unrhdr` allocator starting at file number 3. Root is reserved as file number 2.

`pfs_fileno_uninit()` deletes the allocator and destroys the mutex.

`pfs_fileno_alloc()` assigns:
- root: fixed file number 2.
- directories/files/symlinks/procdirs: a unique allocator number.
- `.`: the parent’s file number.
- `..`: the grandparent’s file number, or parent/root for root children.

`pfs_fileno_free()` releases allocator-owned file numbers and ignores root, `.`, and `..` nodes.

## Integration Points

Called from `pseudofs.c` during node add/destroy and filesystem init/uninit. `pseudofs_vnops.c` combines node file numbers with pid for process-dependent entries.

## Risks and Review Notes

The allocator range is bounded by `INT_MAX / NO_PID` because vnode file IDs may be multiplied by `NO_PID` and offset by pid for process-dependent nodes. Correct `.` and `..` numbering depends on parent links being established before allocation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_fileno.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_internal.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_internal.h

## Purpose

Defines private pseudofs internals shared by the core, vnode cache, fileno allocator, and vnode operations.

## Main Interface

`struct pfs_vdata` is per-vnode private data containing:
- `pvd_pn`: backing pseudofs node.
- `pvd_pid`: associated process id or `NO_PID`.
- `pvd_vnode`: back pointer.
- `pvd_hash`: vnode-cache hash link.

Declared internals:
- vnode cache load/unload/alloc/free.
- fileno init/uninit/alloc/free.
- `_vfs_pfs` sysctl declaration.

Debug macros:
- `PFS_TRACE()` and `PFS_RETURN()` emit operation tracing when `PSEUDOFS_TRACE` is enabled.

Inline wrappers:
- `pfs_lock()`, `pfs_unlock()`, and mutex assertions.
- `pn_fill()`, `pn_attr()`, `pn_vis()`, `pn_ioctl()`, `pn_getextattr()`, `pn_close()`, and `pn_destroy()` enforce expected callback presence, process lock state, and node lock state before invoking consumer callbacks.

## Integration Points

Included by pseudofs implementation files, not consumers. It bridges public callback definitions from `pseudofs.h` with internal vnode dispatch and lifecycle code.

## Risks and Review Notes

The inline wrappers encode several lock-state assertions. Violations in a consumer callback or vnode operation path will surface as kernel assertions under diagnostics, making these wrappers important correctness boundaries.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_internal.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vncache.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vncache.c

## Purpose

Implements the shared pseudofs vnode cache, keyed by pseudofs node, pid, and mount.

## Main Entry Points

`pfs_vncache_load()` initializes the global cache mutex, hash table, and process-exit event handler.

`pfs_vncache_unload()` deregisters the process-exit handler, purges all cached vnodes, asserts the cache is empty, destroys the mutex, and destroys the hash table.

`pfs_vncache_alloc()`:
- checks for an existing vnode for `(mount, pfs_node, pid)`.
- uses `vget_prep()`/`vget_finish()` to safely acquire cached vnodes.
- purges namecache entries on hits to avoid duplicate VFS cache entries by later callers.
- allocates a new vnode and `pfs_vdata` on misses.
- maps pseudofs node type to vnode type and root/procdep vnode flags.
- inserts the vnode into the mount queue and then into the cache.
- handles races by rechecking the cache after vnode construction and discarding the loser vnode.

`pfs_vncache_free()` removes vnode private data from the cache and frees it during reclaim.

`pfs_purge()` and `pfs_purge_all()` revoke cached vnodes, restarting scans because `vgone()` can sleep and mutate the cache.

`pfs_exit()` purges process-dependent vnodes for an exiting pid.

## Integration Points

Used by `pfs_root()`, pseudofs lookup, `vptocnp`, reclaim, node destroy, module load/unload, and process-exit cleanup.

## Risks and Review Notes

The purge path intentionally restarts scans after each `vgone()` to avoid holding the cache mutex across sleeping vnode teardown. This is safe but potentially expensive for large caches.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vncache.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vnops.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vnops.c

## Purpose

Implements vnode operations for pseudofs-backed synthetic filesystems. It handles visibility, lookup, attributes, open/read/write, directory enumeration, symlink reads, ioctl/extattr dispatch, reverse path lookup, and vnode reclaim.

## Main Entry Points

Visibility and lookup:
- `pfs_visible_proc()` checks process exit state, `p_cansee()`, and node visibility callbacks.
- `pfs_visible()` resolves pid to process and applies visibility.
- `pfs_lookup_proc()` obtains a held process reference for readdir.
- `pfs_lookup()` handles `.`/`..`, static child nodes, process-directory pid names, visibility, vnode-cache allocation, and namecache insertion. Delete and rename are unsupported.

Attributes and access:
- `pfs_getattr()` synthesizes file attributes, pid-adjusted file ids, timestamps, uid/gid from target process credentials, default modes, and optional consumer attr callback output.
- `pfs_access()` delegates to `vaccess()` after `VOP_GETATTR()`.
- `pfs_setattr()` silently ignores attribute changes.

Operations:
- `pfs_open()` verifies requested read/write modes against node flags and rejects advisory locks.
- `pfs_close()` calls a node close callback only on last close.
- `pfs_ioctl()` verifies a regular file, callback presence, and current visibility before invoking `pn_ioctl()`.
- `pfs_getextattr()` similarly dispatches optional extended-attribute callbacks.
- `pfs_read()` supports raw `uio` readers, buffered sbuf readers, and `PFS_AUTODRAIN` streaming reads with offset skipping.
- `pfs_write()` supports raw writers or sbuf-backed writes, capped at `PFS_MAXBUFSIZ`.
- `pfs_readdir()` lists static nodes and expands `pfstype_procdir` into visible process pid entries while holding `allproc_lock`.
- `pfs_readlink()` calls the node fill callback into a fixed path buffer.
- `pfs_vptocnp()` reconstructs vnode component names for reverse lookup and gets the parent vnode through the vnode cache.
- `pfs_reclaim()` frees vnode-cache state.

`pfs_vnodeops` registers the above plus `vfs_cache_lookup` and unsupported mutation VOPs.

## Integration Points

This file is the VFS dispatcher for all consumers registered through pseudofs, including procfs. It uses `pseudofs_internal.h` wrappers to enforce callback lock expectations and `pseudofs_vncache.c` for vnode reuse.

## Risks and Review Notes

Read paths drop the vnode lock while invoking fill callbacks and hold process references where needed. Consumer callbacks must tolerate process state changes between visibility checks and fill execution.

Directory offsets are fixed-size `PFS_DELEN` slots, not packed `dirent` sizes. Readers must use valid aligned offsets and buffer sizes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/pseudofs/pseudofs_vnops.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs.h

## Purpose

Defines public mount arguments, mount flags, version constants, and the kernel mount control block for FreeBSD SMBFS.

## Main Interface

Constants:
- `SMBFS_VERSION`, `SMBFS_VFSNAME`.
- mount flags such as soft, interruptible, strong, NLS present, and no-long-name mode.
- `SMBFS_MAXPATHCOMP`.

`struct smbfs_args` carries user mount parameters: device id, flags, mount point, root path, uid/gid, file/dir modes, and case option.

`struct smbmount` stores kernel mount state: owner uid/gid/modes, mount pointer, root node, device, owner credential, flags, next inode, share pointer, path stack, case option, and `sm_didrele` unmount/reclaim coordination flag.

Macros convert between mount, vnode, and smbfs mount objects.

Declared functions:
- `smbfs_ioctl()`
- `smbfs_doio()`
- `smbfs_vinvalbuf()`

## Integration Points

Included by SMBFS VFS, vnode, node, I/O, and SMB request implementation files. It ties SMBFS to `netsmb` share/device objects.

## Risks and Review Notes

This header represents SMBFS’s old SMB1-oriented mount state. Several fields, such as mount flags and root path buffers, are shared by user mount ABI and kernel internals, so compatibility constraints are high.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_io.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_io.c

## Purpose

Implements SMBFS file, directory, buffer-cache, and VM pager I/O helpers.

## Main Entry Points

Directory reads:
- `smbfs_readvdir()` emits `.` and `..`, opens or reuses a server search context, advances to the requested directory offset, reads entries via `smbfs_findnext()`, optionally performs fast vnode lookup/cache entry creation, and maps `ENOENT` to EOF.

File reads/writes:
- `smbfs_readvnode()` rejects unsupported segment modes and vnode types, handles directory reads, invalidates buffers if cached mtime changed, and reads from the open SMB fid with `smb_read()`.
- `smbfs_writevnode()` handles append/sync invalidation, enforces file-size limits with `vn_rlimit_fsize()`, writes with `smb_write()`, updates cached size, and adjusts pager size.

Buffer and pager I/O:
- `smbfs_doio()` maps a `struct buf` to a kernel `uio` and issues `smb_read()` or `smb_write()`, zero-filling short reads and preserving dirty buffers on interrupted or commit-needed writes.
- `smbfs_getpages()` maps VM pages into a pbuf, reads file data into them, and marks valid ranges.
- `smbfs_putpages()` maps dirty pages and writes them synchronously, then undirties pages on success.
- `smbfs_vinvalbuf()` serializes buffer flush/invalidate with `NFLUSHINPROG`/`NFLUSHWANT`, cleans vnode pages, retries `vinvalbuf()`, and handles interruptible waits.

## Integration Points

Called by SMBFS vnode operations for read/write/readdir/strategy/getpages/putpages and by node inactivity/close paths. It depends on `netsmb` `smb_read()`/`smb_write()`, SMB credentials, search contexts from `smbfs_smb.c`, and node cache fields.

## Risks and Review Notes

The directory offset model is `sizeof(struct dirent)` slots and maintains a single `n_dirseq` search context per node, so seek patterns can cause search reopen/skip work.

The buffer-write comment references NFS commit flags, reflecting inherited/old buffer-cache logic. Interrupted writes and dirty buffer preservation should be regression-tested for SMBFS specifically.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_io.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.c

## Purpose

Manages SMBFS vnode/private-node allocation, hash lookup, reclaim/inactive cleanup, and attribute caching.

## Main Entry Points

`smffs_hash()` computes an FNV-1 hash for names.

`smbfs_node_alloc()`:
- handles root/dotdot special cases.
- looks for existing vnodes with `vfs_hash_get()` using parent/name comparison.
- refreshes cached attributes on hits and kills stale vnodes whose file type no longer matches server attributes.
- allocates new vnode and `struct smbnode`, builds remote path, initializes vnode type/data, parent reference, inode number, and mount queue membership.
- inserts the vnode into the VFS hash and resolves races.

`smbfs_nget()` wraps node allocation using parent path and separator rules, then enters attributes if provided.

`smbfs_reclaim()` removes a vnode from the hash, frees name/path/node storage, clears vnode data, and releases referenced parent vnodes.

`smbfs_inactive()` closes open files or directory search contexts, invalidates buffers, sends SMB close for regular files, clears `NOPEN`, removes attr cache, and recycles nodes marked `NGONE`.

Attribute cache:
- `smbfs_attr_cacheenter()` updates cached size, mtime, DOS attrs, pager size, and attr timestamp.
- `smbfs_attr_cachelookup()` returns `ENOENT` for stale attrs older than two seconds, otherwise builds `struct vattr` from mount defaults, cached size/time, DOS flags, and share transmit size.

## Integration Points

Used by SMBFS lookup/readdir/create paths and by I/O code. It links VFS vnode identity to SMB remote paths and `netsmb` file attributes.

## Risks and Review Notes

Vnode identity is keyed by parent vnode plus name, while pseudo inode numbers are server-derived or hashed elsewhere. Rename/remove/server-side type changes require attr refresh and stale vnode teardown to avoid wrong vnode type reuse.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.h

## Purpose

Defines SMBFS vnode-private node state, node flags, vnode conversion macros, and node/I/O helper prototypes.

## Main Interface

`struct smbnode` stores:
- flags for flushing, modified state, parent references, pending wire flush, open state, and removed/renamed state.
- parent vnode and current vnode.
- mount pointer.
- attr cache timestamp, times, size, inode numbers, DOS attrs.
- SMB file id and granted access mode.
- remote path/name buffers and lengths.
- directory search context and offset.
- VFS hash linkage.

`struct smbcmp` is the VFS hash comparison key of parent, name length, and name.

Macros:
- `VTOSMB()`, `SMBTOV()`, `SMBFS_DNP_SEP()`.

Declared functions cover inactive/reclaim, node lookup/allocation, hash, VM page I/O, vnode read/write, and attribute cache operations.

## Integration Points

Shared by SMBFS node, VOP, I/O, VFS, and SMB request files.

## Risks and Review Notes

The node carries both vnode lifecycle state and wire protocol state. Callers must keep `NOPEN`, `n_fid`, directory search context, and parent references synchronized with vnode inactive/reclaim paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_node.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_smb.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_smb.c

## Purpose

Implements SMB1 wire-level filesystem operations for SMBFS: locks, statfs, file size/attrs/times, open/close/create/delete/rename/move/mkdir/rmdir, directory search, and lookup.

## Main Entry Points

Identity and locking:
- `smbfs_getino()` synthesizes inode numbers from parent inode plus filename hash.
- `smbfs_smb_lock()` uses `SMB_COM_LOCKING_ANDX` for LANMAN1+ dialects.

Filesystem stats:
- `smbfs_smb_statfs()` tries TRANS2 size info, then allocation info, then legacy disk info.

Size/flush:
- `smbfs_smb_seteof()` sends TRANS2 set end-of-file.
- `smbfs_smb_setfsize()` tries EOF info first, then falls back to legacy zero-length write at the requested offset.
- `smbfs_smb_flush()` sends `SMB_COM_FLUSH` only when `NFLUSHWIRE` is set.

Attributes/times:
- `smbfs_smb_query_info()` sends `SMB_COM_QUERY_INFORMATION`.
- `smbfs_smb_setpattr()`, `smbfs_smb_setptime2()`, `smbfs_smb_setpattrNT()`, `smbfs_smb_setftime()`, and `smbfs_smb_setfattrNT()` cover legacy, TRANS2, and NT basic-info variants.

Namespace and file operations:
- `smbfs_smb_open()` sends `SMB_COM_OPEN` and records fid/granted mode.
- `smbfs_smb_close()` sends `SMB_COM_CLOSE`.
- `smbfs_smb_create()` creates and immediately closes a file.
- `smbfs_smb_delete()`, `smbfs_smb_rename()`, `smbfs_smb_move()`, `smbfs_smb_mkdir()`, and `smbfs_smb_rmdir()` build path-based SMB requests.

Directory search:
- Legacy `SMB_COM_SEARCH` path: `smbfs_smb_search()`, `smbfs_findopenLM1()`, `smbfs_findnextLM1()`, `smbfs_findcloseLM1()`.
- TRANS2 path: `smbfs_smb_trans2find2()`, `smbfs_findopenLM2()`, `smbfs_findnextLM2()`, `smbfs_findcloseLM2()`.
- Public wrappers `smbfs_findopen()`, `smbfs_findnext()`, and `smbfs_findclose()` choose dialect-specific behavior, skip `.`/`..`, convert filenames to local encoding, and assign pseudo inode numbers.

Lookup:
- `smbfs_smb_lookup()` handles root specially, otherwise runs a single-entry directory search and returns attributes.

## Integration Points

This file is used by SMBFS VOP, I/O, node, and VFS operations. It depends heavily on `netsmb` request builders (`smb_rq`, `smb_t2rq`, `mbchain`, `mdchain`) and utility functions from `smbfs_subr.c`.

## Risks and Review Notes

The implementation is SMB1 dialect-dependent and includes legacy fallbacks for old servers. Unicode directory names, resume-name handling, and dialect-specific info levels are the highest-risk compatibility areas.

Several operations depend on old commands such as `SMB_COM_OPEN`, `SMB_COM_CREATE`, and `SMB_COM_SEARCH`; modern SMB behavior is outside this file’s protocol model.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_smb.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.c -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.c

## Purpose

Provides SMBFS utility routines for timestamp conversion, full path encoding, server-to-local filename conversion, and SMB credential allocation.

## Main Entry Points

Time conversion:
- `smb_time_local2server()` and `smb_time_server2local()` apply server timezone offsets to Unix seconds.
- `smb_time_NT2local()` converts NT 100ns timestamps since 1601 to Unix timespec.
- `smb_time_local2NT()` converts Unix time to NT timestamp units.
- `smb_time_unix2dos()` and `smb_dos2unixtime()` convert between Unix timespec and FAT date/time fields.

Path/name conversion:
- `smbfs_fullpath()` writes a full SMB path into an `mbchain`, with Unicode padding/termination when required, dialect-dependent uppercase conversion, existing node path, optional separator, optional child name, and NUL terminator.
- `smbfs_fname_tolocal()` converts server filenames through `vc_tolocal` iconv state and applies case options; for failed Unicode conversion, it substitutes `?` to avoid embedded NULs in local names.

Credentials:
- `smbfs_malloc_scred()` and `smbfs_free_scred()` allocate/free `struct smb_cred` using SMBFS malloc type.

## Integration Points

Used by `smbfs_smb.c`, I/O paths, and VOP code when building SMB requests and decoding server directory entries.

## Risks and Review Notes

Timestamp conversion mixes server timezone offsets for DOS/server seconds but treats NT timestamps as UTC. Filename conversion has a Unicode failure fallback that preserves operation progress at the cost of lossy names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.c -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.h

## Purpose

Declares SMBFS shared helper types, search context state, SMB wire-operation prototypes, time/path/name conversion helpers, and malloc types.

## Main Interface

Memory types:
- `M_SMBFSDATA`
- `M_SMBFSCRED`

`struct smbfattr` carries DOS attributes, size, atime/ctime/mtime, and pseudo inode.

Directory search:
- `SMBFS_RDD_*` flags describe findfirst/findnext state.
- `struct smbfs_fctx` stores wildcard, attr mask, share/credential, active request pointer, response counters, search key, fixed/allocated filename buffers, search id, info level, resume-name state, and current returned attrs/name.

Declared SMB-level operations:
- locking, statfs, file size.
- path and file attribute/timestamp setters.
- open/close/create/delete/flush/rename/move/mkdir/rmdir.
- findopen/findnext/findclose and lookup.
- full path construction and filename conversion.
- SMB time conversions.
- SMB credential allocation/free.

## Integration Points

Included by SMBFS node, I/O, request, and vnode operation files. It is the main internal API between VFS-facing SMBFS code and SMB wire request construction.

## Risks and Review Notes

The search context contains a union of request types and dialect-dependent fields. Correct cleanup requires matching the chosen search mode so outstanding request objects, server search handles, resume names, and allocated name buffers are all released.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/fs/smbfs/smbfs_subr.h -->