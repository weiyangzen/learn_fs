<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpc.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpc.c

## Purpose

`gpc.c` implements legacy i.MX6 General Power Controller domains for ARM, PU, DISPLAY, and PCI. It supports old top-level onecell DT bindings and newer `pgc` child-node bindings, controlling GPC/PGC registers plus optional regulators and reset-propagation clocks.

## Important APIs, types, and functions

`struct imx_pm_domain` embeds `generic_pm_domain` and stores regmap, regulator, clocks, register offset, GPC request bit, and IPG rate. `imx6_pm_domain_power_on()` enables supply/clocks, requests power-up through `GPC_CNTR`, polls completion, and disables reset clocks. `imx6_pm_domain_power_off()` requests power-down, waits ISO delays, and disables supply. Probe paths are `imx_pgc_power_domain_probe()`, `imx_gpc_old_dt_init()`, and `imx_gpc_probe()`.

## Control flow

The top-level probe maps the GPC regmap, applies errata flags, and either registers old static onecell domains or instantiates one child platform device per `pgc` node. Child probes parse supply/clocks, initially power on if needed, initialize genpd, and register simple providers. Genpd callbacks then perform the register-level power sequences.

## State and persistence behavior

State is static domain descriptors plus copied child platform data. Hardware state persists in GPC request/status and PGC control/delay registers, regulator state, and clock state. Errata flags can force PU runtime-always-on or DISPLAY always-on.

## Dependencies and integration points

The driver depends on regmap MMIO, clocks, regulators, platform devices, OF, genpd, and device links. It matches i.MX6 GPC compatibles and exports domains to DT consumers.

## Risks and edge cases

Static descriptor copying requires care, IPG rate affects ISO delay calculation, errata intentionally change runtime behavior, old-binding removal is narrow, and missing optional supplies or excessive clocks can alter sequencing.

## Test signals

Test old/new DT bindings, all compatibles, PU supply and clocks, request polling timeout, errata behavior, provider registration, runtime PM for GPU/VPU/display/PCI consumers, and remove paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/gpc.c -->
