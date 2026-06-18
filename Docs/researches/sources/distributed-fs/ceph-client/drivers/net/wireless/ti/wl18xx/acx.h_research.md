# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/acx.h

## Purpose
Defines the WiLink 8-specific ACX command ids, interrupt masks, firmware statistics layout, and packed payload structures used by `wl18xx/acx.c`, debugfs, and wl18xx runtime operations.

## Important APIs, types, and functions
- ACX ids `ACX_NS_IPV6_FILTER` through `ACX_TIME_SYNC_CFG` extend the common wlcore ACX namespace.
- `WL18XX_ACX_EVENTS_VECTOR` and `WL18XX_INTR_MASK` declare interrupt/event bits enabled by wl18xx.
- `struct wl18xx_acx_host_config_bitmap`, checksum, peer-capability, notification, RX BA filter, AP sleep, dynamic trace, and time-sync structures are command payload ABIs.
- `struct wl18xx_acx_statistics` aggregates nested error, TX, RX, ISR, power, filter, rate, aggregation, pipeline, diversity, thermal, calibration, roaming, and DFS counters.
- Function prototypes expose the wl18xx ACX helper surface.

## Control flow
No executable flow. The structures constrain callers that build ACX commands and debugfs stat readers that interpret firmware statistics.

## State and persistence behavior
The header describes firmware-owned state snapshots and configuration payloads. Statistics are volatile firmware counters. Configuration structures become firmware state only when sent by `wl1271_cmd_configure()`.

## Dependencies and integration points
Includes wlcore core and common ACX definitions. The statistics layout is used by `wl18xx/debugfs.c`; command payloads are used by `wl18xx/acx.c`; event and interrupt masks are used by `wl18xx/main.c` boot/interrupt setup.

## Risks and test signals
Because all structures are packed firmware ABIs, field order, size, alignment, and endian annotations are high-risk. Debugfs counter reads, firmware statistics clear, interrupt delivery, checksum enablement, peer HT updates, and AP sleep/time sync commands are the main runtime test signals.
