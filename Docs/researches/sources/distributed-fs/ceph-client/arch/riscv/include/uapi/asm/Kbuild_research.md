<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/Kbuild -->
# sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/Kbuild

Purpose: Lists RISC-V UAPI headers exported or generated for userspace.

Important APIs/types/functions: Uses Kbuild `generic-y`/`generated-y` style declarations.

Control flow: Header installation tooling reads this file during `headers_install`.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with kernel UAPI header export and libc/toolchain builds.

Risks: Missing entries hide required ABI headers from userspace.

Test signals: `make headers_install`, libc build smoke tests, and UAPI header checks.

Source read size: 3 lines, 85 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/uapi/asm/Kbuild -->
