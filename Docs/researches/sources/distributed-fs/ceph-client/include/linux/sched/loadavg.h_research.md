# sources/distributed-fs/ceph-client/include/linux/sched/loadavg.h

Purpose: declares fixed-point global load-average constants and helpers.

Important APIs and types: `avenrun[]`, `get_avenrun()`, `FSHIFT`, `FIXED_1`, `LOAD_FREQ`, `EXP_1`, `EXP_5`, `EXP_15`, `calc_load()`, `calc_load_n()`, `LOAD_INT()`, `LOAD_FRAC()`, and `calc_global_load()` make up the interface.

Control flow: scheduler load code periodically samples active tasks, applies exponential decay constants, and exposes 1/5/15-minute load averages through proc/sysinfo consumers.

State and persistence: global `avenrun` stores runtime fixed-point load averages. It is not persisted across boot.

Dependencies and integration points: depends on HZ and scheduler active-count accounting. Integrates with `/proc/loadavg`, sysinfo, and NOHZ load updates.

Risks and test signals: risks include fixed-point rounding drift, wrong active-task counts under NOHZ, and ABI-visible load output changes. Test load generation, idle/nohz CPUs, proc/sysinfo values, and low-HZ/high-HZ configs.
