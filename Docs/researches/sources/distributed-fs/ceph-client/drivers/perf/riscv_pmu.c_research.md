# sources/distributed-fs/ceph-client/drivers/perf/riscv_pmu.c

Purpose: shared RISC-V perf PMU framework used by concrete backends such as SBI PMU and legacy CSR-only PMU. It provides generic perf callback wiring, counter accounting, mmap user-page support, period programming, and CSR read helpers.

Important APIs, types, and functions: exported helpers include `arch_perf_update_userpage`, `riscv_pmu_ctr_read_csr`, `riscv_pmu_ctr_get_width_mask`, `riscv_pmu_event_update`, `riscv_pmu_stop`, `riscv_pmu_event_set_period`, `riscv_pmu_start`, and `riscv_pmu_alloc`. Backend callbacks live in `struct riscv_pmu` from `<linux/perf/riscv_pmu.h>`: `event_map`, `ctr_get_idx`, `ctr_get_width`, `ctr_read`, `ctr_start`, `ctr_stop`, `ctr_clear_idx`, `csr_index`, and optional map/unmap hooks.

Control flow: allocation creates the PMU and per-CPU `cpu_hw_events` arrays, then installs generic `struct pmu` callbacks. Event init rejects branch stack sampling, asks the backend to map perf attributes to hardware or firmware encoding, sets `hwc->idx = -1`, stores `event_base` and `config`, and initializes non-sampling periods to half the counter width. Add asks the backend for a counter index, records the event in per-CPU slots, and starts on demand. Start computes a conservative initial value and calls the backend `ctr_start`; stop calls `ctr_stop`, updates the software count, and marks perf state bits.

State and persistence: persistent runtime state is per-CPU event slots, `n_events`, optional snapshot address fields initialized for later SBI use, and perf `local64_t` counters. `arch_perf_update_userpage` publishes counter width, optional user-readable counter index, and sched-clock conversion parameters to mmap consumers.

Dependencies and integration: depends on core perf, RISC-V CSRs, sched clock, SMP/per-CPU state, and backend platform drivers. It is intentionally backend-neutral.

Risks: wrap handling depends on accurate backend counter width; bad widths cause deltas to undercount or overcount. User mmap counter access depends on backend flags and valid CSR index. `riscv_pmu_ctr_read_csr` has a whitelist switch for cycle/instret/HPM CSR ranges; invalid CSR values return `-EINVAL` as an unsigned long and log an error. Test signals include backend registration, `perf stat` hardware/cache/raw events, mmap reads when allowed, 32-bit high/low CSR paths, and sampling period behavior near wrap.
