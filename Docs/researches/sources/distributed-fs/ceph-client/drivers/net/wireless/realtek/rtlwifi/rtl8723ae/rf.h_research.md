# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/rf.h

Purpose: `rf.h` declares the RF6052 helper interface used by `phy.c`.

Important APIs/types: defines `RF6052_MAX_TX_PWR` as `0x3F` and declares bandwidth, CCK tx-power, OFDM tx-power, and RF config functions.

Control flow: no executable flow; it is a boundary for RF helper calls from PHY routines.

State and persistence: no local state. Implementations mutate PHY cached RF words and hardware RF/BB power registers.

Dependencies/integration: requires `struct ieee80211_hw` and integer types from surrounding includes. `phy.c` consumes the API; `rf.c` implements it.

Risks: `RF6052_MAX_TX_PWR` must match chip limits. Prototype drift breaks builds. The API accepts raw `u8 *ppowerlevel` arrays and channel numbers without size/range enforcement at the header boundary.

Test signals: compile coverage and runtime tx-power/bandwidth tests through `phy.c`.
