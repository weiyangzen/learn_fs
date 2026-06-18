# sources/distributed-fs/openafs/src/config/param.arm64_linux26.h

Purpose: Linux architecture parameter header for OpenAFS, selected during `param.h` generation for `param.arm64_linux26.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It selects the Linux architecture environment, syscall number used by afsd/kernel integration, endian setting, and UKERNEL-visible sysname identity.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "arm64_linux26", `SYS_NAME_ID` = SYS_NAME_ID_arm64_linux26, `AFS_SYSCALL` = not defined, endian mode = little-endian, environment macros including AFS_64BITPOINTER_ENV, AFS_64BITUSERPOINTER_ENV, AFS_ARM64_LINUX_ENV, AFS_MAXVCOUNT_ENV, and feature macros including AFS_LINUX_64BIT_KERNEL. It contains 38 source lines and 11 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
