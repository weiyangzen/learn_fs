<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry.S -->
# sources/distributed-fs/ceph-client/arch/x86/entry/entry.S

Purpose: This common x86 entry assembly file defines shared low-level helpers and exported symbols used by both native entry code and KVM. It lives partly in `.noinstr.text` and `.entry.text` because the routines are called in sensitive entry/exit contexts.

Important APIs/types/functions: `write_ibpb` writes `MSR_IA32_PRED_CMD` with `x86_pred_cmd` and fills the return buffer if needed. `__WARN_trap` emits a `ud1` trap for WARN handling. `x86_verw_sel` is a cache-line-aligned kernel data-segment selector disguised as entry text so VERW can be addressed after page-table switches. `THUNK warn_thunk_thunk, __warn_thunk` creates a register-preserving warning thunk. The file exports `write_ibpb`, `__WARN_trap`, `x86_verw_sel`, and `__ref_stack_chk_guard` under stack protector/SMP conditions.

Control flow: `write_ibpb` is called by mitigation code to issue an indirect branch prediction barrier and optionally clear RSB state. `__WARN_trap` deliberately traps and returns only if the trap machinery resumes. Exit-to-user paths can reference `x86_verw_sel` while KPTI is active for MDS-style buffer clearing. The generated thunk saves registers, calls the C warning thunk, restores registers, and returns.

State and persistence: It writes CPU MSRs and may affect branch predictor/RSB microarchitectural state. `x86_verw_sel` is persistent read-only entry text data. No ordinary kernel heap or file state is used.

Dependencies and integration points: It depends on `calling.h`, MSR indexes, unwind hints, segment definitions, cache alignment, CPU feature alternatives, and nospec helpers. KVM references exported mitigation symbols.

Risks and test signals: These symbols sit in noinstr/entry contexts, so instrumentation and unwind annotations must remain correct. IBPB/RSB clearing must use the right MSR value and feature predicate. Tests should include objtool noinstr validation, KVM module symbol resolution, WARN trap behavior, mitigation selftests, and boot tests with stack protector plus SMP.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/entry/entry.S -->
