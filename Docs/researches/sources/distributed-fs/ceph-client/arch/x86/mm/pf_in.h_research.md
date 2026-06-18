# sources/distributed-fs/ceph-client/arch/x86/mm/pf_in.h

## Purpose
`pf_in.h` defines the small mmiotrace fault-instruction decoding contract shared by the page-fault interception code and `pf_in.c`.

## Important APIs, Types, and Functions
`enum reason_type` describes how a faulting instruction relates to the traced MMIO region: `NOT_ME`, `NOTHING`, `REG_READ`, `REG_WRITE`, `IMM_WRITE`, and `OTHERS`. The declared functions are `get_ins_type()`, `get_ins_mem_width()`, `get_ins_reg_val()`, and `get_ins_imm_val()`.

## Control Flow and State
There is no runtime control flow or storage in the header. It fixes the classification vocabulary and decoder function signatures. `struct pt_regs` is used by declaration without being defined here, so includers must already have the appropriate architecture register context available.

## Dependencies and Integration Points
The header is local to x86 MM mmiotrace support and integrates with `pf_in.c` plus the mmiotrace fault handler that needs to decide whether a page fault represents an MMIO access to log or emulate.

## Risks and Test Signals
Risks are ABI drift between the enum meanings and mmiotrace callers, and missing includes if declarations are reused outside the existing path. Test signals are successful x86 builds with mmiotrace enabled and correct classification labels in mmiotrace output.
