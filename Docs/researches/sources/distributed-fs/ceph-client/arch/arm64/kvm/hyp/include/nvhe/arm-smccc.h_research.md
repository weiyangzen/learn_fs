# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/arm-smccc.h

## Purpose

This nVHE header wraps SMCCC SMC calls so EL2 tracing records a hyp exit and re-entry around firmware calls.

## Important APIs, Types, And Functions

Macros are `hyp_smccc_1_1_smc(...)` and `hyp_smccc_1_2_smc(...)`.

## Control Flow

Each macro emits `trace_hyp_exit(NULL, HYP_REASON_SMC)`, performs the underlying SMCCC SMC call, then emits `trace_hyp_enter(NULL, HYP_REASON_SMC)`.

## State And Persistence Behavior

No persistent state is owned here, but tracing side effects may reserve and commit hyp trace entries.

## Dependencies And Integration Points

It depends on `linux/arm-smccc.h` and `asm/kvm_hypevents.h`, and is used by nVHE code paths making firmware calls.

## Risks And Test Signals

Risks are trace recursion or missing enter/exit balance around SMC. Test signals are nVHE trace streams showing SMC intervals and firmware calls preserving SMCCC results.
