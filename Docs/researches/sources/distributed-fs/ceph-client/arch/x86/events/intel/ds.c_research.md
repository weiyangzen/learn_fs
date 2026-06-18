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
