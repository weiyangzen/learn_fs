# Group Research: group_1282_netbsd_src_sources_os_bsd_netbsd_src_sys_sys_errno_h_sources_os_bsd_845f3a0faeea

Scope checked against `Docs/research_subset_a.md`: subset A includes `sources/os/bsd/netbsd-src`. All 37 listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/errno.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/errno.h

Read completely: 190 lines.

## Purpose
Defines NetBSD system error numbers, their stable numeric ABI values, compatibility aliases, and kernel-only pseudo-errors.

## Main Interfaces
- Standard errno constants: `EPERM` through `ENOTRECOVERABLE`.
- Alias: `EWOULDBLOCK` maps to `EAGAIN`.
- Limit marker: `ELAST` equals the largest errno value.
- Kernel/internal pseudo-errors under `_KERNEL || _KMEMUSER`: `EJUSTRETURN`, `ERESTART`, `EPASSTHROUGH`, `EDUPFD`, `EMOVEFD`.

## Dependencies And Integration
This header is a base ABI dependency for kernel and userland error reporting. VFS, file descriptor, ioctl, exec, networking, NFS, extended attributes, and synchronization code all use these symbolic return values.

## Risks And Edge Cases
- Numeric values are ABI-stable and must not be casually reordered.
- Kernel pseudo-errors are negative and are not user-visible errno values.
- `ELAST` must track the largest positive errno.

## Filesystem Relevance
High. Filesystem syscalls, vnode operations, mount code, NFS file handles, extended attributes, and device ioctls communicate failures through this namespace.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/errno.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/evcnt.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/evcnt.h

Read completely: 157 lines.

## Purpose
Declares NetBSD event counters: lightweight named counters used by kernel subsystems and exposed for diagnostics.

## Main Interfaces
- `struct evcnt`: 64-bit count, list linkage, type, group/name lengths, optional parent, group/name strings.
- Counter types: `EVCNT_TYPE_MISC`, `EVCNT_TYPE_INTR`, `EVCNT_TYPE_TRAP`, `EVCNT_TYPE_ANY`.
- Static counter macros: `EVCNT_INITIALIZER`, `EVCNT_ATTACH_STATIC`, `EVCNT_ATTACH_STATIC2`.
- Kernel routines: `evcnt_init`, `evcnt_attach_static`, `evcnt_attach_dynamic`, `evcnt_attach_dynamic_nozero`, `evcnt_detach`.
- `ev_count32` selects the right 32-bit half by endian order.

## Dependencies And Integration
Uses `sys/queue.h` and `sys/stdint.h`; kernel users link counters into `allevents`. Interrupt, trap, storage, and filesystem/device paths can use it for counters.

## Risks And Edge Cases
- Group/name strings are length-limited by `EVCNT_STRING_MAX`.
- 32-bit counter access depends on `_BYTE_ORDER`.
- Static attach relies on link sets.

## Filesystem Relevance
Moderate. Not filesystem-specific, but useful for filesystem, block, and device instrumentation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/evcnt.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/event.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/event.h

Read completely: 360 lines.

## Purpose
Defines the kqueue/kevent user ABI and kernel knote/filter interfaces for event notification.

## Main Interfaces
- Filters: `EVFILT_READ`, `EVFILT_WRITE`, `EVFILT_VNODE`, `EVFILT_PROC`, `EVFILT_SIGNAL`, `EVFILT_TIMER`, `EVFILT_FS`, `EVFILT_USER`, and others.
- `struct kevent` and `EV_SET`.
- Event actions and flags: `EV_ADD`, `EV_DELETE`, `EV_ENABLE`, `EV_DISABLE`, `EV_ONESHOT`, `EV_CLEAR`, `EV_RECEIPT`, `EV_DISPATCH`, `EV_EOF`, `EV_ERROR`.
- Note flags: vnode notes (`NOTE_DELETE`, `NOTE_WRITE`, `NOTE_EXTEND`, `NOTE_ATTRIB`, `NOTE_RENAME`, `NOTE_REVOKE`, etc.), process notes, timer units, user-event fflag operations.
- Kernel interfaces: `struct filterops`, `struct knote`, `KNOTE`, `knote`, `knote_fdclose`, `klist_*`, `kevent1`, `kfilter_register`, `kfilter_unregister`.
- Userland declarations: `kqueue`, `kqueue1`, `kevent`.

## Dependencies And Integration
Uses feature-test macros, integer types, queue lists, ioctl definitions, file descriptor state, filter registration, and kernel object-specific locks. Vnodes and files attach knotes for notification.

## Risks And Edge Cases
- `struct knote` has explicit field-locking rules across fd-table, kqueue, and object locks.
- `EVFILT_USER` encodes fflag modification operations in high bits.
- `EVFILT_VNODE` depends on vnode code correctly issuing notes for filesystem mutations.
- `EV_ERROR` reports errno in `data`.

## Filesystem Relevance
High. VFS and vnode operations use `EVFILT_VNODE` and `EVFILT_FS` to notify userland of file and mount changes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/event.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/eventfd.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/eventfd.h

Read completely: 59 lines.

## Purpose
Declares NetBSD's Linux-compatible `eventfd(2)` interface.

## Main Interfaces
- `typedef uint64_t eventfd_t`.
- Flags mapped to open flags: `EFD_SEMAPHORE`, `EFD_CLOEXEC`, `EFD_NONBLOCK`.
- Kernel entry: `do_eventfd`.
- Userland calls: `eventfd`, `eventfd_read`, `eventfd_write`.

## Dependencies And Integration
Includes `sys/fcntl.h` for flag definitions. Eventfd objects are represented as descriptor type `DTYPE_EVENTFD` in file infrastructure.

## Risks And Edge Cases
- ABI compatibility depends on preserving Linux-style flag semantics.
- `EFD_SEMAPHORE` is encoded as `O_RDWR`, so callers must treat the exported constants as ABI values, not independent bit names.

## Filesystem Relevance
Low direct relevance, but it shares file descriptor and polling/kqueue infrastructure with filesystem descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/eventfd.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/eventvar.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/eventvar.h

Read completely: 71 lines.

## Purpose
Declares private kqueue implementation structures for kernel and kmem inspection.

## Main Interfaces
- Constants: `KQ_NEVENTS`, `KQ_EXTENT`, `KFILTER_MAXNAME`, `KFILTER_EXTENT`.
- `struct kqueue`: pending-event queue, mutex, owning `filedesc_t`, select info, condition variable, count/flag word.
- Count flags: `KQ_RESTART`, `KQ_CLOSING`, `KQ_MAXCOUNT`, `KQ_COUNT`.
- DDB printer: `kqueue_printit`.

## Dependencies And Integration
Includes mutex, select, and file descriptor headers. Kqueue descriptors are file objects and interact with fd table close paths and vnode knotes.

## Risks And Edge Cases
- `kq_count` combines count and state flags, so masking with `KQ_COUNT` is required.
- This is not a general public API despite being a header.

## Filesystem Relevance
Moderate. It backs file/vnode event delivery to userland.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/eventvar.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/exec.h

Read completely: 328 lines.

## Purpose
Defines the machine-independent exec framework: process argument metadata, executable-format switch entries, exec packages, VM commands, and exec/posix_spawn kernel entry points.

## Main Interfaces
- User-visible `struct ps_strings` and kernel `struct ps_strings32`.
- `struct execsw`: format handler metadata and callbacks for probing, argument copying, register setup, stack setup, and core dumping.
- `struct exec_package`: pathname/header/vnode/attributes, VM layout, entry point, fake script args, emulation data, interpreter vnode, PaX flags, OS version, machine arch.
- Exec flags: `EXEC_INDIR`, `EXEC_HASFD`, `EXEC_HASARGL`, `EXEC_SKIPARG`, `EXEC_DESTR`, `EXEC_32`, `EXEC_FORCEAUX`, `EXEC_TOPDOWN_VM`, `EXEC_FROM32`.
- `struct exec_vmcmd_set`, `struct exec_vmcmd`, `NEW_VMCMD`, `NEW_VMCMD2`.
- Kernel routines: `exec_makecmds`, `exec_runcmds`, `exec_read`, `check_exec`, `check_veriexec`, `execve1`, `do_posix_spawn`, `exec_add`, `exec_remove`, `exec_sigcode_alloc`, `emul_find_root`, `emul_find_interp`.

## Dependencies And Integration
Connects vnode-backed executable files, namei path resolution, UVM mappings, emulation roots, veriexec, core dump code, and machine-dependent register setup.

## Risks And Edge Cases
- Exec packages carry vnode and interpreter state that must be unwound correctly on failure.
- Fake argument vectors handle script indirection.
- 32-bit emulation uses separate ps-string and ABI flags.
- VM command ordering and flags determine process address-space construction.

## Filesystem Relevance
High. Executables are opened and read through VFS/vnodes; mount `noexec`, vnode permissions, veriexec, and interpreter path lookup all feed exec.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_aout.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_aout.h

Read completely: 184 lines.

## Purpose
Defines the legacy a.out executable header, magic values, machine-id/flag encoding, segment address/offset macros, and kernel preparation routines.

## Main Interfaces
- `struct exec`: a.out header fields for text, data, bss, symbols, entry, relocation sizes.
- Magic values: `OMAGIC`, `NMAGIC`, `ZMAGIC`, `QMAGIC`.
- Flags: `EX_DYNAMIC`, `EX_PIC`, `EX_DPMASK`.
- Header field macros: `N_GETMAGIC`, `N_GETMAGIC2`, `N_GETMID`, `N_GETFLAG`, `N_SETMAGIC`.
- Layout macros: `N_ALIGN`, `N_BADMAG`, `N_TXTADDR`, `N_DATADDR`, `N_BSSADDR`, `N_TXTOFF`, `N_DATOFF`, relocation and symbol/string offsets.
- Kernel handlers: `exec_aout_makecmds`, `exec_aout_prep_*`, `cpu_exec_aout_makecmds`.

## Dependencies And Integration
Uses endian conversion, a.out machine IDs, and machine-dependent a.out definitions. Plugs into the generic exec switch.

## Risks And Edge Cases
- `a_midmag` is network-byte-order encoded for newer format variants.
- Layout macros depend on `AOUT_LDPGSZ` and magic-specific historical behavior.
- `QMAGIC` is marked deprecated but still recognized.

## Filesystem Relevance
Moderate. It is an exec format consuming vnode file contents through the exec framework.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_aout.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_coff.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_coff.h

Read completely: 156 lines.

## Purpose
Defines COFF executable headers, section metadata, flag constants, alignment/layout macros, and kernel COFF preparation hooks.

## Main Interfaces
- `struct coff_filehdr`, `struct coff_aouthdr`, `struct coff_scnhdr`, `struct coff_slhdr`, `struct coff_exechdr`.
- File flags: `COFF_F_RELFLG`, `COFF_F_EXEC`, `COFF_F_LNNO`, `COFF_F_LSYMS`, byte-order/architecture flags.
- Section flags: `COFF_STYP_TEXT`, `COFF_STYP_DATA`, `COFF_STYP_BSS`, and others.
- Layout helpers: `COFF_ROUND`, `COFF_ALIGN`, `COFF_HDR_SIZE`, `COFF_BLOCK_ALIGN`, `COFF_TXTOFF`, `COFF_DATOFF`, `COFF_SEGMENT_ALIGN`.
- Kernel routines: `exec_coff_makecmds`, `exec_coff_prep_omagic`, `exec_coff_prep_nmagic`, `exec_coff_prep_zmagic`.

## Dependencies And Integration
Includes machine-dependent COFF definitions and plugs into exec image loading.

## Risks And Edge Cases
- Segment offsets depend on machine `COFF_SEGMENT_ALIGNMENT` and magic.
- Header uses C `long`/`short`, so ABI assumptions are tied to supported COFF platforms.

## Filesystem Relevance
Moderate. COFF loading reads executable file segments through VFS-backed exec paths.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_coff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_ecoff.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_ecoff.h

Read completely: 187 lines.

## Purpose
Defines ECOFF executable formats, including optional padded 32-bit layouts, segment offset/alignment macros, and ECOFF kernel exec hooks.

## Main Interfaces
- Optional `ECOFF32_PAD` block defining fixed-width `ecoff32_*` types and `ecoff32_*` headers.
- Native `struct ecoff_filehdr`, `struct ecoff_aouthdr`, `struct ecoff_scnhdr`, `struct ecoff_exechdr`.
- Magic values: `ECOFF_OMAGIC`, `ECOFF_NMAGIC`, `ECOFF_ZMAGIC`.
- Layout helpers: `ECOFF_ROUND`, `ECOFF_BLOCK_ALIGN`, `ECOFF_TXTOFF`, `ECOFF_DATOFF`, `ECOFF_SEGMENT_ALIGN`, plus 32-bit variants.
- Kernel routines: `exec_ecoff_makecmds`, `cpu_exec_ecoff_probe`, `cpu_exec_ecoff_setregs`, `exec_ecoff_prep_*`.

## Dependencies And Integration
Includes endian and machine ECOFF definitions. Used by architecture compatibility exec paths.

## Risks And Edge Cases
- Optional 32-bit padded layout exists only when `ECOFF32_PAD` is defined.
- Layout depends on machine-dependent padding and segment alignment macros.
- ECOFF probing and register setup are CPU-dependent.

## Filesystem Relevance
Moderate. Another exec format consuming file contents through VFS/vnode exec reads.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_ecoff.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_elf.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_elf.h

Read completely: 1534 lines.

## Purpose
Defines NetBSD's ELF ABI types, headers, constants, notes, auxiliary vectors, size-selection macros, and kernel ELF exec/core-dump interfaces.

## Main Interfaces
- ELF integer/address typedefs for 32-bit and 64-bit classes.
- File headers: `Elf32_Ehdr`, `Elf64_Ehdr`; program headers; section headers; symbols; relocations; dynamic entries; notes; versioning records.
- Identification constants: `EI_*`, `ELFMAG*`, `ELFCLASS*`, `ELFDATA*`, `ELFOSABI_*`, `ET_*`, extensive `EM_*`.
- Program/section constants: `PT_*`, `PF_*`, `SHT_*`, `SHF_*`, section indexes.
- Symbol/relocation helpers: `ELF*_R_*`, `ELF_ST_*`, visibility and versioning macros.
- Dynamic tags and flags: `DT_*`, `DF_*`, `DF_1_*`.
- Auxiliary vectors: `Aux32Info`, `Aux64Info`, `AT_*`.
- Notes: GNU ABI/build-id/hwcap, SuSE, Go build id, FDO packaging metadata, NetBSD ABI/emulation/PaX/MACHINE_ARCH/MCMODEL/core notes.
- Type-selection macros: `ELFSIZE`, `Elf_Ehdr`, `Elf_Phdr`, `ElfW`, `ELFNAME`, `AuxInfo`.
- Kernel limits and interfaces: `ELF_MAXPHNUM`, `ELF_MAXSHNUM`, `ELF_MAXNOTESIZE`, `ELF_AUX_ENTRIES`, `struct elf_args`, `exec_elf32_makecmds`, `exec_elf64_makecmds`, `elf*_populate_auxv`, `elf*_copyargs`, `elf*_check_header`, `coredump_elf*`.

## Dependencies And Integration
Includes machine ELF definitions and can coexist with `sys/elfdefinitions.h`. It is central to exec image loading, dynamic linker setup, ABI tagging, PaX policy, machine-architecture notes, and ELF core dumps.

## Risks And Edge Cases
- Some definitions are skipped if `sys/elfdefinitions.h` was already included, but NetBSD overrides `EM_ALPHA`.
- `ELF_NIDENT` is defined as `EI_INDENT`, which appears to preserve a prior spelling but is suspicious if consumers expect `EI_NIDENT`.
- Kernel caps program headers, section headers, and note size to limit memory-allocation abuse.
- ABI note sizes/names must match external toolchain expectations.
- `ELFSIZE` controls many generic type aliases; wrong selection changes structure interpretation.

## Filesystem Relevance
High. ELF is the primary executable/core format read from vnode files and affected by filesystem permissions, mount flags, and path/interpreter lookup.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_elf.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_script.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_script.h

Read completely: 49 lines.

## Purpose
Defines shebang script exec recognition constants and the kernel script exec handler declaration.

## Main Interfaces
- `EXEC_SCRIPT_MAGIC` as `#!`.
- `EXEC_SCRIPT_MAGICLEN`.
- `SCRIPT_HDR_SIZE`, based on magic length, `MAXINTERP`, optional space, and newline.
- Kernel handler: `exec_script_makecmds`.

## Dependencies And Integration
Used by exec format dispatch after reading executable headers from a vnode.

## Risks And Edge Cases
- Interpreter parsing is bounded by `SCRIPT_HDR_SIZE`.
- Script indirection interacts with `EXEC_INDIR`, fake args, and held script descriptors in `exec.h`.

## Filesystem Relevance
High for script execution. It maps a file's first bytes to interpreter path lookup and exec recursion.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/exec_script.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/extattr.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/extattr.h

Read completely: 125 lines.

## Purpose
Defines the BSD extended-attribute namespace ABI, extattr control commands, kernel credential checks, and userland extattr functions.

## Main Interfaces
- Namespaces: `EXTATTR_NAMESPACE_EMPTY`, `USER`, `SYSTEM` and string names.
- `EXTATTR_NAMESPACE_NAMES` initializer.
- `EXTATTR_MAXNAMELEN`.
- Control commands: `EXTATTR_CMD_START`, `EXTATTR_CMD_STOP`.
- Kernel: `EXTATTR_LIST_LENPREFIX`, `extattr_check_cred`.
- Userland operations for fd/file/link: get, set, delete, list, control, namespace conversion, copy helpers, `fcpxattr`, `cpxattr`, `lcpxattr`.

## Dependencies And Integration
Ties user APIs to VFS extended attribute vnode operations and authorization via credentials.

## Risks And Edge Cases
- Namespace values and names are ABI-facing.
- List output can be length-prefixed via VOP flag.
- System namespace authorization depends on `extattr_check_cred`.

## Filesystem Relevance
High. Defines filesystem extended attribute user/kernel contract.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/extattr.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/extent.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/extent.h

Read completely: 121 lines.

## Purpose
Declares the extent allocator: a kernel resource-range allocator for address, bus, I/O, or similar numeric regions.

## Main Interfaces
- `struct extent_region`: allocated range and flags.
- `struct extent`: named range space, lock/cv, allocated-region list, start/end, behavior flags.
- `struct extent_fixed`: extent with fixed descriptor storage.
- Internal flags: `EXF_FIXED`, `EXF_NOCOALESCE`, `EXF_EARLY`.
- Allocation flags: `EX_WAITOK`, `EX_FAST`, `EX_CATCH`, `EX_NOCOALESCE`, `EX_MALLOCOK`, `EX_WAITSPACE`, `EX_BOUNDZERO`, `EX_EARLY`.
- Alignment/boundary sentinels: `EX_NOALIGN`, `EX_NOBOUNDARY`.
- APIs: `extent_create`, `extent_destroy`, `extent_alloc*`, `extent_alloc_region`, `extent_free`, `extent_print`, `extent_init`.

## Dependencies And Integration
Uses queues, mutexes, and condition variables. Consumers include kernel resource managers and potentially storage/device drivers.

## Risks And Edge Cases
- Early-boot extents skip normal locking.
- Fixed storage can run out unless callers allow allocation or waiting.
- Boundary/alignment arguments alter allocation search behavior.

## Filesystem Relevance
Indirect. Useful for block/device resource allocation underneath filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/extent.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fault.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fault.h

Read completely: 79 lines.

## Purpose
Defines fault-injection control ABI and the kernel `fault_inject` hook.

## Main Interfaces
- Scopes: `FAULT_SCOPE_GLOBAL`, `FAULT_SCOPE_LWP`.
- Mode: `FAULT_MODE_NTH_ONESHOT`.
- Minimum nth trigger: `FAULT_NTH_MIN`.
- Ioctl payloads: `fault_ioc_enable`, `fault_ioc_disable`, `fault_ioc_getinfo`.
- Ioctls: `FAULT_IOC_ENABLE`, `FAULT_IOC_DISABLE`, `FAULT_IOC_GETINFO`.
- Kernel hook: `fault_inject()` real when `FAULT` is configured, otherwise inline false.

## Dependencies And Integration
Includes `opt_fault.h` in kernel option builds and uses ioctl encoding.

## Risks And Edge Cases
- User-visible ioctls are available only outside kernel or with `FAULT`.
- Non-FAULT kernels compile fault checks away to false.

## Filesystem Relevance
Moderate for testing. Fault injection can exercise filesystem error paths if used by lower layers.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fault.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fcntl.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fcntl.h

Read completely: 366 lines.

## Purpose
Defines open/fcntl file status flags, descriptor flags, advisory lock structures, file seals, filesystem-control fcntl encoding, seek constants, fadvise constants, `*at` flags, and userland declarations.

## Main Interfaces
- Open flags: `O_RDONLY`, `O_WRONLY`, `O_RDWR`, `O_NONBLOCK`, `O_APPEND`, `O_SYNC`, `O_NOFOLLOW`, `O_CREAT`, `O_TRUNC`, `O_EXCL`, `O_NOCTTY`, `O_DSYNC`, `O_RSYNC`, `O_DIRECT`, `O_DIRECTORY`, `O_CLOEXEC`, `O_SEARCH`, `O_NOSIGPIPE`, `O_REGULAR`, `O_EXEC`, `O_CLOFORK`.
- Kernel conversions: `FFLAGS`, `OFLAGS`, `O_MASK`, `FMASK`, `FCNTLFLAGS`.
- Fcntl commands: `F_DUPFD`, `F_GETFD`, `F_SETFD`, `F_GETFL`, `F_SETFL`, locks, `F_CLOSEM`, `F_MAXFD`, `F_DUPFD_CLOEXEC`, `F_GETPATH`, file seals, `F_DUPFD_CLOFORK`, `F_DUPFD_CLOBOTH`.
- Descriptor flags: `FD_CLOEXEC`, `FD_CLOFORK`.
- Locking: `struct flock`, `F_RDLCK`, `F_UNLCK`, `F_WRLCK`, `LOCK_SH`, `LOCK_EX`, `LOCK_NB`, `LOCK_UN`.
- Seals: `F_SEAL_*`.
- Filesystem fcntl encoding: `F_FSCTL`, `F_FSIN`, `F_FSOUT`, `_FCN*`, `_FCN_FSPRIV*`.
- `POSIX_FADV_*`; `AT_FDCWD`, `AT_EACCESS`, symlink and remove-directory flags.
- Userland: `open`, `creat`, `fcntl`, `flock`, `posix_fadvise`, `posix_fallocate`, `openat`.

## Dependencies And Integration
Feeds VFS open, file descriptor state, vnode fileops, advisory locks, filesystem private fcntls, posix fallocate/fadvise, and `*at` syscalls.

## Risks And Edge Cases
- Open flags and kernel `f_flag` differ by `+1` conversion.
- Feature-test macros gate visibility of POSIX/XSI/NetBSD extensions.
- `O_CLOFORK` and `FD_CLOFORK` are newer ABI additions.
- Filesystem-control fcntl encodes parameter length and private filesystem number.

## Filesystem Relevance
High. This is the main open/fcntl ABI for filesystems and file descriptors.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fcntl.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fd_set.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fd_set.h

Read completely: 108 lines.

## Purpose
Defines `fd_set` and macros for select-style file descriptor bitsets.

## Main Interfaces
- Internal type: `__fd_mask`.
- Bit geometry: `__NFDBITS`, `__NFDSHIFT`, `__NFDMASK`.
- Default `FD_SETSIZE` of 256.
- `fd_set` with `fds_bits`.
- Macros: `FD_SET`, `FD_CLR`, `FD_ISSET`, `FD_ZERO`, and NetBSD-visible `FD_COPY`, `fd_mask`, `NFDBITS`.

## Dependencies And Integration
Used by `select(2)` and descriptor readiness code. Includes feature-test and machine integer types.

## Risks And Edge Cases
- `FD_SETSIZE` may be user-defined before inclusion.
- Macros do not bounds-check descriptor indices.
- `FD_ZERO`/`FD_COPY` use compiler builtins when available.

## Filesystem Relevance
Moderate. Filesystem descriptors participate in readiness APIs, especially for special files and devices.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fd_set.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fdio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fdio.h

Read completely: 84 lines.

## Purpose
Defines floppy disk formatting structures, options, and ioctls.

## Main Interfaces
- `enum fdformat_result`.
- `FDFORMAT_VERSION`.
- `struct fdformat_cmd`: head/cylinder command.
- `struct fdformat_parms`: geometry and formatting parameters.
- Options: `FDOPT_NORETRY`, `FDOPT_SILENT`.
- Ioctls: `FDIOCGETOPTS`, `FDIOCSETOPTS`, `FDIOCSETFORMAT`, `FDIOCGETFORMAT`, `FDIOCFORMAT_TRACK`.

## Dependencies And Integration
Uses ioctl command encoding via `sys/ioccom.h`; consumed by floppy drivers and user tools.

## Risks And Edge Cases
- Format parameter structure is versioned and should be extended only at the end.
- Driver-specific conversion is needed for transfer rates and media geometry.

## Filesystem Relevance
Low to moderate. It addresses block media below filesystems rather than filesystem logic itself.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fdio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/featuretest.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/featuretest.h

Read completely: 152 lines.

## Purpose
Normalizes feature-test macros so headers expose the correct standards and NetBSD extension namespaces.

## Main Interfaces
- Documents major macros: `_ANSI_SOURCE`, `_POSIX_SOURCE`, `_POSIX_C_SOURCE`, `_XOPEN_SOURCE`, `_NETBSD_SOURCE`.
- Documents minor macros: `_REENTRANT`, `_ISOC99_SOURCE`, `_ISOC11_SOURCE`, `_ISOC23_SOURCE`, `_OPENBSD_SOURCE`, `_GNU_SOURCE`.
- Converts `_POSIX_SOURCE` to `_POSIX_C_SOURCE`.
- Defaults to `_NETBSD_SOURCE` when no major macro is defined.
- Implies `_REENTRANT` for POSIX/XOPEN thread-era profiles.
- Maps `_XOPEN_SOURCE` 500/600/700/800 to corresponding `_POSIX_C_SOURCE` values.

## Dependencies And Integration
Included by many public headers such as `fcntl.h`, `event.h`, `fd_set.h`, and `float_ieee754.h`.

## Risks And Edge Cases
- Header intentionally has no include guard because behavior depends on include order and macro state.
- Visibility conditions in other headers depend on the normalized values.

## Filesystem Relevance
Moderate. Controls whether filesystem-related APIs like `openat`, `posix_fallocate`, and NetBSD flags are visible to userland.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/featuretest.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/file.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/file.h

Read completely: 237 lines.

## Purpose
Defines kernel file objects, file operation vectors, descriptor data unions, descriptor types, and common file I/O helpers.

## Main Interfaces
- `struct fileops`: read, write, ioctl, fcntl, poll, stat, close, kqfilter, restart, mmap, seek, advlock, pathconf, fadvise, truncate.
- `union file_data`: vnode, socket, pipe, kqueue, eventfd, timerfd, memfd, and miscellaneous backing pointers.
- `struct file`: offset, credentials, ops, data, global list, lock, flags, type, advice, reference counters.
- Descriptor types: `DTYPE_VNODE`, `SOCKET`, `PIPE`, `KQUEUE`, `MISC`, `MQUEUE`, `SEM`, `EVENTFD`, `TIMERFD`, `MEMFD`.
- Kernel helpers: `dofileread`, `dofilewrite`, vector read/write, ownership/signal helpers, common null/bad fileops, `vnops`.

## Dependencies And Integration
Includes `fcntl.h`, `unistd.h`, queue/mutex/cv headers. Vnode-backed files use `vnops`; descriptor tables in `filedesc.h` hold `struct file *`.

## Risks And Edge Cases
- `struct file` is exported by old `KERN_FILE` sysctl; fields should only be appended.
- Reference counts include normal, message-queue, and UNIX-domain deferred-close references.
- Fileops must honor offsets, credentials, locks, and descriptor flags.

## Filesystem Relevance
High. This is the core kernel abstraction for open filesystem objects.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/file.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fileassoc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fileassoc.h

Read completely: 53 lines.

## Purpose
Declares per-vnode/per-mount file association tables for attaching subsystem-private data to files.

## Main Interfaces
- Opaque `fileassoc_t` and callback types.
- Registration: `fileassoc_register`, `fileassoc_deregister`.
- Lookup and mutation: `fileassoc_lookup`, `fileassoc_add`, `fileassoc_clear`.
- Cleanup: `fileassoc_table_delete`, `fileassoc_table_clear`, `fileassoc_file_delete`.
- Iteration callback: `fileassoc_table_run`.

## Dependencies And Integration
Uses mount and vnode objects. Consumers can associate metadata with vnodes without changing filesystem node structures.

## Risks And Edge Cases
- Cleanup callbacks must be correct because data lifetime is tied to vnode and mount teardown.
- Associations depend on vnode identity stability.

## Filesystem Relevance
High. Used for filesystem-adjacent metadata such as veriexec or security state associated with vnodes.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fileassoc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/filedesc.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/filedesc.h

Read completely: 265 lines.

## Purpose
Defines process file descriptor tables, per-descriptor state, current/root directory state, and kernel descriptor-management APIs.

## Main Interfaces
- Sizing constants: `NDFILE`, `NDEXTENT`, `NDENTRIES`, bitmap helpers.
- `fdfile_t`: per-descriptor close-on-exec/fork flags, allocation state, refcount, file pointer, knotes, close cv.
- `fdtab_t`: active descriptor table.
- `filedesc_t`: built-in descriptors, lock, active table pointer, bitmaps, knote hash, high-water marks, refcount, close flags, built-in table/maps.
- `cwdinfo_t`: current/root/emulation root vnodes, umask, refcount, rwlock.
- Kernel APIs: descriptor allocation, duplication, sharing/copying/freeing, close-on-exec/fork, fd lookup/put, vnode/socket lookup, close, clone, pipe, cwd management, path reconstruction, `closef`, fcntl lock helper.

## Dependencies And Integration
Includes locks, queues, vnode pointers, knotes, file objects, process/lwp state, and path helpers. It is used by open/close, fork/exec, kqueue, VFS lookup, and socket/file operations.

## Risks And Edge Cases
- Close-on-exec/fork flags should be set via `fd_set_exclose`/`fd_set_foclose` to keep summary booleans consistent.
- Descriptor tables can be shared by multiple processes and have active-table replacement.
- Refcount high bit `FR_CLOSING` marks closing interlock state.
- Built-in descriptors have strict cache-line alignment.

## Filesystem Relevance
High. Every open file, directory fd, `*at` syscall, cwd/root, and vnode descriptor path depends on this structure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/filedesc.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/filio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/filio.h

Read completely: 64 lines.

## Purpose
Defines generic file-descriptor ioctls.

## Main Interfaces
- Close-on-exec ioctls: `FIOCLEX`, `FIONCLEX`.
- Hole/data seeking ioctls: `FIOSEEKDATA`, `FIOSEEKHOLE`.
- Readiness/queue ioctls: `FIONREAD`, `FIONWRITE`, `FIONSPACE`.
- Nonblocking/async/owner ioctls: `FIONBIO`, `FIOASYNC`, `FIOSETOWN`, `FIOGETOWN`.
- Block mapping: `OFIOGETBMAP`, `FIOGETBMAP`, alias `FIBMAP`.

## Dependencies And Integration
Uses ioctl command encoding and `off_t`/`daddr_t`. Vnode fileops and device/socket code implement relevant commands.

## Risks And Edge Cases
- `OFIOGETBMAP` preserves old 32-bit block-number ABI.
- `FIOSEEKDATA`/`FIOSEEKHOLE` rely on filesystem support for sparse file knowledge.

## Filesystem Relevance
High. Provides generic file ioctls, including hole/data and block mapping queries.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/filio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/flashio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/flashio.h

Read completely: 118 lines.

## Purpose
Defines user/kernel ioctl ABI for flash memory devices.

## Main Interfaces
- Status/type enums: `FLASH_ERASE_DONE`, `FLASH_ERASE_FAILED`, `FLASH_TYPE_UNKNOWN`, `FLASH_TYPE_NOR`, `FLASH_TYPE_NAND`.
- Types: `flash_off_t`, `flash_size_t`, `flash_addr_t`.
- Ioctl payloads: `flash_erase_params`, `flash_badblock_params`, `flash_info_params`, `flash_dump_params`.
- Commands: `FLASH_ERASE_BLOCK`, `FLASH_DUMP`, `FLASH_GET_INFO`, `FLASH_BLOCK_ISBAD`, `FLASH_BLOCK_MARKBAD`.

## Dependencies And Integration
Uses `sys/ioctl.h`; includes kernel/standalone or user integer/boolean types depending on context.

## Risks And Edge Cases
- `flash_dump_params` carries a user buffer pointer across ioctl ABI.
- Bad-block state is meaningful mainly for NAND-like media.
- Offset/size types are fixed-width for ABI stability.

## Filesystem Relevance
Moderate. Supports flash media operations underneath flash filesystems or block abstractions.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/flashio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/float_ieee754.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/float_ieee754.h

Read completely: 159 lines.

## Purpose
Supplies IEEE-754 `float.h` constants for machine-dependent `float.h` headers.

## Main Interfaces
- `_FLOAT_IEEE754`.
- `FLT_ROUNDS` via `__flt_rounds()`.
- Conditional `FLT_EVAL_METHOD`.
- GCC builtin-backed constants for `FLT_*` and `DBL_*`, with fallback literal definitions.
- Default `LDBL_*` definitions matching double precision when the machine header has not supplied extended precision.
- `DECIMAL_DIG` when visible by standards/profile macros.

## Dependencies And Integration
Includes cdefs and feature-test macros; intended to be included by a port's `float.h`, not used standalone.

## Risks And Edge Cases
- Long double defaults to double unless machine-specific header defines otherwise.
- Standards visibility controls `FLT_EVAL_METHOD` and `DECIMAL_DIG`.
- Older compiler fallback constants must match IEEE-754 assumptions.

## Filesystem Relevance
Low. General ABI/math support; no direct filesystem logic.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/float_ieee754.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fstrans.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fstrans.h

Read completely: 73 lines.

## Purpose
Declares filesystem transaction and suspension APIs plus copy-on-write callback registration.

## Main Interfaces
- Suspend control flags: `SUSPEND_SUSPEND`, `SUSPEND_RESUME`.
- States: `FSTRANS_NORMAL`, `FSTRANS_SUSPENDED`, `FSTRANS_SUSPENDING`.
- Transaction APIs: `fstrans_init`, `fstrans_lwp_dtor`, `fstrans_start`, `fstrans_start_nowait`, `fstrans_start_lazy`, `fstrans_done`, `fstrans_held`, `fstrans_is_owner`.
- Mount lifecycle/state: `fstrans_mount`, `fstrans_unmount`, `fstrans_setstate`, `fstrans_getstate`.
- COW hooks: `fscow_establish`, `fscow_disestablish`, `fscow_run`.
- Public suspend/resume: `vfs_suspend`, `vfs_resume`.

## Dependencies And Integration
Includes `sys/mount.h`; implemented by VFS transaction code and used by filesystem operations, unmount, suspension, and buffer COW paths.

## Risks And Edge Cases
- Callers must pair `fstrans_start` and `fstrans_done`.
- Lazy/nowait starts differ during suspension.
- COW callbacks run in buffer write contexts and must obey locking/lifetime constraints.

## Filesystem Relevance
High. It is the public interface for safe filesystem suspension and transaction bracketing.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fstrans.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fstypes.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/fstypes.h

Read completely: 299 lines.

## Purpose
Defines filesystem IDs, file handles, mount flags, exported/internal flag descriptions, visibility masks, and sync wait modes.

## Main Interfaces
- `fsid_t`.
- Kernel file handles: `struct fid`, `struct fhandle`, `fhandle_t`, `FHANDLE_SIZE_*`, `FHANDLE_*` helpers.
- Basic mount flags: `MNT_RDONLY`, `MNT_SYNCHRONOUS`, `MNT_NOEXEC`, `MNT_NOSUID`, `MNT_NODEV`, `MNT_UNION`, `MNT_ASYNC`, `MNT_RELATIME`, `MNT_DISCARD`, `MNT_EXTATTR`, `MNT_LOG`, `MNT_NOATIME`, `MNT_AUTOMOUNTED`, `MNT_SOFTDEP`, etc.
- Export flags: `MNT_EXRDONLY`, `MNT_EXPORTED`, `MNT_DEFEXPORTED`, `MNT_EXPORTANON`, `MNT_EXKERB`, `MNT_EXNORESPORT`, `MNT_EXPUBLIC`.
- Internal flags: `MNT_LOCAL`, `MNT_QUOTA`, `MNT_ROOTFS`; `IMNT_*`.
- Masks/lists: `MNT_BASIC_FLAGS`, `MNT_VISFLAGMASK`, `MNT_OP_FLAGS`, `__MNT_FLAG_BITS`, `__IMNT_FLAG_BITS`.
- Wait modes: `MNT_WAIT`, `MNT_NOWAIT`, `MNT_LAZY`.

## Dependencies And Integration
Used by mount, statvfs, export/NFS filehandle code, VFS sync/unmount, and filesystem flag parsing/display.

## Risks And Edge Cases
- The header warns flags are not in numeric order and new flags should reuse unused bits.
- Some bits are shared/synonymous, such as `MNT_EXKERB` and `MNT_POSIX1EACLS`.
- Filehandle size is variable but bounded by max/min compatibility constants.

## Filesystem Relevance
High. Defines core mount and filehandle ABI/state used by VFS and filesystems.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/fstypes.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/futex.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/futex.h

Read completely: 184 lines.

## Purpose
Defines NetBSD's Linux-compatible futex ABI plus robust futex metadata and kernel routines.

## Main Interfaces
- Commands: `FUTEX_WAIT`, `WAKE`, `FD`, `REQUEUE`, `CMP_REQUEUE`, `WAKE_OP`, PI and bitset variants.
- Flags: `FUTEX_PRIVATE_FLAG`, `FUTEX_CLOCK_REALTIME`, `FUTEX_CMD_MASK`.
- Wake-op encoding: `FUTEX_OP`, masks, operations, comparison operators.
- Robust futex word bits: `FUTEX_WAITERS`, `FUTEX_OWNER_DIED`, `FUTEX_SYNCOBJ_*`, `FUTEX_TID_MASK`, `FUTEX_BITSET_MATCH_ANY`.
- Robust-list ABI offsets and sizes.
- Optional libc-private robust-list structs.
- Kernel routines: `futex_robust_head_lookup`, `futex_release_all_lwp`, `do_futex`, `futex_sys_init`, `futex_sys_fini`.

## Dependencies And Integration
Includes `sys/timespec.h`. Integrates with LWP lifecycle and Linux-compat synchronization behavior.

## Risks And Edge Cases
- Robust futex ABI is specified as three longwords and has separate 32-bit size.
- `FUTEX_SYNCOBJ_*` reserves high TID bits, reducing max encoded thread id.
- PI futex entries are distinguished by the low bit of list entries.

## Filesystem Relevance
Low direct relevance. It is process synchronization infrastructure, not filesystem code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/futex.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gcq.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/gcq.h

Read completely: 463 lines.

## Purpose
Implements generic intrusive circular queues with inline operations, merge support, typed container recovery, and traversal/dequeue macros.

## Main Interfaces
- Structures: `struct gcq`, `struct gcq_head`.
- Initializers: `GCQ_INIT`, `GCQ_INIT_HEAD`, `gcq_init`, `gcq_init_head`.
- State helpers: `gcq_onlist`, `gcq_empty`, `gcq_linked`.
- Insertion/removal/merge: `gcq_insert_after`, `gcq_insert_before`, `gcq_insert_head`, `gcq_insert_tail`, `gcq_tie`, `gcq_merge`, `gcq_remove`, `gcq_clear`, `gcq_remove_all`.
- Container macro: `GCQ_ITEM`.
- Dequeue/get macros for first/last/next/prev, typed and conditional variants.
- Iteration macros: `GCQ_FOREACH*`, reverse, safe-next, read-only, dequeueing, typed variants.
- Search macros: `GCQ_FIND*`.

## Dependencies And Integration
Usable in kernel or userland testing; depends on assertion support and standard integer/offset types. Generic infrastructure for subsystems needing intrusive queues.

## Risks And Edge Cases
- Items must be initialized before insertion; assertions check self-linked state.
- Traversal after removal requires correct safe iteration macros.
- Some conditional helper macros reference `fn`/`var` in ways that look fragile or possibly erroneous.
- `GCQ_FOREACH_RO_TYPED` uses `gcq_lined`, likely a typo for `gcq_linked`.

## Filesystem Relevance
Indirect. Generic kernel data-structure support that filesystem/block code could use.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gcq.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gennameih.awk -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/gennameih.awk

Read completely: 96 lines.

## Purpose
Generates `namei.h` and `rump_namei.h` from `namei.src`, adding prefixed variants of `NAMEIFL` flags.

## Main Interfaces
- `getrcsid(idstr)`: extracts RCS id content.
- `printheader(outfile)`: writes generated-file warning and provenance.
- `BEGIN`: sets script version, output files `namei.h` and `../rump/include/rump/rump_namei.h`.
- First input line becomes source file header.
- `NAMEIFL` lines are converted into `#define` lines and remembered as `NAMEI_` flags.
- `END`: appends `NAMEI_` defines to `namei.h` and `RUMP_` defines to rump header.

## Dependencies And Integration
Used by the build process in `src/sys/sys` for namei flag header generation.

## Risks And Edge Cases
- Output paths are relative to the working directory where awk is run.
- Field parsing with `-F` relies on the source line structure.
- Generated headers must remain synchronized with `namei.src`.

## Filesystem Relevance
High. `namei` is central pathname lookup infrastructure for VFS.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gennameih.awk -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gmon.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/gmon.h

Read completely: 154 lines.

## Purpose
Defines kernel/user profiling data structures and sysctl identifiers for `gmon` profiling output.

## Main Interfaces
- `struct gmonhdr`: profiling file header.
- `GMONVERSION`.
- `HISTCOUNTER`, `HISTFRACTION`, `HASHFRACTION`, `ARCDENSITY`, `MINARCS`, `MAXARCS`.
- `struct tostruct`, `struct rawarc`, `struct gmonparam`.
- `_gmonparam`.
- Profiling states: `GMON_PROF_ON`, `BUSY`, `ERROR`, `OFF`.
- Sysctl selectors: `GPROF_STATE`, `GPROF_COUNT`, `GPROF_FROMS`, `GPROF_TOS`, `GPROF_GMONPARAM`, `GPROF_PERCPU`.

## Dependencies And Integration
Includes machine profiling definitions. Used by profiling instrumentation and kernel sysctl export.

## Risks And Edge Cases
- Arc and histogram sizing trades memory for profiling granularity.
- `MAXARCS` is tied to `HISTCOUNTER` width.

## Filesystem Relevance
Low direct relevance. Profiling can measure filesystem code but does not implement filesystem behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gmon.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gpio.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/gpio.h

Read completely: 151 lines.

## Purpose
Defines the GPIO user ioctl ABI, pin configuration flags, interrupt flags, and compatibility structures.

## Main Interfaces
- Pin states: `GPIO_PIN_LOW`, `GPIO_PIN_HIGH`.
- `GPIOMAXNAME`.
- Configuration flags: input/output/inout, open-drain, push-pull, tristate, pull-up/down, inversion, user access, pulsate, alternate functions.
- Interrupt flags and masks: edge/level modes, `GPIO_INTR_MPSAFE`.
- Structures: `gpio_info`, `gpio_req`, `gpio_set`, `gpio_attach`.
- Ioctls: `GPIOINFO`, `GPIOSET`, `GPIOUNSET`, `GPIOREAD`, `GPIOWRITE`, `GPIOTOGGLE`, `GPIOATTACH`.
- `COMPAT_50` old structs and ioctls.

## Dependencies And Integration
Uses ioctl encoding and time header. Consumed by gpio device drivers and userland tools.

## Risks And Edge Cases
- Compatibility ioctls preserve old ABI.
- Pin names are fixed-size buffers.
- Hardware capabilities and requested flags must be validated by drivers.

## Filesystem Relevance
Low. Device-control ABI, not filesystem code.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/gpio.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/hash.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/hash.h

Read completely: 106 lines.

## Purpose
Provides generic 32-bit hash helpers for buffers and strings, with optional machine overrides, and declares MurmurHash2.

## Main Interfaces
- Initial seeds: `HASH32_BUF_INIT`, `HASH32_STR_INIT`.
- Inline `hash32_buf`.
- Inline `hash32_str`.
- Inline `hash32_strn`.
- Declaration: `murmurhash2`.

## Dependencies And Integration
Includes `sys/types.h` and optional `machine/hash.h` when available. Generic hash support for kernel/user consumers.

## Risks And Edge Cases
- `hash32_strn` advances and tests the character before checking the decremented length, so zero-length behavior deserves care.
- Machine-specific implementations can override generic helpers.

## Filesystem Relevance
Moderate. Hash helpers can support name caches, lookup tables, and filesystem metadata structures.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/hash.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/heartbeat.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/heartbeat.h

Read completely: 75 lines.

## Purpose
Declares optional kernel heartbeat instrumentation hooks.

## Main Interfaces
- Kernel-only guard.
- Optional `opt_heartbeat.h`.
- With `HEARTBEAT`: `heartbeat_start`, `heartbeat`, `heartbeat_suspend`, `heartbeat_resume`, `heartbeat_dump`.
- Without `HEARTBEAT`: inline no-op start/heartbeat/suspend/resume.

## Dependencies And Integration
Kernel configuration option controls whether calls compile to real functions or no-ops.

## Risks And Edge Cases
- Header intentionally errors in userland.
- `heartbeat_dump` is declared only when `HEARTBEAT` is enabled.

## Filesystem Relevance
Low. General kernel diagnostic/liveness instrumentation.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/heartbeat.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/hook.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/hook.h

Read completely: 52 lines.

## Purpose
Declares a simple kernel hook-list facility for registering and running callbacks.

## Main Interfaces
- `HOOKNAMSIZ`.
- Opaque `khook_list_t` and `khook_t`.
- List lifecycle: `simplehook_create`, `simplehook_destroy`.
- Execution: `simplehook_dohooks`.
- Registration: `simplehook_establish`, `simplehook_disestablish`.
- Query: `simplehook_has_hooks`.

## Dependencies And Integration
Uses mutex types; callbacks take a single opaque pointer. Subsystems can expose hook points without custom list code.

## Risks And Edge Cases
- Disestablish accepts a mutex pointer, implying synchronization requirements around callback removal.
- Hook callback order and failure semantics depend on implementation.

## Filesystem Relevance
Moderate potential relevance. Filesystem or VFS subsystems can use hooks for lifecycle notifications.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/hook.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/idle.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/idle.h

Read completely: 37 lines.

## Purpose
Declares CPU idle loop and idle LWP creation functions.

## Main Interfaces
- Forward declaration `struct cpu_info`.
- `idle_loop(void *)`.
- `create_idle_lwp(struct cpu_info *)`.

## Dependencies And Integration
Scheduler/CPU initialization infrastructure consumes this header.

## Risks And Edge Cases
- Architecture and scheduler code must create one idle LWP per CPU as expected by the implementation.

## Filesystem Relevance
Low. General scheduler infrastructure.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/idle.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/idtype.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/idtype.h

Read completely: 62 lines.

## Purpose
Defines `idtype_t`, the ABI enum used by process-selection system calls.

## Main Interfaces
- `P_MYID`, `P_ALL`, `P_PID`, `P_LWPID`, `P_PPID`, `P_PGID`, `P_SID`, `P_CID`, `P_UID`, `P_GID`, `P_TASKID`, `P_PROJID`, `P_POOLID`, `P_ZONEID`, `P_CTID`, `P_CPUID`, `P_PSETID`.
- `_P_MAXIDTYPE` forces wide enum representation and leaves room for future values.

## Dependencies And Integration
Used by wait/signal/process-control APIs that select targets by identifier class.

## Risks And Edge Cases
- The header explicitly warns not to reorder or insert values in the middle because syscall ABI would break.
- Some Solaris-derived constants are not applicable to NetBSD but remain in the enum.

## Filesystem Relevance
Low. Process ABI support only indirectly affects filesystem operations.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/idtype.h -->

<!-- BEGIN FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ieee754.h -->
# File Research: sources/os/bsd/netbsd-src/sys/sys/ieee754.h

Read completely: 218 lines.

## Purpose
Defines bitfield layouts and helper unions for IEEE-754 single, double, and optional 128-bit long-double formats.

## Main Interfaces
- Precision constants: `SNG_EXPBITS`, `SNG_FRACBITS`, `DBL_EXPBITS`, `DBL_FRACHBITS`, `DBL_FRACLBITS`, optional `EXT_*`.
- Layout structs: `ieee_single`, `ieee_double`, optional `ieee_ext`, endian-dependent.
- Infinity/NaN exponents: `SNG_EXP_INFNAN`, `DBL_EXP_INFNAN`, optional `EXT_EXP_INFNAN`.
- Biases: `SNG_EXP_BIAS`, `DBL_EXP_BIAS`, optional `EXT_EXP_BIAS`.
- Unions: `ieee_single_u`, `ieee_double_u`, optional `ieee_ext_u`.
- Access macros and zero-fraction predicates.
- `EXT_TO_ARRAY32` for 128-bit long double fraction extraction.

## Dependencies And Integration
Includes machine endian definitions and expects machine headers to define long-double support when relevant.

## Risks And Edge Cases
- Bitfield layout is endian-dependent and compiler ABI-sensitive.
- 128-bit long double support appears only when `__HAVE_LONG_DOUBLE == 128`.
- `SNGU_ZEROFRAC_P`/`DBLU_ZEROFRAC_P` names test nonzero fraction despite “ZEROFRAC” wording.

## Filesystem Relevance
Low. General numeric ABI support; no direct filesystem behavior.
<!-- END FILE RESEARCH: sources/os/bsd/netbsd-src/sys/sys/ieee754.h -->