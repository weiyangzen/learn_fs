# sources/distributed-fs/ceph-client/arch/parisc/include/asm/signal.h

Purpose: exposes PA-RISC signal ABI definitions to kernel code.

Important APIs/types/functions: includes `uapi/asm/signal.h` and, for kernel builds, `asm/sigcontext.h`.

Control flow: signal delivery and return code use the included constants and context layouts to build user-visible frames.

State and persistence: signal masks and frames persist in task/user-stack state. Dependencies and integration: signal core, compat signal handling, ptrace, and uapi headers.

Risks and test signals: ABI mismatch breaks signal handlers. Test signal selftests, header install, and 32/64-bit signal frame compatibility.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
