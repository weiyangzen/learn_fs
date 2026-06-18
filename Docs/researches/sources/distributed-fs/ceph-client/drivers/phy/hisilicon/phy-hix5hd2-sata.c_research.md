# sources/distributed-fs/ceph-client/drivers/phy/hisilicon/phy-hix5hd2-sata.c

## Purpose
HIX5HD2 SATA PHY provider. It optionally powers the PHY through a peripheral syscon bit, resets and configures the SATA PHY analog parameters, and steps speed-mode control so settings take effect.

## Important APIs, types, and functions
- `struct hix5hd2_priv` stores MMIO base and optional peripheral syscon.
- `hix5hd2_sata_phy_init()` reads optional `hisilicon,power-reg`, sets power bit, programs MPLL/ref/reset, amplitude, pre-emphasis, and speed mode registers.
- Probe maps one memory resource, optionally gets `hisilicon,peripheral-syscon`, creates one PHY, and registers simple xlate.

## Control flow
Only `.init` is implemented. Init optionally powers via syscon, asserts/deasserts PHY reset with delays, programs analog tuning, then writes GEN1, GEN3, and final GEN2 speed-mode sequences.

## State and persistence
No driver-managed persistent state. Hardware registers retain analog and power settings.

## Dependencies and integration points
Generic PHY, platform MMIO, optional syscon/regmap, OF property `hisilicon,power-reg`. Used by SATA controller consumers.

## Risks and test signals
Risks include using `devm_ioremap()` instead of resource-managed exclusive mapping, optional syscon failures silently treated as absent, and no power-off path. Test with/without `power-reg`, SATA link at GEN1/2/3, repeated init calls, and missing resource handling.
