# sources/distributed-fs/ceph-client/arch/x86/events/intel/lbr.c

## Purpose

This file implements Intel Last Branch Record support for perf. It handles legacy LBR MSR stacks, architectural LBR, hardware and software branch filtering, per-task call-stack save/restore, PEBS LBR consumption, virtual LBR host exclusion, branch counter reordering, and KVM export of LBR register metadata.

## Important APIs, Types, And Data

- Legacy filter constants describe `MSR_LBR_SELECT` suppress-style bits; architectural constants describe `MSR_ARCH_LBR_CTL` capture-style bits.
- `intel_pmu_lbr_add()`, `intel_pmu_lbr_del()`, `intel_pmu_lbr_enable_all()`, and `intel_pmu_lbr_disable_all()` are runtime perf hooks.
- Save/restore implementations include `intel_pmu_lbr_save/restore()` for legacy stacks, `intel_pmu_arch_lbr_save/restore()` for architectural MSRs, and XSAVE-backed `intel_pmu_arch_lbr_xsaves/xrstors()`.
- Read paths include `intel_pmu_lbr_read_32()`, `intel_pmu_lbr_read_64()`, `intel_pmu_arch_lbr_read()`, and `intel_pmu_arch_lbr_read_xsave()`.
- `intel_pmu_setup_lbr_filter()` builds software branch masks and optional hardware filter config.
- CPU-family initialization functions populate `x86_pmu` LBR fields for Core, Atom, NHM, SNB, HSW, SKL, SLM, KNL, and architectural LBR.
- Static keys gate optional LBR info fields: mispredict, cycles, and branch type.

## Control Flow

Initialization is split by LBR generation. Legacy model-specific init sets depth, TOS/from/to MSRs, optional info MSR, and filter maps. `intel_pmu_lbr_init()` interprets the enumerated LBR format and enables flags for TSX, from-address flags, info MSRs, or cycle-in-TO encodings. `intel_pmu_arch_lbr_init()` uses CPUID leaf 28, programs maximum depth, records capability bits, builds a task context cache, chooses XSAVE if the enumerated state size matches kernel structs, installs architectural read/save/restore callbacks, and disables unsupported filter requests in `arch_lbr_ctl_map`.

When a branch-stack event is added, `intel_pmu_lbr_add()` records whether LBR_SELECT is needed, stores the requested branch selector, increments call-stack users for per-task or CPU-wide contexts, requests perf scheduler callbacks, and resets LBRs for first-time users. On scheduling, `intel_pmu_lbr_sched_task()` saves/restores call-stack LBR state when task context storage exists, otherwise resets on schedule-in to avoid mixing address spaces. Enable writes DEBUGCTL and either `MSR_LBR_SELECT` or `MSR_ARCH_LBR_CTL`; disable clears the relevant hardware enable path.

Reading copies MSR entries into `cpuc->lbr_entries`, decodes flags from either from-address bits or LBR info MSRs, handles TSX and cycle fields, skips invalid call-stack entries, and filters entries against the requested branch type. The software filter uses hardware branch type when architectural LBR supplies it, otherwise calls `branch_type()` for opcode-based classification, then compacts rejected entries. PEBS can supply an LBR array directly via `intel_pmu_store_pebs_lbrs()`.

## State And Persistence

Global `x86_pmu` fields store LBR depth, MSR bases, capabilities, maps, callbacks, and task context cache. Per-CPU `cpu_hw_events` tracks active LBR users, selector state, PEBS LBR users, last task context/log ID, saved entries, counters, and optional XSAVE buffer. Per-task perf context data stores call-stack LBR snapshots and user counts. State is volatile and rebuilt on PMU initialization or context scheduling.

## Dependencies And Integration Points

The implementation depends on perf branch sample attributes, x86 PMU callbacks, DEBUGCTL MSRs, CPUID, XSAVE sizing, KVM export (`EXPORT_SYMBOL_FOR_KVM(x86_perf_get_lbr)`), PEBS adaptive branch-stack support, branch decoder helpers, static CPU feature checks, and scheduler callbacks. It also integrates with virtual LBR by checking guest masks for `INTEL_PMC_IDX_FIXED_VLBR`.

## Risks And Edge Cases

- Legacy `LBR_SELECT` is suppress-style while architectural `LBR_CTL` is capture-style; incorrect map handling inverts filters.
- Some LBR formats need sign-extension quirks when TSX is disabled, handled by `lbr_from_quirk_key`.
- Context switches require reset or save/restore because LBR entries are not address-space tagged.
- Call-stack LBR and `FREEZE_LBRS_ON_PMI` interact poorly, so enable logic clears freeze for call-stack mode.
- Architectural LBR XSAVE is disabled if CPUID state size does not exactly match kernel expectations.
- Software filtering can shrink the branch stack and relies on correct opcode decoding for branch types not supplied by hardware.
- Branch counter data is temporarily stored in `perf_branch_entry.reserved` and must be cleared after reordering.

## Test Signals

Signals include correct branch stacks from `perf record -j any`, call-stack branch sampling across context switches, kernel/user filter behavior, TSX/mispredict/cycle/type fields where supported, architectural LBR CPUID and XSAVE path selection, PEBS samples with branch stacks, virtual LBR host exclusion in KVM scenarios, and no stale LBR data after branch-counter group removal.
