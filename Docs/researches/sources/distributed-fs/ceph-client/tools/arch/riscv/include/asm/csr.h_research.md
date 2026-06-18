# sources/distributed-fs/ceph-client/tools/arch/riscv/include/asm/csr.h

## Purpose
Comprehensive RISC-V CSR and status-bit header for tools.

## Important APIs, Types, and Functions
Defines status bits, SATP/HGATP fields, exception and interrupt causes, PMP flags, hypervisor/AIA/envcfg/stateen masks, CSR numeric addresses for user/supervisor/virtual supervisor/hypervisor/machine/vector registers, mode-dependent aliases, interrupt enable bits, and inline CSR helpers `csr_swap()`, `csr_read()`, `csr_write()`, `csr_read_set()`, `csr_set()`, `csr_read_clear()`, and `csr_clear()`.

## Control Flow, State, and Persistence
Macros choose M-mode versus S-mode aliases at compile time. Inline helpers emit `csrr*` assembly and return old values where appropriate. No persistent storage is kept except the targeted hardware CSR side effects.

## Dependencies and Integration Points
Depends on `linux/bits.h`, `_AC/_ULL` style constants, and compiler support for RISC-V CSR inline assembly. Integrated with low-level RISC-V tools, perf, KVM, and vDSO-adjacent code.

## Risks and Test Signals
Risks include spec drift for AIA/hypervisor/vector CSRs, XLEN-dependent masks, wrong mode aliases, and dangerous writes through generic helpers. Test signals are riscv32/riscv64 builds, CSR encoding compile tests, and runtime smoke tests for read/set/clear on safe CSRs.
