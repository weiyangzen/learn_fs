# sources/distributed-fs/ceph-client/drivers/soc/renesas/r9a08g045-sysc.c

## Purpose

This file supplies RZ/G3S-specific initialization data for the generic Renesas RZ system-controller driver. It describes SoC ID decoding and the readable/writeable register allowlist for the R9A08G045 SYSC block.

## Important APIs, Types, and Functions

`rzg3s_sysc_soc_id_init_data` defines family `RZ/G3S`, expected ID `0x85e0447`, device-ID offset `0xa04`, and revision/specific-ID masks. `rzg3s_regmap_readable_reg()` and `rzg3s_regmap_writeable_reg()` whitelist XSPI, Ethernet, PCIe, I2C/I3C, USB power-ready, and reset-resume registers. `rzg3s_sysc_init_data` exports these callbacks and `max_register`.

## Control Flow

No probe occurs here. `rz-sysc.c` references `rzg3s_sysc_init_data` from its OF match table when `CONFIG_SYSC_R9A08G045` is enabled, then uses the data for soc-bus registration and regmap access control.

## State and Persistence Behavior

The file is immutable init data. Runtime state lives in the generic RZ SYSC driver and in the hardware registers exposed through regmap.

## Dependencies and Integration Points

It depends on `rz-sysc.h`, bit masks, and the generic RZ SYSC driver. Other drivers access allowed registers through the syscon/regmap registered by `rz-sysc.c`.

## Risks and Edge Cases

An incomplete allowlist can block legitimate client access; an overly broad list can expose reserved registers to syscon users. `max_register = 0xe20` must cover all allowed registers. The SoC ID masks must match the hardware manual to avoid false mismatch failures.

## Test Signals

Boot on RZ/G3S, verify detected family/revision, successful syscon registration, allowed read/write access for each listed register, and denied access for reserved offsets.
