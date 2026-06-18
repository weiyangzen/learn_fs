<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/Kbuild

Purpose: controls exported UAPI header generation for Xtensa. It marks `unistd_32.h` as generated and reuses generic `ucontext.h`.

Control flow is Kbuild header-install/generation logic rather than runtime execution. State is generated syscall header output and installed UAPI header set. Dependencies include architecture syscall tables and generic UAPI infrastructure. Integration points are `make headers_install`, libc header consumption, syscall table generation, and UAPI packaging. Risks are missing generated headers or accidentally exporting incompatible local headers. Test signals include `headers_install`, generated `unistd_32.h` presence, libc/toolchain builds, and UAPI header diff checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/xtensa/include/uapi/asm/Kbuild -->
