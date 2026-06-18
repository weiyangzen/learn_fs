# sources/distributed-fs/openafs/src/config/param.i386_nbsd50.h

Purpose: NetBSD platform selector for OpenAFS, selected during `param.h` generation for `param.i386_nbsd50.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. For newer NetBSD variants this is a thin selector that layers architecture and sysname macros over common NetBSD/XBSD definitions; older alpha/i386 NetBSD 1.5/1.6 headers also carry embedded UKERNEL compatibility definitions.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "i386_nbsd50", `SYS_NAME_ID` = SYS_NAME_ID_i386_nbsd50, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_X86_ENV, AFS_X86_XBSD_ENV, and feature macros including AFS_I386_PARAM_H. It contains 20 source lines and 6 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
