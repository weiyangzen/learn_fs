# sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-drv.c

Purpose: SPARC sun4v Niagara2/VF/KT/M4/M7 hardware RNG driver that exposes the hypervisor RNG through the Linux `hwrng` core. It supports guest read-only use and control-domain configuration/self-test.

Important APIs, types, and functions: `struct n2rng`, `struct n2rng_unit`, `n2rng_probe()`, `n2rng_remove()`, `n2rng_data_read()`, `n2rng_work()`, `n2rng_control_selftest()`, `n2rng_control_configure_units()`, and hypervisor wrappers around `sun4v_rng_*`. Device matching selects `struct n2rng_template` for chip version and multi-unit capability.

Control flow: probe registers RNG HVAPI v2 then v1 fallback, allocates per-unit control state, detects control-domain access, registers `hwrng`, and schedules delayed work. Work either performs guest data-read validation or, in control domain, disables preemption, runs diagnostic self-tests per unit, configures control registers, and marks `N2RNG_FLAG_READY`. Reads return cached upper/lower halves of a 64-bit HV read and schedule retest on failures.

State and persistence: state is in flags, per-unit control arrays, HV API version, health parameters, and delayed work. No disk persistence. `N2RNG_FLAG_SHUTDOWN` prevents retry work after remove.

Dependencies and integration: depends on SPARC hypervisor APIs, OF platform matching, `hwrng`, delayed work, physical-address-safe buffers, and `n2rng.h` constants/assembly entry points.

Risks and test signals: risks include HV busy/block retry limits, static `retries` shared across devices in `n2rng_work()`, control-domain self-test timing, multi-unit `rng-#units` DT property correctness, and physical address alignment. Tests should exercise HVAPI v1/v2 fallback, guest vs control behavior, self-test failure retry, remove during delayed work, and hwrng read recovery.
