# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbe/ixgbe_phy.h

## Purpose
`ixgbe_phy.h` is the PHY/module access contract for ixgbe. It declares EEPROM offsets, SFP/QSFP capability masks, vendor OUIs, I2C timing constants, CS4227/port-expander constants, flow-control bits, overtemperature registers, and prototypes for PHY, MDIO, module, and I2C helpers.

## Important APIs and constants
The header exposes `ixgbe_mii_bus_init`, PHY identity/reset/read/write helpers, link setup and capability helpers, TNX-specific link methods, NL reset, copper power control, module identification, SFP init-sequence lookup, overtemperature check, byte-level I2C EEPROM/SFF8472 access, and combined I2C operations.

SFP/QSFP offsets and masks identify module type, 1G/10G capabilities, direct-attach cable type, bitrate, cable length, SFF-8472 support, soft rate select, diagnostic monitoring, and vendor OUI bytes. I2C timing constants encode standard-mode SDA/SCL setup, hold, high, low, rise, fall, stop, and bus-free timings used by the bit-banged implementation.

## Control flow and integration
Implementation code uses the offsets and masks to read module EEPROM, classify module types, enforce supported optics policy, and determine PHY initialization sequences. Link setup and reset code use prototypes here through MAC operation tables and `hw->phy.ops`. The header is included by `ixgbe_phy.c` and by board-specific ixgbe code that configures PHY ops.

## State and persistence
The header itself has no mutable state. It defines constants that map persistent EEPROM content and volatile PHY/I2C/MDIO hardware registers. Because these values describe external module EEPROM layouts and hardware register programming, compatibility depends on keeping the constants aligned with hardware specifications.

## Dependencies
It includes `ixgbe_type.h` for core hardware types, link speed types, and enum definitions. The function declarations depend on `struct ixgbe_hw`, `ixgbe_link_speed`, and Linux integer types available through included ixgbe headers.

## Risks and edge cases
Wrong offsets or masks can misclassify optics, advertise invalid link capabilities, or read/write the wrong I2C device. Timing constants are used in low-level bus toggling, so casual changes can break marginal modules. CS4227 and port-expander constants are hardware-specific and should not be generalized without board validation.

## Test signals
Validation should compare SFP/QSFP EEPROM parsing against known modules, confirm I2C timing-sensitive modules still read reliably, verify exported prototypes match operation table assignments, and exercise copper/fiber/QSFP boards with PHY reset, autonegotiation, and low-power operations.
