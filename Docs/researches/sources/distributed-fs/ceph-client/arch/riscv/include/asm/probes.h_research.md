<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/probes.h -->
# sources/distributed-fs/ceph-client/arch/riscv/include/asm/probes.h

Purpose: Defines RISC-V architecture interfaces for `probes.h`.

Important APIs/types/functions: The file is a small architecture header whose exported macros/types are consumed by nearby RISC-V kernel code.

Control flow: Control flow is compile-time or inline only, with runtime behavior provided by implementation files.

State and persistence: No substantial private state is stored in this header.

Dependencies and integration points: Integrates with the surrounding RISC-V architecture subsystem and generic Linux kernel APIs.

Risks: The main risk is ABI or include-contract drift with its implementation users.

Test signals: Architecture build coverage and subsystem-specific runtime tests.

Source read size: 24 lines, 563 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/include/asm/probes.h -->
