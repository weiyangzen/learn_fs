# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci-domain.c

Purpose: builds generic PM domains for PSCI CPU idle hierarchical topology, allowing cpuidle to coordinate shared domain states through genpd and PSCI OS-initiated mode when available.

Important APIs and functions: `psci_pd_init()` allocates a genpd from DT idle domain states with `dt_idle_pd_alloc()`, sets CPU/IRQ-safe flags, configures power-off behavior depending on OSI support, initializes genpd with `pm_domain_cpu_gov` when states exist, and registers an OF provider. `psci_pd_power_off()` calls `psci_set_domain_state()` with the selected domain state data. Probe scans PSCI child nodes with `#power-domain-cells`, initializes providers, links topology with `dt_idle_pd_init_topology()`, and calls `psci_set_osi_mode()`.

Control flow and state: a global list tracks provider nodes for reverse-order cleanup on failure. In PC mode domains are marked always-on; in OSI mode they can power off and active wakeup is enabled, with PREEMPT_RT forcing runtime PM always-on outside system suspend.

Dependencies and integration points: depends on DT `arm,psci-1.0`, DT idle genpd helpers, PSCI OSI support, generic PM domains, runtime PM, and `cpuidle-psci.c` domain-state handoff.

Risks and test signals: risks include genpd cleanup using plain `kfree()` rather than full `dt_idle_pd_free()` after provider removal, OSI mode failure tearing down all domains, topology requiring correctly nested DT power domains, and PREEMPT_RT limiting runtime idle use. Test signals include provider creation for every CPU power-domain node, topology links in genpd debugfs, log line selecting OSI or PC mode, `psci_pd_power_off()` setting per-CPU domain state, and cleanup on malformed topology.
