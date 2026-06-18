# Group Research: group_443_freebsd_src_sources_os_bsd_freebsd_src_sys_sys_elf_common_h_sources__e81a5385778e

Scope: `Docs/research_subset_a.md`, source tree `sources/os/bsd/freebsd-src`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf_common.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/elf_common.h

## Purpose
Defines ELF constants, note formats, dynamic tags, symbol/version metadata, auxiliary vector values, and relocation numbers that are independent of ELF word size. This is the shared namespace consumed by `elf32.h`, `elf64.h`, loaders, linkers, kernel image activation, core dump handling, and binary inspection tools.

## Main Interfaces
- `Elf_Note` / `Elf_Nhdr`: generic ELF note header.
- `Elf_GNU_Hash_Header`: GNU hash section header.
- ELF identity macros: `EI_*`, `ELFMAG*`, `IS_ELF`, `ELFCLASS*`, `ELFDATA*`, `ELFOSABI_*`.
- ELF object, machine, and architecture flag values: `ET_*`, `EM_*`, `EF_*`.
- Section constants: `SHN_*`, `SHT_*`, `SHF_*`, `GRP_COMDAT`, compression types.
- Program header and dynamic linker constants: `PT_*`, `PF_*`, `DT_*`, `DF_*`, `DF_1_*`.
- Note constants for FreeBSD, GNU, NetBSD, Solaris, FDO packaging metadata, and architecture properties.
- Symbol, visibility, syminfo, and versioning constants: `STB_*`, `STT_*`, `STV_*`, `VER_*`, `SYMINFO_*`.
- Auxv entries: `AT_*`, `AT_COUNT`.
- Relocation values for i386, amd64/x86-64, AArch64, ARM, IA-64, LoongArch, MIPS, PowerPC, RISC-V, and SPARC.
- BSD ELF flags: `ELF_BSDF_SIGFASTBLK`, `ELF_BSDF_VMNOOVERCOMMIT`.

## Dependencies And Integration
The file assumes fixed-width FreeBSD integer typedefs such as `u_int32_t` are already available from including context. It intentionally avoids architecture-specific structure layout, leaving width-specific typedefs to other ELF headers. It is included by many kernel and userland ELF consumers, so numeric values are ABI and toolchain contract.

## Implementation Notes
There is almost no executable logic beyond `IS_ELF`. The file is a compatibility table. The highest-risk edits are numeric changes, reuse of reserved values, or accidental divergence from ELF psABI/GABI assignments. FreeBSD-specific note and section values also participate in kernel/userland ABI, especially core dump notes and exec feature controls.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf_common.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf_generic.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/elf_generic.h

## Purpose
Provides generic ELF type and macro aliases that resolve to either 32-bit or 64-bit ELF definitions based on `__ELF_WORD_SIZE`.

## Main Interfaces
- Requires `__ELF_WORD_SIZE` to be exactly `32` or `64`.
- Defines `ELF_CLASS` and `ELF_DATA` from word size and `BYTE_ORDER`.
- Name construction macros: `__elfN`, `__ElfN`, `__ELFN`, `__ElfType`.
- Linux-compatible `ElfW(x)` alias.
- Generic typedefs: `Elf_Addr`, `Elf_Ehdr`, `Elf_Shdr`, `Elf_Phdr`, `Elf_Dyn`, `Elf_Rel`, `Elf_Rela`, `Elf_Relr`, `Elf_Sym`, versioning types, and non-standard hash/size types.
- Generic relocation and symbol helper aliases: `ELF_R_SYM`, `ELF_R_TYPE`, `ELF_R_INFO`, `ELF_ST_*`.

## Dependencies And Integration
Depends on `sys/cdefs.h`, byte-order macros, and the word-size-specific ELF types having been defined by the including ELF header path. It is a convenience layer for code that should not spell `Elf32_*` or `Elf64_*`.

## Risk Notes
Incorrect `__ELF_WORD_SIZE` or missing byte-order definitions fail at preprocessing time. Changes here can break broad ELF consumers because it controls canonical generic type names.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/elf_generic.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/endian.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/endian.h

## Purpose
Exports byte-swap macros and alignment-safe little/big-endian encode/decode helpers for 16-, 32-, and 64-bit integers.

## Main Interfaces
- Typedef guards for `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`.
- `bswap16`, `bswap32`, `bswap64` mapping to machine helpers.
- Decode helpers: `be16dec`, `be32dec`, `be64dec`, `le16dec`, `le32dec`, `le64dec`.
- Encode helpers: `be16enc`, `be32enc`, `be64enc`, `le16enc`, `le32enc`, `le64enc`.

## Dependencies And Integration
Includes `sys/cdefs.h`, `sys/_types.h`, and `machine/endian.h`. The inline helpers operate byte-by-byte and are safe for unaligned bytestreams, making them useful for filesystem, network, disk-label, and protocol parsing.

## Risk Notes
This header intentionally does not avoid namespace pollution because non-POSIX consumers rely on these macros. Edits must preserve exact byte ordering and avoid introducing alignment assumptions.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/endian.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/epoch.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/epoch.h

## Purpose
Declares FreeBSD epoch-based synchronization interfaces and global epoch helpers, especially for network stack read-side critical sections.

## Main Interfaces
- Public context type: `struct epoch_context`, `epoch_context_t`, `epoch_callback_t`.
- Kernel-only opaque `epoch_t`.
- Flags: `EPOCH_PREEMPT`, `EPOCH_LOCKED`.
- Global epochs: `global_epoch`, `global_epoch_preempt`, `net_epoch_preempt`.
- Tracker: `struct epoch_tracker`, with optional `EPOCH_TRACE` metadata.
- Kernel APIs: `epoch_alloc`, `epoch_free`, `epoch_wait`, `epoch_wait_preempt`, `epoch_drain_callbacks`, `epoch_call`, `in_epoch`, `in_epoch_verbose`.
- Preemptible enter/exit wrappers with optional file/line tracing.
- Network macros: `NET_EPOCH_ENTER`, `NET_EPOCH_EXIT`, `NET_EPOCH_WAIT`, `NET_EPOCH_CALL`, `NET_EPOCH_ASSERT`, task initialization helpers.

## Dependencies And Integration
Kernel section includes locks, per-CPU declarations, and Concurrency Kit `ck_epoch`. It integrates with `grouptask` scheduling for network tasks.

## Risk Notes
Correct pairing of enter/exit and proper tracker lifetime are critical. Trace mode changes function signatures through macros, so implementations must stay synchronized with this header.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/epoch.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/errno.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/errno.h

## Purpose
Defines FreeBSD errno values for userland and kernel code, including POSIX errors, BSD extensions, capability-mode errors, and kernel-only pseudo-errors.

## Main Interfaces
- Userland `errno` macro maps to `(*__error())`.
- Standard errors `EPERM` through `EINTEGRITY`, with `ELAST` equal to `97`.
- POSIX namespace gates hide non-POSIX names under `_POSIX_SOURCE`.
- Kernel/standalone pseudo-errors:
  - `ERESTART`
  - `EJUSTRETURN`
  - `ENOIOCTL`
  - `EDIRIOCTL`
  - `ERELOOKUP`
- Optional C11 bounds-checking typedef `errno_t` when extension visibility allows it.

## Dependencies And Integration
Userland includes `sys/cdefs.h` for declarations. Kernel code uses the same numeric errno definitions and additionally relies on negative pseudo-errors for syscall and ioctl control flow.

## Risk Notes
Errno numbers are ABI. New errors must not disturb existing values or `ELAST`. Pseudo-errors are internal control signals and should not leak as user-visible errno values.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eui64.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/eui64.h

## Purpose
Defines the IEEE EUI-64 address representation and userland conversion routines.

## Main Interfaces
- `EUI64_SIZ`: ASCII representation buffer size.
- `EUI64_LEN`: 8-byte binary length.
- `struct eui64 { u_char octet[8]; }`.
- Userland functions:
  - `eui64_aton`
  - `eui64_ntoa`
  - `eui64_ntohost`
  - `eui64_hostton`

## Dependencies And Integration
The structure is shared ABI for code that handles EUI-64 identifiers. Conversion APIs are not exposed to kernel builds.

## Risk Notes
Binary length and ASCII buffer size are fixed assumptions for callers. Any format change belongs in conversion implementation, not this structure contract.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eui64.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/event.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/event.h

## Purpose
Defines the kqueue/kevent public ABI and kernel-side knote/filter interfaces.

## Main Interfaces
- Public filters: `EVFILT_READ`, `WRITE`, `AIO`, `VNODE`, `PROC`, `SIGNAL`, `TIMER`, `PROCDESC`, `FS`, `LIO`, `USER`, `SENDFILE`, `EMPTY`, `JAIL`, `JAILDESC`.
- `EV_SET` initializer, with C99 compound-literal and older fallback forms.
- `struct kevent`, compatibility `freebsd11_kevent`, and 32-bit ABI structures.
- Event action/result flags: `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_ONESHOT`, `EV_CLEAR`, `EV_RECEIPT`, `EV_DISPATCH`, `EV_EOF`, `EV_ERROR`.
- Filter flags: `NOTE_*` for user, file, vnode, process, jail, and timer filters.
- Kqueue flags: `KQUEUE_CLOEXEC`, `KQUEUE_CPONFORK`.
- Kernel structures:
  - `struct knlist`
  - `struct filterops`
  - `struct knote`
  - `struct kevent_copyops`
- Kernel APIs for knote list management, filter registration, fd close notification, and kqueue task draining.
- Userland syscalls: `kqueue`, `kqueuex`, `kqueue1`, `kevent`.

## Dependencies And Integration
Includes queue primitives and ABI types. Kernel knotes integrate with files, vnodes, processes, jails, AIO, kqueues, and polling/select notification paths.

## Risk Notes
`struct kevent` layout is user ABI. Kernel `knote` locking rules are subtle: kqueue lock, knlist lock, and `kn_influx`/`KN_SCAN` state coordinate concurrent detach and scan paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eventfd.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/eventfd.h

## Purpose
Declares FreeBSD eventfd-compatible counter file descriptor API and kernel hooks.

## Main Interfaces
- `eventfd_t` as `uint64_t`.
- Flags: `EFD_SEMAPHORE`, `EFD_NONBLOCK`, `EFD_CLOEXEC`.
- Kernel APIs:
  - `eventfd_create_file`
  - `eventfd_get`
  - `eventfd_put`
  - `eventfd_signal`
- Userland APIs:
  - `eventfd`
  - `eventfd_read`
  - `eventfd_write`

## Dependencies And Integration
Includes `sys/types.h`. Kernel APIs integrate with `struct file` and `struct thread` without exposing the internal `struct eventfd`.

## Risk Notes
Flag values match file descriptor and nonblocking conventions. `eventfd_get`/`put` imply reference management that callers must pair correctly.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eventfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eventhandler.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/eventhandler.h

## Purpose
Defines the kernel eventhandler framework, a typed callback-list mechanism for low-frequency kernel lifecycle and subsystem notifications.

## Main Interfaces
- `struct eventhandler_list`: named callback list with lock, dead count, run count, and ordered entries.
- Lock macros: `EHL_LOCK`, `EHL_UNLOCK`, `EHL_LOCK_ASSERT`.
- Invocation and registration macros:
  - `EVENTHANDLER_LIST_DEFINE`
  - `EVENTHANDLER_DIRECT_INVOKE`
  - `EVENTHANDLER_DEFINE`
  - `EVENTHANDLER_INVOKE`
  - `EVENTHANDLER_REGISTER`
  - `EVENTHANDLER_DEREGISTER`
  - `EVENTHANDLER_DEREGISTER_NOWAIT`
- Core APIs: `eventhandler_register`, `eventhandler_deregister`, `eventhandler_deregister_nowait`, `eventhandler_find_list`, `eventhandler_prune_list`, `eventhandler_create_list`.
- Optional VIMAGE registration path.
- Priority constants: `EVENTHANDLER_PRI_FIRST`, `ANY`, `LAST`.
- Standard event declarations for shutdown, power, low memory, mountroot, VFS mount/unmount, process/thread lifecycle, coredump progress, UMA zone changes, KLD load/unload, framebuffer registration, CAM probe veto, swap events, newbus device events, route address changes, and kernel environment changes.

## Dependencies And Integration
Uses `_eventhandler.h`, mutexes, KTR tracing, power types, queues, SYSINIT, and many forward-declared subsystem types. Direct list definition avoids global list lookup for hot-ish events.

## Risk Notes
Handlers run outside the event list lock during callback execution, with `el_runcount` preventing unsafe pruning. Deregistration and dead-entry pruning must preserve this run-count protocol.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eventhandler.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eventvar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/eventvar.h

## Purpose
Defines kernel-private `struct kqueue` internals.

## Main Interfaces
- Constants: `KQ_NEVENTS`, `KQEXTENT`.
- `struct kqueue` fields for:
  - lock and reference count
  - pending knote queue and count
  - select/sigio integration
  - owning file descriptor table
  - state bits
  - linear and hash knote tables
  - deferred task
  - credentials
  - fork source for copy-on-fork behavior
- State bits: `KQ_SEL`, `KQ_SLEEP`, `KQ_FLUXWAIT`, `KQ_ASYNC`, `KQ_CLOSING`, `KQ_TASKSCHED`, `KQ_TASKDRAIN`, `KQ_CPONFORK`.

## Dependencies And Integration
Kernel-only header. Depends on `_task.h` plus types declared by `event.h` and other kernel headers.

## Risk Notes
This structure is not user-serviceable but is central to kqueue synchronization. State-bit changes must match `kern_event.c`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/eventvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/exec.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/exec.h

## Purpose
Defines process startup argument metadata, executable image switch registration, and kernel helpers for exec image activators.

## Main Interfaces
- `struct ps_strings`: argv/env pointer and count block historically placed at top of user stack.
- `struct execsw`: executable image activator function pointer and name.
- Kernel macros:
  - `PS_STRINGS`
  - `PROC_PS_STRINGS`
  - `PROC_SIGCODE`
  - `PROC_HAS_SHP`
- Kernel APIs:
  - `exec_map_first_page`
  - `exec_unmap_first_page`
  - `exec_register`
  - `exec_unregister`
- `EXEC_SET`: module registration macro for executable image handlers.

## Dependencies And Integration
Includes machine-specific `machine/exec.h`; kernel path includes module support. Image activators plug into the exec subsystem through `execsw`.

## Risk Notes
`ps_strings` is user ABI and still used as a fallback by process argument sysctls. `EXEC_SET` depends on module init ordering at `SI_SUB_EXEC`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/extattr.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/extattr.h

## Purpose
Defines FreeBSD extended attribute namespaces and declares extended attribute syscalls or kernel credential checks.

## Main Interfaces
- Namespaces:
  - `EXTATTR_NAMESPACE_EMPTY`
  - `EXTATTR_NAMESPACE_USER`
  - `EXTATTR_NAMESPACE_SYSTEM`
- String names and `EXTATTR_NAMESPACE_NAMES` initializer macro.
- `EXTATTR_MAXNAMELEN`.
- Kernel API: `extattr_check_cred`.
- Userland APIs: `extattrctl`, `extattr_{delete,get,list,set}_{fd,file,link}`.

## Dependencies And Integration
Kernel mode operates on vnodes, credentials, threads, and access modes. Userland declarations expose the extattr syscall family.

## Risk Notes
Namespace numeric values are syscall ABI. Filesystems implementing extattrs must align their permission behavior with `extattr_check_cred`.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/exterr_cat.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/exterr_cat.h

## Purpose
Defines stable category identifiers for FreeBSD extended errors.

## Main Interfaces
- Category constants including mmap, filedesc, ktrace, FUSE paths, inotify, genio, bridge, swap, VFS syscall/bio, GEOM, fork, process exit, VMM, HWPMC IBS, and linker categories.
- Explicit guidance that IDs are ABI between kernel and libc and must never be reused or changed.

## Dependencies And Integration
Included by extended-error kernel and userland support. The comments identify a libc filename generation script that must be run when adding categories.

## Risk Notes
This is pure ABI. Only append new category IDs; do not renumber or reuse.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/exterr_cat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/exterrvar.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/exterrvar.h

## Purpose
Defines kernel and userland interfaces for FreeBSD extended error reporting.

## Main Interfaces
- Includes `_exterr.h`, `_uexterror.h`, and `exterr_cat.h`.
- Constants:
  - `UEXTERROR_MAXLEN`
  - `UEXTERROR_VER`
  - `EXTERRCTL_ENABLE`, `DISABLE`, `UD`
  - `EXTERRCTLF_FORCE`
- Kernel requires `EXTERR_CATEGORY` before inclusion.
- Kernel macros:
  - `EXTERROR(...)`
  - `EXTERROR_KE(...)`
  - helper selectors for zero, one, or two parameters
- Kernel APIs:
  - `exterr_clear`
  - `exterr_db_print`
  - `exterr_set_from`
  - `exterr_set`
  - `exterr_to_ue`
  - `ktrexterr`
- Userland API: `exterrctl`.

## Dependencies And Integration
Kernel macros capture error code, category, optional string, two uintptr parameters, and source line. `EXTERR_STRINGS` controls whether messages are retained.

## Risk Notes
Callers must define the correct category before inclusion. Macro argument dispatch is sensitive to call shape, and source-line capture is part of diagnostic value.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/exterrvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fail.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/fail.h

## Purpose
Defines the kernel failpoint facility used for sysctl-controlled fault injection in tests and debugging.

## Main Interfaces
- Return codes: `FAIL_POINT_RC_CONTINUE`, `RETURN`, `QUEUED`.
- `struct fail_point`: name, source location, refcount, current setting, flags, sleep callbacks, callout.
- Flags:
  - `FAIL_POINT_DYNAMIC_NAME`
  - `FAIL_POINT_USE_TIMEOUT_PATH`
  - `FAIL_POINT_NONSLEEPABLE`
- Fast-path macro: `FAIL_POINT_IS_OFF`.
- APIs:
  - `fail_point_init`
  - `fail_point_is_off`
  - `fail_point_alloc_callout`
  - `fail_point_use_timeout_path`
  - `fail_point_destroy`
  - `fail_point_eval`
  - `fail_point_eval_nontrivial`
  - sysctl handlers in kernel builds
- Sleep callback setters for pre/post sleep hooks.
- Definition/evaluation macros:
  - `KFAIL_POINT_DEFINE`, `KFAIL_POINT_DECLARE`
  - `KFAIL_POINT_RETURN`
  - `KFAIL_POINT_RETURN_VOID`
  - `KFAIL_POINT_ERROR`
  - `KFAIL_POINT_GOTO`
  - `KFAIL_POINT_SLEEP_CALLBACKS`
  - `KFAIL_POINT_CODE`, `KFAIL_POINT_CODE_FLAGS`, `KFAIL_POINT_CODE_COND`
- Sysctl root declaration: `_debug_fail_point`, alias `DEBUG_FP`.

## Dependencies And Integration
Uses sysctl, callouts, locks, condition variables, linker sets, and kernel system headers. Failpoints become sysctl nodes with status nodes.

## Implementation Notes
`fail_point_eval` is inline and returns immediately when `fp_setting == NULL`, preserving near-zero disabled overhead. Nontrivial parsing and actions live outside the header.

## Risk Notes
Macro-generated local `RETURN_VALUE` can collide with surrounding code expectations. Sleep/timeout mode requires valid post-sleep callbacks. Failpoint state lifetime is protected by `fp_ref_cnt` and must remain synchronized with implementation.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fail.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fbio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/fbio.h

## Purpose
Defines framebuffer and video adapter ioctls, data structures, modes, and kernel framebuffer registration hooks.

## Main Interfaces
- Framebuffer type constants `FBTYPE_*`.
- `struct fbtype` and `FBIOGTYPE`.
- RGB offsets: `struct fb_rgboffs`, `FBIO_GETRGBOFFS`.
- Kernel `struct fb_info` with device pointers, enter/leave/blank callbacks, physical/virtual framebuffer addresses, flags, stride, bpp, cmap, RGB offsets.
- Kernel APIs: `fbd_list`, `fbd_register`, `fbd_unregister`, `register_framebuffer`, `unregister_framebuffer`.
- Color map: `struct fbcmap`, `FBIOPUTCMAP`, `FBIOGETCMAP`.
- Video mode and adapter structures:
  - `struct video_info`
  - `struct video_adapter`
  - `struct video_adapter_info`
- Mode constants for legacy VGA/EGA/CGA/Hercules/text/VESA modes.
- Ioctls for adapter info, mode query/set, window origin, display start, line width, palette, blanking, and RGB offsets.

## Dependencies And Integration
Includes `ioccom.h`; kernel builds include eventhandler support so framebuffer registration emits `register_framebuffer` and `unregister_framebuffer` events.

## Risk Notes
All ioctl numbers and structure layouts are ABI. `struct fb_info` embeds a raw `fbtype` prefix that must not be reordered. Some helper macros assume nonzero height and valid bpp/stride fields.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fbio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fcntl.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/fcntl.h

## Purpose
Defines open, fcntl, advisory locking, `*at`, file sealing, and space-control flags plus userland prototypes.

## Main Interfaces
- Typedef guards for `mode_t`, `off_t`, `pid_t`.
- Open/status flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_NONBLOCK`, `O_APPEND`, `O_SYNC`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_DIRECT`, `O_DIRECTORY`, `O_EXEC`, `O_CLOEXEC`, `O_VERIFY`, `O_PATH`, `O_RESOLVE_BENEATH`, `O_DSYNC`, `O_EMPTY_PATH`, `O_NAMEDATTR`, `O_CLOFORK`.
- Kernel conversion helpers: `FFLAGS`, `OFLAGS`, `FMASK`, `FCNTLFLAGS`, `FUSERALLOWED`.
- `*at` constants: `AT_FDCWD`, `AT_EACCESS`, `AT_SYMLINK_*`, `AT_REMOVEDIR`, `AT_RESOLVE_BENEATH`, `AT_EMPTY_PATH`, rename flags.
- `fcntl` commands: `F_DUPFD`, `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, lock commands, duplicate-with-flags commands, seals, `F_KINFO`, `F_DUP3FD`, `F_DUPFD_CLOFORK`.
- FD flags: `FD_CLOEXEC`, `FD_RESOLVE_BENEATH`, `FD_CLOFORK`.
- Locking: `struct flock`, `struct __oflock`, `LOCK_*`, kernel lock-mode flags.
- Space control: `struct spacectl_range`, `SPACECTL_DEALLOC`.
- Advice constants for `posix_fadvise`.
- Userland prototypes: `open`, `creat`, `fcntl`, `flock`, `fspacectl`, `openat`, `posix_fadvise`, `posix_fallocate`.

## Dependencies And Integration
Shared by libc and kernel. Kernel file flags are a superset of open/fcntl flags, with careful conversion between `O_*` and `F*` encodings.

## Risk Notes
Flag bits are scarce and ABI-sensitive. The header explicitly warns that new `O_*` bits must be coordinated. `FFLAGS/OFLAGS` behavior around `O_EXEC` and `O_PATH` is important for descriptor permission semantics.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fdcio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/fdcio.h

## Purpose
Defines floppy disk controller ioctl structures, options, transfer rates, and common media geometry presets.

## Main Interfaces
- Formatting constants: `FD_FORMAT_VERSION`, `FD_MAX_NSEC`.
- `struct fd_formb` with nested hardware-format fields and ID fields.
- Convenience macros for nested format fields.
- `struct fd_type`: disk geometry and format parameters.
- `struct fdc_status`, `struct fdc_readid`.
- Drive type enum `fd_drivetype`.
- Ioctls: `FD_FORM`, `FD_GTYPE`, `FD_STYPE`, `FD_GOPTS`, `FD_SOPTS`, `FD_CLRERR`, `FD_READID`, `FD_GSTAT`, `FD_GDTYPE`.
- Drive options: `FDOPT_NORETRY`, `FDOPT_NOERRLOG`, `FDOPT_NOERROR`.
- Transfer rates: `FDC_500KBPS`, `FDC_300KBPS`, `FDC_250KBPS`, `FDC_1MBPS`.
- Common media presets: `FDF_3_*`, `FDF_5_*`.

## Dependencies And Integration
Includes `ioccom.h`; userland gets `sys/types.h`. Structures are designed to match legacy floppy hardware command formats.

## Risk Notes
`fd_form_data` layout is hardware-dependent and explicitly must not change. Ioctl compatibility and legacy geometry constants are the main hazards.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fdcio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/file.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/file.h

## Purpose
Defines kernel file object types, file operation vectors, the kernel `struct file`, reference helpers, and inline dispatch wrappers.

## Main Interfaces
- Descriptor types: `DTYPE_NONE`, `VNODE`, `SOCKET`, `PIPE`, `FIFO`, `KQUEUE`, `CRYPTO`, `MQUEUE`, `SHM`, `SEM`, `PTS`, `DEV`, `PROCDESC`, `EVENTFD`, `TIMERFD`, `INOTIFY`, `JAILDESC`, `NTSYNC`.
- File offset locking APIs and flags: `FOF_*`, `foffset_*`, `fsetfl_*`.
- Operation typedefs: read/write, truncate, ioctl, poll, kqfilter, stat, close, fdclose, chmod, chown, sendfile, seek, kinfo, mmap, aio, seals, fallocate, fspacectl, compare, fork.
- `struct fileops` and flags `DFLAG_PASSABLE`, `DFLAG_SEEKABLE`, `DFLAG_FORK`.
- `struct file`: flags, refcount, data pointer, ops, vnode, credentials, type, vnode-specific sequencing/advice/cdevpriv, offset.
- Userland/sysctl `struct xfile`.
- Kernel globals: `vnops`, `badfileops`, `path_fileops`, `socketops`, `maxfiles`, `maxfilesperproc`.
- Reference/get APIs: `fget*`, `fdrop`, `fdrop_close`, `fhold`, vnode-specific getters, remote getters.
- Initialization and vnode/file helpers: `finit`, `finit_vnode`, `vn_*`, invalid operation stubs.
- Inline operation dispatchers: `fo_read`, `fo_write`, `fo_truncate`, `fo_ioctl`, `fo_poll`, `fo_stat`, `fo_close`, `fo_kqfilter`, `fo_chmod`, `fo_chown`, `fo_sendfile`, `fo_seek`, `fo_fill_kinfo`, `fo_mmap`, `fo_aio_queue`, `fo_add_seals`, `fo_get_seals`, `fo_fallocate`, `fo_fspacectl`, `fo_cmp`.

## Dependencies And Integration
Kernel side includes locks, queues, refcounts, VM types, and forward declarations for vnode, proc, uio, knote, nameidata, credentials, and Capsicum rights. It is the central polymorphic object layer beneath descriptors and VFS/socket/device paths.

## Risk Notes
Reference release paths differ: `fdrop` treats last release as unlikely, while `fdrop_close` treats it as likely. Optional fileops return `ENODEV` or `EINVAL` depending on operation. `struct file` lock annotations matter for offset, vnode advice, and cdev private data.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/filedesc.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/filedesc.h

## Purpose
Defines process file descriptor tables, per-descriptor Capsicum rights, current/root directory state, descriptor locks, and kernel descriptor allocation/lookup APIs.

## Main Interfaces
- `struct filecaps`: rights, allowed ioctls, allowed fcntls.
- `struct filedescent`: file pointer, caps, per-fd flags, sequence counter.
- `struct fdescenttbl`: allocated descriptor table.
- `struct pwd`: copy-on-write current/root/jail/ABI root directories.
- `struct pwddesc`: locked pointer to `pwd` plus umask/refcount.
- `struct filedesc`: open files, free bitmap, refs, sx lock, kqueue list, leader hold state.
- `struct filedesc_to_leader`: POSIX lock ownership tracking for shared descriptor tables.
- Per-fd flags: `UF_EXCLOSE`, `UF_RESOLVE_BENEATH`, `UF_FOCLOSE`.
- Lock macros for `pwddesc` and `filedesc`.
- Dup modes and flags: `FDDUP_*`, `FDDUP_FLAG_CLOEXEC`, `FDDUP_FLAG_CLOFORK`.
- Filecap helpers: `filecaps_init`, `copy`, `move`, `free`.
- Descriptor lifecycle APIs: `falloc*`, `finstall*`, `fdalloc*`, `fdclose`, `fdcloseexec`, `fdcopy`, `fdunshare`, `fdescfree`, `fdinit`, `fdshare`.
- Lookup APIs: `fget_cap*`, `fget_unlocked*`, `fget_only_user`, `fget_noref_unlocked`, `fget_noref`, `fdeget_noref`.
- Directory state APIs: `pdcopy`, `pdinit`, `pdshare`, `pdunshare`, `pwd_*`, `pwd_hold*`, `pwd_drop`, `pwd_set`.

## Dependencies And Integration
Includes Capsicum rights, kqueue structures, locks, sequence counters, SMR primitives, and machine limits. It coordinates with `file.h`, VFS namei/path lookup, process lifecycle, fork/exec behavior, and capability mode.

## Risk Notes
Descriptor lookup has multiple safety modes: locked, unlocked with ref, no-ref, SMR, and only-user fast paths. Callers must choose the correct one. Capability sequence counters guard against races between file pointer and rights changes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/filedesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/filio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/filio.h

## Purpose
Defines generic file descriptor ioctls shared by files, devices, sockets, pipes, and some VFS objects.

## Main Interfaces
- Ioctls:
  - `FIOCLEX`, `FIONCLEX`
  - `FIONREAD`, `FIONBIO`, `FIOASYNC`
  - `FIOSETOWN`, `FIOGETOWN`
  - `FIODTYPE`, `FIOGETLBA`
  - `FIODGNAME`
  - `FIONWRITE`, `FIONSPACE`
  - `FIOSEEKDATA`, `FIOSEEKHOLE`
  - `FIOBMAP2`
  - `FIOSSHMLPGCNF`, `FIOGSHMLPGCNF`
- `struct fiodgname_arg`.
- `struct fiobmap2_arg`.
- Kernel 32-bit compatibility `struct fiodgname_arg32`, `FIODGNAME_32`.
- Kernel helper `fiodgname_buf_get_ptr`.

## Dependencies And Integration
Includes `_types.h` and `ioccom.h`. Integrates with VFS sparse-file seeking, block mapping, descriptor flags, and POSIX shm largepage configuration.

## Risk Notes
Ioctl numbers and argument layouts are ABI. `FIODGNAME` needs pointer translation on 32-bit compatibility paths.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/filio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/firmware.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/firmware.h

## Purpose
Declares the kernel loadable firmware registry abstraction.

## Main Interfaces
- `struct firmware`: name, data pointer, data size, version.
- Registration:
  - `firmware_register`
  - `firmware_unregister`
- Lookup:
  - `firmware_get`
  - `firmware_get_flags`
  - flag `FIRMWARE_GET_NOWARN`
- Release:
  - `firmware_put`
  - flag `FIRMWARE_UNLOAD`

## Dependencies And Integration
Firmware images are often embedded in kernel modules. The registry tracks references so modules containing firmware data cannot unload while in use. Dependent images may reference a master image.

## Risk Notes
Clients must pair `firmware_get*` with `firmware_put`. Automatic module loading depends on master image name matching the module name.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/firmware.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fnv_hash.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/fnv_hash.h

## Purpose
Provides inline Fowler/Noll/Vo hash implementations for 32-bit and 64-bit buffers and strings.

## Main Interfaces
- Types: `Fnv32_t`, `Fnv64_t`.
- Constants: `FNV1_32_INIT`, `FNV1_64_INIT`, `FNV_32_PRIME`, `FNV_64_PRIME`.
- Functions:
  - `fnv_32_buf`
  - `fnv_32_str`
  - `fnv_64_buf`
  - `fnv_64_str`

## Dependencies And Integration
Assumes `u_int*` types and `size_t` are available from including context. Used where a compact non-cryptographic hash is sufficient.

## Risk Notes
This is not a security hash. The implementation multiplies then XORs each byte, matching FNV-1 rather than FNV-1a.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/fnv_hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/font.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/font.h

## Purpose
Defines VT font metadata, Unicode-to-glyph mapping structures, bitmap data, and packed on-disk/in-memory VFNT headers.

## Main Interfaces
- `enum vfnt_map_type`: normal, normal-right, bold, bold-right maps.
- `struct font_info`: checksum, dimensions, bitmap size, map counts.
- Packed `struct vfnt_map`: source codepoint, destination glyph, run length.
- `struct vt_font`: map pointers, bitmap bytes, dimensions, map counts, refcount.
- `vt_font_bitmap_data_t`: compressed/uncompressed bitmap package and loaded font pointer.
- `FONT_FLAGS`: auto, manual, builtin, reload.
- `struct fontlist` and `font_list_t`.
- `FONT_HEADER_MAGIC` and packed `struct font_header`.

## Dependencies And Integration
Uses queue macros. The comments specify binary-search lookup over sorted maps and fallback behavior from bold to normal glyphs and missing glyphs to glyph 0.

## Risk Notes
Packed structures and magic string define VFNT file format compatibility. Map ordering is an implicit correctness requirement for lookup performance and behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/font.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gmon.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/gmon.h

## Purpose
Defines gprof/gmon profiling file structures, kernel profiling state, arc records, and profiling sysctl identifiers.

## Main Interfaces
- `struct gmonhdr`: header for `gmon.out`.
- `GMONVERSION`.
- `HISTCOUNTER` type, controlled by `GPROF4`.
- Profiling sizing constants: `HISTFRACTION`, `HASHFRACTION`, `ARCDENSITY`, `MINARCS`, `MAXARCS`.
- Arc structures: `struct tostruct`, `struct rawarc`.
- `struct gmonparam`: profiling buffers, bounds, hash fraction, rate, overhead counters, histogram type.
- Global `_gmonparam`.
- States: `GMON_PROF_ON`, `BUSY`, `ERROR`, `OFF`, `HIRES`.
- Sysctl IDs: `GPROF_STATE`, `COUNT`, `FROMS`, `TOS`, `GMONPARAM`.
- Kernel helpers/macros: `KCOUNT`, `PC_TO_I`, optional `GUPROF` calibration/profiling functions, `kmupetext`, `mexitcount`, etc.
- Userland functions: `moncontrol`, `monstartup`.

## Dependencies And Integration
Includes `machine/profile.h` for function alignment and pointer-sized profiling types. Kernel support exposes profiling data through sysctl.

## Risk Notes
Several sizing macros depend on architecture function alignment. `MAXARCS` is constrained by `u_short` link storage. Structure layouts are consumed by profiling tools.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gpio.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/gpio.h

## Purpose
Defines GPIO pin state/configuration flags, ioctl argument structures, event reporting formats, and GPIO control ioctls.

## Main Interfaces
- Pin states: `GPIO_PIN_LOW`, `GPIO_PIN_HIGH`.
- Name limit: `GPIOMAXNAME`.
- Pin flags for direction, drive mode, pullups, inversion, pulsate, preset output state.
- Interrupt flags: level/edge modes, attached state, masks.
- `struct gpio_pin`: pin number, name, caps, flags.
- `struct gpio_req`: pin number and value.
- Event reporting:
  - `struct gpio_event_detail`
  - `struct gpio_event_summary`
  - `struct gpio_event_config`
  - report types `GPIO_EVENT_REPORT_DETAIL`, `GPIO_EVENT_REPORT_SUMMARY`
- Batch operations:
  - `struct gpio_access_32`
  - `struct gpio_config_32`
- Ioctls: `GPIOMAXPIN`, `GPIOGETCONFIG`, `GPIOSETCONFIG`, `GPIOGET`, `GPIOSET`, `GPIOTOGGLE`, `GPIOSETNAME`, `GPIOACCESS32`, `GPIOCONFIG32`, `GPIOCONFIGEVENTS`.

## Dependencies And Integration
Includes `ioccom.h` and userland `stdbool.h` outside kernel/standalone. Batch operations assume driver-specific mapping of adjacent pins to 32-bit words.

## Risk Notes
The event structures include `bool`, so ABI layout must be checked across architectures. Atomicity promises for `GPIOACCESS32` are strict; `GPIOCONFIG32` explicitly allows best-effort non-atomic hardware behavior.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gpt.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/gpt.h

## Purpose
Thin compatibility wrapper that defines GPT UUID type and includes the shared GPT disk layout header.

## Main Interfaces
- Includes `sys/uuid.h`.
- Defines `GPT_UUID_TYPE` as `struct uuid`.
- Includes `sys/disk/gpt.h`.

## Dependencies And Integration
This lets consumers include `sys/gpt.h` and receive GPT structures parameterized with FreeBSD `struct uuid`.

## Risk Notes
The wrapper is intentionally minimal. Any layout semantics live in `sys/disk/gpt.h`; changing `GPT_UUID_TYPE` would affect GPT structure ABI.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gpt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gsb_crc32.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/gsb_crc32.h

## Purpose
Declares CRC32 and CRC32C calculation helpers, including kernel inline table CRC32 and architecture-specific CRC32C acceleration entry points.

## Main Interfaces
- Kernel-only external table: `crc32_tab`.
- Kernel inline functions:
  - `crc32_raw`
  - `crc32`
- Generic CRC32C: `calculate_crc32c`.
- Architecture-specific CRC32C:
  - `sse42_crc32c` for amd64/i386
  - `armv8_crc32c` for aarch64
- Testing helpers: `singletable_crc32c`, `multitable_crc32c`.

## Dependencies And Integration
Includes `sys/types.h`. Kernel `crc32` wraps `crc32_raw` with initial/final bitwise inversion. CRC32C implementations are selected elsewhere.

## Risk Notes
CRC32 and CRC32C are different polynomials; callers must use the right API. Architecture-specific prototypes must match CPU feature dispatch code.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gsb_crc32.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gtaskqueue.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/gtaskqueue.h

## Purpose
Declares kernel taskqueue group support for grouped tasks, dynamic thread groups, and IRQ/CPU binding.

## Main Interfaces
- Kernel-only header.
- `struct grouptask`: embedded `gtask`, taskqueue pointer, list linkage, unique key, name, device, IRQ resource, CPU.
- Queue APIs:
  - `gtaskqueue_block`
  - `gtaskqueue_unblock`
  - `gtaskqueue_cancel`
  - `gtaskqueue_drain`
  - `gtaskqueue_drain_all`
  - `grouptaskqueue_enqueue`
- Group task APIs:
  - `grouptask_block`
  - `grouptask_unblock`
  - `taskqgroup_attach`
  - `taskqgroup_attach_cpu`
  - `taskqgroup_detach`
  - `taskqgroup_create`
  - `taskqgroup_destroy`
  - `taskqgroup_bind`
  - `taskqgroup_drain_all`
- Initialization and enqueue macros: `GTASK_INIT`, `GROUPTASK_INIT`, `GROUPTASK_ENQUEUE`.
- Declaration/definition macros: `TASKQGROUP_DECLARE`, `TASKQGROUP_DEFINE`.
- Declares `qgroup_softirq`.

## Dependencies And Integration
Includes `_task.h`, bus/device types, taskqueue, and system types. `TASKQGROUP_DEFINE` uses SYSINIT ordering for creation and SMP binding.

## Risk Notes
Task group binding depends on init ordering (`SI_SUB_TASKQ`, `SI_SUB_SMP`). `GROUPTASK_NAMELEN` bounds task names at 32 bytes.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/gtaskqueue.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hash.h -->
# File Research: sources/os/bsd/freebsd-src/sys/sys/hash.h

## Purpose
Provides simple inline 32-bit string/buffer hashing helpers and kernel hash table allocation/hash algorithm declarations.

## Main Interfaces
- Default hash macros: `HASHINIT`, `HASHSTEP`.
- Inline hashes:
  - `hash32_buf`
  - `hash32_str`
  - `hash32_strn`
  - `hash32_stre`
  - `hash32_strne`
- Kernel `struct hashalloc_args` with version, error, size, bucket header size, hash type, head type, lock type, malloc flags/type, lock name, constructor, destructor.
- Kernel allocation APIs: `hashalloc`, `hashfree`.
- Kernel hash functions:
  - `jenkins_hash`
  - `jenkins_hash32`
  - `murmur3_32_hash`
  - `murmur3_32_hash32`

## Dependencies And Integration
Includes `sys/types.h`. The `*_stre` helpers are intended for pathname component hashing in `namei`-style code. Kernel allocation supports multiple bucket head types and lock strategies.

## Risk Notes
The inline `HASHSTEP` hash is simple and non-cryptographic. `hashalloc_args` versioning is present but currently version `0`; callers must inspect `error` after allocation attempts.
<!-- END FILE RESEARCH: sources/os/bsd/freebsd-src/sys/sys/hash.h -->