# sources/distributed-fs/ceph-client/drivers/net/wireless/rsi/rsi_91x_ps.c

## Purpose
This file manages the host-side power-save state machine for RSI WLAN power save. It sets default sleep parameters, sends enable/disable requests through management code, reconfigures U-APSD while associated, and consumes firmware power-save confirmations.

## Important APIs, Types, and Functions
The public functions are `str_psstate`, `rsi_default_ps_params`, `rsi_enable_ps`, `rsi_disable_ps`, `rsi_conf_uapsd`, and `rsi_handle_ps_confirm`. The internal helper `rsi_modify_ps_state` logs and assigns `adapter->ps_state`.

## Control Flow
Defaults enable LP sleep with zero traffic thresholds, a default listen interval, and deep-sleep wake period. `rsi_enable_ps` accepts only `PS_NONE`, sends `rsi_send_ps_request(..., true, vif)`, and transitions to `PS_ENABLE_REQ_SENT`. `rsi_disable_ps` accepts only `PS_ENABLED`, sends a wakeup request, and transitions to `PS_DISABLE_REQ_SENT`. `rsi_conf_uapsd` temporarily disables and re-enables PS when U-APSD settings change. `rsi_handle_ps_confirm` reads the firmware confirm token and completes the pending transition to `PS_ENABLED` or `PS_NONE`.

## State and Persistence Behavior
The file mutates `adapter->ps_state` and initializes `adapter->ps_info`. State is volatile and represents a handshake with firmware, not durable configuration. The actual request payload is built in `rsi_91x_mgmt.c` from `ps_info`, association state, DTIM/listen values, and `common->uapsd_bitmap`.

## Dependencies and Integration Points
It is called from mac80211 config changes, association updates, WoWLAN setup, and firmware confirm handling. It depends on `rsi_send_ps_request`, `PS_CONFIRM_INDEX`, `RSI_SLEEP_REQUEST`, `RSI_WAKEUP_REQUEST`, `struct rsi_ps_info`, and `adapter->ps_lock` for callers that protect state transitions.

## Risks
The state machine rejects duplicate or out-of-order requests but only logs failures, so mac80211 PS state can diverge from firmware state. Confirm handling returns an error for unknown tokens but does not repair state. U-APSD reconfiguration assumes firmware accepts back-to-back disable/enable requests. Callers must hold the correct lock because this file does not lock internally.

## Test Signals
Exercise PS enable/disable from mac80211, firmware sleep/wakeup confirms, invalid confirms, repeated enable/disable requests, U-APSD toggles while associated, AP-mode PS suppression, WoWLAN coex PS disable, and suspend/resume transitions that reset `adapter->ps_state`.
