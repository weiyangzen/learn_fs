<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/ste-ux500-pm-domain.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/st/ste-ux500-pm-domain.c

## Purpose
Minimal ST-Ericsson ux500 genpd provider exposing the VAPE power domain.

## Important APIs, Types, And Functions
Defines no-op `pd_power_on()` and `pd_power_off()`, static `ux500_pm_domain_vape`, onecell array `ux500_pm_domains`, and probe/init functions `ux500_pm_domains_probe()` and `ux500_pm_domains_init()`.

## Control Flow
At `arch_initcall`, the platform driver binds to `stericsson,ux500-pm-domains`. Probe allocates onecell data, points it at the static VAPE domain array, initializes each domain, and registers the onecell provider.

## State And Persistence Behavior
State is static domain storage plus allocated onecell data. Power callbacks are placeholders returning success, so actual register context save/restore is expected in consumer runtime PM paths and regulator gating is not implemented here.

## Dependencies And Integration Points
Depends on ux500 DT bindings for `DOMAIN_VAPE` and `NR_DOMAINS`, generic PM domains, and a matching DT provider node.

## Risks
The callbacks do not gate hardware, so this provider mainly models dependency ordering. The probe does not check `of_genpd_add_provider_onecell()` return value and does not handle null entries in the array beyond the single VAPE domain assumption.

## Test Signals
Boot should register the VAPE provider and consumers should attach by onecell index. Functional power saving requires platform-specific regulator/runtime PM work outside this file.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/st/ste-ux500-pm-domain.c -->
