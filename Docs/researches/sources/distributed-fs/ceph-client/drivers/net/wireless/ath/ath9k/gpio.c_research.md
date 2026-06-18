# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/gpio.c

Purpose: Provides non-HTC ath9k GPIO-adjacent support: LED registration/control, hardware rfkill polling, and optional Bluetooth coexistence timer management for PCI/AHB devices.

Important APIs and functions: LED entry points are `ath_init_leds()` and `ath_deinit_leds()`, backed by `ath_fill_led_pin()` and `ath_led_brightness()`. Rfkill functions are `ath9k_rfkill_poll_state()` and `ath_start_rfkill_poll()`. BT coexistence exports include `ath9k_init_btcoex()`, `ath9k_start_btcoex()`, `ath9k_stop_btcoex()`, `ath9k_btcoex_timer_resume()`, `ath9k_btcoex_timer_pause()`, `ath9k_btcoex_aggr_limit()`, interrupt handling, cleanup, and debug dump helpers.

Control flow: LED init selects a default GPIO by silicon revision, requests it as output, sets active-low/off state, and registers a mac80211 LED class device. Rfkill polling wakes the hardware, reads the configured GPIO polarity, restores power state, and reports to wiphy. BT coexistence initialization selects 2-wire, 3-wire, or MCI hardware setup; period and no-stomp timers alternate Bluetooth and WLAN priority, detect BT priority traffic, update MCI RSSI/profile handling, and program coexistence weights.

State and persistence: Runtime state lives in `ath_softc`, `ath_hw`, and `sc->btcoex`: LED registration/name, GPIO ownership, rfkill GPIO/polarity, timer state, op flags, priority counters, MCI profile counters, and wait times. There is no durable persistence.

Dependencies and integration points: Depends on `ath9k.h`, mac80211 LED and rfkill APIs, kernel timers/jiffies, ath9k power-save wake/restore, ath9k hardware GPIO and BTCOEX helpers, MCI profile code, TX queue mapping, and debug dump macros.

Risks: Timer callbacks access hardware and must coordinate with power state and teardown via synchronous timer deletion. BT priority counters are time-window based and can misclassify scan traffic. LED GPIO defaults vary by chip revision. Rfkill reads require power-save transitions around GPIO access.

Test signals: LED registration/unregistration across module load/unload, LED active-high override, rfkill polarity changes, BTCOEX 2-wire/3-wire/MCI init/start/stop, timer pause/resume during suspend/reset, MCI interrupts, aggregation limit changes under BT priority, and debug dumps.
