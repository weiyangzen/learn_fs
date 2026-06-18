# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/b43legacy/phy.h

## Purpose
Defines the public PHY interface and register/table constants for b43legacy. It centralizes antenna and interference mode enums, routed PHY register address macros, OFDM/G-PHY table selectors, version masks, and prototypes for PHY initialization, calibration, LO, power, and antenna operations.

## Important APIs, Types, and Functions
Key enums are `B43legacy_ANTENNA*` and `B43legacy_INTERFMODE_*`. Register helpers include `B43legacy_PHY_BASE()`, `B43legacy_PHY_OFDM()`, `B43legacy_PHY_EXTG()`, and `B43legacy_OFDMTAB()`. Prototypes expose `b43legacy_phy_lock()`, `b43legacy_phy_read()`, `b43legacy_phy_init_tssi2dbm_table()`, `b43legacy_phy_init()`, `b43legacy_set_rx_antenna()`, `b43legacy_phy_set_antenna_diversity()`, `b43legacy_phy_calibrate()`, `b43legacy_phy_connect()`, `b43legacy_phy_lo_*()`, `b43legacy_phy_xmitpower()`, `b43legacy_phy_set_baseband_attenuation()`, and `b43legacy_power_saving_ctl_bits()`.

## Control Flow, State, and Persistence
The header has no executable state. It defines the symbolic contract used by `phy.c`, `radio.c`, `sysfs.c`, and MAC/radio paths to address routed PHY registers and to mutate `struct b43legacy_phy` state owned elsewhere.

## Dependencies and Integration Points
Includes Linux integer types and forward declares `struct b43legacy_wldev`. It is used anywhere b43legacy needs PHY register definitions, OFDM tables, antenna diversity settings, or transmit-power recalculation hooks.

## Risks and Test Signals
Incorrect register constants or enum values break hardware programming globally. Build coverage should catch missing prototypes; runtime test signals are PHY init success, stable RX/TX, antenna selection, interference sysfs behavior, and no mismatched routed register accesses.
