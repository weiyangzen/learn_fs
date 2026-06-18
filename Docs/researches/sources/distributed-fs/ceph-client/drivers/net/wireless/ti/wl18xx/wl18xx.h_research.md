# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/wl18xx.h

## Purpose
Declares WiLink 8 chip constants, private driver state, firmware-status ABI variants, PHY/static-data structures, and clock configuration types.

## Important APIs, types, and functions
- Minimum firmware macros require chip version 8, interface 9, major 0, minor 58, with subtype ignored.
- Resource constants define command size, aggregation buffer, descriptor counts, MAC addresses, BA sessions, AP stations, and links.
- `struct wl18xx_priv` stores command buffer, private config, TX release index, and extra spare-key count.
- `struct wl18xx_fw_status_priv`, packet counters, `wl18xx_fw_status`, and `wl18xx_fw_status_8_9_1` mirror firmware status layouts for different API versions.
- `struct wl18xx_static_data_priv` carries PHY firmware version from static data.
- `struct wl18xx_clk_cfg` and clock enum support PLL programming.

## Control flow
No executable flow. `main.c` fills/reads these structures during setup, boot, firmware-status conversion, and TX completion.

## State and persistence behavior
Defines per-device in-memory state and volatile firmware status snapshots. No persistent files. The command buffer is reused for firmware command writes; `extra_spare_key_count` persists until keys are removed or hardware is reinitialized.

## Dependencies and integration points
Includes wl18xx private `conf.h`. Used by almost every wl18xx implementation file and by common wlcore through allocated private data/status lengths.

## Risks and test signals
Firmware status ABI mismatches can break interrupt, RX, TX, and logger handling. Resource constants must remain consistent with firmware and wlcore array bounds. Test boot on firmware versions using both status layouts, TX completion, link suspend/priority thresholds, command size handling, and key add/remove spare-block accounting.
