# sources/distributed-fs/ceph-client/drivers/pmdomain/apple/pmgr-pwrstate.c

Purpose: Apple SoC PMGR power-state driver exposing each PMGR pwrstate node as a generic PM domain and reset controller.

Important APIs/types/functions: `struct apple_pmgr_ps` holds device, genpd, reset controller, parent syscon regmap, register offset, and optional minimum state. `apple_pmgr_ps_set()` writes target power state and optionally enables PMGR auto mode; `apple_pmgr_ps_is_active()` detects boot state; `apple_pmgr_ps_power_on/off()` implement genpd callbacks; `apple_pmgr_reset_assert/deassert/reset/status()` implement reset-controller operations; `apple_pmgr_ps_probe()` registers provider, parent domains, and reset controller.

Control flow: probe gets the parent syscon regmap, reads `label` and `reg`, configures IRQ-safe genpd callbacks, applies optional `apple,min-state`, detects active or auto-enabled state, handles `apple,always-on` by powering on if necessary and setting `GENPD_FLAG_ALWAYS_ON`, enables auto-PM for active domains, initializes genpd with current state, registers a simple provider, adds declared parent power domains as genpd subdomains, removes the platform device from regular PM participation, and registers one reset line. Power transitions clear sticky flags, set target state, poll actual state up to 100 us, and optionally enable auto mode. Reset assert disables device access then asserts reset under the genpd spinlock; deassert clears reset and device-disable.

State and persistence: software keeps one domain/reset provider per DT node. Hardware state is the PMGR register containing target/actual states, reset, auto-enable, min-state, parent-off, and sticky clock/power-gated flags. No disk persistence.

Dependencies/integration: depends on DT child nodes below a PMGR syscon, generic PM domains, OF genpd provider/subdomain APIs, regmap polling, and reset-controller framework. Consumers use both `power-domains` and reset phandles with zero reset cells.

Risks: resets only work while powered and clocked; the driver logs but does not prevent reset while off or poweroff with reset active. Poll timeout is short and hardware-sensitive. Parent-domain linking must handle probe deferral correctly. The driver deliberately removes the platform device from regular PM because hierarchy handles power, so changing that can double-manage domains.

Test signals: each DT node with label/reg registers a genpd and reset provider; active boot domains remain active and auto-enabled; always-on domains recover if off at boot; parent subdomain links succeed or defer; reset consumers see assert/deassert/status changes; power state polling reaches requested states without timeout.
