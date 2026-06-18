# sources/distributed-fs/openafs/src/config/param.i386_dfbsd_23.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.i386_dfbsd_23.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_dfbsd_23", `SYS_NAME_ID` = SYS_NAME_ID_i386_dfbsd_23, `AFS_SYSCALL` = 339, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_DFBSD22_ENV, AFS_DFBSD23_ENV, AFS_DFBSD_ENV, AFS_ENV, AFS_FAKEOPEN_ENV, AFS_GREEDY43_ENV, AFS_NAMEI_ENV, AFS_USR_DFBSD22_ENV, AFS_USR_DFBSD23_ENV, AFS_USR_DFBSD_ENV, AFS_VFSINCL_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS, AFS_SYSCALL. It contains 153 source lines and 65 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
