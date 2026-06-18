# sources/distributed-fs/ceph-client/arch/mips/kernel/perf_event_mipsxx.c

## Purpose
Implements the Linux perf PMU backend for MIPS hardware performance counters. It maps generic, cache, and raw perf events to CPU-family-specific CP0 PerfCtl/PerfCnt encodings, manages per-CPU counter allocation, handles overflows, and registers the MIPS PMU as the `"cpu"` perf provider during early boot.

## Important APIs, Types, and Functions
- `struct cpu_hw_events` stores per-CPU active `perf_event *` slots, counter-use bitmap, and saved PerfCtl values used when global PMU disable/enable pauses local counters.
- `struct mips_perf_event` describes a hardware event id, usable counter mask, and MIPS MT range (`T`, `V`, `P`) for thread/VPE/processor-wide counting.
- `struct mips_pmu mipspmu` is the selected runtime PMU descriptor: counter width, overflow bit, IRQ, event maps, raw mapper, and read/write counter callbacks.
- `mipspmu_event_init()`, `__hw_perf_event_init()`, `mipspmu_add()`, `mipspmu_del()`, `mipspmu_start()`, `mipspmu_stop()`, and `mipspmu_read()` implement the `struct pmu` operations.
- `mipsxx_pmu_read_counter*()`, `mipsxx_pmu_write_counter*()`, `mipsxx_pmu_read_control()`, and `mipsxx_pmu_write_control()` access CP0 performance registers, including VPE counter swizzling for shared TC counters.
- `mipsxx_pmu_map_raw_event()` and `octeon_pmu_map_raw_event()` validate raw perf configs and infer counter masks for CPU-specific event banks.
- `mipsxx_pmu_handle_shared_irq()` is the core overflow handler, used directly or via `mipsxx_pmu_handle_irq()`.
- `init_hw_perf_events()` detects supported CPU families, chooses event/cache maps, counter widths, IRQ source, resets counters, and calls `perf_pmu_register()`.

## Control Flow
Initialization starts at `early_initcall(init_hw_perf_events)`: it counts hardware counters, adjusts for shared TC counter mode, discovers the perf IRQ, selects maps based on `current_cpu_type()`, determines 32/48/64-bit counter behavior, resets all counters on all CPUs, and registers the PMU. When a perf event is opened, `mipspmu_event_init()` rejects branch stack sampling and unsupported types, lazily reserves the IRQ path using `active_events` and `pmu_reserve_mutex`, maps the requested event, initializes period accounting, validates group counter fit, and installs `hw_perf_event_destroy()`. Adding an event allocates a compatible counter from `used_mask`, disables any stale hardware state, attaches the event to `cpuc->events[idx]`, and optionally starts it. Starting programs the sample period and saved control word; stopping disables counting, updates software counts, and marks the perf event stopped/up-to-date. On overflow, the handler pauses local counters, takes the shared-TC read lock when configured, scans active counters for the overflow bit, updates periods, calls `perf_event_overflow()`, resumes counters, and runs pending irq work.

## State and Persistence
State is hardware and per-CPU rather than persistent across boots. `DEFINE_PER_CPU(cpu_hw_events)` tracks current counter assignment. `mipspmu` is global static runtime configuration chosen once at boot. `active_events` and `pmu_reserve_mutex` manage lazy IRQ reservation lifetime. `raw_event` is a shared scratch descriptor protected by `raw_event_mutex`. Hardware CP0 PerfCtl/PerfCnt registers hold programmed events and counts; `saved_ctrl[]` mirrors control words so counters can be paused/resumed around perf-wide disable and shared IRQ serialization. No filesystem persistence is involved.

## Dependencies and Integration Points
Integrates with the generic perf core (`struct pmu`, `perf_event_update_userpage()`, `perf_event_overflow()`), MIPS CP0 register accessors, CPU feature detection, MIPS MT/VPE topology, timer interrupt sharing through `perf_irq`, and platform IRQ discovery via `get_c0_perfcount_int` or `cp0_perfcount_irq`. CPU-family event tables cover MIPS 24K/34K/74K/proAptiv/P5600/P6600/I6400/I6500/1004K/1074K/interAptiv, Loongson32/64, Cavium Octeon, and BMIPS5000.

## Risks
Counter allocation is greedy and can reject valid groups if an earlier event occupies a counter needed by a more constrained event. Shared TC counters rely on careful pause/read-lock/write-lock ordering; mistakes can deadlock or count while disabled. Raw event validation is CPU-specific and easy to drift from hardware manuals. Loongson type 2 has 48-bit counters and 10-bit event ids, so generic 64-bit assumptions would misprogram counters. IRQ sharing with the timer depends on correct `perf_irq` save/restore. The overflow test relies on the configured overflow bit and counter masking.

## Test Signals
Boot logs should show `"Performance counters: <name> PMU enabled"` with expected counter count/width/IRQ. `perf stat` with generic events, cache events, and raw events should either count or return `EOPNOTSUPP` consistently per CPU. Event groups should fail cleanly when counter masks cannot fit. Overflow sampling should deliver samples and not lose timer interrupts when sharing the timer IRQ. CPU hotplug and perf open/close cycles should reset counters and release IRQ state without warnings.
