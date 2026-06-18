# sources/distributed-fs/ceph-client/include/linux/energy_model.h

Purpose: scheduler/device energy model interface describing performance states, power/cost tables, and CPU performance domains used by Energy Aware Scheduling and device power estimation.

Important APIs/types/functions: `struct em_perf_state`, `struct em_perf_table`, `struct em_perf_domain`, flags `EM_PERF_STATE_INEFFICIENT`, `EM_PERF_DOMAIN_*`, callback `struct em_data_callback`, registration/update helpers, `em_cpu_get()`, `em_pd_get()`, `em_table_alloc/free()`, `em_cpu_energy()`, `em_pd_get_efficient_state()`, `em_perf_state_from_pd()`, and disabled stubs when `CONFIG_ENERGY_MODEL` is off.

Control flow: a CPU/device provider registers a performance domain with callbacks; EM code builds cost tables and updates them under RCU/kref. Scheduler hot paths read tables under RCU and compute energy by mapping utilization to an efficient performance state and multiplying `ps->cost * sum_util`.

State/persistence: runtime state includes RCU-protected performance tables, per-domain cpumasks, limits, flags, and kobjects. No disk persistence; data may reflect firmware/DT/driver power tables.

Dependencies/integration: cpumasks, device model, scheduler topology/cpufreq, jump labels, RCU, krefs, thermal/capacity limits.

Risks/test signals: risks are overflow on 32-bit platforms, stale RCU table access, incorrect inefficient-state filtering, mismatched cpumasks/CPUFreq policies, and invalid power/frequency monotonicity. Test EM registration, EAS scheduling decisions, hotplug, table updates, chip binning, disabled config stubs, and lockdep RCU assertions.
