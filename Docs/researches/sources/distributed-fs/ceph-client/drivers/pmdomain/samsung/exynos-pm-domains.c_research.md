<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/exynos-pm-domains.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/exynos-pm-domains.c

## Purpose
Samsung Exynos generic PM domain driver. It creates one genpd per DT power-domain node, toggles the local power control register, waits for status, optionally links parent/child domains, and registers a simple provider.

## Important APIs, Types, And Functions
- `struct exynos_pm_domain_config` carries the `local_pwr_cfg` bit pattern for control/status.
- `struct exynos_pm_domain` stores MMIO base, genpd, and config bits.
- `exynos_pd_power()`, `exynos_pd_power_on()`, and `exynos_pd_power_off()` implement register toggling.
- `exynos_pd_probe()` maps the node, initializes genpd, registers provider, and adds an optional subdomain link.

## Control Flow
The core-init driver binds to `samsung,exynos4210-pd` or `samsung,exynos5433-pd`, allocates a domain, names it from `label` or node basename, maps registers, installs callbacks, optionally powers off Exynos4210 ARM domains at boot to reset splash-screen handoff state, reads status to choose the initial off flag, initializes genpd, registers the node as a simple provider, and if the node references a parent power domain, adds this node as a subdomain.

## State And Persistence Behavior
Per-domain runtime state is the MMIO base and local power bit mask. Hardware status at `base + 0x4` determines initial genpd state. The driver enables runtime PM on the platform device but does not implement remove/unwind.

## Dependencies And Integration Points
Depends on DT nodes with register resources, optional `label`, optional parent `power-domains`, generic PM domains, and Exynos-compatible control/status layout. Consumers reference each node as a power-domain provider.

## Risks
The polling loop has a fixed roughly 1 ms timeout. `of_iomap()` mapping is not devm-managed, and provider/subdomain failures are only partially unwound. Parent phandle parsing after provider registration means partial success can leave the child provider registered even if subdomain linking fails.

## Test Signals
Boot should register each Exynos PD node, optional subdomain log should show correct parent/child relation, and power toggles should complete without `enable/disable failed` timeout logs. Splash-screen reset behavior on Exynos4210 ARM configs should be validated.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/samsung/exynos-pm-domains.c -->
