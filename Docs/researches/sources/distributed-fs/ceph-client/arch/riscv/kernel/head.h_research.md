# sources/distributed-fs/ceph-client/arch/riscv/kernel/head.h

Purpose: Declares early RISC-V boot helpers shared between boot assembly and C setup.

Important APIs/types/functions: Declares `setup_vm()`, `setup_vm_final()`, and early page-table or relocation symbols used by `head.S` and MM setup.

Control flow: No runtime logic is in the header. It establishes call contracts for early assembly to invoke C VM initialization.

State and persistence: No direct state; it names boot-time page table setup interfaces that mutate global MMU state.

Dependencies and integration points: Integrates `head.S`, early MM code, KASLR/FDT boot logic, and final kernel page-table installation.

Risks and test signals: Prototype drift between assembly calls and C definitions can fail at link time or boot. Test all RISC-V MMU build modes and early boot under QEMU.
