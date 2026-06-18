# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wl18xx/main.c

## Purpose
Main WiLink 8 lower-driver implementation. It supplies wl18xx defaults, hardware tables, boot sequencing, firmware-status conversion, TX/RX descriptor semantics, HT capability advertisement, module-parameter overrides, and the `wlcore_ops` table that lets common wlcore drive wl18xx hardware.

## Important APIs, types, and functions
- Defaults: `wl18xx_conf` and `wl18xx_default_priv_conf` seed common/private configuration when a binary config file is absent.
- Hardware tables: `wl18xx_ptable`, `wl18xx_rtable`, rate-index maps, and PLL clock tables describe address partitions, registers, rates, and clock setup.
- Boot/setup: `wl18xx_identify_chip()`, `wl18xx_set_clk()`, `wl18xx_pre_boot()`, `wl18xx_pre_upload()`, `wl18xx_set_mac_and_phy()`, `wl18xx_boot()`, `wl18xx_enable_interrupts()`.
- Runtime ops: command trigger/ack, TX block math, TX/RX descriptor helpers, checksum hooks, status conversion, link priority, key handling, rate-mask helpers, and scan/event/debugfs callbacks.
- Config and platform: `wl18xx_load_conf_file()`, `wl18xx_conf_init()`, `wl18xx_setup()`, `wl18xx_probe()`, `module_platform_driver()`, module parameters, and `MODULE_FIRMWARE()`.

## Control flow
Probe allocates common wlcore hardware with wl18xx private data and mailbox size, assigns `wl18xx_ops` and partition table, then calls `wlcore_probe()`. Setup fills wlcore limits/capabilities, loads config or defaults, applies module parameters, selects HT capabilities, and enables 5 GHz only when antennas are configured. Boot programs clocks and PRCM state, performs pre-upload workarounds, uploads firmware, writes PHY/MAC params to PHY init memory, sets event masks, runs firmware through common boot code, and enables interrupts.

At runtime wlcore calls this file through `wlcore_ops`: command mailbox writes are padded to `WL18XX_CMD_MAX_SIZE`, TX descriptors use 268-byte block math and optional last-frame SDIO padding, firmware status is converted according to firmware API major version, checksum offload annotates TX descriptors and RX skbs when enabled, and link priority thresholds are read from the firmware status private block.

## State and persistence behavior
Per-device state is in `struct wl1271` plus `struct wl18xx_priv`: private config, command buffer, `last_fw_rls_idx`, and extra spare-key count. Persistent inputs are firmware (`WL18XX_FW_NAME`) and optional binary configuration file named by platform data. Module parameters are read-only after load and override config values. Boot writes hardware registers, PHY init memory, and firmware state; no files are written by the driver.

## Dependencies and integration points
Integrates Linux platform driver, firmware loader, mac80211/cfg80211, wlcore core/boot/io/tx/rx/acx APIs, wl18xx ACX/command/scan/event/debugfs modules, and platform data family names. It is the registration point for all wl18xx callbacks consumed by wlcore.

## Risks and test signals
High-risk areas are firmware ABI version handling, config file size/magic/version validation, clock/partition/register programming, event mask coverage, checksum offload consistency, firmware status structure selection, HT capability choices from antenna/config/module params, and spare-block updates for TKIP/GEM keys. Test signals include probe/remove, boot with real firmware/config fallback, PG/fuse logging, random MAC fallback, 2.4/5 GHz capability advertisement, checksum on/off traffic, TKIP/GEM key add/remove, scan and scheduled scan, DFS CAC/radar, channel switch, suspend notification filtering, and recovery reinitializing private counters.
