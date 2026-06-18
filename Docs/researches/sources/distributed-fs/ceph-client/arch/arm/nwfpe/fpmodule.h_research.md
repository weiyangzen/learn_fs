# sources/distributed-fs/ceph-client/arch/arm/nwfpe/fpmodule.h

## Purpose
Defines numeric indices for ARM saved user registers used by NWFPE helper code.

## Important APIs, Types, And Functions
Defines `REG_R0` through `REG_R10`, `REG_FP`, `REG_IP`, `REG_SP`, `REG_LR`, `REG_PC`, `REG_CPSR`, and `REG_ORIG_R0`. `REG_R9` is duplicated with the same value.

## Control Flow
No runtime flow. Constants are consumed by inline register accessors and CPDT/CPRT logic.

## State, Dependencies, And Integration
No state. Integrates with `struct pt_regs::uregs[]` layout expected by ARM ptrace/register conventions and with `fpmodule.inl` read/write helpers.

## Risks And Test Signals
Risks are index drift from ARM `pt_regs` layout, duplicated constants hiding edits, and PC/CPSR confusion. Test signals are conversion/transfer tests that read/write general registers, PC-relative FP transfers, and CPSR condition-code comparisons.
