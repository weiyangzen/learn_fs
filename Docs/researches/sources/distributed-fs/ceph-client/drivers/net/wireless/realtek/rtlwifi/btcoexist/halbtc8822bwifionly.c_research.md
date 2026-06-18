# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/btcoexist/halbtc8822bwifionly.c

## Purpose
Provides RTL8822B Wi-Fi-only hardware setup for systems without active Bluetooth coexistence control. It configures baseband registers so Wi-Fi owns or selects the proper antenna path and grant signals.

## Important APIs, Types, and Functions
Exports `ex_hal8822b_wifi_only_hw_config()`, `ex_hal8822b_wifi_only_scannotify()`, `ex_hal8822b_wifi_only_switchbandnotify()`, and `hal8822b_wifi_only_switch_antenna()`. All use `struct wifi_only_cfg` and the inline `halwifionly_phy_set_bb_reg()` wrapper from `halbtcoutsrc.h`.

## Control Flow
Hardware configuration writes a fixed register sequence: BB control at `0x4c`, software control at `0xcb4`, antenna mux at `0x974`, `0x1990`, `0xcbc`, debug/grant selection at `0x70`, and grant registers `0x1704`/`0x1700`. Scan and switch-band notifications both delegate to `hal8822b_wifi_only_switch_antenna()`, which writes `0xcbc[9:8]` to select the 5 GHz or 2.4 GHz antenna path.

## State and Persistence Behavior
There is no file-local state. State persists only in programmed BB registers. The behavior is idempotent for repeated notifications with the same band.

## Dependencies and Integration Points
Depends on `halbt_precomp.h`, `struct wifi_only_cfg`, and Realtek BB register access through `rtl_set_bbreg()`. It is intended to be called by the generic Wi-Fi-only path in `halbtcoutsrc.c`/`rtl_btc.c`, although the current generic `exhalbtc_init_hw_config_wifi_only()` and notification wrappers are stubbed in this source set, so integration depends on other build variants or future dispatch wiring.

## Risks and Test Signals
The register sequence is all magic values, so incorrect RFE or board assumptions can break antenna selection. Current upstream glue may not call these functions, making this file dead unless another path dispatches it. Test signals are BB register readback after Wi-Fi-only init, scan and band switch on 2.4/5 GHz, RF throughput by band, and grant signal observation (`gnt_wl=1`, `gnt_bt=0`) on supported hardware.
