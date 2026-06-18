# Research: sources/distributed-fs/ceph-client/drivers/pmdomain/mediatek/airoha-cpu-pmdomain.c

Purpose: Airoha EN7581 CPU power/performance-state provider. It exposes an always-on CPU genpd and a read-only CPU clock backed by ATF/SMCCC AVS firmware calls.

Important APIs and functions: `struct airoha_cpu_pmdomain_priv` embeds `clk_hw` and `generic_pm_domain`. `airoha_cpu_pmdomain_clk_get()` invokes `AIROHA_SIP_AVS_HANDLE` with `AIROHA_AVS_OP_GET_FREQ` and reports MHz as Hz. `airoha_cpu_pmdomain_set_performance_state()` invokes `AIROHA_AVS_OP_FREQ_DYN_ADJ` and treats response bit 0 set as failure. Probe registers the clock, OF clock provider, PM domain, and genpd provider; remove unregisters provider and genpd.

Control flow: probe allocates private state, registers a `CLK_GET_RATE_NOCACHE` clock named `cpu`, publishes it with `of_clk_hw_simple_get`, initializes an always-on domain named `cpu_pd`, then publishes a simple genpd provider. There are no power on/off callbacks; the only genpd operation is performance-state setting.

State and persistence behavior: no persisted state. Firmware is the source of truth for frequency and performance state. The PM domain remains always on, so Linux controls frequency/performance votes rather than CPU power gating.

Dependencies and integration points: requires ARM SMCCC, common clock provider APIs, platform driver matching `airoha,en7581-cpufreq`, genpd, and CPUFreq/OPP consumers that use the clock and PM performance states.

Risks: firmware response format is trusted; only bit 0 is checked for set-performance failure. `determine_rate()` returns success without rounding or applying a new rate, so consumers must use performance states rather than `clk_set_rate()`. The SMCCC call has no locking, retries, or timeout abstraction.

Test signals: DT probe should create `cpu` clock and `cpu_pd`. CPUFreq should observe rate changes after performance-state requests. Firmware error injection should return `-EINVAL` when bit 0 is set.
