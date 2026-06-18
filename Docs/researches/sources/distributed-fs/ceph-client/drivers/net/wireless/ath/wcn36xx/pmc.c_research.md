# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/wcn36xx/pmc.c

## Purpose
Implements the small WCN36xx power-management controller layer for BMPS station power save and keepalive null-packet programming. It translates driver policy decisions from `main.c` into SMD power-management requests and updates per-VIF power state.

## Important APIs, Types, and Functions
`wcn36xx_pmc_enter_bmps_state()` asks firmware to enter BMPS for a VIF, updates `vif_priv->pw_state`, resets the BMPS failure counter, and enables mac80211 beacon filtering on success. `wcn36xx_pmc_exit_bmps_state()` exits BMPS only when the VIF is currently marked `WCN36XX_BMPS`, restores `WCN36XX_FULL_POWER`, and clears the beacon-filter driver flag. `wcn36xx_enable_keep_alive_null_packet()` sends a firmware keepalive request using `WCN36XX_HAL_KEEP_ALIVE_NULL_PKT`. `WCN36XX_BMPS_FAIL_THREHOLD` defines the failure count that triggers connection-loss reporting.

## Control Flow and State
Entering BMPS calls `wcn36xx_smd_enter_bmps()`. On success it stores BMPS state in `struct wcn36xx_vif` and sets `IEEE80211_VIF_BEACON_FILTER`; on failure it increments `bmps_fail_ct` and calls `ieee80211_connection_loss()` once the threshold is reached. Exiting BMPS is guarded against unbalanced calls: if the VIF is not in BMPS it returns `-EALREADY` without sending firmware exit. Keepalive programming is stateless in this file and delegates to SMD.

## Dependencies and Integration Points
Includes `wcn36xx.h`, which provides `struct wcn36xx_vif`, logging, HAL constants, and SMD declarations. `main.c` calls BMPS enter/exit from `wcn36xx_change_ps()` when mac80211 toggles `IEEE80211_CONF_PS` and calls keepalive setup after STA association. Firmware message layouts are defined in `hal.h` by BMPS and keepalive request/response structures.

## Risks and Test Signals
The TODO about ensuring a clean TX chain before BMPS means entering power save while frames are pending can be risky. Failure handling intentionally converts repeated BMPS failures into connection loss, so transient firmware timing after association can disrupt connectivity if the threshold is too aggressive. Exiting when the software state is stale skips firmware exit. Test signals include PS enable/disable around association, BMPS enter before first beacon, repeated BMPS failure causing connection loss, beacon-filter flag transitions, keepalive request success after association, and suspend/resume interactions with BMPS state.
