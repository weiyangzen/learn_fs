# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rc.h

## Purpose
Header for rtlwifi rate-control constants, private state, and registration functions.

## Important APIs, Types, And Functions
Defines max rate indexes for B, G, A, N MCS7/MCS15, and AC MCS7/MCS8/MCS9. `struct rtl_rate_priv` stores `ht_cap`. APIs are `rtl_rate_control_register()` and `rtl_rate_control_unregister()`.

## Control Flow
Module init/exit register or unregister `rtl_rc`; `rc.c` uses constants to build rate series.

## State And Persistence
No global storage. Runtime per-station instances are allocated by rate-control callbacks.

## Dependencies And Integration Points
Integrates with mac80211 rate control and rtlwifi station private state.

## Risks
Constants must match mac80211 index semantics. Struct extensions require allocation/free updates.

## Test Signals
Module lifecycle, compile coverage, and expected max-rate selection in B/G/A/N/AC.
