<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rmobile-sysc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rmobile-sysc.c

## Purpose
Renesas R-Mobile SYSC power-domain framework. It discovers PM domain nodes under `renesas,sysc-rmobile`, creates recursive generic PM domains, handles simple SPDCR/SWUCR/PSTR power sequencing, and marks domains containing special hardware as always-on or console-protected.

## Important APIs, Types, And Functions
- `struct rmobile_pm_domain` wraps genpd with governor, optional suspend hook, MMIO base, and PSTR bit shift.
- Power functions are `rmobile_pd_power_down()`, `__rmobile_pd_power_up()`, and `rmobile_pd_power_up()`.
- Domain setup uses `get_special_pds()`, `add_special_pd()`, `pd_type()`, `rmobile_setup_pm_domain()`, `rmobile_init_pm_domain()`, and recursive `rmobile_add_pm_domains()`.
- `rmobile_init_pm_domains()` is the postcore entry point.

## Control Flow
At postcore init, the driver scans all `renesas,sysc-rmobile` nodes, maps the controller, locates the `pm-domains` child, scans CPU/console/debug/memory-controller consumers once, and recursively creates domains for child nodes. A child with no `reg` property is treated as a top-level always-on domain; otherwise `reg` gives the PSTR bit. Normal domains get CPG MSTP PM-clock attach hooks, active wakeup, no-stay-on, and are powered up during initialization. Parent recursion adds subdomains and registers each child node as a simple provider.

## State And Persistence Behavior
Per-domain state is dynamically allocated and retained for genpd lifetime. `special_pds` is initdata used only to classify domains. Hardware state is in SPDCR/SWUCR/PSTR. Console domains can veto suspend via `rmobile_pd_suspend_console()` when console suspend is disabled.

## Dependencies And Integration Points
Depends on Device Tree hierarchy, CPG MSTP clock attach helpers, generic PM domains, PM clock support, OF console pointer, and special compatible matches for debug/memory controller devices. Consumers bind through per-domain simple providers.

## Risks
Recursive provider creation can leak partially allocated domains on failure because init code does not unwind. Special-domain classification depends on consumer `power-domains` phandles being present and matching exactly. Poll timeouts use small retry windows; hardware delays outside assumptions could fail power transitions.

## Test Signals
Boot should create providers for all PM domain child nodes and classify CPU/console/debug/memctl domains correctly. Runtime PM should power-cycle normal domains and retain console/CPU/debug/memory-controller domains. Console suspend tests should verify `no_console_suspend` prevents console domain power-off.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/renesas/rmobile-sysc.c -->
