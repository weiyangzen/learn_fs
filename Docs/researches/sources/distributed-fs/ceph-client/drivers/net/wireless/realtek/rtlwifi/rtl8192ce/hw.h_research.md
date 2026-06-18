# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192ce/hw.h

## Purpose
This header declares the RTL8192CE hardware-control API consumed by `sw.c` and related modules. It also provides the channel-to-power-group helper used for EFUSE TX-power table expansion.

## Important APIs, Types, And Functions
`rtl92c_get_chnl_group()` maps 2.4 GHz channels into three regulatory power groups. Prototypes cover hardware init/disable/suspend/resume, EEPROM read, interrupt recognition and mask updates, network type, BSSID checking, QoS, beacon programming, hardware register get/set, rate-table updates, channel access, RF kill, hardware security, CAM key programming, and BT coexistence initialization.

## Control Flow
The header is declarative; `sw.c` wires these functions into `rtl8192ce_hal_ops`, and rtlwifi core calls them during probe, open/stop, config changes, security changes, and power management.

## State And Persistence
No storage is declared. Functions declared here mutate runtime driver state and hardware registers in `hw.c`. `rtl92c_get_chnl_group()` is pure and has no state.

## Dependencies And Integration Points
It depends on rtlwifi/mac80211 types and is included by CE software registration and PHY code. It binds the CE-specific hardware implementation to the generic rtlwifi HAL.

## Risks And Edge Cases
The channel grouping helper assumes channel numbering where values less than 3, less than 9, and 9 or above map to groups 0, 1, and 2; callers pass zero-based channel indexes in some loops, so off-by-one expectations must be preserved. Prototype drift breaks HAL registration at build time.

## Test Signals
Build success and HAL callbacks exercising init, interrupts, network type, beacon, rate, RF kill, security, and BT paths validate this header.
