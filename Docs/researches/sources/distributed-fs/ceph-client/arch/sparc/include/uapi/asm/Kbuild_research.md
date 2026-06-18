<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/Kbuild

Purpose: Declares generated UAPI syscall-number headers for SPARC.

Important APIs and control flow: `generated-y += unistd_32.h` and `generated-y += unistd_64.h` tell Kbuild to export generated syscall tables for 32-bit and 64-bit user ABI consumers.

State, dependencies, and risks: state is build-system metadata only. Dependencies are syscall table generation and UAPI header installation. Risks are missing generated headers breaking libc/kernel-header consumers or mismatching `unistd.h` includes. Test signals are `headers_install`, sparc32/sparc64 syscall header generation, and userspace compile checks using `asm/unistd.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/sparc/include/uapi/asm/Kbuild -->
