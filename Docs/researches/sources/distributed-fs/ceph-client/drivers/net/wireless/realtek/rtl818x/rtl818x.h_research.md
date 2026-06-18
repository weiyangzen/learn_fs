# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtl818x/rtl818x.h

## Purpose
This shared header defines the RTL818x CSR register layout, register bit definitions, RTL8187SE raw-offset aliases, RF operation callback type, and common TX/RX descriptor flags used by RTL8180/RTL8187-family drivers.

## Important APIs, Types, And Functions
The central type is `struct rtl818x_csr`, a packed map of the device register space with unions for chip-specific interpretations. `struct rtl818x_rf_ops` defines the RF callback contract: name, init, stop, set channel, and optional RSSI calculation.

Important definitions cover command bits, interrupt bits for classic chips and RTL8187SE, TX/RX configuration bits, EEPROM command bits, analog/config bits, media status, RF pin registers, TX gain/antenna fields, contention/EDCA registers, RTL8187B revision IDs, and AC parameter shifts. `REG_ADDR1/2/4` and aliases such as `SW_3W_DB0`, `SW_3W_CMD1`, and `SI_DATA_REG` expose non-standard RTL8187SE offsets beyond the packed CSR.

## Control Flow
There is no runtime control flow. This file provides the symbolic contract that lets separate PCI/USB/RF files perform register I/O safely enough to be maintainable.

## State And Persistence
`struct rtl818x_csr` represents persistent hardware state, not allocated software state. The packed layout maps MAC address, multicast hash, TSF, TX/RX config, EEPROM command, analog parameters, PHY/RF pins, GPIO, gain, EDCA, and related registers.

## Dependencies And Integration Points
The header is shared by RTL8180 PCI and RTL8187 USB code. RTL8187 code treats `priv->map` as a pointer at register base `0xFF00`, while RTL8180 code maps actual MMIO. RF files use `rtl818x_rf_ops`; descriptor flags are shared by TX/RX descriptor construction and parsing.

## Risks
Packed register layouts and unions are fragile: an incorrect offset affects real hardware programming. Some fields have different meanings on RTL8187B or RTL8187SE, requiring raw-address workarounds. The `REG_ADDR*` macros assume a local variable named `priv`, which is convenient but brittle. TX and RX descriptor flags intentionally overlap bit positions with different meanings, so callers must use them in the correct direction.

## Test Signals
Compile coverage across RTL8180, RTL8187, and RTL8187SE paths is important. Runtime signals are correct register writes during probe/start/config, no endian/packing warnings, valid interrupts/configuration on each supported chip family, and descriptor flags matching observed TX/RX behavior.
