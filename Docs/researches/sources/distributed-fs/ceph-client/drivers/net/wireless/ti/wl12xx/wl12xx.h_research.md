# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl12xx/wl12xx.h

## Purpose
Declares wl12xx chip-family constants, private state, clock enumerations, firmware-version requirements, and firmware-status layouts for WiLink 6/7 chips.

## Important APIs, types, and functions
- Chip ids cover wl127x and wl128x PG revisions.
- Minimum single-role and multi-role firmware version macros drive wlcore firmware validation.
- Resource limits define aggregation buffer size, TX/RX descriptors, MAC addresses, BA sessions, AP station count, and link count.
- `struct wl12xx_priv` stores wl12xx private configuration, reference/TCXO clock selections, and RX memory pool address data.
- Clock enums enumerate supported reference and TCXO clock encodings.
- `struct wl12xx_fw_packet_counters` and `struct wl12xx_fw_status` describe the common firmware status block consumed by wlcore.

## Control flow
No executable flow. These declarations are consumed by wl12xx setup, boot, TX/RX, and firmware-status conversion logic in companion files.

## State and persistence behavior
Defines in-memory runtime state only. `wl12xx_priv` is allocated with the common `wl1271` object and carries configuration/state for one device instance. Firmware status structures mirror volatile device mailboxes and are not persisted.

## Dependencies and integration points
Includes wl12xx `conf.h` and uses wlcore firmware-version sentinel macros, queue/link constants, and Linux integer types. The status layout integrates with common wlcore interrupt/TX/RX processing.

## Risks and test signals
Resource-limit mismatches can break array bounds or mac80211 advertised capabilities. Firmware status ABI changes can corrupt interrupt, RX descriptor, or TX completion handling. Test signals include wl127x/wl128x boot with SR/MR firmware, TX completion accounting, PS/fast link bitmap handling, and 5 GHz enablement through NVS.
