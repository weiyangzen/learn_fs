# sources/distributed-fs/ceph-client/drivers/cpuidle/cpuidle-psci.h

Purpose: declares the cross-file PSCI cpuidle helpers shared by the PSCI CPU idle driver and PSCI CPU power-domain driver.

Important APIs and types: forward declarations cover `struct device_node` and `struct generic_pm_domain`. `psci_set_domain_state()` lets a genpd power-off callback publish the selected domain state to the current CPU's PSCI idle entry path. `psci_dt_parse_state_node()` parses and validates a DT idle-state node into a PSCI suspend parameter.

Control flow and state: the header has no state; it defines the narrow contract that connects `cpuidle-psci-domain.c` to per-CPU state in `cpuidle-psci.c`.

Dependencies and integration points: depends on `u32` from included kernel types in the including C files and on PSCI driver implementation details.

Risks and test signals: risks include no standalone include of `<linux/types.h>`, so compile success depends on including files having already provided `u32`; API misuse would set domain state outside the intended current-CPU idle path. Test signals are successful compilation of both PSCI files and domain idle entries observing the state selected by genpd.
