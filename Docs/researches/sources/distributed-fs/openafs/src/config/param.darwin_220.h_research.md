# sources/distributed-fs/openafs/src/config/param.darwin_220.h

Purpose: Darwin/macOS platform configuration for OpenAFS, selected during `param.h` generation for `param.darwin_220.h`. It tells common OpenAFS kernel, user-space-kernel, and utility code which operating-system and architecture assumptions apply. It carries a richer Darwin kernel and UKERNEL feature matrix, including syscall/ioctl, vnode, locking, cache, and 64-bit-client assumptions for the named Darwin generation.

Important APIs/types/functions: this header exports preprocessor state, not functions. Key definitions are `SYS_NAME` = "amd64_darwin_220", `SYS_NAME_ID` = SYS_NAME_ID_amd64_darwin_220, `AFS_SYSCALL` = 230, endian mode = little-endian, environment macros including AFS_64BITUSERPOINTER_ENV, AFS_64BIT_ENV, AFS_64BIT_IOPS_ENV, AFS_ARM64_DARWIN_ENV, AFS_ARM_ENV, AFS_DARWIN100_ENV, AFS_DARWIN110_ENV, AFS_DARWIN120_ENV, AFS_DARWIN130_ENV, AFS_DARWIN140_ENV, AFS_DARWIN150_ENV, AFS_DARWIN160_ENV, and feature macros including AFS_64BIT_CLIENT, AFS_64BIT_SIZEOF, AFS_CACHE_VNODE_PATH, AFS_CLBYTES, AFS_DIRENT, AFS_GCPAGS, AFS_GLOBAL_SUNLOCK, AFS_HAVE_FFS, AFS_NEW_BKG, AFS_NONFSTRANS. It contains 193 source lines and 108 distinct `#define` names.

Control flow: there is no runtime control flow. Build logic concatenates or includes this header into generated `afs/param.h`; subsequent C files select platform-specific code paths with these macros. Conditional sections split kernel-only and `UKERNEL` userspace-kernel definitions where the source provides both.

State and persistence: no runtime state is stored. The definitions become persistent build identity in installed `param.h`, object files, kernel modules, and utilities compiled for the target sysname.

Dependencies and integration: integrates with `Makefile.in` `AFS_PARAM`/`AFS_PARAM_COMMON`, `afs_sysnames.h` ID constants, platform kernel headers, and shared OpenAFS subsystems such as VFS, namei, RX, cache, syscall/pioctl, and fstrace. Downstream code depends on these macros to choose ABI layouts, pointer widths, allocator calls, UIO segments, and syscall numbers.

Risks and test signals: risks include stale OS-version feature macros, mismatched `SYS_NAME_ID`, wrong pointer-width or endian flags, duplicate kernel/UKERNEL values, and syscall-slot drift. Test signals are compiling the target sysname, generating `param.h`, building libafs or Windows/user utilities for that platform, and smoke-testing afsd startup, pioctl/syscall setup, cache initialization, and fstrace/RX behavior where applicable.
