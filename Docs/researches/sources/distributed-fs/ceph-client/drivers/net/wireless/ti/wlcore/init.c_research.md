# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/init.c

## Purpose
`init.c` sequences wlcore firmware/hardware initialization and per-vif initialization. It reserves firmware template memory, configures core ACX settings, initializes AP/STA role behavior, installs rate policies, sets BA policy, and enables the data path.

## Important APIs and functions
Top-level functions are `wl1271_hw_init()`, `wl1271_init_vif_specific()`, `wl1271_init_templates_config()`, `wl1271_init_pta()`, `wl1271_init_energy_detection()`, `wl1271_init_ap_rates()`, `wl1271_ap_init_templates()`, and `wl1271_sta_hw_init()`.

Static helpers build AP deauth/null/QoS-null templates, configure RX lifetime, slot/service-period/RTS settings, STA beacon filtering, beacon/DTIM broadcast options, firmware logging, AP hardware sleep, STA keep-alive behavior, BA policies, STA role ACX settings, and AP role ACX settings.

## Control flow
`wl1271_hw_init()` first delegates chip-specific hardware init, reserves all common firmware templates with empty placeholders, configures memory and firmware logging, applies regulatory/DFS config, sets PTA/SoftGemini, initializes target memory config, RX behavior, DCO itrim, TX completion options, RX interrupt pacing, energy detection, fragmentation threshold, data path, PM config, rate management, and hangover settings. On failures after memory-map allocation, it frees `wl->target_mem_map`.

`wl1271_init_vif_specific()` chooses AP or STA initialization based on `wlvif->bss_type`, configures sleep authorization and AP event masks for first roles, applies mode-specific ACX settings, programs PHY defaults, iterates configured AC/TID arrays, configures encryption features, runs post-memory template setup, sets BA policies, and calls chip-specific vif init.

## State and persistence behavior
Initialization consumes persistent `wl->conf` fields and writes live firmware state through ACX and command calls. It mutates event masks, BA counters, `wlvif->ba_support`, `wlvif->ba_allowed`, template reservations, rate-policy indexes, and target memory map ownership. Template memory reservations persist in firmware and are later overwritten with live frame templates.

## Dependencies and integration points
It depends on command/template APIs, ACX configuration functions, TX rate helpers, event unmasking, IO/data path commands, hw_ops chip callbacks, mac80211 vif state, and configuration structures from `conf.h`. It is invoked from wlcore bring-up and interface creation paths.

## Risks
Initialization is order-sensitive. Data path enablement before PM/rate/hangover completion, missing template reservations, mismatched AC/TID counts, or wrong first-AP/first-STA sleep authorization can cause firmware errors or power issues. `BUG_ON(wl->conf.tx.tid_conf_count != wl->conf.tx.ac_conf_count)` makes invalid configuration fatal.

## Test signals
Signals include complete firmware boot, all ACX init stages succeeding, STA association after vif init, AP beacon/probe/deauth/null templates, AP rate policies across ACs, BA session setup, event masks for AP events, data path enablement, recovery from init failures without memory leaks, and debug logs under `DEBUG_BOOT`, `DEBUG_AP`, and `DEBUG_ACX`.
