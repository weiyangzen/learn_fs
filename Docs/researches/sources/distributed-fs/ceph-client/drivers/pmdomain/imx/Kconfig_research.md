<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Kconfig

## Purpose

This Kconfig fragment defines i.MX PM-domain provider options for GPCv2, i.MX8M block controls, i.MX9 block controls, and SCU firmware-backed domains.

## Important APIs, types, and functions

`IMX_GPCV2_PM_DOMAINS` depends on i.MX/OF compile-test plus PM, selects genpd and regmap MMIO, and defaults for i.MX7D. `IMX8M_BLK_CTRL` and `IMX9_BLK_CTRL` are bools selected by matching SoC and GPCv2 symbols. `IMX_SCU_PD` depends on `IMX_SCU`.

## Control flow

There is no runtime flow. Kconfig resolution decides which provider objects the Makefile builds and which framework dependencies are selected.

## State and persistence behavior

The only persistent output is kernel configuration. It controls whether provider drivers, OF match tables, initcalls, and modules are present.

## Dependencies and integration points

It integrates with `ARCH_MXC`, `SOC_IMX7D`, `SOC_IMX8M`, `SOC_IMX9`, genpd, common clock, regmap MMIO, and i.MX SCU firmware support.

## Risks and edge cases

Hidden block-controller symbols can silently omit providers if SoC symbols are missing. `IMX_SCU_PD` relies on broader platform genpd availability. Compile-test coverage is broader for GPCv2 than for SoC-default block controllers.

## Test signals

Check config matrices for i.MX7D, i.MX8M, i.MX9, SCU-enabled SoCs, and COMPILE_TEST; verify selected objects and dependency closure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Kconfig -->
