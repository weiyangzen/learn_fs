<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Makefile

## Purpose

The Makefile maps i.MX PM-domain Kconfig symbols to build objects for legacy GPC, GPCv2, SCU, i.MX8M/i.MX8MP block controls, i.MX93 slice domains, and i.MX9 block controls.

## Important APIs, types, and functions

Rules build `gpc.o`, `gpcv2.o`, `scu-pd.o`, `imx8m-blk-ctrl.o`, `imx8mp-blk-ctrl.o`, `imx93-pd.o`, and `imx93-blk-ctrl.o` from their corresponding config symbols.

## Control flow

No runtime flow exists. Kbuild expands selected `obj-*` lines into built-in or module artifacts.

## State and persistence behavior

The persistent effect is the kernel build graph and generated objects/modules.

## Dependencies and integration points

It depends on i.MX PM-domain and architecture Kconfig symbols and integrates with the platform drivers registered by the compiled objects.

## Risks and edge cases

`CONFIG_IMX8M_BLK_CTRL` intentionally builds both generic and i.MX8MP-specific block-control drivers. `imx93-pd.o` follows `SOC_IMX9`, while `imx93-blk-ctrl.o` follows `IMX9_BLK_CTRL`.

## Test signals

Inspect verbose build output, `modules.order`, and OF aliases for representative built-in and module configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/imx/Makefile -->
