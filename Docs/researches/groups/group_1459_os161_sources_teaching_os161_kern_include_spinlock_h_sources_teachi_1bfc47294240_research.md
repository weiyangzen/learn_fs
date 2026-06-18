# Group Research: group_1459_os161_sources_teaching_os161_kern_include_spinlock_h_sources_teachi_1bfc47294240

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/spinlock.h -->
# File Research: sources/teaching/os161/kern/include/spinlock.h

Defines the machine-independent public interface for OS/161 spinlocks. `struct spinlock` wraps the machine-dependent lock word, the owning CPU pointer, and optional Hangman deadlock-detector metadata. The header emphasizes that spinlocks are CPU-owned, not thread-owned, and that users should treat the structure as opaque despite its public layout for static allocation.

Exports `SPINLOCK_INITIALIZER`, `spinlock_init`, `spinlock_cleanup`, `spinlock_acquire`, `spinlock_release`, and `spinlock_do_i_hold`. Acquisition disables interrupts and release may restore them, making this file tightly coupled to `spl.h`, `machine/spinlock.h`, current CPU state, and low-level scheduler invariants.

Risk points: callers must not inspect internals directly, cleanup requires the lock to be unlocked, and misuse can block interrupts or deadlock CPUs.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/spinlock.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/spl.h -->
# File Research: sources/teaching/os161/kern/include/spl.h

Defines the machine-independent interrupt priority interface used by low-level synchronization and interrupt-sensitive code. OS/161 reduces traditional BSD-style interrupt priorities to `IPL_NONE` and `IPL_HIGH`, with `spl0()` enabling interrupts, `splhigh()` disabling them, and `splx(old)` restoring a prior state.

The inline wrappers call `splx(IPL_NONE)` and `splx(IPL_HIGH)`. Lower-level `splraise(oldipl, newipl)` and `spllower(oldipl, newipl)` are used by `splx` and spinlock code to transition interrupt state explicitly.

Important invariant: SPL affects only the current processor. Correct nesting depends on callers saving the old return value and restoring it with `splx`.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/spl.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/stat.h -->
# File Research: sources/teaching/os161/kern/include/stat.h

Provides the kernel-facing `stat` interface by including shared ABI definitions from `kern/stat.h` and shared file-type macros from `kern/stattypes.h`. It maps underscore-prefixed ABI constants to conventional names: `S_IFMT`, `S_IFREG`, `S_IFDIR`, `S_IFLNK`, `S_IFIFO`, `S_IFSOCK`, `S_IFCHR`, and `S_IFBLK`.

This header contains no logic; its role is compatibility and namespace presentation. VFS and device code use these macros to report vnode object types in `stat` data and type checks.

Risk is limited to ABI consistency: these aliases must track the shared `kern/*` definitions used by userland-visible structures.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/stat.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/stdarg.h -->
# File Research: sources/teaching/os161/kern/include/stdarg.h

Defines kernel varargs support around GCC builtins. It typedefs `va_list` to `__va_list` under GCC and selects `__builtin_stdarg_start` for older GCC versions or `__builtin_va_start` for GCC 4.8 and newer. It also defines `va_arg`, `va_copy`, and `va_end`.

The header additionally declares kernel printf-family varargs entry points: `vkprintf`, `vsnprintf`, and the shared printf driver `__vprintf`, using `__PF` annotations from `cdefs.h`.

This file is a portability boundary between compiler ABI details and kernel formatting code. It assumes GCC-compatible builtins; non-GCC compilers would need parallel definitions.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/stdarg.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/synch.h -->
# File Research: sources/teaching/os161/kern/include/synch.h

Declares higher-level synchronization primitives. Semaphores are fully shaped here with a name, wait channel, spinlock, and volatile count, and export `sem_create`, `sem_destroy`, `P`, and `V`.

Locks, condition variables, and reader-writer locks are intentionally skeletal teaching interfaces. `struct lock` includes a name and optional Hangman hook with placeholder fields for students. `struct cv` and `struct rwlock` likewise contain names and placeholders. The exported operations define expected semantics: exclusive locks, Mesa-style CVs, and read/write acquisition/release.

Dependencies include `spinlock.h`, wait channels, current-thread state, and scheduler sleep/wakeup behavior. The main risk is incomplete implementation: correctness depends on atomic sleep/release/reacquire behavior and ownership tracking.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/synch.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/syscall.h -->
# File Research: sources/teaching/os161/kern/include/syscall.h

Declares the system call entry and process entry helpers. `syscall(struct trapframe *tf)` is the dispatcher called from trap handling. `enter_forked_process(struct trapframe *tf)` is a student-supplied helper for fork return in the child. `enter_new_process(argc, argv, env, stackptr, entrypoint)` transitions to user mode and is marked `__DEAD`.

The file also declares in-kernel syscall implementations for reboot and time: `sys_reboot` and `sys___time`.

It bridges machine trapframes, user pointer types, virtual addresses, and syscall implementations. Correctness depends on trapframe ownership, user/kernel pointer validation, and not returning from user-mode entry.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/syscall.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/test.h -->
# File Research: sources/teaching/os161/kern/include/test.h

Central declaration header for OS/161 kernel tests, boot/menu entry points, and synchronization problem drivers. It declares tests for arrays, bitmaps, thread lists, threads, semaphores, locks, CVs, RW locks, filesystem stress, kmalloc, networking, HMAC, and automation deadlock/livelock checks.

It also declares `runprogram`, `menu`, and `kmain`. Optional blocks are controlled by generated config headers `opt-synchprobs.h` and `opt-automationtest.h`. Synchronization-problem hooks cover whalemating and stoplight primitives.

The `kprintf_t`/`kprintf_n` macros switch output behavior under `SECRET_TESTING`, with `silent` discarding formatted output. This file is mostly test surface area, but it influences automated grading and kernel diagnostics.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/test.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/thread.h -->
# File Research: sources/teaching/os161/kern/include/thread.h

Defines the public thread structure and scheduler lifecycle API. `struct thread` stores a fixed-size name, wait-channel name, state, machine-dependent state, intrusive list node, kernel stack, saved context, CPU pointer, process pointer, optional Hangman actor, and interrupt state fields.

Thread states are `S_RUN`, `S_READY`, `S_SLEEP`, and `S_ZOMBIE`. Stack constants define 4 KiB kernel stacks and helpers for stack-base comparison. The header also declares an array type for threads.

Exports system startup/shutdown functions, CPU startup, panic stop, `thread_fork`, `thread_exit`, `thread_yield`, timer scheduling hooks, migration consideration, and thread-count waiting. Public extension points are intentionally minimal.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/thread.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/threadlist.h -->
# File Research: sources/teaching/os161/kern/include/threadlist.h

Defines an intrusive doubly linked list specialized for `struct thread`. Lists contain permanent head and tail sentinel nodes, eliminating end-case handling. Each thread embeds a `threadlistnode`, and each node carries `tln_self` to recover the owning thread without pointer arithmetic.

Exports node/list init and cleanup, emptiness checks, add/remove at both ends, insertion before/after existing threads, arbitrary removal, and forward/reverse iteration macros.

The important invariant is that `struct threadlist` must not be assigned or memcpy’d after initialization because sentinel links point inside the structure. Correct use also depends on each thread being on at most one list through its embedded node.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/threadlist.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/threadprivate.h -->
# File Research: sources/teaching/os161/kern/include/threadprivate.h

Declares thread subsystem internals that must be visible to machine-dependent code. It is placed in the public include directory only because architecture-specific thread code needs it.

Exports `thread_startup`, machine-dependent thread init/cleanup, assembler context switching via `switchframe_switch`, and `switchframe_init` for new thread setup. The types are forward declared: `struct thread`, `struct thread_machdep`, and `struct switchframe`.

This file is the boundary between portable thread management and architecture-specific saved-register frames. It should be used only by the thread subsystem; external users would couple themselves to scheduler internals.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/threadprivate.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/types.h -->
# File Research: sources/teaching/os161/kern/include/types.h

Master kernel type header. Its comment documents include-order conventions: every source includes `types.h` first, other headers should include direct dependencies, and lower-level headers precede higher-level subsystems.

It includes user-visible `kern/types.h` and machine-private `machine/types.h`, defines typed `userptr_t` and `const_userptr_t` as pointers to an opaque one-byte struct, then maps underscore ABI types to conventional kernel names such as `uint32_t`, `size_t`, `off_t`, `pid_t`, and socket-related types.

It also defines `CHAR_BIT`, `NULL`, `bool`, `true`, and `false`. The `userptr_t` design helps prevent accidental mixing of user and kernel pointers at compile time.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/types.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/uio.h -->
# File Research: sources/teaching/os161/kern/include/uio.h

Defines BSD-style `struct uio`, the kernel abstraction for moving data between kernel buffers and user or kernel memory while tracking offset and residual byte count. It uses `struct iovec`, `uio_iovcnt`, `uio_offset`, `uio_resid`, segment flag, read/write direction, and associated address space.

Directions are `UIO_READ` and `UIO_WRITE`; segments distinguish user instruction space, user data space, and kernel space. Exports `uiomove`, `uiomovezeros`, and `uio_kinit`.

Important semantics: `uiomove` mutates iovec fields, increments `uio_offset`, decrements `uio_resid`, and requires the active address space to match `uio_space` for user transfers. Directory offsets may be filesystem cookies, not byte counts.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/uio.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/version.h -->
# File Research: sources/teaching/os161/kern/include/version.h

Small version-identification header. `BASE_VERSION` is fixed at `"2.0.3"` to identify the OS/161 base code. `GROUP_VERSION` is set to `"0"` and is intended for local course or project modifications.

There is no executable logic and no dependencies beyond include guards. It is useful for boot banners, support diagnostics, and distinguishing modified student kernels from the distributed base.

Risk is operational rather than technical: changing `BASE_VERSION` would obscure provenance, while leaving `GROUP_VERSION` unchanged after significant changes reduces traceability.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/version.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/vfs.h -->
# File Research: sources/teaching/os161/kern/include/vfs.h

Publishes the Virtual File System interface. Low-level calls manage current directories, sync, root lookup, and device-name lookup. Mid-level calls perform full-path lookup and parent lookup. High-level pathname calls implement open, close, readlink, symlink, mkdir, link, remove, rmdir, rename, chdir, and getcwd.

The header also declares VFS bootstrap, boot filesystem management, device/filesystem registration, mount/unmount, swap attach/detach, and unmount-all. It defines a vnode array type and exposes the global `vfs_biglock` API.

The comments explicitly mark the big lock as a teaching simplification to remove for the filesystem assignment. Most functions accept mutable path buffers because lookup may destructively parse them.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/vfs.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/vm.h -->
# File Research: sources/teaching/os161/kern/include/vm.h

Declares VM subsystem entry points and common fault constants. It includes `machine/vm.h`, defines `VM_FAULT_READ`, `VM_FAULT_WRITE`, and `VM_FAULT_READONLY`, and exports `vm_bootstrap`, `vm_fault`, `alloc_kpages`, `free_kpages`, `coremap_used_bytes`, and `vm_tlbshootdown`.

This is intentionally sparse and assignment-oriented. It forms the contract among trap handling, kmalloc page allocation, coremap accounting, and interprocessor TLB shootdown handling.

Risk areas are implementation-dependent: address validation, fault-type handling, physical page ownership, and shootdown correctness are not resolved in this header.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/vm.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/vnode.h -->
# File Research: sources/teaching/os161/kern/include/vnode.h

Defines OS/161’s abstract file object. `struct vnode` carries a reference count protected by a spinlock, an owning filesystem pointer, filesystem-specific data, and a `vnode_ops` dispatch table. Device vnodes may have `vn_fs == NULL`.

`struct vnode_ops` covers open/reclaim, read/write/readlink/getdirentry/ioctl/stat/type/seek/fsync/mmap/truncate/namefile, creation/removal/link/rename operations, and lookup/lookparent. `VOP_*` macros validate the vnode with `vnode_check` then dispatch through the table.

The header also exports reference manipulation, initialization/cleanup, and many typed failure stubs for unsupported operations. Main invariants: ops magic must match `VOP_MAGIC`, refcounts must remain positive while in use, and filesystems must return referenced vnodes from lookup-style operations.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/vnode.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/include/wchan.h -->
# File Research: sources/teaching/os161/kern/include/wchan.h

Declares opaque wait channels used to block and wake threads. A wait channel has a symbolic name, creation/destruction calls, diagnostic emptiness check, sleep, wake-one, and wake-all operations.

The sleep API requires the associated spinlock to be held. `wchan_sleep` atomically releases that lock while sleeping and reacquires it before returning. Wake APIs expect the spinlock to be held; FIFO behavior is current implementation detail, not an interface promise.

This header underpins semaphores and likely other blocking primitives. Correctness depends on using the same lock to protect the condition being waited on and avoiding sleep from interrupt context.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/include/wchan.h -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/device.c -->
# File Research: sources/teaching/os161/kern/vfs/device.c

Implements vnode operations for VFS devices by adapting `struct device_ops` to the vnode interface. `dev_eachopen` rejects creation, truncation, exclusive create, and append flags before delegating to `DEVOP_EACHOPEN`. Reads and writes validate seek position with `dev_tryseek`, assert correct `uio_rw`, then call `DEVOP_IO`.

Block devices require block-aligned offsets within device bounds; character devices are treated as nonseekable by `dev_isseekable`, though `dev_tryseek` currently accepts positions. `dev_stat` synthesizes size, block size, type, permissions, link count, and device numbers. Lookup of an empty suffix returns the device itself; nonempty suffixes fail.

`dev_create_vnode` allocates and initializes a permanent device vnode. `dev_uncreate_vnode` is only for failure paths.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/device.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/devnull.c -->
# File Research: sources/teaching/os161/kern/vfs/devnull.c

Implements the `null:` device. `nullopen` accepts all opens. `nullio` returns immediate EOF for reads by doing nothing, and discards writes by setting `uio_resid` to zero without reading the source buffer. This intentionally allows writes from invalid pointers to succeed, matching traditional null-device behavior. `nullioctl` rejects all ioctls with `EINVAL`.

`devnull_create` allocates a `struct device`, fills its ops, marks it as a character device with zero blocks and block size one, clears private data, and registers it with `vfs_adddev("null", dev, 0)`.

Failure to allocate or register panics during bootstrap.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/devnull.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/vfscwd.c -->
# File Research: sources/teaching/os161/kern/vfs/vfscwd.c

Implements current-working-directory operations. `vfs_getcurdir` takes `curproc->p_lock`, increfs `p_cwd` if present, and returns `ENOENT` otherwise. `vfs_setcurdir` verifies the vnode type is `S_IFDIR`, increfs the new directory, swaps it under the process lock, then decrefs the old directory. `vfs_clearcurdir` clears and releases the old reference.

`vfs_chdir` resolves a pathname with `vfs_lookup`, installs it with `vfs_setcurdir`, and drops the lookup reference. `vfs_getcwd` writes `volume-or-device-name:` followed by `VOP_NAMEFILE(cwd, uio)`.

The code depends on balanced vnode references and assumes current directories are filesystem-backed, not device vnodes.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/vfscwd.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/vfsfail.c -->
# File Research: sources/teaching/os161/kern/vfs/vfsfail.c

Provides typed stub implementations for vnode operations that are invalid or unsupported for a given vnode type. Because portable C does not allow safely sharing function pointers across incompatible signatures, each operation family has its own wrapper with matching arguments.

The stubs return specific errno values: `ENOTDIR` for directory-required operations on non-directories, `EISDIR` for file operations on directories, `EINVAL` for invalid operations, `ENOSYS` for unimplemented features, and `EPERM` for permission-denied mmap. Covered families include uio ops, mmap, truncate, creat, symlink, mkdir, link, remove/rmdir, rename, lookup, and lookparent.

Filesystems and device vnodes use these stubs to fill unsupported `vnode_ops` slots consistently.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/vfsfail.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/vfslist.c -->
# File Research: sources/teaching/os161/kern/vfs/vfslist.c

Maintains the global VFS named-device table. Each `knowndev` records a device name, optional raw name, device pointer, device vnode, and mounted or hardwired filesystem. `SWAP_FS` is a sentinel marking a device used as swap.

`vfs_bootstrap` creates the device array, creates the recursive teaching `vfs_biglock`, registers `null:`, and bootstraps `semfs`. The big lock tracks recursion depth and has defensive behavior for unimplemented student locks.

The file implements sync across filesystems, root lookup by device or volume name, device-name lookup for a filesystem, duplicate-name checks, `vfs_adddev`, `vfs_addfs`, mount, unmount, swap attach/detach, and unmount-all. Mountable devices expose both `name` and `nameraw`.

Main risks: coarse recursive locking, linear global table scans, and careful handling of mounted, raw, hardwired, and swap states.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/vfslist.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/vfslookup.c -->
# File Research: sources/teaching/os161/kern/vfs/vfslookup.c

Implements pathname translation entry points. A static `bootfs_vnode` anchors absolute paths beginning with `/`. `vfs_setbootfs` normalizes a filesystem name to include a trailing colon, changes to it, gets the resulting current directory, and installs it as bootfs under the VFS big lock. `vfs_clearbootfs` drops that reference.

The internal `getdevice` destructively parses a path into a starting vnode and remaining subpath. It handles relative paths via current directory, `device:path` via `vfs_getroot`, `/path` via bootfs, and `:path` via the root of the current filesystem.

`vfs_lookup` and `vfs_lookparent` hold `vfs_biglock`, call `getdevice`, dispatch to `VOP_LOOKUP` or `VOP_LOOKPARENT`, and balance references.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/vfslookup.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/vfspath.c -->
# File Research: sources/teaching/os161/kern/vfs/vfspath.c

Implements high-level pathname operations. `vfs_open` validates access mode, handles `O_CREAT` with `vfs_lookparent` plus `VOP_CREAT`, otherwise uses `vfs_lookup`, calls `VOP_EACHOPEN`, and handles `O_TRUNC` only for writable opens. On success it returns a referenced vnode.

`vfs_close` decrefs without reporting errors, with comments explaining why close failures are not propagated. Remove, mkdir, rmdir, symlink, and rename-style operations resolve parent directories and final names, call the corresponding VOP, then decref parents. `vfs_link` and `vfs_rename` reject cross-filesystem operations with `EXDEV`.

Symlink support is explicitly partial: `vfs_symlink` and `vfs_readlink` exist, but broader VFS symlink traversal is noted as incomplete.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/vfspath.c -->

<!-- BEGIN FILE RESEARCH: sources/teaching/os161/kern/vfs/vnode.c -->
# File Research: sources/teaching/os161/kern/vfs/vnode.c

Implements generic vnode lifecycle and validation. `vnode_init` installs the ops table, initializes refcount to one, initializes the refcount spinlock, and stores filesystem and private data. `vnode_cleanup` asserts refcount is one, cleans the spinlock, and poisons logical ownership fields to null/zero.

`vnode_incref` increments under `vn_countlock`. `vnode_decref` decrements when refcount is greater than one; when dropping the last reference it leaves the count for `VOP_RECLAIM`, calls reclaim outside the spinlock, and warns on unexpected errors other than `EBUSY`.

`vnode_check` validates non-null/non-poison pointers, ops magic, filesystem pointer sanity, and refcount range before every `VOP_*` dispatch.
<!-- END FILE RESEARCH: sources/teaching/os161/kern/vfs/vnode.c -->