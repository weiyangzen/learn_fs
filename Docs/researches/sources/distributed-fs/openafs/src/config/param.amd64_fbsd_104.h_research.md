# sources/distributed-fs/openafs/src/config/param.amd64_fbsd_104.h

Purpose: FreeBSD platform overlay for OpenAFS, selected during `param.h` generation for `param.amd64_fbsd_104.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It relies on `param.generic_fbsd.h` for shared FreeBSD kernel and UKERNEL definitions, while this overlay contributes the concrete sysname, version feature macros, and architecture-specific pointer/fake-open settings.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_fbsd_104", `SYS_NAME_ID` = SYS_NAME_ID_amd64_fbsd_104, `AFS_SYSCALL` = not defined, endian mode = not explicit, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_FBSD101_ENV, AFS_FBSD102_ENV, AFS_FBSD103_ENV, AFS_FBSD104_ENV, AFS_USR_FBSD101_ENV, AFS_USR_FBSD102_ENV, AFS_USR_FBSD103_ENV, AFS_USR_FBSD104_ENV, AFS_X86_FBSD101_ENV, AFS_X86_FBSD102_ENV, and feature macros including none. It contains 38 source lines and 18 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
