# sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu_legacy.c

Purpose: fallback RISC-V PMU backend for systems without the SBI PMU extension. It exposes only the always-present architectural cycle and instruction-retired counters through the shared RISC-V perf framework.

Important APIs, types, and functions: `pmu_legacy_ctr_get_idx` maps `PERF_COUNT_HW_CPU_CYCLES` to CSR cycle index 0 and `PERF_COUNT_HW_INSTRUCTIONS` to instret index 2. `pmu_legacy_read_ctr` reads `CSR_CYCLE`/`CSR_INSTRET` and their high halves on 32-bit builds. `pmu_legacy_event_mapped` and `pmu_legacy_event_unmapped` toggle `PERF_EVENT_FLAG_USER_READ_CNT` for mmap user access. `riscv_pmu_legacy_skip_init` is called by the SBI backend to suppress fallback registration.

Control flow: late init registers a simple platform driver and synthetic platform device unless `pmu_init_done` has been set. Probe allocates a shared `struct riscv_pmu`, sets its parent, then `pmu_legacy_init` fills backend callbacks, counter mask, capabilities, and registers PMU name `cpu` with raw type. Start cannot program hardware; it snapshots the current CSR into `prev_count` so generic update can calculate deltas.

State and persistence: only `pmu_init_done` persists globally during boot. Runtime state lives in generic perf structures and per-CPU slots allocated by `riscv_pmu_alloc`. The hardware counters cannot be stopped or reset by this backend.

Dependencies and integration: depends on platform-device bootstrap, generic RISC-V PMU code, RISC-V CSR access, and perf core. It intentionally marks `PERF_PMU_CAP_NO_INTERRUPT` and `PERF_PMU_CAP_NO_EXCLUDE` because it lacks overflow interrupts and privilege filtering.

Risks: unsupported events return `-ENOENT`; sampling and filtering are not useful because counters are free-running and cannot be programmed. Counts are deltas from global architectural counters, not isolated per-event hardware programs. The file comments note the implementation is temporary and intended for removal. Test signals include boot without SBI PMU, exactly two accepted hardware events, no interrupt sampling, correct 32-bit high-half reads, and SBI systems skipping legacy registration.
