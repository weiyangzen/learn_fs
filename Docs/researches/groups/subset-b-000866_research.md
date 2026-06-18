# Research Report: subset-b-000866

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/cstate.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/cstate.c

## Purpose

This file exposes Intel C-state residency MSRs as perf PMUs. It creates separate logical PMUs for core-scope, package/die-scope, and module/cluster-scope residency counters so perf users can count residency alongside ordinary events without special MSR tooling. The counters are read-only, free-running residency counters, so the implementation supports system-wide counting only and explicitly rejects sampling.

## Important APIs, Types, And Data

- `struct cstate_model` is the per-CPU-model capability table. It lists supported core, package, and module event bitmasks plus quirk flags.
- `core_msr[]`, `pkg_msr[]`, and `module_msr[]` map perf event IDs to concrete residency MSRs and sysfs event groups.
- `cstate_core_pmu`, `cstate_pkg_pmu`, and `cstate_module_pmu` are `struct pmu` instances registered with `PERF_PMU_SCOPE_CORE`, `PERF_PMU_SCOPE_PKG` or `PERF_PMU_SCOPE_DIE`, and `PERF_PMU_SCOPE_CLUSTER`.
- `intel_cstates_match[]` maps Intel VFM identifiers to `struct cstate_model` instances covering Nehalem through recent Atom/Core/Xeon families.
- `DEFINE_CSTATE_FORMAT_ATTR()` and `PMU_EVENT_ATTR_STRING()` define perf sysfs format and event aliases such as `c1-residency`, `c6-residency`, and `c10-residency`.

## Control Flow

Module initialization enters `cstate_pmu_init()`, rejects hypervisors, matches the boot CPU against `intel_cstates_match[]`, probes MSR availability in `cstate_probe()`, then registers the PMUs in `cstate_init()`. Probing uses `perf_msr_probe()` with the model bitmasks, so the advertised event set is the intersection of model knowledge and readable MSRs.

Event setup goes through `cstate_pmu_event_init()`. It validates the PMU type, rejects sampling and task events, bounds-checks `attr.config` with `array_index_nospec()`, verifies the probed MSR mask, and stores the selected MSR in `event->hw.event_base`. Add/start snapshots the current MSR value into `prev_count`; stop/read calls `cstate_pmu_event_update()`, which atomically advances `prev_count` and accumulates the delta into `event->count`.

## State And Persistence

Global state is limited to probed MSR masks and booleans tracking whether each PMU was registered. Per-event state is the selected MSR address, the event ID in `hw.config`, and `prev_count`. There is no persistent storage beyond live kernel PMU registration and no hardware programming other than `rdmsrq()`.

## Dependencies And Integration Points

The file depends on perf core PMU registration, x86 CPU model matching, topology scope helpers, MSR accessors, and `perf_msr_probe()`. Sysfs integration is through perf PMU event and format groups. Multi-die packages are exposed as `cstate_die` by changing the PMU scope/name during registration.

## Risks And Edge Cases

- Counter deltas assume unsigned free-running MSR behavior; wrap handling relies on natural unsigned subtraction.
- The PMUs reject per-task and sampling usage, so callers expecting interrupt-driven samples receive `-EINVAL`.
- Probe correctness depends on model tables staying aligned with Intel MSR availability.
- The KNL quirk block assigns `MSR_KNL_CORE_C6_RESIDENCY` through `pkg_msr[PERF_CSTATE_CORE_C6_RES]`, while core event initialization later reads `core_msr[]`; this is a notable audit point because it appears inconsistent with the comment and enum domain.
- Hypervisor environments are rejected entirely, avoiding virtualized MSR ambiguity at the cost of no guest exposure.

## Test Signals

Useful validation includes boot/module load on supported and unsupported Intel models, sysfs presence under `/sys/bus/event_source/devices/cstate_*`, `perf stat -a -e cstate_core/c6-residency/` style counts, rejection of sampling/per-task events, and model-specific checks for renamed `cstate_die` on multi-die systems. KNL/SLM quirk tests should verify the actual MSR selected for the affected residency event.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/cstate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/ds.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/ds.c

## Purpose

This file implements Intel Debug Store support for perf, covering BTS branch tracing and PEBS precise sampling. It allocates per-CPU buffers, maps DS buffers through the CPU entry area, enables and disables PEBS/BTS hardware, translates PEBS records into perf samples, handles PEBS event constraints, and initializes generation-specific PEBS behavior from Core/Core2 through adaptive and architectural PEBS.

## Important APIs, Types, And Data

- `DEFINE_PER_CPU_PAGE_ALIGNED(struct debug_store, cpu_debug_store)` and `per_cpu(cpu_hw_events).ds` provide per-CPU DS descriptors.
- `union intel_x86_pebs_dse`, `union omr_encoding`, and data-source tables convert PEBS memory encodings into `PERF_MEM_*` data source values.
- `struct pebs_record_core`, `pebs_record_nhm`, `pebs_record_hsw`, and `pebs_record_skl` describe legacy DS PEBS formats. Adaptive and architectural PEBS formats are consumed through shared structs from x86 perf headers.
- `reserve_ds_buffers()`, `release_ds_buffers()`, `alloc_arch_pebs_buf_on_cpu()`, `init_arch_pebs_on_cpu()`, and `fini_arch_pebs_on_cpu()` manage PEBS/BTS storage.
- `intel_pmu_enable_bts()`, `intel_pmu_disable_bts()`, and `intel_pmu_drain_bts_buffer()` implement BTS.
- `intel_pebs_constraints()` selects PEBS constraints and flags for precise events.
- `intel_pmu_pebs_add/del/enable/disable/enable_all/disable_all()` maintain PEBS runtime state.
- Drain paths are `intel_pmu_drain_pebs_core()`, `intel_pmu_drain_pebs_nhm()`, `intel_pmu_drain_pebs_icl()`, and `intel_pmu_drain_arch_pebs()`.
- Initialization enters `intel_pebs_init()`, then either `intel_arch_pebs_init()` or `intel_ds_pebs_init()`.

## Control Flow

PEBS setup starts with capability initialization. `intel_pebs_init()` chooses architectural PEBS when `pebs_format == 0xf`; otherwise `intel_ds_pebs_init()` validates `DTES64`, enables DS PEBS if the CPU advertises PEBS, selects the record size, drain function, large-PEBS flags, baseline/adaptive behavior, and optional PEBS-via-PT capability.

Buffer reservation is separate from event scheduling. `reserve_ds_buffers()` allocates a DS descriptor for each possible CPU, then BTS and/or PEBS buffers depending on `x86_pmu` capability flags. Legacy DS PEBS and BTS buffers are mapped into `cpu_entry_area` with `ds_update_cea()` and global TLB flushes; architectural PEBS stores a physical base in `MSR_IA32_PEBS_BASE`.

When a precise event is admitted, `intel_pebs_constraints()` checks the active CPU or hybrid PMU constraint table, stamps event flags, and either returns a matching constraint, lets `PMU_FL_PEBS_ALL` fall back to normal constraints, or rejects with `emptyconstraint`. On add/delete, `intel_pmu_pebs_add()` and `intel_pmu_pebs_del()` update `n_pebs`, `n_large_pebs`, `n_pebs_via_pt`, scheduler callback needs, and adaptive data configuration. On enable, `intel_pmu_pebs_enable()` sets `pebs_enabled` bits, handles load-latency/store bits, updates `MSR_PEBS_DATA_CFG` when adaptive layout changes, recomputes interrupt thresholds, programs auto-reload slots in `debug_store`, and optionally enables PEBS output through Intel PT.

Drain flow is generation-specific. Legacy core drains a single PMC0 stream. NHM-style drains scan records between `pebs_buffer_base` and `pebs_index`, count status bits, handle zero-status and collision cases, log lost samples, and emit perf samples. ICL adaptive drains variable-size `pebs_basic` records and dispatches by `applicable_counters`. Architectural PEBS reads `MSR_IA32_PEBS_INDEX`, resets the write index and threshold, walks potentially fragmented records, and uses the same last-record overflow semantics. All drain paths reset the producer index before processing to return the buffer to hardware quickly.

## State And Persistence

Persistent runtime state lives in per-CPU `cpu_hw_events`: DS pointer, PEBS buffer virtual address, BTS buffer address, `pebs_enabled`, PEBS record size/configuration, active PEBS data config, PEBS counts, and event pointers by counter index. `x86_pmu` holds global capability flags, data-source tables, PEBS constraints, PEBS buffer size, record size, and function pointers. No disk persistence exists; all state is CPU-local or PMU-global and rebuilt during CPU/PMU initialization.

## Dependencies And Integration Points

This file sits at the center of x86 perf integration. It uses MSRs (`MSR_IA32_DS_AREA`, `MSR_IA32_PEBS_ENABLE`, `MSR_PEBS_DATA_CFG`, `MSR_IA32_PEBS_INDEX`, reload MSRs), CPU entry-area mappings, TLB flushing, x86 instruction decoding for PEBS IP fixups, perf sample/output APIs, Intel PT AUX-output capability, LBR helpers for PEBS branch stacks and IP correction, hybrid PMU variables, scheduler callbacks, and topdown metric update static calls.

## Risks And Edge Cases

- DS buffer mapping changes require correct cross-CPU TLB invalidation; stale CPU entry-area mappings would be severe.
- Adaptive PEBS record size changes must drain first because drain code assumes uniform record size within a buffer.
- PEBS status collisions can drop records when several PEBS events collapse into one status; the file logs lost samples but cannot reconstruct them.
- PEBS-via-PT and hybrid PMUs have asymmetric capability concerns; the code explicitly ignores per-PMU PT-output availability on hybrid systems.
- IP fixup for older PEBS relies on LBR contents and NMI-safe instruction copying/decoding; failure causes non-exact samples.
- Counter snapshot records may contain deleted, stopped, or uninitialized events; `intel_perf_event_update_pmc()` deliberately drops missing event pointers.
- BTS filtering performs an extra pass to avoid leaking kernel addresses when `exclude_kernel` is set.

## Test Signals

Relevant signals include boot logs naming PEBS format and qualifiers, successful `perf record -e cycles:p/pp/ppp`, PEBS load-latency data source correctness, adaptive PEBS samples with branch stacks/registers/weights/read groups, context-switch draining for large PEBS, BTS samples with kernel filtering, CPU hotplug allocation/teardown, hybrid core/atom data-source differences, and KVM/guest behavior around PEBS-via-PT and architectural PEBS. Stress tests should include multiple precise events, counter groups, auto-reload, and PEBS buffer-empty drains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/ds.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/knc.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/knc.c

## Purpose

This file provides the x86 perf PMU backend for Intel Xeon Phi Knights Corner. KNC has a small non-architectural PMU with two programmable counters, custom global control/status MSRs, a KNC-specific event map, and cache-event encodings.

## Important APIs, Types, And Data

- `knc_perfmon_event_map[]` maps generic perf hardware events to KNC event selectors.
- `knc_hw_cache_event_ids` maps perf cache triplets to KNC encodings, including special handling for valid event zero via `ARCH_PERFMON_EVENTSEL_INT`.
- `knc_event_constraints[]` pins a set of L2/snoop/prefetch events to counter 0.
- KNC global MSR constants define status, overflow acknowledge, and global counter control registers.
- `knc_pmu` is the `struct x86_pmu` installed by `knc_pmu_init()`.

## Control Flow

`knc_pmu_init()` copies the static `knc_pmu` into the global `x86_pmu` and installs KNC cache-event IDs. Generic perf setup uses `knc_pmu_event_map()` for predefined events and `x86_pmu_hw_config()` for normal event configuration. Enable/disable operations write the per-counter event select MSR with or without `ARCH_PERFMON_EVENTSEL_ENABLE`; global enable/disable flips the two KNC global enable bits.

Interrupt handling is local to `knc_pmu_handle_irq()`. It disables all counters, reads global overflow status, acknowledges pending bits, loops up to 100 times while status remains set, updates/restarts active events with `intel_pmu_save_and_restart()`, emits `perf_event_overflow()`, then restores global enable only if the PMU was enabled before the interrupt path.

## State And Persistence

State is held in the common per-CPU `cpu_hw_events` event array and active mask, with hardware state in KNC MSRs. There is no private persistent state beyond the selected `x86_pmu` callbacks and copied cache-event map.

## Dependencies And Integration Points

The file integrates with generic x86 perf scheduling, event constraints, APIC perf IRQ accounting, safe MSR writes, and perf overflow delivery. It relies on common Intel helpers for save/restart and x86 event setup while substituting KNC-specific global control and status handling.

## Risks And Edge Cases

- Only counters 0 and 1 are globally enabled; constraints and masks must stay consistent with this limit.
- The IRQ loop has a 100-iteration stuck guard; repeated status bits trigger warning and debug dump.
- The event map contains unsupported cache combinations as zero or `-1`; callers depend on generic validation to reject unsupported encodings.
- Safe MSR writes ignore return values in enable/disable paths, so hardware write failures are not propagated.

## Test Signals

Validation should include KNC boot selection, `perf stat` for cycles/instructions/cache/branches, constrained L2 events, overflow interrupt delivery, no stuck IRQ loop warnings, and sysfs format attributes for `event`, `umask`, `edge`, `inv`, and `cmask`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/knc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/lbr.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/lbr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/p4.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/p4.c

## Purpose

This file implements perf support for NetBurst Pentium 4 and old Xeon PMUs. P4 uses non-architectural CCCR counter-control registers, ESCR event-select registers, hyperthread-aware thread fields, event aliases, and PEBS metric MSRs, so the file supplies a custom PMU backend rather than relying on architectural Intel PMU support.

## Important APIs, Types, And Data

- `struct p4_event_bind` maps each NetBurst event to opcode, valid ESCR mask bits, possible ESCR MSRs per logical thread, shared-event permission status, and legal counters.
- `struct p4_pebs_bind` maps cache-event PEBS metrics to `MSR_IA32_PEBS_ENABLE` and `MSR_P4_PEBS_MATRIX_VERT`.
- `p4_event_bind_map[]` is the central resource table for event scheduling.
- `p4_hw_cache_event_ids` and `p4_general_events[]` translate generic perf events/cache triplets to packed ESCR/CCCR config.
- `p4_event_aliases[]` allows selected equivalent events, notably non-halted cycles, to use alternate resources when the primary binding conflicts.
- `p4_pmu` is the `struct x86_pmu` installed by `p4_pmu_init()`.

## Control Flow

`p4_pmu_init()` verifies the EMON enable bit, installs cache-event IDs, copies `p4_pmu` into `x86_pmu`, and clears counter config registers to avoid stale overflow behavior, especially in kdump/single-CPU situations. Event setup enters `p4_hw_config()`, builds default CCCR/ESCR fields for the current CPU and exclude flags, handles HT-thread tagging, validates raw events, merges raw config, fills the CCCR event-select field, and delegates to `x86_setup_perfctr()`.

Scheduling uses `p4_pmu_schedule_events()`. For each event, it computes the current logical thread, finds the bound ESCR index, reuses an existing counter when valid, otherwise searches the binding's legal counters and ESCR availability. If resources conflict, it tries an alias up to two passes. It then swaps thread-specific config bits if the event migrated between HT siblings and records the chosen counter.

Enable writes PEBS metric MSRs when a metric is requested, programs the selected ESCR, then writes CCCR with enable set. Disable clears enable, overflow, and reserved CCCR bits. IRQ handling walks all counters, catches in-flight IRQs for counters just disabled, clears official or unflagged overflows, updates event counts, resets periods, emits perf overflow samples, and finally unmasks LVTPC only after overflow flags are cleared.

## State And Persistence

Runtime state is mostly generic perf state plus packed P4 config in `hw_perf_event.config`. Per-CPU `p4_running` tracks counters that may still deliver in-flight NMIs after disable. Hardware state persists in CCCR, PERFCTR, ESCR, PEBS enable, and PEBS matrix MSRs until reprogrammed or cleared at init. There is no disk persistence.

## Dependencies And Integration Points

The file depends on `asm/perf_event_p4.h` for packing/unpacking helpers and event definitions, APIC LVTPC handling, MSR access, generic x86 perf setup, constraints, cache-event translation, and permission checks through `perf_allow_cpu()` for shared HT events.

## Risks And Edge Cases

- P4 resource scheduling is fragile because ESCRs are sparse, counters are event-specific, and HT thread fields must match the CPU where the event runs.
- Some events are shared across logical threads and require elevated permission when HT is active.
- Counter 1 and cascaded counters are explicitly unsupported or warned due to errata.
- `p4_pmu_disable_pebs()` intentionally leaves PEBS metrics enabled because safe reference tracking is missing; this can leave hardware metric MSRs programmed longer than ideal.
- Overflow detection must handle both CCCR overflow bits and unflagged overflow inferred from counter sign.
- Raw-event validation must reject invalid ESCR masks, unsupported model-specific events, and PEBS enable bits from user config.

## Test Signals

Validation includes boot on NetBurst with EMON enabled/disabled, `perf stat` for generic events, HT sibling migration, shared-event permission rejection, alias scheduling for simultaneous cycle events, raw config validation, overflow/NMI delivery without unknown-NMI storms, and cache events that program PEBS metric MSRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/p4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/p6.c -->
# sources/distributed-fs/ceph-client/arch/x86/events/intel/p6.c

## Purpose

This file provides the x86 perf PMU backend for P6-family Intel processors. It supplies generic event and cache-event mappings, P6-specific constraints, simple two-counter enable/disable behavior, and a Pentium Pro RDPMC erratum workaround.

## Important APIs, Types, And Data

- `p6_perfmon_event_map[]` maps perf generic hardware events to P6 event selectors.
- `p6_hw_cache_event_ids` maps perf cache triplets to P6 encodings, with unsupported combinations represented by zero or `-1`.
- `P6_NOP_EVENT` programs `L2_RQSTS` with zero MESI mask to effectively disable a counter.
- `p6_event_constraints[]` restricts selected floating-point events to counter 0 or counter 1.
- `p6_pmu` is the `struct x86_pmu` installed by `p6_pmu_init()`.

## Control Flow

`p6_pmu_init()` copies `p6_pmu` into the global `x86_pmu`, registers a Pentium Pro quirk if needed, and installs cache-event IDs. Generic perf event setup uses `p6_pmu_event_map()`, `x86_pmu_hw_config()`, and `x86_schedule_events()`.

P6 has a single effective global enable bit on `MSR_P6_EVNTSEL0`. `p6_pmu_disable_all()` clears `ARCH_PERFMON_EVENTSEL_ENABLE` there, and `p6_pmu_enable_all()` sets it. Individual disable does not have a separate enable bit per counter; instead `p6_pmu_disable_event()` writes `P6_NOP_EVENT` to the event select register. `p6_pmu_enable_event()` writes the configured selector and relies on the later global enable path.

## State And Persistence

State is held in the common x86 perf event structures and in the two P6 event select/perf counter MSRs. Counter values are treated as effectively 32-bit despite 40 implemented bits because upper bits sign-extend bit 31. No private persistent state exists beyond the selected PMU and optional RDPMC attributes changed by the quirk.

## Dependencies And Integration Points

The file integrates with generic x86 perf IRQ handling (`x86_pmu_handle_irq`), generic event setup and scheduling, event constraints, sysfs format attributes, and Intel event sysfs display. It uses x86 CPU model detection to install the Pentium Pro RDPMC quirk.

## Risks And Edge Cases

- Disabling by programming a NOP event depends on `P6_NOP_EVENT` truly not counting on all target P6 variants.
- The global enable bit on EVNTSEL0 means enable/disable ordering differs from later per-counter PMUs.
- Effective 32-bit counter width must be respected despite 40-bit MSR fields.
- Pentium Pro steppings before 9 have broken userspace RDPMC; the quirk disables user RDPMC exposure.
- Several cache-event table entries are placeholders or unsupported, so validation paths must prevent misleading counts.

## Test Signals

Signals include P6 boot PMU selection, generic `perf stat` events, constrained floating-point event scheduling, counter overflow through generic x86 IRQ handling, sysfs format fields (`event`, `umask`, `edge`, `pc`, `inv`, `cmask`), and RDPMC disabled warnings on affected Pentium Pro steppings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/events/intel/p6.c -->
