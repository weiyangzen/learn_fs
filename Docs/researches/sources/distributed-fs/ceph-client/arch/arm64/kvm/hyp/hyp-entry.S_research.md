# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/hyp-entry.S

## Purpose

This assembly file defines the EL2 exception vectors used while running guests and the hardened vector variants used for Spectre mitigations.

## Important APIs, Types, And Functions

Key symbols are `__kvm_hyp_vector` and `__bp_harden_hyp_vecs`. Important local handlers are `el1_sync`, `el1_trap`, `el1_irq`, `el1_error`, `el2_sync`, `el2_error`, and generated invalid vectors. Macros include `save_caller_saved_regs_vect`, `restore_caller_saved_regs_vect`, `valid_vect`, `invalid_vect`, `hyp_ventry`, and `generate_vectors`.

## Control Flow

EL1 sync traps decode ESR EC, fast-return known SMCCC workaround HVCs, or branch to `__guest_exit` with `ARM_EXCEPTION_TRAP`. IRQ/FIQ and SError exits also branch to `__guest_exit`. Unexpected EL2 exceptions call `kvm_unexpected_el2_exception()` and retry via adjusted ELR or panic path. Hardened vector tables add ESB, BTI, BHB mitigation, optional SMC workaround, and indirect branch patch slots.

## State And Persistence Behavior

The file manipulates stack-saved caller registers, ESR/ELR/SPSR, vCPU pointer recovery, and exception return state. It does not own persistent data, but its vector table contents are patched by alternatives.

## Dependencies And Integration Points

It connects CPU exception vector entry to `entry.S`, `switch.h`, Spectre mitigation infrastructure, SMCCC workaround IDs, and vector branch patching.

## Risks And Test Signals

Risks include broken vector alignment/preamble length, missed BTI/mitigation requirements, clobbered HVC registers, and invalid EL2 exception recovery loops. Test signals are HVC workaround fast paths, trap/IRQ/SError exits, Spectre vector patching, illegal exception return handling, and hyp panic on invalid vectors.
