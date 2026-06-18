# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/exception.c

## Purpose

This file emulates exception entry into AArch64 EL1/EL2 or AArch32 modes for pending KVM-injected exceptions and implements `__kvm_adjust_pc()`.

## Important APIs, Types, And Functions

Core helpers are `enter_exception64()`, `get_except32_cpsr()`, `enter_exception32()`, `kvm_inject_exception()`, and `__kvm_adjust_pc()`. It also has VHE/nVHE-specific sysreg read/write wrappers and banked AArch32 SPSR writers.

## Control Flow

When `PENDING_EXCEPTION` is set, `__kvm_adjust_pc()` calls `kvm_inject_exception()`, which selects AArch32 UND/IABT/DABT or AArch64 EL1/EL2 sync/IRQ/SError injection. Exception entry saves the old PC/PSTATE into the target ELR/SPSR, computes vector offset from source and target mode, updates PC to VBAR plus offset plus type, and constructs new PSTATE. Otherwise, `INCREMENT_PC` causes `kvm_skip_instr()`.

## State And Persistence Behavior

The code mutates PC, CPSR/PSTATE, ELR/SPSR registers, ESR/FAR-related exception state indirectly, AArch32 banked SPSRs/LRs, and vCPU flags. It preserves old state in architecture-defined return registers.

## Dependencies And Integration Points

It is called by host and hyp paths through `__kvm_adjust_pc`, and by nested exception injection before reloading a virtual EL2 context. It depends on VHE/nVHE sysreg access conventions, MTE/RAS feature checks, and AArch32 compatibility state.

## Risks And Test Signals

Risks are incorrect vector offsets, wrong PSTATE masking, writing the wrong SPSR under VHE, failing to clear pending flags, and AArch32 return-address errors. Test signals include injected undefined/data/prefetch aborts, EL2 nested sync/IRQ/SError, MTE TCO behavior, PAN/SSBS inheritance, and PC increment after emulated traps.
