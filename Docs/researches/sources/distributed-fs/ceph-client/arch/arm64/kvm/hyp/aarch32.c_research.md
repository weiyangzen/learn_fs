# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/aarch32.c

## Purpose

This hyp file supports AArch32 guest instruction emulation by validating conditional execution and advancing Thumb/ARM PCs, including ITSTATE maintenance.

## Important APIs, Types, And Functions

The exported helpers are `kvm_condition_valid32()` and `kvm_skip_instr32()`. Internal data includes the `cc_map[16]` NZCV condition lookup table and `kvm_adjust_itstate()`.

## Control Flow

For trap classes that may be conditional, `kvm_condition_valid32()` gets the condition from ESR or Thumb IT state, evaluates it against CPSR NZCV, and tells higher-level exit code whether the trapped instruction should execute. `kvm_skip_instr32()` advances PC by 2 for 16-bit Thumb traps or 4 otherwise, then advances ITSTATE.

## State And Persistence Behavior

The file mutates `vcpu->arch.ctxt.regs.pc` and CPSR IT bits. It reads PSTATE/CPSR, trap class, trapped instruction length, and condition code.

## Dependencies And Integration Points

It is used by generic PC-adjust helpers in `hyp/adjust_pc.h` and host exit handling. It depends on arm64 KVM emulate helpers and AArch32 PSR definitions.

## Risks And Test Signals

Risks include wrong ITSTATE advancement, Thumb instruction length mistakes, and conditional traps incorrectly treated as executed. Test signals are AArch32 guests running CP15/CP14/SVC/FP trapped instructions inside IT blocks and condition-failed traps advancing without side effects.
