# Group Research: group_1284_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_mount_h_sources_os_bsd_e1e7c6b2165b

Scope: `Docs/research_subset_a.md`, NetBSD kernel/public system headers under `sources/os/bsd/netbsd-src/sys/sys`. All listed files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mount.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mount.h

## Purpose
Defines NetBSD VFS mount ABI and kernel mount infrastructure: filesystem type names, `struct mount`, `struct vfsops`, WAPBL hook dispatch, legacy export argument layouts, VFS kernel entry points, and userland mount-related declarations.

## Main API
- Public constants: `MNAMELEN`, `MOUNT_*` filesystem type strings, `VFS_*` sysctl identifiers, `VQ_MOUNT`, `VQ_UNMOUNT`.
- Kernel structures: `struct mount`, `struct vfsops`, `struct wapbl_ops`, `struct vfs_hooks`.
- VFS operation wrappers: `VFS_MOUNT`, `VFS_START`, `VFS_UNMOUNT`, `VFS_ROOT`, `VFS_SYNC`, `VFS_FHTOVP`, `VFS_VPTOFH`, `VFS_SNAPSHOT`, `VFS_EXTATTRCTL`, `VFS_SUSPENDCTL`.
- Filesystem implementation helper macro: `VFS_PROTOS(fsname)`.
- Kernel mount lifecycle and lookup helpers: `vfs_getvfs`, `vfs_mountroot`, `vfs_busy`, `vfs_unbusy`, `vfs_attach`, `vfs_detach`, `vfs_ref`, `vfs_rele`, `vfs_mountalloc`, `dounmount`, `do_sys_mount`.
- Quota forwarding helpers: `vfs_quotactl_*`.
- Userland declarations: `getfh`, `unmount`, `mount`, `fhopen`, `fhstat`.

## Dependencies
Pulls in core system headers including `sys/param.h`, `sys/ucred.h`, `sys/statvfs.h`, and, for kernel/exposed mount consumers, `sys/uio.h`, `sys/queue.h`, `sys/rwlock.h`, `sys/specificdata.h`, and `sys/condvar.h`.

## Risks and Notes
This is a central ABI boundary. `struct export_args30` is explicitly frozen for old binary mount utilities. `struct mount` separates mostly stable and volatile data and aligns `mnt_refcnt` to avoid cache contention. WAPBL hooks are indirection shims for journaling support and require valid `mnt_wapbl_op` before macro use.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mount.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mqueue.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mqueue.h

## Purpose
Defines POSIX message queue limits, attributes, and NetBSD kernel-side message queue state.

## Main API
- Public constants: `MQ_OPEN_MAX`, `MQ_PRIO_MAX`.
- Public structure: `struct mq_attr`.
- Kernel-only flags: `MQ_UNLINKED`, `MQ_RECEIVE`.
- Kernel constants: `MQ_NAMELEN`, `MQ_DEF_MSGSIZE`, `MQ_PQSIZE`, `MQ_PQRESQ`.
- Kernel structures: `mqueue_t`, `mq_msg_t`.
- Kernel functions: `mq_send1`, `mq_recv1`, `mqueue_get`, `mq_handle_open`, `mqueue_print_list`.

## Dependencies
Kernel mode depends on condition variables, mutexes, queues, select state, basic types, and `KERNEL_NAME_MAX` from `sys/param.h`.

## Risks and Notes
The implementation uses per-priority tail queues plus a bitmap, so priority bounds are part of the storage layout. Internal flags live in `mq_flags`, which POSIX permits, but consumers must not assume `mq_flags` contains only user-visible queue mode bits.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/msan.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/msan.h

## Purpose
Declares NetBSD KMSAN kernel memory sanitizer hooks and no-op stubs when KMSAN is disabled.

## Main API
- KMSAN states: `KMSAN_STATE_UNINIT`, `KMSAN_STATE_INITED`.
- Allocation/source types: `KMSAN_TYPE_STACK`, `KMSAN_TYPE_KMEM`, `KMSAN_TYPE_MALLOC`, `KMSAN_TYPE_POOL`, `KMSAN_TYPE_UVM`.
- DMA object types: `KMSAN_DMA_LINEAR`, `KMSAN_DMA_MBUF`, `KMSAN_DMA_UIO`, `KMSAN_DMA_RAW`.
- Runtime functions when enabled: `kmsan_init`, `kmsan_shadow_map`, `kmsan_lwp_alloc`, `kmsan_lwp_free`, `kmsan_dma_sync`, `kmsan_dma_load`, `kmsan_orig`, `kmsan_mark`, `kmsan_check_mbuf`, `kmsan_check_buf`.

## Dependencies
Includes `opt_kmsan.h` under `_KERNEL_OPT`; when `KMSAN` is enabled, depends on `sys/types.h` and `sys/bus.h`.

## Risks and Notes
When `KMSAN` is not defined, all hooks compile to `__nothing`. Code using these calls must not rely on side effects unless the sanitizer option is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/msan.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/msg.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/msg.h

## Purpose
Defines System V message queue ABI, kernel storage structures, sysctl export structures, limits, and syscall/internal entry points.

## Main API
- Public constant: `MSG_NOERROR`.
- Public types: `msgqnum_t`, `msglen_t`.
- Public structure: `struct msqid_ds`.
- NetBSD extensions: `struct msginfo`, `struct msgid_ds_sysctl`, `struct msg_sysctl_info`.
- Kernel structures: `struct __msg`, `struct msgmap`, `kmsq_t`.
- Kernel limits: `MSGSSZ`, `MSGSEG`, computed `MSGMAX`, `MSGMNB`, `MSGMNI`, `MSGTQL`.
- ID helpers: `MSQID`, `MSQID_IX`, `MSQID_SEQ`.
- Userland calls: `msgctl`, `msgget`, `msgsnd`, `msgrcv`.
- Kernel calls: `msginit`, `msgfini`, `msgctl1`, `msgsnd1`, `msgrcv1`.

## Dependencies
Depends on `sys/ipc.h`; kernel sections also use mutexes and condition variables.

## Risks and Notes
The segment size must be a valid power-of-two range checked by implementation code. `struct msqid_ds` contains private implementation fields, so ABI users should treat them as opaque despite header visibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/msg.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/msgbuf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/msgbuf.h

## Purpose
Defines the kernel circular message buffer used for console/log storage.

## Main API
- `struct kern_msgbuf` with magic, write/read offsets, size, and flexible buffer.
- Magic constant: `MSG_MAGIC`.
- Kernel globals: `msgbufmapped`, `msgbufenabled`, `msgbufp`, `log_open`.
- Kernel functions: `initmsgbuf`, `loginit`, `logputchar`.
- Inline helper: `logenabled`.

## Dependencies
Minimal; kernel users rely on the broader kernel environment for globals and initialization.

## Risks and Notes
`logenabled` checks both global enable state and the buffer magic. The buffer uses `char msg_bufc[1]`, an old flexible-array pattern, so allocation must account for the actual backing size.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/msgbuf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mtio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mtio.h

## Purpose
Defines magnetic tape ioctl structures, operation codes, device type/status constants, and kernel minor-device bit layout.

## Main API
- Command structures: `struct mtop`, `struct mtget`.
- Tape operations: `MTWEOF`, `MTFSF`, `MTBSF`, `MTFSR`, `MTBSR`, `MTREW`, `MTOFFL`, `MTNOP`, `MTRETEN`, `MTERASE`, `MTEOM`, `MTNBSF`, `MTCACHE`, `MTNOCACHE`, `MTSETBSIZ`, `MTSETDNSTY`, `MTCMPRESS`, `MTEWARN`.
- Status/type constants: `MT_IS*`, `MT_DS_RDONLY`, `MT_DS_MOUNTED`.
- Ioctls: `MTIOCTOP`, `MTIOCGET`, `MTIOCIEOT`, `MTIOCEEOT`, `MTIOCRDSPOS`, `MTIOCRDHPOS`, `MTIOCSLOCATE`, `MTIOCHLOCATE`.
- Kernel minor bits: `T_UNIT`, `T_NOREWIND`, `T_DENSEL`, density selectors.

## Dependencies
Uses `sys/ioccom.h` for ioctl encoding.

## Risks and Notes
The header notes that status registers are device-dependent and SCSI sense information does not fit cleanly into `mt_erreg`. 32-bit block-position ioctls are legacy-shaped and may not cover newer large tape command models.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mtio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mutex.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/mutex.h

## Purpose
Defines NetBSD kernel mutex abstraction, including adaptive/spin mutex types, machine-dependent contract, and public kernel mutex APIs.

## Main API
- Types: `kmutex_type_t`, opaque `kmutex_t`.
- Mutex classes: `MUTEX_SPIN`, `MUTEX_ADAPTIVE`, `MUTEX_DEFAULT`, `MUTEX_DRIVER`, `MUTEX_NODEBUG`.
- Private implementation constants under `__MUTEX_PRIVATE`.
- Kernel functions: `_mutex_init`, `mutex_init`, `mutex_destroy`, `mutex_enter`, `mutex_exit`, `mutex_spin_enter`, `mutex_spin_exit`, `mutex_tryenter`, `mutex_owned`, `mutex_ownable`.
- Object mutex routines: `mutex_obj_init`, `mutex_obj_alloc`, `mutex_obj_hold`, `mutex_obj_free`, `mutex_obj_refcnt`, `mutex_obj_tryalloc`.

## Dependencies
Includes `machine/mutex.h` for architecture-specific layout and operations; kernel mode also includes interrupt-level definitions.

## Risks and Notes
This header is a contract between machine-independent and machine-dependent kernel code. Architectures must provide either simple mutex support or the full operation set. Spin mutexes interact with IPL state and per-CPU spin-lock counts, so misuse can break interrupt or scheduler invariants.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/mutex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/namei.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/namei.h

## Purpose
Generated pathname lookup and name cache header. It defines `pathbuf`, `nameidata`, component lookup flags, name cache internals, lookup/cache APIs, and namei cache statistics.

## Main API
- Path buffer routines: `pathbuf_create`, `pathbuf_assimilate`, `pathbuf_copyin`, `pathbuf_destroy`, `pathbuf_copystring`, `pathbuf_stringcopy_get`, `pathbuf_stringcopy_put`.
- Lookup structures: `struct componentname`, `struct nameidata`.
- Operation constants: `LOOKUP`, `CREATE`, `DELETE`, `RENAME`.
- Lookup flags: `LOCKLEAF`, `LOCKPARENT`, `FOLLOW`, `TRYEMULROOT`, `NOCACHE`, `NOCROSSMOUNT`, `RDONLY`, `ISDOTDOT`, `MAKEENTRY`, `ISLASTCN`, `REQUIREDIR`, `CREATEDIR`, and masks.
- Initialization macros: `NDINIT`, `NDAT`.
- Kernel simple lookup APIs: `namei_simple_kernel`, `namei_simple_user`, `nameiat_simple*`.
- Name cache APIs: `cache_lookup`, `cache_enter`, `cache_purge`, `cache_revlookup`, `cache_cross_mount`, `cache_lookup_mount`, vnode/cache init/fini routines.
- Statistics: `struct nchstats`.

## Dependencies
Kernel/module sections require vnode-related types, credentials, locks, queues, mutexes, and memory allocation. Private namecache sections use red-black trees.

## Risks and Notes
The file is generated from `namei.src`; edits must be made to the source generator input. `pathbuf` lifetime rules are explicit: callers must keep the path buffer alive until `nameidata` use is finished. Name cache internals have carefully documented lock ownership fields.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/namei.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/null.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/null.h

## Purpose
Defines `NULL` portably for C, C++, and older/newer GNU C++ cases.

## Main API
- `NULL` as `((void *)0)` for C.
- `NULL` as `0` for C++ except newer GNU C++ where `__null` is used.

## Dependencies
None.

## Risks and Notes
This is a small compatibility header. It only defines `NULL` when it is not already defined.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/null.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/once.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/once.h

## Purpose
Declares NetBSD one-time initialization/finalization state and helpers.

## Main API
- Type: `once_t`.
- States: `ONCE_VIRGIN`, `ONCE_RUNNING`, `ONCE_DONE`.
- Functions: `once_init`, `_init_once`, `_fini_once`.
- Macros: `ONCE_DECL`, `RUN_ONCE`, `INIT_ONCE`, `FINI_ONCE`.

## Dependencies
Uses `uint16_t` and prediction macros expected from normal system includes.

## Risks and Notes
`RUN_ONCE` fast-paths when status is `ONCE_DONE` and otherwise calls `_init_once`. The structure stores initialization error and reference count, so consumers should propagate the return value.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/once.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/optstr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/optstr.h

## Purpose
Declares helpers for parsing kernel option strings into strings, numbers, hex/binary numbers, and optionally MAC addresses.

## Main API
- `optstr_get`.
- `optstr_get_string`.
- `optstr_get_number`.
- `optstr_get_number_hex`.
- `optstr_get_number_binary`.
- `optstr_get_macaddr` when Ethernet support is compiled in.

## Dependencies
Includes generated `ether.h`, `sys/types.h`, and `net/if_ether.h` when `NETHER > 0`.

## Risks and Notes
MAC parsing is conditionally compiled on Ethernet support. Callers must pass adequate output buffers and distinguish absent keys from parse failure via the boolean result.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/optstr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/param.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/param.h

## Purpose
Provides core NetBSD system parameters, version macros, kernel/user constants, alignment and rounding helpers, filesystem/path limits, scheduler priority constants, stack macros, and kernel sizing defaults.

## Main API
- Version identifiers: `BSD`, `BSD4_3`, `BSD4_4`, `__NetBSD_Version__`, `__NetBSD_Prereq__`, historical `NetBSD`.
- Kernel mode tags: `_HARDKERNEL`, `_SOFTKERNEL`.
- Limits: `MAXCOMLEN`, `MAXINTERP`, `MAXLOGNAME`, `NCARGS`, `NGROUPS`, `NOFILE`, `MAXUPRC`, `MAXHOSTNAMELEN`.
- Utility macros: `MIN`, `MAX`, `ALIGN`, `ALIGNED_POINTER`, `ALIGNED_POINTER_LOAD`, `ACCESSIBLE_POINTER`, `setbit`, `clrbit`, `isset`, `isclr`, `howmany`, `roundup`, `rounddown`, `roundup2`, `rounddown2`, `powerof2`.
- Device/block conversions: `DEV_BSHIFT`, `DEV_BSIZE`, `ctod`, `dtoc`, `ctob`, `btoc`, `dbtob`, `btodb`.
- Filesystem/path constants: `MAXBSIZE`, `MAXFRAG`, `MAXPATHLEN`, `MAXSYMLINKS`, `KERNEL_NAME_MAX`.
- Scheduling priorities: legacy `P*` priorities, `PRI_*`, soft interrupt and kernel thread priorities.
- Kernel helpers: `mstohz`, `hztoms`, `hz2bintime`.

## Dependencies
Includes `sys/null.h`, integer/types headers, system limits, machine parameters and limits, signal definitions, and kernel-only resource/ucred/uio/UVM headers.

## Risks and Notes
This is one of the broadest dependency roots in the kernel. `roundup2`/`rounddown2` are deliberately written to avoid type-width truncation. Many constants are ABI- or compatibility-sensitive and should not be casually changed.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/param.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/paravirt_membar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/paravirt_membar.h

## Purpose
Declares a paravirtualized memory barrier synchronization hook.

## Main API
- `paravirt_membar_sync(void)`.

## Dependencies
None beyond the kernel build context.

## Risks and Notes
The header is intentionally minimal. Correctness depends on the platform implementation providing the required synchronization semantics.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/paravirt_membar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pax.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pax.h

## Purpose
Defines PaX security feature flags and function hooks for ASLR, MPROTECT, and Segvguard.

## Main API
- Process flags: `P_PAX_ASLR`, `P_PAX_MPROTECT`, `P_PAX_GUARD`.
- Global setup: `pax_init`, `pax_set_flags`, `pax_setup_elf_flags`.
- MPROTECT hooks: `pax_mprotect_maxprotect`, `pax_mprotect_validate`, `pax_mprotect_prot`, plus debug-aware macros.
- Segvguard hooks: `pax_segvguard`, `pax_segvguard_cleanup`.
- ASLR hooks: `PAX_ASLR_DELTA`, `pax_aslr_init_vm`, `pax_aslr_stack`, `pax_aslr_stack_gap`, `pax_aslr_exec_offset`, `pax_aslr_rtld_offset`, `pax_aslr_mmap`.

## Dependencies
Includes `uvm/uvm_extern.h` and forward-declares process, LWP, exec, and vmspace types.

## Risks and Notes
Most functions compile to inline no-ops when their corresponding feature options are disabled. Default ASLR fallback returns deterministic offsets, so callers must not assume randomization unless `PAX_ASLR` is enabled.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pax.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pcq.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pcq.h

## Purpose
Declares an opaque producer/consumer queue API for kernel use.

## Main API
- Opaque type: `pcq_t`.
- Maximum length: `PCQ_MAXLEN`.
- Functions: `pcq_put`, `pcq_peek`, `pcq_get`, `pcq_maxitems`, `pcq_create`, `pcq_destroy`.

## Dependencies
Includes `sys/kmem.h`; APIs are kernel-only.

## Risks and Notes
The queue object is opaque, so users rely on the implementation for synchronization and memory ordering. `pcq_put` returns boolean success/failure, likely for full-queue handling.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pcq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pcu.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pcu.h

## Purpose
Declares Processor Control Unit state-management hooks for lazy per-LWP machine-dependent CPU resources such as FPU/vector state.

## Main API
- `PCU_UNIT_COUNT`, defaulting to zero.
- When units exist: `pcu_ops_t` with state save/load/release callbacks.
- Flags: `PCU_VALID`, `PCU_REENABLE`.
- Functions: `pcu_switchpoint`, `pcu_discard_all`, `pcu_save_all`, `pcu_load`, `pcu_save`, `pcu_save_all_on_cpu`, `pcu_discard`, `pcu_valid_p`.
- MD operation table: `pcu_ops_md_defs`.

## Dependencies
Requires kernel or kmem-user context; uses `lwp_t` and boolean support.

## Risks and Notes
If `PCU_UNIT_COUNT` is zero, high-level calls become empty macros. Machine-dependent code must correctly detect and trap future PCU use after `pcu_state_release`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pcu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/percpu.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/percpu.h

## Purpose
Declares NetBSD per-CPU storage allocation, traversal, and callback APIs.

## Main API
- Initialization: `percpu_init`, `percpu_init_cpu`.
- Allocation: `percpu_alloc`, `percpu_free`, `percpu_create`.
- Current CPU access: `percpu_getref`, `percpu_putref`.
- Traversal: `percpu_foreach`, `percpu_foreach_xcall`.
- Low-level traversal/access: `percpu_traverse_enter`, `percpu_traverse_exit`, `percpu_getptr_remote`.
- Callback type: `percpu_callback_t`.

## Dependencies
Includes `sys/percpu_types.h`.

## Risks and Notes
Callers must pair `percpu_getref` with `percpu_putref`. Remote pointer access is explicitly low-level and should be reserved for cases that can satisfy traversal and CPU-lifetime constraints.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/percpu.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/percpu_types.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/percpu_types.h

## Purpose
Provides forward declarations and basic data types for per-CPU storage without exposing full implementation.

## Main API
- Forward declaration: `struct cpu_info`.
- Opaque type: `percpu_t`.
- Per-CPU backing descriptor: `percpu_cpu_t` with size and data pointer.

## Dependencies
Includes `sys/types.h`.

## Risks and Notes
This header is deliberately small to break include cycles. It does not provide allocation or synchronization semantics; those are in `percpu.h`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/percpu_types.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/physmap.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/physmap.h

## Purpose
Declares physical memory segment maps and helpers for creating, mapping, destroying, and zeroing physical mappings from user/kernel address descriptions.

## Main API
- Types: `physmap_segment_t`, `struct physmap`.
- Creation: `physmap_create_iov`, `physmap_create_linear`, `physmap_create_pagelist`.
- Destruction: `physmap_destroy`.
- Mapping lifecycle: `physmap_map_init`, `physmap_map`, `physmap_map_fini`.
- Utility: `physmap_zero`.

## Dependencies
Kernel/kmem-user only; includes `sys/types.h`, `sys/uio.h`, and `uvm/uvm_extern.h`.

## Risks and Notes
`struct physmap` uses a zero-length segment array, so allocation must size the object for `pm_maxsegs`. Mapping calls involve VM protections and address-space references; lifetime ordering matters.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/physmap.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pipe.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pipe.h

## Purpose
Defines pipe buffer sizing, pipe state bits, per-pipe kernel structure, and pipe sysctl/init declarations.

## Main API
- Size constants: `PIPE_SIZE`, `BIG_PIPE_SIZE`, `PIPE_DIRECT_CHUNK`, `PIPE_MINDIRECT`.
- Structures: `struct pipebuf`, `struct pipe`.
- State bits: `PIPE_ASYNC`, `PIPE_EOF`, `PIPE_SIGNALR`, `PIPE_LOCKFL`, `PIPE_RESTART`.
- Sysctl subtypes: `KERN_PIPE_MAXKVASZ`, `KERN_PIPE_LIMITKVA`, `KERN_PIPE_MAXBIGPIPES`, `KERN_PIPE_NBIGPIPES`, `KERN_PIPE_KVASIZE`.
- Kernel functions: `sysctl_dopipe`, `pipe_init`.

## Dependencies
Includes select state, time, and UVM declarations.

## Risks and Notes
The header documents direct-write and buffering thresholds. Each pipe has a peer pointer and preallocated KVA buffer, so close/rundown paths must coordinate state, waiters, and peer lifetime carefully.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pipe.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pmf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pmf.h

## Purpose
Declares the NetBSD Power Management Framework event, suspend/resume, and device registration APIs.

## Main API
- Generic events: display, audio, lid, radio, power/speed/throttle, keyboard brightness event enum values.
- Qualifier type: `pmf_qual_t`.
- Qualifier constants: `PMF_Q_NONE`, `PMF_Q_SELF`, `PMF_Q_DRVCTL`.
- Framework calls: `pmf_init`, `pmf_event_inject`, `pmf_event_register`, `pmf_event_deregister`.
- Platform calls: `pmf_set_platform`, `pmf_get_platform`.
- System suspend/resume/shutdown: `pmf_system_resume`, `pmf_system_bus_resume`, `pmf_system_suspend`, `pmf_system_shutdown`.
- Device lifecycle: `pmf_device_register1`, `pmf_device_deregister`, `pmf_device_suspend`, `pmf_device_resume`, recursive/subtree helpers.
- Class registration: network, input, display.
- Inline qualifier helpers: `pmf_qual_suspension`, `pmf_qual_depth`, `pmf_qual_descend_ok`.

## Dependencies
Kernel/kmem-user sections use `sys/types.h` and `sys/device_if.h`.

## Risks and Notes
Suspend/resume depth is carried by qualifiers. Recursive operations should respect `pmf_qual_descend_ok`; drivers must register callbacks that tolerate being called during system-wide power transitions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pmf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/poll.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/poll.h

## Purpose
Defines POSIX poll ABI, event flags, kernel common poll routine, and modern `ppoll`/NetBSD `pollts` declarations.

## Main API
- Type: `nfds_t`.
- Structure: `struct pollfd`.
- Event flags: `POLLIN`, `POLLPRI`, `POLLOUT`, `POLLRDNORM`, `POLLWRNORM`, `POLLRDBAND`, `POLLWRBAND`, `POLLERR`, `POLLHUP`, `POLLNVAL`.
- NetBSD timeout constant: `INFTIM`.
- Kernel function: `pollcommon`.
- Userland calls: `poll`, `pollts`, `ppoll`.

## Dependencies
Uses feature-test macros; kernel mode uses signal types, while userland `ppoll`/`pollts` declarations use `sigset_t` and `struct timespec`.

## Risks and Notes
`POLLERR`, `POLLHUP`, and `POLLNVAL` are non-testable returned events. `pollts` is NetBSD-specific and version-renamed for ABI compatibility.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/poll.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pool.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pool.h

## Purpose
Defines NetBSD fixed-size pool allocator and pool-cache interfaces, including sysctl statistics, allocator backends, pool descriptors, cache groups, per-CPU cache state, flags, and kernel APIs.

## Main API
- Sysctl snapshot: `struct pool_sysctl`.
- Exposed internals under `__POOL_EXPOSE`: `struct pool_allocator`, `struct pool`, `struct pool_cache`, `pool_cache_group`, `pool_cache_cpu_t`.
- Flags: `PR_WAITOK`, `PR_NOWAIT`, `PR_WANTED`, `PR_PHINPAGE`, `PR_LIMITFAIL`, `PR_RECURSIVE`, `PR_NOTOUCH`, `PR_NOALIGN`, `PR_LARGECACHE`, `PR_GROWING`, `PR_ZERO`, `PR_USEBMAP`, `PR_PSERIALIZE`.
- Global allocators: `pool_allocator_kmem`, `pool_allocator_nointr`, `pool_allocator_meta`.
- Pool APIs: `pool_init`, `pool_destroy`, `pool_get`, `pool_put`, `pool_reclaim`, `pool_prime`, `pool_setlowat`, `pool_sethiwat`, `pool_sethardlimit`, `pool_drain`.
- Cache APIs: `pool_cache_init`, `pool_cache_bootstrap`, `pool_cache_destroy`, `pool_cache_get_paddr`, `pool_cache_put_paddr`, `pool_cache_invalidate`, `pool_cache_reclaim`, limit/prime/drain helpers.
- Diagnostics: `pool_printit`, `pool_printall`, `pool_chk`, `pool_whatis`.

## Dependencies
Kernel internals use parameters, mutexes, condition variables, queues, trees, callback support, and optional pool configuration.

## Risks and Notes
Pool locking deliberately does not cover backend page allocator calls. `PR_PSERIALIZE` indicates delayed safe reclamation requirements. Cache group sizing and per-CPU state are cache-line sensitive, and diagnostic fields change behavior under redzone/quarantine configurations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pool.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/power.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/power.h

## Purpose
Defines user/kernel power management event ABI for power switches, envsys sensor events, and power device ioctls.

## Main API
- Power switch types: `PSWITCH_TYPE_POWER`, `SLEEP`, `LID`, `RESET`, `ACADAPTER`, `HOTKEY`, `RADIO`.
- Hotkey names: display cycle, lock screen, battery info, eject, zoom, vendor, and ThinkPad-style function keys unless suppressed.
- Switch events: `PSWITCH_EVENT_PRESSED`, `PSWITCH_EVENT_RELEASED`.
- Structures: `struct pswitch_state`, `struct penvsys_state`, `power_event_t`, `struct power_type`.
- Envsys types/events: temperature, voltage, power, battery, fan, drive, indicator; normal, critical, warning, battery, low-power, state-changed, limits/capacity, null events.
- Ioctls: `POWER_EVENT_RECVDICT`, `POWER_IOC_GET_TYPE`.

## Dependencies
Uses `sys/ioccom.h`; userland includes `stdint.h`.

## Risks and Notes
Power event messages are fixed at 32 bytes so userland can read one event at a time. Kernel compatibility defines the older incorrectly encoded `POWER_IOC_GET_TYPE_WITH_LOSSAGE`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/power.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/proc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/proc.h

## Purpose
Defines NetBSD process/session/process-group structures, emulation hooks, process state flags, fork/wait/sleep/process-management kernel APIs, and kernel stack parameter defaults.

## Main API
- Structures: `struct session`, `struct pgrp`, `struct sc_autoload`, `struct emul`, `struct proc`, `struct proclist_desc`.
- Process status values: `SIDL`, `SACTIVE`, `SDYING`, `SSTOP`, `SZOMB`, `SDEAD`; helper `P_ZOMBIE`.
- Process flags: `PK_*`, `PS_*`, `PSL_*`, `PST_PROFIL`, `PL_*`.
- Helpers: `P_EXITSIG`, `P_WAITSTATUS`, `SESS_LEADER`, `PROC_PTRSZ`, `PROC_REGSZ`, `PROC_FPREGSZ`, `PROC_DBREGSZ`, `PROC_MACHINE_ARCH`, `PROCLIST_FOREACH`.
- Fork flags: `FORK_PPWAIT`, `FORK_SHAREVM`, `FORK_SHARECWD`, `FORK_SHAREFILES`, `FORK_SHARESIGS`, `FORK_NOWAIT`, `FORK_CLEANFILES`, `FORK_SYSTEM`.
- Kernel globals: `proc0`, `nprocs`, `maxproc`, `proc_lock`, `allproc`, `zombproc`, `initproc`, `emul_netbsd`.
- Process APIs: find/lookup, process group/session management, `tsleep`, `mtsleep`, `wakeup`, `kpause`, `exit1`, `kill1`, wait helpers, proc allocation/free, fork, credential/VM helpers, proc-specific data, kqueue notifications.
- Stack macros: `KSTACK_LOWEST_ADDR`, `KSTACK_SIZE`.

## Dependencies
Includes `sys/lwp.h`; kernel/kmem-user sections pull machine proc/pcb, aio, idtype, locks, mqueue, queues, radixtree, signal/event/specificdata, resources, and UVM-related types through referenced structures.

## Risks and Notes
The `struct proc` field comments encode lock ownership and stability requirements. Creation zero/copy ranges are defined by marker macros, making layout changes sensitive. Many APIs require holding `proc_lock` or `p_lock`; incorrect locking can break process lifetime, tracing, wait, and signal behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/proc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/prot.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/prot.h

## Purpose
Declares common credential-change helpers and flag masks for `setresuid`/`setresgid` semantics.

## Main API
- Permission relation flags: `ID_E_EQ_E`, `ID_E_EQ_R`, `ID_E_EQ_S`, `ID_R_EQ_E`, `ID_R_EQ_R`, `ID_R_EQ_S`, `ID_S_EQ_E`, `ID_S_EQ_R`, `ID_S_EQ_S`.
- Functions: `do_setresuid`, `do_setresgid`.

## Dependencies
Uses `struct lwp`, `uid_t`, `gid_t`, and `u_int` from surrounding kernel/system includes.

## Risks and Notes
The flags describe which current IDs may authorize setting which target IDs. Callers must pass the right policy mask for the specific syscall variant.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/prot.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/protosw.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/protosw.h

## Purpose
Defines the kernel networking protocol switch: protocol dispatch vectors, user request operations, control input/output commands, timer helpers, lookup functions, and wrappers for non-MPSAFE protocols.

## Main API
- Core structure: `struct protosw`.
- Protocol flags: `PR_ATOMIC`, `PR_ADDR`, `PR_CONNREQUIRED`, `PR_WANTRCVD`, `PR_RIGHTS`, `PR_LISTEN`, `PR_LASTHDR`, `PR_ABRTACPTDIS`, `PR_PURGEIF`, `PR_ADDR_OPT`.
- User request codes: `PRU_ATTACH` through `PRU_PURGEIF`, `PRU_NREQ`.
- Control commands: `PRC_*`, `PRC_NCMDS`, `PRC_IS_REDIRECT`.
- Control output commands: `PRCO_GETOPT`, `PRCO_SETOPT`.
- Kernel user request vector: `struct pr_usrreqs`.
- Timer globals/macros: `pfslowtimo_now`, `pffasttimo_now`, `PRT_SLOW_*`, `PRT_FAST_*`.
- Lookup/control dispatch: `pffindproto`, `pffindtype`, `pffinddomain`, `pfctlinput`, `pfctlinput2`.
- Wrappers: `PR_WRAP_USRREQS`, `PR_WRAP_CTLOUTPUT`, `PR_WRAP_CTLINPUT`, `PR_WRAP_INPUT`.

## Dependencies
Forward declares networking/socket structures. Kernel wrappers depend on `kernel_lock`, `softnet_lock`, and socket internals.

## Risks and Notes
The header preserves legacy protocol request IDs and optional request-name tables. Wrapper macros generate many static functions and should be used carefully to avoid name collisions. Non-MPSAFE wrappers serialize through global kernel or softnet locks.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/protosw.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pserialize.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pserialize.h

## Purpose
Declares passive serialization primitives for reader sections and writer grace-period synchronization.

## Main API
- Opaque type: `pserialize_t`.
- Functions: `pserialize_init`, `pserialize_create`, `pserialize_destroy`, `pserialize_perform`, `pserialize_read_enter`, `pserialize_read_exit`, `pserialize_in_read_section`, `pserialize_not_in_read_section`.

## Dependencies
Kernel-only.

## Risks and Notes
Readers use enter/exit tokens; writers use `pserialize_perform` to wait for pre-existing readers to drain. Objects removed from pserialize-protected structures must not be freed before the grace period.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pserialize.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pset.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pset.h

## Purpose
Defines processor set userland API constants and kernel initialization/state declarations.

## Main API
- Special IDs: `PS_NONE`, `PS_MYID`, `PS_QUERY`.
- Userland calls: `pset_assign`, `pset_bind`, `pset_create`, `pset_destroy`.
- NetBSD extension: `_pset_bind`.
- Kernel type: `pset_info_t`.
- Kernel function: `psets_init`.

## Dependencies
Uses feature-test macros, basic types, and `idtype_t`.

## Risks and Notes
The public API exposes processor-set IDs and binding by id type. Kernel `pset_info_t` is currently minimal, so most behavior is in implementation code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pset.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pslist.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pslist.h

## Purpose
Provides a passive-serialization-friendly singly linked list with writer and reader operations, atomic publication, poisoning, and type-safe container macros.

## Main API
- Structures: `struct pslist_head`, `struct pslist_entry`.
- Initialization/destruction: `pslist_init`, `pslist_destroy`, `pslist_entry_init`, `pslist_entry_destroy`.
- Writer operations: insert head/before/after, remove, first/next.
- Reader operations: first/next with consume loads.
- Convenience macros: `PSLIST_INIT`, `PSLIST_ENTRY_INIT`, `PSLIST_WRITER_INSERT_*`, `PSLIST_WRITER_REMOVE`, `PSLIST_WRITER_FOREACH`, `PSLIST_READER_FOREACH`.

## Dependencies
Uses `sys/param.h` and atomic operations. Kernel assertions map to `KASSERT`; userland maps to `assert`.

## Risks and Notes
Writers must exclude other writers but not readers. After writer removal, `ple_next` is intentionally left intact until readers drain; callers must use a grace mechanism such as `pserialize_perform` before destroying or reusing entries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pslist.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/psref.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/psref.h

## Purpose
Declares passive reference tracking for objects that can be referenced without heavy locking while supporting controlled draining/destruction.

## Main API
- Structures: `struct psref_target`, `struct psref`, opaque `struct psref_class`.
- Initialization: `psref_init`, `psref_class_create`, `psref_class_destroy`, `psref_target_init`, `psref_target_destroy`.
- Reference operations: `psref_acquire`, `psref_release`, `psref_copy`.
- Assertion helper: `psref_held`.
- Debug hooks/macros when `PSREF_DEBUG` is enabled.

## Dependencies
Includes optional debug config, basic types, and `sys/queue.h`.

## Risks and Notes
`prt_draining` is written only once to block new references during destruction. `struct psref` is per-reference, CPU-local bookkeeping; callers must observe CPU and lifetime rules implemented by the psref subsystem.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/psref.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ptrace.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ptrace.h

## Purpose
Defines ptrace request numbers, event masks, I/O and LWP status structures, signal-info transport, userland declaration, and kernel ptrace/machine-register support hooks.

## Main API
- Requests: `PT_TRACE_ME`, `PT_READ_I`, `PT_READ_D`, `PT_WRITE_I`, `PT_WRITE_D`, `PT_CONTINUE`, `PT_KILL`, `PT_ATTACH`, `PT_DETACH`, `PT_IO`, `PT_DUMPCORE`, `PT_SYSCALL`, `PT_SYSCALLEMU`, event/siginfo/LWP requests, and machine-dependent range from `PT_FIRSTMACH`.
- Structures: `ptrace_event_t`, `ptrace_state_t`, `struct ptrace_io_desc`, optional legacy `struct ptrace_lwpinfo`, `struct ptrace_lwpstatus`, `ptrace_siginfo_t`.
- Event bits: `PTRACE_FORK`, `PTRACE_VFORK`, `PTRACE_VFORK_DONE`, `PTRACE_LWP_CREATE`, `PTRACE_LWP_EXIT`, `PTRACE_POSIX_SPAWN`.
- I/O operations: `PIOD_READ_D`, `PIOD_WRITE_D`, `PIOD_READ_I`, `PIOD_WRITE_I`, `PIOD_READ_AUXV`.
- Kernel methods: `struct ptrace_methods`.
- Kernel helpers: `ptrace_update_lwp`, `ptrace_hooks`, `process_doregs`, `process_dofpregs`, `process_dodbregs`, `process_domem`, `do_ptrace`, register read/write hooks, `ptrace_machdep_dorequest`.
- Userland: `ptrace`.

## Dependencies
Includes signal and siginfo headers plus `machine/ptrace.h`; kernel compatibility can include netbsd32 definitions.

## Risks and Notes
The header preserves obsolete `PT_LWPINFO` under legacy/kernel conditions. 32/64-bit process register type aliases are carefully conditional for compat kernels. Machine-dependent requests and register support are optional.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ptrace.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ptree.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ptree.h

## Purpose
Declares a generic Patricia/tree-like keyed node structure and operations with pluggable key matching/testing callbacks.

## Main API
- Direction enum: `PT_DESCENDING`, `PT_ASCENDING`.
- Types: `pt_slot_t`, `pt_bitoff_t`, `pt_bitlen_t`, `pt_node_t`, `pt_tree_ops_t`, `pt_tree_t`, `pt_filter_t`.
- Public functions: `ptree_init`, `ptree_insert_node`, `ptree_insert_mask_node`, `ptree_mask_node_p`, `ptree_find_filtered_node`, `ptree_find_node`, `ptree_remove_node`, `ptree_iterate`, `ptree_check`.
- Private macros under `_PT_PRIVATE` encode slot/type/nodedata/branchdata bitfields.

## Dependencies
Uses boolean and integer types when outside kernel/standalone.

## Risks and Notes
`pt_node_t` slots must be first, and private macros tag low pointer bits. Embedded nodes must satisfy alignment assumptions that leave type bits available. Tree behavior is driven by callback correctness.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ptree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pty.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/pty.h

## Purpose
Declares pseudo-terminal allocation/check helpers and the `ptm_pty` handler switch used to route PTM behavior between BSD ptys and ptyfs.

## Main API
- Functions: `pty_isfree`, `pty_check`.
- PTM functions when enabled: `ptmattach`, `pty_fill_ptmget`, `pty_grant_slave`, `pty_makedev`, `pty_sethandler`, `pty_getmp`.
- Handler structure: `struct ptm_pty` with `allocvp`, `makename`, `getvattr`, `getmp`.
- Globals: optional `ptm_bsdpty`, `npty`.

## Dependencies
Uses kernel types such as `struct lwp`, `dev_t`, `struct mount`, `struct vnode`, and `struct vattr`.

## Risks and Notes
`struct mount *` arguments are meaningful for ptyfs but can be `NULL` for BSDPTY. The handler switch is a central compatibility point between old and filesystem-backed pty implementations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/pty.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/queue.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/queue.h

## Purpose
Provides BSD intrusive collection macros for singly linked lists, doubly linked lists, simple queues, tail queues, and singly linked tail queues.

## Main API
- SLIST: `SLIST_HEAD`, `SLIST_ENTRY`, accessors, foreach/safe foreach, init/insert/remove macros.
- LIST: `LIST_HEAD`, `LIST_ENTRY`, accessors, `LIST_MOVE`, init/insert/remove/replace macros.
- SIMPLEQ: `SIMPLEQ_HEAD`, `SIMPLEQ_ENTRY`, accessors, foreach/safe foreach, init/insert/remove/concat/last macros.
- TAILQ: `TAILQ_HEAD`, `TAILQ_ENTRY`, first/last/next/prev/foreach/reverse foreach, init/insert/remove/replace/concat macros.
- STAILQ: `STAILQ_HEAD`, `STAILQ_ENTRY`, accessors, init/insert/remove/foreach/concat/last macros.
- Optional debug support: `QUEUEDEBUG_*` checks under kernel `DIAGNOSTIC` or explicit `QUEUEDEBUG`.

## Dependencies
On NetBSD includes `sys/null.h`; debug mode uses `panic` in kernel or `err` in userland.

## Risks and Notes
These macros are intrusive and do not perform locking. Debug poisoning helps catch corrupted list links after removal. Some macros evaluate arguments more than once or rely on exact field names, so callers must use side-effect-free arguments.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/queue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/quota.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/quota.h

## Purpose
Defines generic quota key/value ABI for quota records and semantic restriction flags.

## Main API
- ID types: `QUOTA_IDTYPE_USER`, `QUOTA_IDTYPE_GROUP`.
- Object types: `QUOTA_OBJTYPE_BLOCKS`, `QUOTA_OBJTYPE_FILES`.
- Special values: `QUOTA_DEFAULTID`, `QUOTA_NOLIMIT`, `QUOTA_NOTIME`.
- Restrictions: `QUOTA_RESTRICT_NEEDSQUOTACHECK`, `QUOTA_RESTRICT_UNIFORMGRACE`, `QUOTA_RESTRICT_32BIT`, `QUOTA_RESTRICT_READONLY`.
- Structures: `struct quotakey`, `struct quotaval`.

## Dependencies
Includes `sys/types.h`.

## Risks and Notes
The header separates billed entity (`quotakey`) from limit/usage value (`quotaval`). Restriction flags are hints for comprehensible diagnostics, not enforcement by themselves.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/quota.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/quotactl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/quotactl.h

## Purpose
Defines NetBSD internal quota control command ABI used by libquota and the kernel.

## Main API
- Name length: `QUOTA_NAMELEN`.
- Status structures: `struct quotastat`, `struct quotaidtypestat`, `struct quotaobjtypestat`.
- Cursor structure: `struct quotakcursor`.
- Commands: `QUOTACTL_STAT`, `IDTYPESTAT`, `OBJTYPESTAT`, `GET`, `PUT`, `DEL`, cursor open/close/skip/get/atend/rewind, `QUOTAON`, `QUOTAOFF`.
- Argument union: `struct quotactl_args`.
- Userland internal call: `__quotactl`.

## Dependencies
Includes `sys/stdint.h` and refers to quota key/value types expected from `quota.h` users.

## Risks and Notes
The header explicitly says application code should use `<quota.h>` instead. `quotakcursor` is semi-opaque but copied in/out on each cursor operation, so its fixed size is ABI-sensitive.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/quotactl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/radioio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/radioio.h

## Purpose
Defines FM radio device ioctl ABI, frequency limits, capability bits, and status structure.

## Main API
- Frequency constants: `MIN_FM_FREQ`, `MAX_FM_FREQ`, `IF_FREQ`.
- Structure: `struct radio_info`.
- Capability bits: stereo/signal detection, mono control, hardware search/AFC, reference frequency, lock sensitivity, reserved/card type fields.
- Info bits: `RADIO_INFO_STEREO`, `RADIO_INFO_SIGNAL`.
- Ioctls: `RIOCGINFO`, `RIOCSINFO`, `RIOCSSRCH`.

## Dependencies
Includes `sys/param.h` and `sys/ioccom.h`.

## Risks and Notes
Frequency is in kHz. The capability field reserves bit ranges for card type and future use; drivers and tools must mask rather than compare the entire field blindly.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/radioio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/radixtree.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/radixtree.h

## Purpose
Declares a generic 64-bit-key radix tree with node lookup/update, gang lookup, and tag support.

## Main API
- Structure: `struct radix_tree` with root and height.
- Kernel subsystem functions: `radix_tree_init`, `radix_tree_await_memory`.
- Tree lifecycle: `radix_tree_init_tree`, `radix_tree_fini_tree`, `radix_tree_empty_tree_p`.
- Node operations: `radix_tree_insert_node`, `radix_tree_replace_node`, `radix_tree_remove_node`, `radix_tree_lookup_node`, `radix_tree_gang_lookup_node`, reverse gang lookup.
- Tags: `radix_tree_tagmask_t`, `RADIX_TREE_TAG_ID_MAX`, `radix_tree_get_tag`, `set_tag`, `clear_tag`, tagged gang lookup, reverse tagged lookup, `radix_tree_empty_tagged_tree_p`.

## Dependencies
Uses kernel/standalone `sys/types.h` or userland boolean/integer headers.

## Risks and Notes
Tag IDs are limited by `RADIX_TREE_TAG_ID_MAX`. Kernel users may need to handle memory pressure via `radix_tree_await_memory` after failed insertions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/radixtree.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/random.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/random.h

## Purpose
Defines NetBSD `getrandom` flags and kernel/user entry points.

## Main API
- Flags: `GRND_NONBLOCK`, `GRND_RANDOM`, `GRND_INSECURE`.
- Kernel function: `dogetrandom`.
- Userland function: `getrandom`.

## Dependencies
Includes `sys/cdefs.h` and machine ANSI typedef hooks for `size_t`/`ssize_t`.

## Risks and Notes
`GRND_INSECURE` explicitly requests output without normal security readiness guarantees. Kernel implementation takes a `struct uio *`, while userland receives a byte count or error via `ssize_t`.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/random.h -->