# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_drv_gpio.c

Purpose: Implements HTC-specific GPIO-adjacent support: 3-wire Bluetooth coexistence work scheduling, HTC LED registration/control, and hardware rfkill polling for USB ath9k_htc devices.

Important APIs and functions: BTCOEX entry points are `ath9k_htc_init_btcoex()`, `ath9k_htc_start_btcoex()`, and `ath9k_htc_stop_btcoex()`, backed by `ath_detect_bt_priority()`, `ath_btcoex_period_work()`, and `ath_btcoex_duty_cycle_work()`. LED entry points are `ath9k_init_leds()`, `ath9k_configure_leds()`, `ath9k_deinit_leds()`, and `ath9k_led_work()`. Rfkill functions are `ath9k_htc_rfkill_poll_state()` and `ath9k_start_rfkill_poll()`.

Control flow: BTCOEX init checks global enablement and the USB product string prefix `wb193`, configures fixed GPIOs for BT active/priority/WLAN active, initializes 3-wire hardware, and schedules delayed work. Period work detects BT priority/scan windows, updates target coex capability over HTC, sets stomp mode, enables hardware coex, and schedules a duty-cycle work item. LED init selects a chip-specific GPIO pin, requests it as output, registers a LED class device, and routes brightness changes through mac80211 work to avoid direct GPIO writes in the brightness callback. Rfkill polling wakes HTC power state, reads GPIO polarity, restores power, and updates wiphy state.

State and persistence: Runtime state includes `priv->btcoex` counters/timing, `priv->op_flags`, delayed work items, LED brightness/name/registration, `ah->led_pin`, and rfkill GPIO/polarity. No durable persistence exists.

Dependencies and integration points: Depends on HTC power-save helpers, `ath9k_htc_update_cap_target()`, ath9k hardware BTCOEX/GPIO functions, mac80211 delayed work and LED APIs, wiphy rfkill polling, product strings from USB probe, and common BT threshold constants.

Risks: BTCOEX support is limited to recognized product strings and 3-wire mode. Work cancellation must be synchronous before disabling hardware. LED brightness is intentionally lightly synchronized and delayed through work. Rfkill GPIO reads require correct power-save wake/restore around USB-backed hardware access.

Test signals: HTC device with and without `wb193` product string, BT scan/priority GPIO pulses, start/stop BTCOEX around interface up/down, LED registration and brightness changes for AR9287/AR9271/AR7010, rfkill polling with both polarities, suspend/disconnect while delayed work is pending.
