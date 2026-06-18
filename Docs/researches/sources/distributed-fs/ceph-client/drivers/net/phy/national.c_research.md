# sources/distributed-fs/ceph-client/drivers/net/phy/national.c

## Purpose
This is a compact phylib driver for the National Semiconductor DP83865 Gigabit PHY. It provides device-specific initialization for gigabit speed fallback and 10BASE-T half-duplex loopback behavior, plus interrupt masking and acknowledgement.

## Important APIs, Types, and Functions
The single driver table entry `dp83865_driver[]` binds `DP83865_PHY_ID` with mask `0xfffffff0`. Main functions are `ns_exp_read()`, `ns_exp_write()`, `ns_ack_interrupt()`, `ns_handle_interrupt()`, `ns_config_intr()`, `ns_giga_speed_fallback()`, `ns_10_base_t_hdx_loopack()`, and `ns_config_init()`. `enum hdx_loopback` supplies readable on/off constants for the loopback helper.

## Control Flow
Initialization calls `ns_giga_speed_fallback()` to power down the PHY, configure expanded memory access, write an internal expanded-memory value, restore BMCR power state, and enable all fallback modes through the LED control register. It then disables 10 Mbps half-duplex loopback by modifying expanded memory register `0x1c0` and acknowledges interrupts.

Interrupt configuration either acknowledges and enables default remote fault, autoneg-complete, and link-change interrupt masks, or disables the mask and acknowledges any pending status. The interrupt handler reads `DP83865_INT_STATUS`, ignores unmasked/uninteresting interrupts, clears asserted bits through `DP83865_INT_CLEAR`, and triggers the phylib state machine.

## State and Persistence
No private software state is allocated. State is held in hardware registers: interrupt mask/status/clear registers, BMCR power-down state, expanded memory register `0x1c0`, and LED/fallback control. Register writes persist until reset or subsequent driver/firmware changes.

## Dependencies and Integration Points
The driver depends on Linux phylib Clause 22 helpers, MII/BMCR definitions, module PHY registration, and netdevice/ethtool headers. It does not expose ethtool stats or custom link status callbacks, relying on generic phylib behavior outside its init and interrupt callbacks.

## Risks
`ns_exp_read()` returns `u8` while `phy_read()` returns negative errors, so MDIO read failures in expanded memory access are truncated rather than propagated. Init helpers do not check every write result, so partial configuration can go unnoticed. The fallback programming sequence is tightly hardware-specific and may be sensitive to power-down timing.

## Test Signals
Tests should verify DP83865 probe, init register writes, link-change/remote-fault interrupt delivery, interrupt disable behavior, and regression coverage for 10BASE-T half-duplex loopback disablement and gigabit fallback interoperability.
