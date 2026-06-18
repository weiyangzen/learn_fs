# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8192du/hw.h

## Purpose
Declares the RTL8192DU hardware lifecycle and register-control API used by the DU driver operation table and adjacent files.

## Important APIs, Types, And Functions
Exports callbacks for getting/setting hardware variables, chip-version readout, hardware init, card disable, interrupt enable/disable, network type selection, BSSID filtering, beacon register programming, beacon interval setting, interrupt-mask update, and linked-state register updates.

## Control Flow
The header has no executable flow. The declared functions are called by rtlwifi core callbacks during probe/init, mac80211 state changes, beacon updates, link transitions, and shutdown.

## State And Persistence
No state is owned here. Implementations update `rtl_priv`, `rtl_usb`, MAC/PHY/PSC state, and hardware registers.

## Dependencies And Integration Points
Requires `struct ieee80211_hw`, `enum nl80211_iftype`, bool, and integer types from including headers. It is included by `hw.c` and DU module wiring.

## Risks
Because these declarations form the HAL contract for DU, prototype drift or missing declarations would break callback assignment. No-op interrupt functions may be surprising to callers that expect mask programming.

## Test Signals
Build success and callback invocation across init, network mode, beacon, and shutdown paths validate the header.
