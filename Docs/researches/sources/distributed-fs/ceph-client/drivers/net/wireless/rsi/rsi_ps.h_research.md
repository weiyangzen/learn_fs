# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_ps.h

Purpose: Declares RSI power-save state, default low-power parameters, and power-save control entry points used by the RSI driver.

Important APIs and types: `enum ps_state` tracks `PS_NONE`, enable/disable request in flight, and enabled state. `struct ps_sleep_params` is the packed firmware request payload for enable/type/connected-sleep, listen interval beacon count, wakeup type, and sleep duration. `struct rsi_ps_info` is driver-side policy state for enablement, thresholds, hysteresis, monitor/listen intervals, DTIM settings, and deep-sleep wake period. APIs include `str_psstate()`, `rsi_enable_ps()`, `rsi_disable_ps()`, `rsi_handle_ps_confirm()`, `rsi_default_ps_params()`, and `rsi_conf_uapsd()`.

Control flow and integration: mac80211 power-save or U-APSD changes flow into `rsi_enable_ps()`/`rsi_disable_ps()`, which send `rsi_request_ps` frames defined in `rsi_mgmt.h`. Firmware confirmations are decoded at `PS_CONFIRM_INDEX` by `rsi_handle_ps_confirm()` and move the driver's PS state machine forward.

State and persistence: The header models transient request state and longer-lived PS policy in `rsi_ps_info`. Firmware state persists until explicit disable or reconfiguration and interacts with listen/DTIM intervals and U-APSD access categories.

Dependencies: Uses `struct rsi_hw`, `struct ieee80211_vif`, and `ps_sleep_params` embedded in the management command ABI.

Risks and test signals: Risks include stuck enable/disable request states, mismatch between mac80211 PS state and firmware confirmations, invalid DTIM/listen interval values, and U-APSD masking errors. Tests should exercise default parameter initialization, PS enable/disable confirmation paths, failed firmware confirms, U-APSD queue configuration, and suspend/resume interaction.

Test signals: Source read size: 63 lines, 1900 bytes.
