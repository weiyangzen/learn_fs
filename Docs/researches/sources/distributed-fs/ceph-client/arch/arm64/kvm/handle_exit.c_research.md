# sources/distributed-fs/ceph-client/arch/arm64/kvm/handle_exit.c

## Purpose

This file is the host-side dispatcher for exceptions returned from arm64 guest execution. It translates hyp exit codes and ESR exception classes into KVM handling, userspace exits, nested reinjection, or fatal nVHE panic reporting.

## Important APIs, Types, And Functions

The main APIs are `handle_exit()`, `handle_exit_early()`, and `nvhe_hyp_panic_handler()`. Trap handlers include `handle_hvc()`, `handle_smc()`, `kvm_handle_fpasimd()`, `kvm_handle_wfx()`, `kvm_handle_guest_debug()`, `handle_sve()`, `kvm_handle_ptrauth()`, `kvm_handle_eret()`, `handle_svc()`, `kvm_handle_gcs()`, and `handle_other()`. `arm_exit_handlers[]` maps ESR ECs to these functions.

## Control Flow

`handle_exit_early()` consumes pending SError before preemption where required. `handle_exit()` strips the exception code and returns to the guest for IRQ/SError, invokes trap handling for sync traps, reports fail-entry for hyp shutdown or illegal return, and emits internal errors for unsupported classes. Trap handling checks conditional execution first, then dispatches by ESR EC. Nested guests often receive reinjected sync exceptions instead of local handling.

## State And Persistence Behavior

The code updates vCPU stats, PC, run exit reason, debug payloads, flags, nested exception state, and panic diagnostics. WFx may set `IN_WFIT`; SMC increments PC before SMCCC handling. Panic handling does not return and exposes hyp offsets for debugging.

## Dependencies And Integration Points

It integrates with SMCCC handling, nested helpers from `emulate-nested.c`, guest abort/sysreg handlers, GIC and timer paths, debug monitor state, RAS helpers, UBSAN/CFI reporting, and nVHE stacktrace dumping.

## Risks And Test Signals

Risks include wrong PC advancement for SMC/HVC/SError replay, forwarding traps into L1 incorrectly, losing debug FAR or single-step state, mishandling WFxT deadlines and offsets, and incomplete panic decoding. Test signals include SMCCC calls, nested HVC/SMC/ERET traps, WFE/WFI/ WFIT stats, guest debug exits, RAS SError injection, GCS UNDEF, and controlled hyp BUG/CFI/UBSAN panic reports.
