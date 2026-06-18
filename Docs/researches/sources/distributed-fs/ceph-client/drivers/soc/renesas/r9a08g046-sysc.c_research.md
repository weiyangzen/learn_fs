# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g046-sysc.c

## Purpose

This file provides RZ/G3L-specific data for the generic RZ system-controller driver, including SoC ID metadata and safe regmap access callbacks for the R9A08G046 SYSC block.

## Important APIs, Types, and Functions

`rzg3l_regmap_readable_reg()` and `rzg3l_regmap_writeable_reg()` enumerate accessible XSPI, Ethernet, PCIe, I2C/I3C, power-ready, and clone-channel selection registers. `rzg3l_sysc_soc_id_init_data` defines family `RZ/G3L`, ID `0x87d9447`, ID offset `0xa04`, and masks. `rzg3l_sysc_init_data` exports callbacks and `max_register = 0xe2c`.

## Control Flow

The generic `rz-sysc.c` match table uses this data when the `renesas,r9a08g046-sysc` compatible is present. Probe then validates SoC identity and registers a syscon-backed regmap with this access policy.

## State and Persistence Behavior

No mutable driver state exists in this file. It contributes static init data consumed during generic probe.

## Dependencies and Integration Points

It integrates with `CONFIG_SYSC_R9A08G046`, `rz-sysc.h`, and syscon clients needing RZ/G3L system-controller registers.

## Risks and Edge Cases

The read/write lists are manually duplicated from hardware knowledge; omissions or wrong write permissions can cause peripheral failures or unsafe reserved-register writes. `max_register` equals the highest allowed register and must remain synchronized with the allowlist.

## Test Signals

Validate SoC detection, revision formatting, syscon registration, read/write allowlist behavior, and client drivers using Ethernet, PCIe, I2C/I3C, and clone-channel registers.
