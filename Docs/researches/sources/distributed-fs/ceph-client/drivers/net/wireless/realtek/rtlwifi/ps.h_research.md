# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/ps.h

## Purpose
Declares rtlwifi power-save entry points shared by core, PCI, RX, and chip-specific code.

## Important APIs, Types, And Functions
`MAX_SW_LPS_SLEEP_INTV` caps software LPS sleep to five beacon intervals. APIs cover NIC enable/disable, IPS off/on/work, LPS enter/leave/mode, SW LPS beacon/work/RF callbacks, P2P PS command/info parsing, and LPS change work.

## Control Flow
Core calls IPS/LPS from mac80211 config and BSS transitions. PCI TX/RX completion can leave LPS under traffic. RX paths feed beacons/action frames to SW LPS and P2P parsing.

## State And Persistence
No storage is defined; functions mutate `rtlpriv->psc`, work items, RF state, and firmware power-save variables.

## Dependencies And Integration Points
Requires `ieee80211_hw`, `work_struct`, chip ops, and bus ops.

## Risks
Callers must use the correct `may_block` context. Work callbacks assume embedding in `struct rtl_works`.

## Test Signals
Blocking/nonblocking LPS calls, delayed IPS/SW LPS work, P2P PS command emission, and build coverage.
