# sources/distributed-fs/openafs/src/config/param.x86_darwin_90.h

This platform header targets Darwin 9 on ppc and x86/x86_64 style builds. It extends the Darwin 8 configuration with `AFS_DARWIN90_ENV`, `AFS_CACHE_VNODE_PATH`, and `AFS_NEW_BKG`. Kernel builds define 64-bit client/I/O behavior, `AFS_NAMEI_ENV`, RX listener and timed sleep support, and Darwin kernel structure aliases.

Its important interfaces are preprocessor macros: architecture selectors `AFS_PPC_ENV`/`AFS_X86_ENV`, system names `ppc_darwin_90` and `x86_darwin_90`, endian macros, uio aliases, allocation wrappers, and `VATTR_NULL usr_vattr_null` in userspace. It includes `afs_sysnames.h` and defines `AFS_HAVE_FFS`.

Control flow is compile-time conditional branching between kernel and `UKERNEL`, then architecture branches. No runtime persistence exists. The file integrates with Darwin 9 kernel/user builds, OpenAFS syscall/pioctl code, vnode and uio consumers, and code that gates behavior on `AFS_CACHE_VNODE_PATH`. Risks include treating `__x86_64__` as `x86_darwin_90` instead of an amd64 sysname, legacy `AFS_VFS34` comments indicating unclear VFS assumptions, and duplicated macro definitions. Test signals are compile success under both `KERNEL` and `UKERNEL`, plus vnode path cache and RX listener/timed sleep regression coverage.
