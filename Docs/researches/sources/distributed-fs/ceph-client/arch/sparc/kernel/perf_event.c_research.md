# sources/distributed-fs/ceph-client/arch/sparc/kernel/perf_event.c

## Purpose
sparc64 hardware performance event support for Linux perf. Maps generic/raw/cache events to SPARC PMU encodings, schedules limited counters, programs PCR/PIC via `pcr_ops`, handles overflow NMIs, arbitrates with the NMI watchdog, and captures callchains.

## Important APIs, Types, and Functions
`struct cpu_hw_events` tracks per-CPU events, encoded values, counter assignments, PCR shadows, enable state, and transactions. `struct perf_event_map` stores event encoding and allowed PIC mask. `struct sparc_pmu` describes each PMU generation. PMU tables cover Ultra3, Niagara1, Niagara2/3, Niagara4/5, and SPARC M7. `sparc_check_constraints()` assigns counters or rejects conflicts. The `struct pmu` callbacks are implemented by `sparc_pmu_event_init/add/del/start/stop/read` and transaction functions. `perf_event_nmi_handler()` processes overflows. `perf_callchain_kernel/user()` collect sample stacks.

## Control Flow
`init_hw_perf_events()` calls `pcr_arch_init()`, selects a PMU by `sparc_pmu_type`, registers PMU `cpu`, and installs an NMI notifier. Event init maps attributes, checks group constraints, grabs PMCs from the watchdog, and sets periods. Enable/start paths assign counters, calculate PCR values, and program PIC periods. NMI handling updates counts, reloads overflowed counters, and calls `perf_event_overflow()`.

## State and Persistence
Per-CPU `cpu_hw_events` is main scheduler state. Global state includes `sparc_pmu`, `pmu`, `active_events`, and `pmc_grab_mutex`. PCR/PIC hardware state is shadowed in `cpuc->pcr[]`. Perf event counts use `local64`. No persistence.

## Dependencies and Integration Points
Uses Linux perf, kprobes, ftrace graph tracing, scheduler clock, atomic/mutex APIs, user access helpers, stack validation, NMI infrastructure, and `pcr_ops`.

## Risks and Test Signals
Older PMUs require matching excludes and conflict checks. Niagara1 has a hardwired/free-running counter. T4+ disables HV tracing. Transaction failure paths are delicate. Overflow detection depends on 32-bit counter semantics. Test with `perf stat`, sampling, unsupported cache-event rejection, group constraints, watchdog restore, and callchain collection without fault-state corruption.
