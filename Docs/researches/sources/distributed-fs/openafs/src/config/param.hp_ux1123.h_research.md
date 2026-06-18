# sources/distributed-fs/openafs/src/config/param.hp_ux1123.h

Purpose: HP-UX platform configuration for OpenAFS, selected during `param.h` generation for `param.hp_ux1123.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It defines both kernel and, where present, user-space-kernel settings for HP-UX, including syscall slot 48, big-endian layout, VFS/UIO constants, allocator mappings, and HP-UX generation flags.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "hp_ux1123", `SYS_NAME_ID` = SYS_NAME_ID_hp_ux1123, `AFS_SYSCALL` = 48, endian mode = big-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_HPUX100_ENV, AFS_HPUX101_ENV, AFS_HPUX102_ENV, AFS_HPUX110_ENV, AFS_HPUX1111_ENV, AFS_HPUX1122_ENV, AFS_HPUX1123_ENV, AFS_HPUX90_ENV, AFS_HPUX_64BIT_ENV, AFS_HPUX_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_HAVE_STATVFS, AFS_KALLOC, AFS_KFREE, AFS_MINCHANGE. It contains 101 source lines and 44 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
