# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_tpc0_eml_spmu_regs.h

Purpose: generated register map for the TPC0 EML system performance monitoring unit. It exports 64 `mmDCORE0_TPC0_EML_SPMU_*` constants from `0x1000` to `0x1FFC`.

Important APIs/types/functions: macro-only API for performance event counters `PMEVCNTR0..5`, cycle counter low/high, trace control/status/enable, event type selectors, counter enables, interrupt enables/status/clear, overflow flags, software increment, lock/auth/device ID registers, and component/peripheral IDs.

Control flow: none. Profiling/debug code configures event selectors and enables counters, then reads event counts or interrupt/overflow status.

State and persistence behavior: event counter values accumulate in hardware and persist until reset or cleared. Enable and event-selector registers define the active profiling session.

Dependencies and integration points: EML trace/perf subsystem adjacent to ETF, STM, funnel, and bus monitor. Performance and trace collection code must use the correct EML base plus these offsets.

Risks: counter overflow, wrong event selection, or forgetting to clear state can produce misleading profiling data. Perf counters can reveal workload characteristics, so access controls matter.

Test signals: counter increments under controlled TPC workloads, overflow interrupt tests, reset/clear behavior, event selector validation, and component ID checks.
