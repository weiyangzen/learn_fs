# sources/distributed-fs/openafs/src/config/param.generic_fbsd.h

Purpose: shared platform configuration for OpenAFS, selected during `param.h` generation for `param.generic_fbsd.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It provides common platform definitions included by thinner version or architecture headers.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = not defined, `SYS_NAME_ID` = not defined, `AFS_SYSCALL` = 339, endian mode = little-endian, environment macros including AFS_64BIT_IOPS_ENV, AFS_ENV, AFS_FBSD_ENV, AFS_GREEDY43_ENV, AFS_NAMEI_ENV, AFS_USR_FBSD_ENV, AFS_VFSINCL_ENV, AFS_VFS_ENV, AFS_X86_ENV, AFS_X86_FBSD_ENV, AFS_X86_XBSD_ENV, AFS_XBSD_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_FBSD_NET_FOREACH, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_MINCHANGE, AFS_NONFSTRANS. It contains 211 source lines and 64 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
