# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/acx.c

## Purpose
Implements the common wlcore ACX configuration/interrogation layer used by TI chip-family lower drivers. It translates wlcore/mac80211 state and `wl->conf` policy into packed firmware information elements for power management, RX/TX behavior, rate policies, beacon filtering, aggregation, coexistence, memory layout, statistics, and optional PM RX filters.

## Important APIs, types, and functions
- Power/save/connectivity helpers include wake-up conditions, sleep authorization, PM config, keep-alive mode/config, beacon/DTIM options, BET, ARP filtering, RSSI/SNR triggers, and connection monitor parameters.
- TX/RX/rate helpers include TX power, RX MSDU lifetime, RTS/fragment thresholds, CCA threshold, service period timeout, AC/TID config, TX options, STA/AP rate policies, rate-management params, hangover, PS RX streaming, and AP max retry.
- Association/HT helpers include AID, preamble, CTS protection, HT capabilities/information, BA initiator policy, BA receiver setup, TSF interrogation, in-connection STA list, and average RSSI interrogation.
- Initialization/statistics helpers include memory config, memory-map interrogation, RX interrupt config, event mailbox mask, firmware statistics interrogation, SoftGemini enable/config, FM coexistence, and feature config.
- Optional `CONFIG_PM` helpers configure default and per-pattern RX data filters.

## Control flow
Most helpers allocate a command-specific structure, fill role/config fields, convert little-endian fields, call `wl1271_cmd_configure()` or `wl1271_cmd_interrogate()`, handle firmware status, and free. Some functions loop over configuration arrays: beacon filter IE rules, SoftGemini parameters, PS RX streaming queues, and rate policy classes. BA receiver setup uses `wlcore_cmd_configure_failsafe()` to translate a firmware "no RX BA session" status into `-EBUSY`.

## State and persistence behavior
The file mutates firmware state extensively. Host-side persistent runtime changes are limited but important: `wl->sleep_auth` is cached after sleep authorization, `wl->target_mem_map` is allocated and populated by memory-map interrogation, `wl->tx_blocks_available` is seeded from firmware memory map, and `wlvif->last_rssi_event` is reset before RSSI trigger configuration. All heap command buffers are transient.

## Dependencies and integration points
Depends on common wlcore command transport, debug logging, wlcore hardware callbacks for rate masks, mac80211 constants, PM RX filter flattening helpers, and `wl->conf` structures from `conf.h`. Called by wlcore main/init/PS/RX/TX paths and lower-driver setup operations such as wl18xx.

## Risks and test signals
Risks include firmware ABI field mismatch, missing endian conversions, unchecked multicast list length relative to fixed table capacity, invalid configuration values flowing from `wl->conf`, memory-map allocation leaks on partial failures, BA failsafe status handling, and PM filter flexible-array sizing. Test signals include association and AP startup, power-save entry/exit, beacon filtering, multicast filtering, ARP offload, rate policy updates, HT/BA negotiation, TSF reads, firmware stats reads, memory-map initialization, RX interrupt threshold behavior, SoftGemini/FM coexistence config, and suspend RX filters.
