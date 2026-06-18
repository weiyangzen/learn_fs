# sources/distributed-fs/ceph-client/tools/perf/util/arm64-frame-pointer-unwind-support.c

Purpose: provides an AArch64-specific helper to recover the caller of the leaf frame when frame-pointer callchain recording has captured LR but not enough unwind context.

Important APIs and functions: `get_leaf_frame_caller_aarch64()` is the exported helper. `get_leaf_frame_caller_enabled()` gates the logic to `CALLCHAIN_FP` mode and requires a recorded `PERF_REG_ARM64_LR`. `add_entry()` collects up to two unwind IP entries from `unwind__get_entries()`.

Control flow: the helper first checks that frame-pointer mode and LR are available. It snapshots the sample's user regs, then temporarily fills cached PC and SP values if the sample did not record them. PC is taken from the user callchain entry after `usr_idx`, and SP is set to zero because the unwind path requires it even though it is not used by this recovery. It then asks generic unwind code for two entries and restores the original regs. The return value depends on callchain order: caller-first returns the first collected IP, callee-first returns the second.

State and persistence: state is strictly temporary in the provided `perf_sample`. The function saves and restores `struct regs_dump`, so no persistent mutation should remain after the call.

Dependencies and integration points: uses perf callchain globals, `perf_sample__user_regs()`, generic unwind support, and AArch64 perf register definitions. It is integrated where perf needs to fix or augment frame-pointer callchains for arm64 leaf frames.

Risks: the function returns `ret` when unwinding fails, even though the function type is `u64`; negative errors become large unsigned values unless callers treat non-canonical IPs carefully. It assumes `sample->callchain` and `usr_idx + 1` are valid when PC is missing. Cache register masks are set rather than normal masks, so behavior depends on unwind code honoring cache fields.

Test signals: arm64 frame-pointer callchain tests should cover missing PC, missing SP, missing LR, both callchain orders, unwind failure, short callchains, and verification that regs are restored after the helper returns.
