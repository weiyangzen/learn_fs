# sources/distributed-fs/ceph-client/drivers/net/wireless/intersil/p54/main.c

## Purpose
This file is the p54 common mac80211 glue layer. It defines module parameters/metadata, `ieee80211_ops`, interface lifecycle, configuration changes, beacon handling, filter/multicast setup, key offload, survey/statistics access, TX flush, common allocation/registration/free/unregistration, and shared driver initialization.

## Important APIs, Types, and Functions
- `p54_ops` maps mac80211 callbacks to p54 implementations.
- Lifecycle callbacks include `p54_start()`, `p54_stop()`, `p54_add_interface()`, and `p54_remove_interface()`.
- Configuration callbacks include `p54_config()`, `p54_bss_info_changed()`, `p54_conf_tx()`, `p54_configure_filter()`, `p54_prepare_multicast()`, and `p54_set_coverage_class()`.
- Key/statistics callbacks include `p54_set_key()`, `p54_get_stats()`, `p54_get_survey()`, `p54_flush()`, and delayed `p54_work()`.
- Beacon helpers include `p54_find_ie()`, `p54_beacon_format_ie_tim()`, and `p54_beacon_update()`.
- Common exported setup/teardown functions are `p54_init_common()`, `p54_register_common()`, `p54_free_common()`, and `p54_unregister_common()`.

## Control Flow
Bus drivers allocate hardware with `p54_init_common()`, fill bus callbacks, parse firmware/EEPROM, and call `p54_register_common()`. Starting the interface opens the bus, initializes default EDCF queues, puts the firmware in monitor mode, schedules statistics work, and updates LEDs. Adding a real interface transitions from monitor to station/AP/adhoc/mesh and sends MAC setup. Config changes serialize under `conf_mutex`, wait for statistics where needed, send scan exit/channel setup, update power-save/MAC state, and refresh statistics. BSS changes update BSSID, beacon template, slot timing, basic rates, and association-related wake/AID fields.

## State and Persistence Behavior
The file initializes and mutates most `p54_common` state: mode, vif, MAC/BSSID, QoS params, queue stats, current channel, survey counters, power-save flags, multicast list, basic rates, AID, wakeup timer, key bitmap, LED state, delayed work, completions, and registration flag. Stop clears queues, stats, beacon request ID, TSF, LED state, and calls the bus stop callback.

## Dependencies and Integration Points
It depends on mac80211/cfg80211, firmware helper functions in `fwio.c`, TX/RX helpers from `txrx.c`, optional LED support, and bus frontends through `priv->open`, `priv->stop`, and `priv->tx`. Key offload depends on privacy capabilities parsed from firmware.

## Risks and Edge Cases
Only one active interface is supported; add-interface fails unless current mode is monitor. Beacon TIM formatting deliberately moves a dummy TIM to the end for firmware overwrite. Hardware crypto is disabled for RX management keys due to firmware corruption. Key slot exhaustion falls back to software RX decryption while still allowing TX offload. Flush relies on firmware queue counters and can timeout. Power save is disabled by default for stability.

## Test Signals
Signals include mac80211 registration, interface add/remove, channel change, association/disassociation, beacon updates, multicast filtering, hardware crypto fallback/offload, survey data, queue flush behavior, and clean unregister/free with no pending work.
