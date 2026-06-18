# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192se/hw.h

## Purpose
This header declares RTL8192SE hardware-control entry points and media-status constants used by `sw.c`, the rtlwifi core, and sibling chip modules. It is the public interface for `hw.c`.

## Important APIs, Types, And Functions
The header defines media status encodings (`MSR_LINK_*`) and `enum WIRELESS_NETWORK_TYPE`. It declares hardware register access callbacks, EEPROM reading, interrupt recognition, init/disable/suspend/resume, network type and BSSID filtering, MAC address setting, QoS/beacon/interrupt-mask updates, rate table updates, channel access setting, RF kill checking, GPIO3 input mode, hardware security enabling, and CAM key programming.

## Control Flow
There is no direct control flow. `sw.c` places most declarations into `rtl8192se_hal_ops`, while `phy.c` calls GPIO/beacon helpers and other modules use security or rate callbacks through the ops table.

## State And Persistence
The functions declared here mutate hardware registers and shared rtlwifi state, but the header itself stores no state. The enum and macro values are compile-time constants matching MSR register encoding.

## Dependencies And Integration Points
It depends on `struct ieee80211_hw`, `struct ieee80211_sta`, `enum nl80211_iftype`, and rtlwifi structures from included parent headers. Its declarations must stay synchronized with `hw.c` definitions and `sw.c` HAL ops.

## Risks
Signature drift breaks HAL wiring. `rtl92se_set_mac_addr()` is declared as a real callback but implemented as a stub, so callers must not assume it writes hardware after init. Network type constants must match hardware MSR bit encoding.

## Test Signals
Build/link tests validate declaration consistency. Runtime tests should exercise each HAL callback through the generic rtlwifi core, especially init/disable, network type changes, beacon setup, rate updates, RF kill, and key programming.
