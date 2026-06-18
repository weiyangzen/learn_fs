# sources/distributed-fs/ceph-client/arch/x86/events/intel/core.c

## Purpose

This file is the Intel x86 core PMU implementation for the Linux perf subsystem in this source snapshot. Despite the enclosing `ceph-client` path, it is kernel architecture code: it maps generic perf events and cache events onto Intel model-specific encodings, initializes the correct `x86_pmu` operations for each Intel CPU family/model, manages PMU MSRs, and handles PMU interrupts, PEBS, LBR/BTS, TopDown metrics, hybrid PMUs, virtualization switching, and hardware errata.

The file is both a data catalogue and a runtime driver. The first half defines event constraints, extra MSR definitions, sysfs event aliases, and cache-event encoding matrices for Core, Core2, Nehalem/Westmere, Sandy/Ivy/Haswell/Broadwell/Skylake/Ice Lake/Golden Cove/Lion Cove/Panther Cove, Atom-family cores, Xeon Phi, and hybrid products. The second half binds those tables into perf callbacks and CPU-model init branches.

## Important APIs, Types, And Functions

- `intel_perfmon_event_map[]` maps `PERF_COUNT_HW_*` generic events to Intel event-select encodings. `intel_pmu_event_map()` exposes that map through `x86_pmu.event_map`.
- `struct event_constraint` tables, such as `intel_core2_event_constraints`, `intel_snb_event_constraints`, `intel_glc_event_constraints`, and `intel_pnc_event_constraints`, limit events to valid general or fixed counters and encode special cases such as TopDown metrics, PDist, memory events, and HT errata.
- `struct extra_reg` tables, such as `intel_snb_extra_regs`, `intel_glc_extra_regs`, `intel_pnc_extra_regs`, and `intel_arw_extra_regs`, describe shared auxiliary MSRs for offcore response, PEBS load latency, frontend PEBS selection, OMR, and snoop response.
- `*_hw_cache_event_ids` and `*_hw_cache_extra_regs` matrices implement perf `PERF_TYPE_HW_CACHE` translation by CPU family. Many last-level-cache and NUMA node events require both an event selector and an offcore/OMR extra-register value.
- `EVENT_ATTR_STR*` declarations build sysfs event aliases for memory loads/stores, TopDown metrics, TSX, and hybrid PMU-specific events.
- `intel_pmu_disable_all()`, `__intel_pmu_enable_all()`, `intel_pmu_enable_event()`, and `intel_pmu_disable_event()` program `MSR_CORE_PERF_GLOBAL_CTRL`, fixed-counter control, PEBS/ACR config extensions, BTS, VLBR, and per-event guest/host masks.
- `intel_pmu_handle_irq()` and `handle_pmi_common()` implement PMI handling: disable/freeze PMU state, drain BTS and PEBS, process Intel PT overflows, update TopDown metrics, restart overflowed counters, save LBR stacks, and call `perf_event_overflow()`.
- `intel_pmu_hw_config()` validates and annotates perf events. It handles precise events, large PEBS, PEBS aliases, branch stack and branch-counter logging, PEBS-via-PT aux output, PEBS counter groups, ACR groups, TopDown metric groups, SPR memory-load auxiliary-event requirements, and AnyThread filtering.
- `intel_get_event_constraints()` composes constraints from VLBR, BTS, shared extra regs, PEBS, static model tables, dynamic masks, and HT-exclusion state.
- `intel_cpuc_prepare()`, `intel_pmu_cpu_starting()`, `intel_cpuc_finish()`, and CPU hotplug helpers allocate and share per-CPU/per-core `intel_shared_regs`, dynamic constraint storage, exclusive counter state, debug store, PEBS buffers, LBR state, and hybrid PMU CPU masks.
- `intel_guest_get_msrs()` and `core_guest_get_msrs()` provide KVM guest/host PMU MSR switch state, with special handling for PEBS isolation, guest DS areas, PEBS data config, and exclude-host/exclude-guest masks.
- `intel_pmu_init()` is the central model dispatch. It reads CPUID leaf 0xa and optional architectural perfmon extension leaf 0x23, chooses `core_pmu` or `intel_pmu`, populates capabilities, selects cache/event/extra-reg tables, installs callbacks, sysfs attributes, LBR/PEBS setup, quirks, hybrid PMUs, and final PMU capability masks.

## Control Flow

Initialization begins in `intel_pmu_init()`. It rejects unsupported CPUs or delegates to P6/P4/KNC init for pre-architectural perfmon families, reads CPUID perfmon capabilities, initializes `x86_pmu`, then switches on `boot_cpu_data.x86_vfm`. Each model branch copies the appropriate cache tables, assigns event and PEBS constraints, chooses extra-register definitions, initializes LBR support, sets flags such as `PMU_FL_HAS_RSP_1`, `PMU_FL_NO_HT_SHARING`, `PMU_FL_MEM_LOADS_AUX`, or `PMU_FL_HAS_OMR`, installs errata quirks, and exposes the correct sysfs event/format groups. Hybrid models call `intel_pmu_init_hybrid()` and then initialize each PMU instance separately.

When an event is opened, perf routes through the PMU `hw_config` callback (`intel_pmu_hw_config()`, `hsw_hw_config()`, `adl_hw_config()`, or `arl_h_hw_config()`). This path first calls generic x86 setup, then rejects invalid BTS, PEBS, branch stack, ACR, TopDown, TSX, aux-output, or AnyThread combinations and mutates `event->hw` flags, dynamic counter masks, sample period, aliases, and group-leader flags.

Scheduling asks `intel_get_event_constraints()` for each event. The function checks fake VLBR and BTS constraints, reserves shared extra MSRs when needed, applies PEBS constraints, then static table constraints. It may further clone constraints into per-CPU dynamic storage for HT exclusion, ACR, branch-counter, PDist, PEBS, or runtime counter-mask restrictions. Scheduling hooks lock exclusive-counter state and record the final assigned counter.

When an event starts, `intel_pmu_enable_event()` programs PEBS/ACR extension state, host/guest masks, fixed control bits, interrupt enable bits, branch-counter bits, BTS, or VLBR state depending on the assigned index. PMU-wide enable writes fixed control if changed and enables only `intel_ctrl` bits not masked for guest execution.

PMI flow enters `intel_pmu_handle_irq()`. It saves `cpuc->enabled`, disables BTS and global PMU control, drains BTS, reads and acknowledges global overflow status, then loops until no status remains or a 100-iteration guard resets the PMU. `handle_pmi_common()` removes non-overflow status bits, drains PEBS rather than producing non-exact samples for PEBS counters, services Intel PT, updates PERF_METRICS/TopDown overflow, force-probes checkpointed counters, restarts ordinary counters with `intel_pmu_save_and_restart()`, captures LBR data when requested, and reports samples. Exit restores PMU state and APIC NMI masking according to early/mid/late ACK policy.

## State And Persistence Behavior

Most state is per-CPU in `cpu_hw_events`: active events, active masks, `fixed_ctrl_val`, PEBS masks, LBR/DS pointers, guest/host counter masks, checkpointed status, ACR config shadow registers, dynamic constraints, shared extra-reg accounting, and hybrid PMU pointer. This state is volatile kernel runtime state, rebuilt on CPU prepare/start and released on CPU dead/finish paths.

Shared auxiliary MSR state lives in `intel_shared_regs` and `er_account`. It may be per-core and shared by SMT siblings unless `PMU_FL_NO_HT_SHARING` forces per-CPU behavior. Allocation uses reference counts and raw spinlocks; events with matching extra-register configs may share the same MSR, while RSP/OMR alternates can be selected when hardware supports multiple registers.

Exclusive counter state for HT errata is stored in `intel_excl_cntrs`, shared by sibling threads and refcounted by core. The state records whether sibling counters are unused, shared, or exclusive and dynamically removes conflicting counters during scheduling. `fixup_ht_bug()` later disables this workaround if topology shows SMT is off.

Hardware persistence is MSR-backed and intentionally shadowed in software to avoid needless writes: fixed counter control, ACR CFG_B/CFG_C, TFA shadow, PEBS index/data config, global control masks, and extra-register allocations are cached or guarded before programming. PMU reset explicitly clears event selectors, counters, fixed counters, BTS indices, overflow status, global control, LBR enable, and LBR freeze state.

Sysfs state includes PMU name, visible event aliases, format attributes, LBR caps, `freeze_on_smi`, and `allow_tsx_force_abort`. Writes to `freeze_on_smi` update all CPUs via `on_each_cpu()`. Writes to `allow_tsx_force_abort` can reschedule CPUs using PMC3.

## Dependencies And Integration Points

The file depends heavily on the x86 perf core declared through `../perf_event.h`, including `x86_pmu`, `cpu_hw_events`, counter index constants, constraint helpers, PEBS/LBR/BTS helpers, generic event setup, and static-call hooks. It also integrates with APIC/NMI handling, CPUID and MSR accessors, CPU topology, hotplug, KVM guest PMU switching, Intel PT, debug store/PEBS buffers, sysfs PMU attribute groups, and perf event group scheduling.

Key external hooks and subsystems include `intel_pmu_lbr_*`, `intel_pmu_pebs_*`, `intel_bts_*`, `intel_pt_interrupt()`, `perf_guest_handle_intel_pt_intr()`, `perf_event_overflow()`, `perf_pmu_resched()`, `x86_add_quirk()`, `x86_add_exclusive()`, `check_hw_exists()`, and `x86_pmu_show_pmu_cap()`. Hybrid paths use `struct x86_hybrid_pmu`, PMU-specific masks and attributes, CPU type discovery from topology, and PMU filtering so hybrid PMUs only accept events on supported CPUs.

## Risks And Edge Cases

- Event encoding tables are highly model-specific. A wrong event ID, extra-register mask, or constraint can silently produce wrong perf counts, reject valid events, or program invalid MSRs.
- Shared extra MSR accounting is concurrency-sensitive. Incorrect `reg->alloc`, refcount, alternate-register selection, or fake-CPU validation behavior can leak allocations or reject schedulable groups.
- PMI handling runs in NMI context and must preserve PMU state while avoiding recursive or spurious interrupts. The code has special paths for PEBS, Intel PT, TopDown metrics, checkpointed counters, BTS, LBR, and loop-stuck reset.
- PEBS isolation with virtualization is security-sensitive: guest PEBS may write guest DS memory, host PEBS must not leak across guest entry, and cross-mapped counters are explicitly masked.
- TopDown metrics use fixed counter 3 and `MSR_PERF_METRICS`; separate reads can race with NMIs, so update paths require PMU disable and saved slot/metric state.
- ACR group support has an explicit limitation: `intel_pmu_acr_late_setup()` relies on active `event_list[]` contiguity, and disabling an ACR event can produce mask bit-shifting issues for remaining group members.
- Several errata workarounds impose non-obvious behavior: Nehalem magic-event reset, Haswell/Broadwell minimum periods, TSX force abort PMC3 exclusion, Sandy Bridge PEBS microcode disabling, Nehalem branch-miss remapping, and HT exclusive counter scheduling.
- Hypervisor MSR probing deliberately skips destructive tests on real hardware but mutates MSRs under hypervisors to detect unsupported emulation. Incorrect masks can disable features or hide usable LBR/extra regs.

## Test Signals

Useful validation signals are mostly integration-level because this is hardware-facing kernel PMU code:

- Boot logs should show the expected PMU name and capabilities from `intel_pmu_init()`, without constraint, MSR-access, or unsupported-event warnings.
- `/sys/bus/event_source/devices/cpu/` or hybrid PMU directories should expose the expected `events`, `format`, `caps`, and hybrid `cpus` attributes for the active CPU model.
- `perf stat` for generic events, cache events, memory aliases, TopDown aliases, TSX aliases, and hybrid PMU-specific aliases should accept valid events and reject invalid combinations such as unsupported AnyThread, invalid PDist counters, missing mem-loads auxiliary groups, invalid ACR groups, or BTS with kernel sampling.
- `perf record` with PEBS precise events, large PEBS sample types, branch stacks, branch counter logging, and Intel PT aux output should produce samples without bogus non-exact PEBS records or PMI loop warnings.
- KVM testing should cover `exclude_host`, `exclude_guest`, guest PEBS, PEBS EPT, DS-area switching, and cross-mapped counter masking.
- CPU hotplug and SMT tests should verify shared extra registers and exclusive counter state are refcounted and released correctly, and that the HT erratum workaround is disabled when SMT is absent.
- Errata-specific tests should exercise minimum sampling periods, TSX force abort toggling, Sandy Bridge PEBS microcode transitions, and Nehalem PMU reset behavior.
