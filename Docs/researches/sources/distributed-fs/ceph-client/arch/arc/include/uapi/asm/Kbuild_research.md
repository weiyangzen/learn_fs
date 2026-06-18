# sources/distributed-fs/ceph-client/arch/arc/include/uapi/asm/Kbuild

UAPI export manifest for ARC asm headers. It marks unistd_32.h as syscall-generated and selects generic ucontext.h. Control flow is header-install and syscall-header generation during kernel build. State is generated/exported userspace header set. Dependencies are scripts/headers_install, syscall-y handling, and generic UAPI ucontext. Risks are missing ABI headers during userspace header export or stale syscall generation. Test signals are `make headers_install`, libc/uapi consumers, and syscall table generation.
