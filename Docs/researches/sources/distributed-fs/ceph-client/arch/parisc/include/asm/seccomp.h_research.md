# sources/distributed-fs/ceph-client/arch/parisc/include/asm/seccomp.h

Purpose: connects PA-RISC to generic seccomp definitions.

Important APIs/types/functions: includes `asm-generic/seccomp.h` and exports the architecture audit/seccomp mode constants expected by generic code.

Control flow: syscall entry checks seccomp state through generic code after architecture syscall number/argument extraction.

State and persistence: seccomp filters persist in task state; this header adds no private state. Dependencies and integration: used by syscall tracing/audit and BPF seccomp.

Risks and test signals: generic mapping must agree with PA-RISC syscall ABI. Test seccomp selftests, audit arch values, and filtered syscall argument extraction.

Test signals: keep PA-RISC 32-bit and 64-bit defconfig build coverage, exercise boot under hardware or QEMU where available, and use sparse/objdump checks for ABI-sensitive layout, instruction, and relocation assumptions.
