<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm2835-pm.c -->
# sources/distributed-fs/ceph-client/drivers/mfd/bcm2835-pm.c

Purpose: implements the Broadcom BCM2835/BCM2711/BCM2712 PM MFD parent. It maps PM and optional ASB register ranges, always creates a watchdog child, and conditionally creates a power-domain child when hardware resources indicate full PM support.

Important APIs and functions: `bcm2835_pm_probe` allocates and initializes shared `struct bcm2835_pm`; `bcm2835_pm_get_pdata` maps register resources in new `reg-names` or old positional DT layouts. Child cells are `"bcm2835-wdt"` and `"bcm2835-power"`.

Control flow: probe stores SoC match data, maps the PM base plus optional `asb` and `rpivid_asb` regions, registers the watchdog child, then registers the power child if ASB registers are available or the SoC is BCM2712. Old DTBs without `reg-names` are supported by positional resources.

State and persistence: `struct bcm2835_pm` stores device pointer, SoC type, PM base, ASB base, and RP1/RPi video ASB base. The parent does not directly manipulate hardware state beyond mapping resources; children perform watchdog and power-domain operations.

Dependencies and integration points: depends on OF platform matching, platform MMIO resources, MFD core, and public BCM2835 PM definitions. It integrates with downstream watchdog and power-domain drivers through parent driver data and MFD children.

Risks: optional ASB mappings silently become NULL on mapping errors, disabling or reducing power-domain support rather than failing probe. Old positional resource fallback is necessary for compatibility but easy to break with DT changes. The file lacks an explicit `MODULE_LICENSE`, which is unusual for a module source.

Test signals: probe with old and new DT resource layouts, watchdog child creation on all compatibles, power child creation only when ASB or BCM2712 conditions are met, BCM2711/BCM2712 resource coverage, and child watchdog/power-domain functional tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mfd/bcm2835-pm.c -->
