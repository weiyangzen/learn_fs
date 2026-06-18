# sources/distributed-fs/ceph-client/arch/x86/include/asm/nospec-branch.h

## Purpose
Defines x86 speculative-execution mitigation macros and helpers for retpolines, RSB stuffing, return thunks, IBPB/IBRS control, call-depth tracking, branch-history clearing, and CPU buffer clearing.

## Important APIs, Types, And Functions
Important macros include `RET_DEPTH_*`, `RSB_RET_STUFF_LOOPS`, `__FILL_RETURN_BUFFER`, `__FILL_ONE_RETURN`, assembler `JMP_NOSPEC`, `CALL_NOSPEC`, `FILL_RETURN_BUFFER`, `UNTRAIN_RET*`, `CLEAR_CPU_BUFFERS`, `CLEAR_BRANCH_HISTORY*`, and C `CALL_NOSPEC`/`THUNK_TARGET`. Types include `retpoline_thunk_t`, `its_thunk_t`, `enum spectre_v2_mitigation`, `enum spectre_v2_user_mitigation`, and `enum ssb_mitigation`. Helpers include `alternative_msr_write()`, `indirect_branch_prediction_barrier()`, `firmware_restrict_branch_speculation_start/end()`, `spec_ctrl_current()`, `update_spec_ctrl_cond()`, `x86_clear_cpu_buffers()`, and `x86_idle_clear_cpu_buffers()`.

## Control Flow
Assembler paths use alternatives to patch mitigation sequences depending on CPU features. Indirect branches route through thunks under retpoline. Return paths can stuff RSB entries, untrain predictors, issue IBPB, or account call depth. Firmware calls temporarily enable IBRS/IBPB. VERW clears CPU buffers when the static key or feature requires it.

## State And Persistence
State includes per-CPU call-depth counters, debug counters, `x86_spec_ctrl_base`, per-CPU current SPEC_CTRL, static keys for mitigation policy, and thunk function pointers. Hardware predictor and buffer state is transient.

## Dependencies And Integration Points
Depends on alternatives, cpufeatures, MSR definitions, objtool annotations, unwind hints, percpu data, and segment selectors. It integrates with entry code, context switch, VM exit, firmware calls, idle, KVM, and compiler-generated retpoline expectations.

## Risks And Edge Cases
Mitigation code is security-critical and instruction-layout-sensitive. Missing annotations can fail objtool validation. Wrong feature gating can leave speculation windows or impose unnecessary overhead. Register clobbers and stack adjustments in RSB stuffing must be exact.

## Test Signals
Objtool noinstr validation, mitigation sysfs tests, Spectre/MDS/TSA mitigation boot logs, KVM VM-exit tests, firmware-call paths, retpoline builds, call-depth debug counters, and CPU-vendor matrix coverage are essential.
