# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/ps.h

## Purpose
`ps.h` declares the wlcore power-save helper interface used by the core driver and related modules. It keeps STA power-save mode programming and AP station sleep notifications available without exposing the implementation details in `ps.c`.

## Important APIs, Types, and Constants
The header includes `wlcore.h` and `acx.h`, then declares `wl1271_ps_set_mode()`, `wl12xx_ps_link_start()`, and `wl12xx_ps_link_end()`. `WL1271_PS_COMPLETE_TIMEOUT` is defined as 500 ms and documents the expected completion wait budget for power-save transitions elsewhere in the driver family.

## Control Flow and Integration
There is no executable control flow. Callers use the declarations to enter/exit STA firmware PSM and to synchronize firmware-reported AP client sleep state with mac80211. The header is consumed by `main.c` and `ps.c`.

## State, Risks, and Test Signals
The header owns no state. Compatibility risks are signature or enum changes that would break callers relying on `enum wl1271_cmd_ps_mode` from ACX command definitions. Compile coverage and power-save transition tests are sufficient signals for this header.
