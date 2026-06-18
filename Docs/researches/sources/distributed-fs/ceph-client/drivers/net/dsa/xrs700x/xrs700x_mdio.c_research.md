# sources/distributed-fs/ceph-client/drivers/net/dsa/xrs700x/xrs700x_mdio.c

## Purpose
This file is the MDIO transport binding for the Arrow SpeedChips XRS700x DSA switch family. It adapts the common XRS700x switch driver to an `mdio_device` by exposing a regmap that translates 32-bit switch register addresses into the hardware indirect MDIO sequence.

## Important APIs, Types, and Functions
- `xrs700x_mdio_reg_read()` and `xrs700x_mdio_reg_write()` split register addressing across `XRS_MDIO_IBA1`, `XRS_MDIO_IBA0`, and `XRS_MDIO_IBD`.
- `xrs700x_mdio_regmap_config` declares 16-bit values, 32-bit registers, 2-byte stride, no cache, big-endian formatting, and max register `XRS_VLAN(VLAN_N_VID - 1)`.
- `xrs700x_mdio_probe()` allocates the common switch object, creates the regmap, stores driver data, and registers DSA.
- Remove and shutdown call common switch teardown/shutdown.
- OF IDs map XRS7003E/F and XRS7004E/F compatible strings to shared variant info.

## Control Flow
Probe is called by the MDIO core after OF matching. It allocates common switch state, initializes devm regmap with the MDIO callbacks, then calls `xrs700x_switch_register()`. Reads write high address bits to `IBA1`, low address bits plus read opcode to `IBA0`, and read data from `IBD`. Writes write data first, then high address, then low address plus write opcode. Remove and shutdown are no-ops when driver data is absent.

## State and Persistence
State lives in the shared `struct xrs700x`, the regmap, the MDIO device, and hardware registers. There is no regmap cache, so all accesses hit hardware. Shutdown clears the device driver data pointer after common shutdown.

## Dependencies and Integration Points
The file depends on Linux MDIO, regmap, OF matching, DSA helpers from `xrs700x.h`, and register constants from `xrs700x_reg.h`. It registers through `mdio_module_driver()`.

## Risks and Edge Cases
The indirect access order is critical. Any MDIO failure aborts the regmap access and is logged. Because max register is based on the VLAN table, future higher-address registers may require updating the regmap bounds. No caching means slow or unreliable MDIO buses directly affect switch operations.

## Test Signals
Probe each compatible, read known ID registers, perform VLAN-range regmap access, validate DSA registration, and exercise remove/shutdown paths.
