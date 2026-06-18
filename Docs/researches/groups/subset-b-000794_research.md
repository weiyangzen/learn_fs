# Research: subset-b-000794

Grouped research for PowerPC perf PMU support files under `sources/distributed-fs/ceph-client/arch/powerpc/perf`. Each section is keyed by the exact source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.c

Purpose: registers the `hv_gpci` perf PMU for IBM Power LPAR systems that expose hypervisor "get performance counter info" counters through `H_GET_PERF_COUNTER_INFO`. It turns generated request encodings into perf events and exposes hypervisor capabilities and selected Power10+ topology/system-information requests through sysfs.

Important APIs/types/functions: `h_gpci_pmu`, `hv_gpci_init`, `single_gpci_request`, `h_gpci_event_init`, `h_gpci_event_update`, `ppc_hv_gpci_cpu_online/offline`, `systeminfo_gpci_request`, the processor topology/config/affinity `*_show` handlers, and `sysinfo_device_attr_create`. Request field formats are exported with `EVENT_DEFINE_RANGE_FORMAT`, while event names come from generated `hv_gpci_event_attrs` and `hv_gpci_event_attrs_v6`.

Control flow and state: initialization checks `FW_FEATURE_LPAR`, reads `hv_perf_caps`, installs CPU hotplug state, probes counter-info version with request `0x10`, chooses the v8 or v6 generated event table, registers the PMU, and conditionally adds Power10+ sysinfo attributes. Normal perf reads call a per-CPU `hv_gpci_reqb` buffer, issue the hcall, decode a big-endian byte range selected by `offset` and `length`, and accumulate deltas in `event->count`. Sysinfo files loop on `H_PARAMETER` partial responses and append hex records into one page.

State and persistence behavior: no persistent storage is written. Runtime state is a PMU registration, generated sysfs attribute groups, a single active collection CPU mask, hotplug migration via `perf_pmu_migrate_context`, per-CPU request buffers, and dynamically allocated sysinfo `device_attribute` objects that live for the lifetime of the PMU.

Dependencies and integration points: depends on PowerPC LPAR firmware, `plpar_hcall_norets`, `hv_perf_caps_get`, generated `req-gen/perf.h` artifacts from `hv-gpci.h`, perf core PMU callbacks, CPU hotplug, and PVR detection for Power10 sysinfo exposure. User integration is through `perf stat -e hv_gpci/.../` and `/sys/bus/event_source/devices/hv_gpci/{format,events,interface,cpumask}`.

Risks: sysinfo output is page-limited and can return `-EFBIG`; partial response cursor extraction is request-specific and easy to break with layout changes; `add_sysinfo_interface_files` allocates attributes without a visible free path after successful registration; hcall return-code handling maps many firmware failures to generic `-EIO`/`-EINVAL`; counters read as zero on read hcall failure, which can hide transient errors.

Test signals: build with PowerPC perf and LPAR support; boot on an LPAR with performance information enabled; verify `hv_gpci` appears under event sources, `cpumask` tracks CPU hotplug, known generated events can be read by `perf stat`, unsupported or unauthorized partitions return `EPERM`/fail cleanly, and Power10+ sysinfo files either contain hex records or report documented hcall errors.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.h

Purpose: small glue header for the hypervisor GPCI PMU. It defines the current counter-info version, capability bit masks, and parameters used by the request generator include to produce event format helpers and event attribute arrays.

Important APIs/types/functions: `COUNTER_INFO_VERSION_CURRENT`, `HV_GPCI_CM_GA`, `HV_GPCI_CM_EXPANDED`, `HV_GPCI_CM_LAB`, `REQUEST_FILE`, `NAME_LOWER`, `NAME_UPPER`, `ENABLE_EVENTS_COUNTERINFO_V6`, and the included `req-gen/perf.h` output. Consumers rely on generated symbols such as `hv_gpci_event_attrs`, `hv_gpci_event_attrs_v6`, event field extractors, and offset assertions.

Control flow and state: the file has no runtime control flow. At compile time it points the request generator at `../hv-gpci-requests.h` and asks it to emit `hv_gpci`-named code, including alternate counter-info-v6 event lists.

State and persistence behavior: no persistent or runtime state is owned here. The constants become compiled kernel ABI for sysfs `kernel_version` and generated event decoding.

Dependencies and integration points: included by `hv-gpci.c`; indirectly depends on `hv-gpci-requests.h` and `req-gen/perf.h`. It must stay synchronized with the hypervisor GPCI specification and with the generated request/event fields used by the perf PMU.

Risks: `COUNTER_INFO_VERSION_CURRENT` and capability masks are ABI-visible; stale version constants can mislead userspace even if the runtime event list probes an older firmware version. Incorrect generator macro names would break symbol names used by `hv-gpci.c`.

Test signals: compile the PowerPC perf tree, confirm generated `hv_gpci` symbols resolve, inspect sysfs `interface/kernel_version`, and run an event from both version-specific generated lists on suitable firmware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/hv-gpci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/imc-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/imc-pmu.c

Purpose: implements In-Memory Collection perf PMUs for OPAL-provided PowerPC IMC domains: nest, core, thread, and trace. It registers PMUs from device-tree descriptors, allocates or references counter memory, starts/stops engines through OPAL calls, and presents free-running memory counters or trace samples through perf.

Important APIs/types/functions: `init_imc_pmu`, `update_events_in_group`, `imc_mem_init`, `update_pmu_ops`, nest/core/thread/trace `*_event_init`, `imc_event_update`, `thread_imc_event_add/del`, `trace_imc_event_add/del/stop`, `dump_trace_imc_data`, `trace_imc_prepare_sample`, CPU hotplug callbacks, and cleanup helpers. Global state includes `nest_imc_cpumask`, `core_imc_cpumask`, per-CPU `thread_imc_mem`/`trace_imc_mem`, per-domain refcounts, and `imc_global_refc`.

Control flow and state: device-tree parsing builds event sysfs attributes from event child nodes and optional scale/unit metadata. Nest PMUs use per-chip HOMER memory discovered in `pmu->mem_info`; core/thread/trace allocate per-core or per-CPU pages and initialize OPAL with physical addresses. Event init validates type, sample mode, CPU/target, offset bounds, and domain exclusivity. Start/add snapshots or enables counter posting via `SPRN_LDBAR`; stop/del computes deltas or emits trace samples. Hotplug migrates nest/core contexts to another CPU in the same node/core or stops counters when the last CPU leaves.

State and persistence behavior: no disk persistence. Runtime state is long-lived allocated counter pages, OPAL engine initialization, per-node/per-core/per-domain reference counts, PMU registrations, dynamic event attributes, and LDBAR programming on each CPU. Counter values are free-running big-endian memory slots; perf event counts are derived from deltas against `prev_count`.

Dependencies and integration points: depends on OPAL IMC calls, `asm/imc-pmu.h`, device-tree nodes with `events`, `events-prefix`, `reg`, `scale`, `unit`, CPU/node topology, perf core PMU callbacks, CPU hotplug, and PowerPC SPR access. Trace mode integrates with perf output buffers by constructing `PERF_RECORD_SAMPLE` records.

Risks: global exclusion between core/thread/trace modes is enforced by a single refcount and can leak on init/add error paths; core and thread modes share core counter start/stop refcounts; memory cleanup only frees online CPU per-CPU pages; trace validation stops at the first invalid record; dynamic sysfs string allocation is not comprehensively unwound; comments note PMU unregister follow-up work in common cleanup.

Test signals: build with OPAL IMC and boot on supported PowerNV hardware; verify device-tree-generated PMUs/events appear; run nest/core/thread counting with CPU hotplug; confirm trace sampling emits samples with sensible IP/misc fields; test mutual exclusion by attempting trace with active core/thread events; inspect OPAL failure logs and refcount behavior under interrupted perf sessions.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/imc-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/internal.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/internal.h

Purpose: declares the architecture PMU initialization entry points used inside the PowerPC perf implementation for processor-specific PMU registration.

Important APIs/types/functions: `init_ppc970_pmu`, `init_power5_pmu`, `init_power5p_pmu`, `init_power6_pmu`, `init_power7_pmu`, `init_power8_pmu`, `init_power9_pmu`, `init_power10_pmu`, `init_power11_pmu`, and `init_generic_compat_pmu`, all returning `int` and marked `__init`.

Control flow and state: this header has no direct control flow. It provides prototypes so common setup code can attempt each CPU-family init routine and so family files can include common declarations without duplicating prototypes.

State and persistence behavior: no state is stored. The declarations describe boot-time registration functions whose implementations register global perf PMU descriptors.

Dependencies and integration points: included by several `arch/powerpc/perf/*` files, notably processor-specific PMU implementations and `isa207-common.h`. It depends on the kernel `__init` annotation being available through surrounding includes.

Risks: prototype drift would cause build failures or wrong init linkage. Missing a newly added family init would prevent central initialization code from seeing the implementation.

Test signals: PowerPC allmodconfig/defconfig builds, plus boot logs showing the correct CPU-family PMU is registered on supported hardware.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.c

Purpose: shared helper implementation for PowerISA v2.07+ PMUs, including POWER8/9/10 style raw event validation, constraint construction, MMCR programming, marked sampling setup, memory data-source decoding, sample weight calculation, alternatives, and reserved field checks.

Important APIs/types/functions: exported helpers `isa207_get_constraint`, `isa207_compute_mmcr`, `isa207_disable_pmc`, `isa207_get_alternatives`, `isa207_get_mem_data_src`, `isa207_get_mem_weight`, `isa3XX_check_attr_config`, and `isa207_pmu_format_group`. Important internal helpers include `is_event_valid`, `mmcra_sdar_mode`, `p10_thresh_cmp_val`, `thresh_cmp_val`, `isa207_find_source`, and threshold/cache/radix constraint helpers.

Control flow and state: event validation selects the valid mask by CPU feature level. Constraint building encodes PMC uniqueness, counter count, cache/L1/L2/L3 grouping, threshold fields, EBB and BHRB requirements, radix scope, and Power10 config1 threshold compare. MMCR computation first records fixed PMC usage, then assigns unpinned events to PMC1-4, sets MMCR1 unit/combine/PMCSEL, MMCRA marked sampling and threshold fields, MMCR2 privilege/idle filters and L2/L3 select, and MMCR3 Power10 event extension fields. Memory source decoding maps SIER fields to perf `PERF_MEM_*` source bits; weight decoding uses MMCRA threshold mantissa/exponent and Power10 SIER2 cycles.

State and persistence behavior: no persistent state. It reads CPU feature flags and SPRs (`MMCRA`, `SIER`, `SIER2`) and writes computed values into caller-provided `mmcr_regs`, `hwc`, data source, and weight structures.

Dependencies and integration points: used by ISA207-family PMU files such as Power8/9/10. It depends on `isa207-common.h`, perf event attributes, PowerPC CPU feature bits, PMU flags (`PPMU_HAS_SIER`, `PPMU_HAS_ATTR_CONFIG1`, `PPMU_ONLY_COUNT_RUN`), and the generic PowerPC perf scheduler's constraint solver.

Risks: bitfield layouts differ across POWER8, POWER9, and POWER10; threshold compare encoding can reject or clamp values; BHRB is only valid with EBB-style requests in raw encoding; guest kernels cannot program some HV-only cache selector state; `pevents[i]` must be valid for branch/exclude/config1 checks; mistakes here affect all newer POWER PMUs.

Test signals: unit-style validation through perf raw events for invalid masks/reserved sample modes, group scheduling tests with conflicting PMCs/cache selectors, `perf mem` source/weight sampling on POWER8/9/10, BHRB sampling tests, and architecture boot tests confirming known generic events count.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.h

Purpose: defines the raw event encoding, constraint bit layout, MMCR bit helpers, SIER decoding masks, and exported helper prototypes shared by PowerISA v2.07 and later PowerPC PMU implementations.

Important APIs/types/functions: event bit macros for EBB/BHRB/IFM/threshold/sample/cache/PMC/unit/combine/marked fields; POWER9 and POWER10 format variants such as `p9_EVENT_VALID_MASK`, `p10_EVENT_VALID_MASK`, `p10_EVENT_MMCR3_MASK`, and `p10_EVENT_THR_CMP_MASK`; constraint macros `CNST_*`, `ISA207_ADD_FIELDS`, `ISA207_TEST_ADDER`; MMCR helpers `MMCR1_*`, `MMCRA_*`, `MMCR2_*`, `MMCR3_SHIFT`; SIER helpers and prototypes for `isa207_*` functions.

Control flow and state: no runtime control flow. The file encodes the contract used by constraint solvers and PMU descriptors to translate perf event config fields into MMCR register values.

State and persistence behavior: no state. Macro constants become ABI-facing sysfs format semantics and internal register programming rules.

Dependencies and integration points: included by `isa207-common.c` and newer processor PMU files. It depends on perf event definitions, PowerPC firmware/cputable headers, `internal.h`, and shared PowerPC PMU types such as `struct mmcr_regs`.

Risks: macro shifts and masks are hardware contracts; any mismatch breaks raw event programming, group scheduling, or sampling. Power10 moved threshold compare into `attr.config1`, so users and callers must handle the extra attribute flag. Constraint adder fields must remain aligned with the generic solver's overflow checks.

Test signals: compile all ISA207-family PMUs; inspect `/sys/bus/event_source/devices/cpu/format/*`; run raw event groups with pinned/unpinned PMCs, threshold fields, BHRB/EBB, Power10 MMCR3 fields, and perf memory sampling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/isa207-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/kvm-hv-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/kvm-hv-pmu.c

Purpose: implements a system-wide `kvm-hv` PMU for nestedv2 Book3S-HV guests, exposing L0 host-wide memory usage statistics to perf in an L1 environment.

Important APIs/types/functions: `kvmppc_pmu`, `kvmppc_register_pmu`, `kvmppc_init_hostwide`, `kvmppc_update_l0_stats`, `kvmppc_pmu_event_update`, `hostwide_get_size`, `hostwide_fill_info`, `hostwide_refresh_info`, `gsb_ops_l0_stats`, and event IDs `KVMPPC_EVENT_HOST_*`.

Control flow and state: module init checks `kvmhv_is_nestedv2`, allocates a guest-state message and buffer for L0 stats, includes the five supported GSIDs, fills the request buffer, and registers the PMU. Each perf read/add/del refreshes L0 stats under `lock_l0_stats`, selects the configured statistic, and adds a positive delta to the perf count. Module exit frees the GSB/GSM and unregisters the PMU.

State and persistence behavior: no persistent storage. Runtime state is global `l0_stats`, one guest-state message, one guest-state buffer, a parser, and a spinlock. Event `prev_count` and `count` track deltas; max-style counters only increase the perf count when the returned value grows.

Dependencies and integration points: depends on nested KVM-HV v2 support, guest-state-buffer helpers (`kvmppc_gsb_*`, `kvmppc_gsm_*`, `kvmppc_gse_*`), perf PMU registration, and L0 support for host-wide GSIDs. Sysfs exposes event names and `format/event`.

Risks: if `perf_pmu_register` fails after `kvmppc_init_hostwide`, init returns without freeing allocated GSM/GSB; all reads serialize on one spinlock and perform a hypervisor communication path; counter semantics are delta-only and ignore decreases; unsupported nested versions silently skip registration with `-EOPNOTSUPP`.

Test signals: build as module/built-in with KVM Book3S-HV; boot nestedv2; verify `/sys/bus/event_source/devices/kvm-hv`; run `perf stat -e kvm-hv/host_heap/` and related events while changing nested guest memory/page-table load; test unload cleanup and non-nested registration failure.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/kvm-hv-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/mpc7450-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/mpc7450-pmu.c

Purpose: processor PMU backend for 32-bit MPC7450-family PowerPC CPUs, translating perf events into MMCR0/MMCR1/MMCR2 settings and registering an early `power_pmu`.

Important APIs/types/functions: `mpc7450_pmu`, `init_mpc7450_pmu`, `mpc7450_classify_event`, `mpc7450_threshold_use`, `mpc7450_get_constraint`, `mpc7450_compute_mmcr`, `mpc7450_get_alternatives`, `mpc7450_disable_pmc`, and generic/cache event maps.

Control flow and state: event classification groups raw events by allowable PMC sets, from any PMC to fixed PMC. Constraint generation encodes required PMC/class use and shared threshold value/scale requirements. MMCR computation counts events by class, allocates PMCs from most constrained to least constrained using `classmap`, programs threshold fields into MMCR0/MMCR2, writes PMC selector fields into MMCR0 for PMC1-2 and MMCR1 for PMC3-6, and sets counter-enable bits.

State and persistence behavior: no persistent state. The file defines a static PMU descriptor and computes per-group register values. On 32-bit, it mirrors MMCR2 into `mmcra` because the architecture aliases `SPRN_MMCRA` to `SPRN_MMCR2`.

Dependencies and integration points: depends on PowerPC perf core `register_power_pmu`, PVR helpers for 7450/7455/7447/7447A/7448 detection, `struct mmcr_regs`, and generic perf hardware/cache event IDs. Registered with `early_initcall`.

Risks: class allocation and threshold sharing are hardware-specific; multiple threshold events must agree on threshold value/scale; invalid PMC selectors are rejected only through classification; 32-bit MMCRA alias behavior is easy to regress.

Test signals: build a 32-bit PowerPC kernel for supported CPUs; boot on MPC7450-family hardware/emulator; verify PMU registration, generic cycle/instruction/cache events, raw threshold events, conflict rejection for impossible groups, and PMC disable behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/mpc7450-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/perf_regs.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/perf_regs.c

Purpose: implements PowerPC perf sampled-register support, mapping perf register IDs to `pt_regs` offsets or PMU SPR reads and validating user-requested register masks.

Important APIs/types/functions: global `PERF_REG_EXTENDED_MASK`, `pt_regs_offset`, `get_ext_regs_value`, `perf_reg_value`, `perf_reg_validate`, `perf_reg_abi`, and `perf_get_regs_user`.

Control flow and state: normal register IDs read from `pt_regs` by offset. Extended PMU IDs read live SPRs or helper `get_pmcs_ext_regs`. SIER/MMCRA return zero when unsupported by config or platform. Validation rejects empty masks and masks outside `PERF_REG_EXTENDED_MASK | PERF_REG_PMU_MASK`. ABI selection checks whether the target task is 32-bit.

State and persistence behavior: no persistent state. `PERF_REG_EXTENDED_MASK` is a global capability mask set by PMU init code such as POWER10/11 setup. Register reads are snapshots from interrupt/user contexts or current SPR state.

Dependencies and integration points: used by perf sample register collection. Depends on `asm/perf_regs.h`, `pt_regs`, PowerPC SPR access, PMU-specific extended mask setup, `is_sier_available`, `get_pmcs_ext_regs`, and task ABI helpers.

Risks: extended SPR reads may be invalid on CPUs unless the mask is set correctly; SIER and MMCRA reuse `pt_regs` `dar`/`dsisr` storage in interrupt paths, so producer and consumer must agree; user register capture ignores the provided `regs` argument and uses `task_pt_regs(current)`.

Test signals: perf record with `--sample-regs` on 32-bit and 64-bit tasks, PMU extended register sampling on POWER10, SIER-disabled systems returning zero, invalid mask rejection, and ABI values matching task mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/perf_regs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-events-list.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-events-list.h

Purpose: X-macro event list of POWER10 raw PMU event encodings consumed by `power10-pmu.c` to generate enum constants and sysfs event attributes.

Important APIs/types/functions: `EVENT(name, code)` entries for cycles, dispatch/execute stalls, completed instructions, branch completion/misprediction, L1/L2/L3/cache/TLB events, alternate cycle/instruction encodings, and synthetic memory profiling aliases `MEM_LOADS`/`MEM_STORES`.

Control flow and state: no runtime control flow. The including file defines `EVENT` differently to create enum values and event attribute pointers.

State and persistence behavior: no state. The constants become raw event ABI exposed under `/sys/bus/event_source/devices/cpu/events` for POWER10/POWER11 style PMUs.

Dependencies and integration points: included by `power10-pmu.c`; event values must match the POWER10 PMU user guide and the raw format documented in that file. Memory access events rely on marked instruction completion plus sample and threshold fields encoded in the raw value.

Risks: event-code mistakes produce wrong counts while still compiling; comments include user-visible event intent and must remain synchronized; DD1 uses a restricted subset in `power10-pmu.c`, so adding events may require DD1 table decisions.

Test signals: compile `power10-pmu.c`, inspect generated sysfs event files, run generic and raw POWER10 events on hardware, and validate memory profiling aliases with `perf mem`/sample mode.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-events-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-pmu.c

Purpose: POWER10 and POWER11 processor PMU backend built on `isa207-common`, with POWER10 raw format documentation, event/sysfs tables, cache maps, branch-history filtering, DD1 differences, and PMU registration.

Important APIs/types/functions: `power10_pmu`, `power11_pmu`, `init_power10_pmu`, `init_power11_pmu`, `power10_compute_mmcr`, `power10_bhrb_filter_map`, `power10_config_bhrb`, `power10_get_alternatives`, `power10_check_attr_config`, event/caps/format attribute groups, generic/cache event tables, and `PERF_REG_EXTENDED_MASK`.

Control flow and state: include-time event list expansion creates constants. Initialization verifies PVR, sets `PPMU_P10_DD1` and DD1-specific events when needed, sets the extended register mask to `PERF_REG_PMU_MASK_31`, registers `power10_pmu`, and advertises EBB. POWER11 clones the POWER10 descriptor and changes the name. Runtime MMCR computation delegates to `isa207_compute_mmcr` then sets `MMCR0_C56RUN`; BHRB filter mapping accepts only supported branch filter modes and programs IFM bits in MMCRA.

State and persistence behavior: no disk persistence. Static PMU descriptors and sysfs attributes persist after registration. `cur_cpu_spec->cpu_user_features2` is updated to expose EBB support. DD1 initialization mutates the global descriptor before registration.

Dependencies and integration points: depends on `isa207-common`, PVR constants, PowerPC perf core, event list header, SPR access, and perf branch sample flags. It integrates with `/sys/bus/event_source/devices/cpu` events, formats, caps, generic perf hardware IDs, cache event translation, BHRB, EBB, and extended PMU register sampling.

Risks: duplicate `GENERIC_EVENT_ATTR` macro names appear for branch/cache aliases but only selected pointers are exported per table; DD1 path must not expose unsupported non-DD1 events; POWER11 currently reuses POWER10 behavior wholesale; branch filters unsupported by hardware return `-1`; raw format fields differ from POWER9 and rely on config1 for threshold compare.

Test signals: boot POWER10 DD1 and non-DD1 plus POWER11 if available; confirm PMU name/events/formats; run generic cycles/instructions/branches/cache events; test raw Power10 fields including threshold compare in config1 and MMCR3 bits; verify BHRB filter acceptance/rejection and extended register sampling.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power10-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power5+-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power5+-pmu.c

Purpose: PMU backend for POWER5+/POWER5++ processors, covering event constraints, alternatives, marked-instruction detection, MMCR computation, generic/cache mappings, and registration.

Important APIs/types/functions: `power5p_pmu`, `init_power5p_pmu`, `power5p_get_constraint`, `power5p_compute_mmcr`, `power5p_get_alternatives`, `power5p_limited_pmc_event`, `power5p_marked_instr_event`, `find_alternative_bdecode`, `power5p_disable_pmc`, `unit_cons`, and generic/cache event maps.

Control flow and state: constraints encode fixed PMC use, PMC5/6 limited events, unit mux requirements, GRS selector fields, byte-lane selectors, and counter count. Alternative lookup handles explicit event tables, byte-decode equivalents, add-event encodings, and run-state substitutions while filtering limited PMC events according to scheduler flags. MMCR computation validates bus byte/unit sharing, selects TTM0/TTM1 units, selects byte lanes/GRS muxes, allocates PMCs, sets adder select for high bus bytes, detects marked events for MMCRA sample enable, and writes MMCR0/MMCR1.

State and persistence behavior: no persistent state. Static descriptor registration is gated by `PVR_POWER5p`. Computed register state is per scheduled group.

Dependencies and integration points: depends on `register_power_pmu`, PowerPC PVR helpers, generic PowerPC perf group constraint solver, perf hardware/cache IDs, and MMCR bit definitions from architecture headers. Flags include `PPMU_LIMITED_PMC5_6` and `PPMU_HAS_SSLOT`.

Risks: POWER5+ differs subtly from POWER5 in constraint bit placement, marked LSU masks, and extra decode alternatives; limited PMC filtering can remove all alternatives; bus byte and unit mux conflicts are complex; marked event detection is table-driven and hardware-specific.

Test signals: POWER5+ boot/registration, generic event counting, raw groups that exercise GRS/LSU byte lanes, limited PMC5/6 events with scheduler flags, marked instruction sampling, and impossible group rejection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power5+-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power5-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power5-pmu.c

Purpose: PMU backend for original POWER5 processors, implementing POWER5-specific event constraints, alternatives, marked event detection, MMCR programming, generic/cache event mapping, and PVR-gated registration.

Important APIs/types/functions: `power5_pmu`, `init_power5_pmu`, `power5_get_constraint`, `power5_compute_mmcr`, `power5_get_alternatives`, `power5_marked_instr_event`, `find_alternative_bdecode`, `power5_disable_pmc`, `unit_cons`, `grsel_shift`, and generic/cache tables.

Control flow and state: constraints track fixed PMCs, PMC1/2 vs PMC3/4 grouping, required TTM units, GRS mux fields, byte-lane selectors, unit conflicts, and total PMC1-4 use. MMCR computation first validates fixed PMC collisions, bus byte/unit compatibility, and PMC group pressure, then selects TTM muxes, byte lanes, GRS selectors, adder bits, and PMCSEL fields. Marked-event detection sets `MMCRA_SAMPLE_ENABLE` for selected direct and LSU bus events.

State and persistence behavior: no persistent state. The file exposes one static `power_pmu` descriptor and computes per-event-group MMCR values.

Dependencies and integration points: integrates with the PowerPC perf core through `register_power_pmu` when `PVR_POWER5` is detected. It depends on shared `struct power_pmu`, perf generic/cache IDs, MMCR bit definitions, and the group constraint solver's `add_fields`/`test_adder` values.

Risks: POWER5 bus muxing is highly constrained; LSU1 low-word byte remapping and GRS selector handling can reject valid events or accept bad ones if bitfields drift; PMC5/6 only support specific run/instruction events; original POWER5 differs from POWER5+ in both constraints and marked masks.

Test signals: boot on POWER5, verify PMU registration, run generic cycles/instructions/cache/branch events, schedule multi-event groups across byte lanes and units, validate marked sampling, and confirm unsupported groups fail instead of misprogramming MMCRs.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power5-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power6-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power6-pmu.c

Purpose: PMU backend for POWER6 processors, implementing event-bus constraints, PMC assignment, marked instruction sampling, alternatives, generic/cache event maps, and CPU registration.

Important APIs/types/functions: `power6_pmu`, `init_power6_pmu`, `p6_compute_mmcr`, `p6_get_constraint`, `p6_get_alternatives`, `p6_limited_pmc_event`, `power6_marked_instr_event`, `p6_disable_pmc`, `direct_event_is_marked`, `marked_bus_events`, and generic/cache tables.

Control flow and state: `p6_compute_mmcr` rejects collisions and more than six events, assigns fixed PMCs or free PMC1-4 slots, configures event-bus byte unit selectors and nest subunit selectors, sets load-lookahead and address-select bits, toggles PMCxSEL encodings for PMC3/4 bus select differences, marks sampling events, and returns MMCR0/MMCR1/MMCRA. Constraint generation mirrors those resources as adder/select fields. Alternatives come from a binary-searched presorted table plus sum-event transforms and run-state substitutions.

State and persistence behavior: no persistent state. Runtime state is a static `power_pmu` descriptor registered on `PVR_POWER6` and per-group computed MMCR values.

Dependencies and integration points: depends on PowerPC perf core, PVR detection, MMCR definitions, and scheduler flags for limited PMC filtering (`PPMU_LIMITED_PMC5_6`, `PPMU_LIMITED_PMC_OK`, `PPMU_LIMITED_PMC_REQD`, `PPMU_ONLY_COUNT_RUN`). Generic/cache maps translate perf standard events to POWER6 raw codes.

Risks: marked event detection mixes direct-event table classes with bus-event masks; limited PMC5/6 alternatives must be filtered correctly; event-bus byte conflicts and nest subunit conflicts are easy to misencode; PMCxSEL rewrites for PMC3/4 are hardware-specific.

Test signals: POWER6 boot registration, generic and raw event counting, run-state-only alternatives, limited PMC scheduling tests, marked sampling tests, and conflicting event-bus group rejection.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power6-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-events-list.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-events-list.h

Purpose: X-macro list of POWER7 event names and raw event codes used by `power7-pmu.c` to define enum constants, sysfs event attributes, and event pointers.

Important APIs/types/functions: hundreds of `EVENT(name, code)` entries covering completion, dispatch, stalls, branch prediction, LSU/cache/TLB, VSU/FPU, marked events, power/thermal events, nest pair events, and run-state counters.

Control flow and state: no runtime control flow. The including file controls expansion by defining `EVENT` as enum entry, `POWER_EVENT_ATTR`, or `POWER_EVENT_PTR`.

State and persistence behavior: no state. Event names and codes become static ABI exposed under POWER7 perf event sysfs.

Dependencies and integration points: included three times by `power7-pmu.c`. The list must remain sorted/consistent enough for generated attributes and for any events referenced by generic mappings or alternative tables.

Risks: wrong codes silently produce wrong counts; adding duplicate names can break enum or sysfs symbol generation; event availability may differ between POWER7 and POWER7+ even though the same list is used.

Test signals: compile `power7-pmu.c`, inspect sysfs events on POWER7/POWER7+, run representative raw events from major units, and compare counts against architectural expectations or vendor tables.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-events-list.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-pmu.c -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-pmu.c

Purpose: PMU backend for POWER7 and POWER7+ processors, including raw event encoding, constraint handling, alternatives, marked instruction detection, MMCR programming, sysfs event generation, generic/cache mappings, and registration.

Important APIs/types/functions: `power7_pmu`, `init_power7_pmu`, `power7_get_constraint`, `power7_compute_mmcr`, `power7_get_alternatives`, `power7_marked_instr_event`, `find_alternative_decode`, `power7_disable_pmc`, the included `power7-events-list.h`, and event/format attribute groups.

Control flow and state: constraints enforce fixed PMC uniqueness, PMC5/6 restrictions to run cycles/instructions, total PMC1-4 pressure, and shared L2 selector value. Alternatives include explicit tables, decode-event PMC swaps, and run-state substitutions. MMCR computation reserves fixed PMCs, assigns free PMC1-4 slots to unpinned events, writes MMCR1 unit/combine/L2SEL/PMCSEL fields, enables MMCRA sampling for marked instruction events, and sets MMCR0 counter-enable bits.

State and persistence behavior: no persistent state. Static PMU descriptor and sysfs attributes are registered for matching PVRs. POWER7+ adds `PPMU_SIAR_VALID`.

Dependencies and integration points: depends on `register_power_pmu`, PVR detection for `PVR_POWER7`/`PVR_POWER7p`, perf generic/cache events, generated event attributes from the event list, and common PowerPC MMCR definitions. Exposes `format/event` as `config:0-19`.

Risks: L2 events require a single shared L2SEL across a group; marked event detection is heuristic over PMCSEL/unit combinations; decode alternatives are limited to certain 4x patterns; POWER7+ behavior differs only by flag in this file.

Test signals: boot POWER7/POWER7+, verify PMU name/events/formats, run generic and selected raw events, schedule groups with conflicting L2SEL and PMC5/6 usage, test marked sampling, and check SIAR validity behavior on POWER7+.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power7-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-events-list.h -->

# sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-events-list.h

Purpose: compact X-macro list of POWER8 event encodings consumed by the POWER8 PMU implementation to define event constants and sysfs event attributes.

Important APIs/types/functions: `EVENT(name, code)` entries for cycles, stalls, completed instructions, branch events, L1/L2/L3/cache/TLB events, run-state alternates, marked events and their alternatives, dispatch/filter events, and `MEM_ACCESS`.

Control flow and state: no runtime control flow. The including POWER8 PMU file defines `EVENT` for enum and sysfs generation.

State and persistence behavior: no state. Event constants become kernel/user ABI through sysfs event names and raw config values.

Dependencies and integration points: included by the POWER8 PMU code, which shares ISA207 helpers. The alternate events listed here feed alternative scheduling and run-state equivalence logic in the POWER8 implementation.

Risks: event-code drift causes incorrect measurements; alternate pairs must remain synchronized with PMU alternative tables; `MEM_ACCESS` encodes marked-instruction random sampling assumptions and must match `isa207-common` format fields.

Test signals: compile the POWER8 PMU, verify sysfs event files, run generic/cache and alternate raw events on POWER8, and validate `MEM_ACCESS` sampling with perf memory workflows.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/perf/power8-events-list.h -->
