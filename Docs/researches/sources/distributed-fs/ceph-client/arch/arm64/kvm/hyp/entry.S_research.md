# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/entry.S

## Purpose

This assembly file implements `__guest_enter()`, the low-level transition between hyp/host register context and guest register context, plus the common guest-exit save path.

## Important APIs, Types, And Functions

The exported symbol is `__guest_enter`. Important labels are `__guest_exit`, `__guest_exit_panic`, and `__guest_exit_restore_elr_and_panic`. It uses macros for callee-saved registers, `sp_el0`, loaded-vCPU tracking, MTE switching, pointer-authentication key switching, and exception-table SError recovery.

## Control Flow

Entry saves hyp callee-saved state and `sp_el0`, checks pending asynchronous exceptions, records the loaded vCPU, switches MTE/ptrauth state, restores guest registers, and executes `eret`. Exit stores guest registers back into `VCPU_CONTEXT`, restores hyp state, clears the loaded vCPU pointer, records RAS DISR state where supported, and returns an exception code possibly marked with pending SError.

## State And Persistence Behavior

It persists full guest GPR state, host hyp callee-saved state, guest/hyp `sp_el0`, ptrauth keys, MTE state, loaded-vCPU per-CPU state, and RAS DISR fault metadata.

## Dependencies And Integration Points

It is entered from hyp switch code and branches from vector code in `hyp-entry.S`. It integrates with `handle_exit.c`, ptrauth/MTE macros, RAS alternatives, and nVHE panic paths.

## Risks And Test Signals

Risks are register corruption, stale loaded-vCPU pointers, missing context-synchronization on deferred entry, ptrauth/MTE leakage, and SError window mishandling. Test signals include stress vCPU migration, async SError injection, ptrauth/MTE-enabled guests, and hyp panic paths that restore ELR before panicking.
