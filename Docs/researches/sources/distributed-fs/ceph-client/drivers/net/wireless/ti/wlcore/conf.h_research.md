# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/conf.h

## Purpose
`conf.h` defines the wlcore configuration file ABI and the in-memory `struct wlcore_conf` consumed by initialization, command, ACX, debugfs, TX, RX, scan, power-save, firmware logging, recovery, and rate-control code.

## Important APIs and types
The header provides rate bitmasks and indices, SoftGemini settings, RX interrupt/queue thresholds, TX rate class/access-category/TID settings, beacon filtering and wake conditions, connection monitoring, power management, roaming trigger weights, foreground and scheduled scan dwell policies, HT block-ack settings, memory pool sizing, FM coexistence, RX streaming, firmware logger configuration, rate management, hangover behavior, and recovery policy.

The top-level persisted layout is `struct wlcore_conf_file`, composed of `struct wlcore_conf_header`, `struct wlcore_conf`, and chip-private trailing data. `WLCORE_CONF_VERSION`, `WLCORE_CONF_MASK`, and `WLCORE_CONF_SIZE` define versioning and expected core size.

## Control flow and integration
Runtime code reads values from `wl->conf` and sends them to firmware through ACX commands and command helpers. `init.c` consumes TX/RX/PM/scan/rate/hangover/memory settings during hardware and vif initialization. `cmd.c` uses TX retry limits, AP aging, and firmware logger fields. `debugfs.c` exposes selected fields as writable runtime controls and may reprogram firmware immediately after writes.

## State and persistence behavior
This is a persistent firmware configuration contract. Values can originate from external wlconf/NVS configuration, are stored in `wl->conf`, and may survive until driver reload or be changed through debugfs. Because many structures are `__packed`, padding and field ordering are part of the ABI. Some values have documented ranges but are not all validated at compile time.

## Dependencies and risks
The file depends on kernel bit helpers and shared scalar types. Risks include version mismatch with configuration blobs, invalid range values causing firmware rejection, confusion between rate bitmasks and rate indices, and subtle behavior changes when debugfs writes alter fields without immediately reapplying all dependent ACX state.

## Test signals
Signals include successful parsing of the wlcore configuration file, hardware initialization completing all ACX stages, stable power-save behavior, correct scan dwell timing, AP WMM/TID setup, RX interrupt pacing, firmware logger operation, and recovery policy behavior when firmware faults occur.
