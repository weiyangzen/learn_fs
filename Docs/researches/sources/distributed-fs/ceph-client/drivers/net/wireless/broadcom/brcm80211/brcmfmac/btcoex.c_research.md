# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmfmac/btcoex.c

## Purpose
Implements brcmfmac Bluetooth coexistence handling for DHCP/critical-protocol windows. When SCO/eSCO activity is detected, it temporarily changes firmware `btc_params` to favor Wi-Fi progress during DHCP, then restores saved coexistence parameters.

## Important APIs, Types, and Functions
Defines `enum brcmf_btcoex_state` and private `struct brcmf_btcoex_info`. Public APIs are `brcmf_btcoex_attach()`, `brcmf_btcoex_detach()`, and `brcmf_btcoex_set_mode()`. Internal helpers read/write `btc_params`, detect SCO activity, save/restore two groups of firmware registers, boost Wi-Fi, run a timer callback, and process the state machine in workqueue context.

## Control Flow, State, and Persistence
Attach allocates state, initializes a timer and work item, and stores it in `cfg->btcoex`. `brcmf_btcoex_set_mode(BRCMF_BTCOEX_DISABLED)` treats the critical protocol as starting: if idle and SCO is detected through repeated `btc_params` 27 reads, it saves part1 registers, writes DHCP-friendly values, records the vif/duration, and schedules work. The work handler moves from START to opportunity window, then to forced Wi-Fi boost after T1, then to idle after T2 or early DHCP completion. Boosting saves part2 registers 50/51/64/65/71 once, writes DHCP values, and restores them on idle. End mode marks DHCP done, cancels timers as needed, restores registers, calls `cfg80211_crit_proto_stopped()`, and clears `vif`. Detach shuts down timer/work and restores any saved firmware parameters.

## Dependencies and Integration Points
Depends on brcmfmac firmware iovar access, cfg80211 critical protocol notifications, P2P/cfg80211 structures, workqueues/timers, and firmware `btc_params` semantics. It is initialized from brcmfmac cfg80211 setup and invoked by critical-protocol mode changes.

## Risks and Test Signals
Risks include not restoring firmware coexistence registers, races between timer/work/end/detach, stale `vif` pointers, firmware read/write failures ignored by many paths, and over-boosting when SCO detection is wrong. Test DHCP with active Bluetooth SCO/eSCO, DHCP completion before T1/T2, timeout path, detach during active timer, repeated critical-protocol requests returning `-EBUSY`, and firmware parameter restoration.
