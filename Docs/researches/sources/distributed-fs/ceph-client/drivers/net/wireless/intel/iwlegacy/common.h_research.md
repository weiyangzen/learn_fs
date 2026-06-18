# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/common.h

## Purpose
`common.h` is the central iwlegacy driver contract shared by 3945/4965-era Intel wireless code. It defines the main driver state (`struct il_priv`), hardware and firmware configuration data, DMA queue layouts, EEPROM/regulatory structures, station/rate-scaling state, mac80211 callback declarations, operation hooks, register access helpers, debug categories, and key constants used throughout the legacy driver.

## Important APIs, Types, and Constants
- Logging and debug macros: `IL_ERR`, `IL_WARN`, `IL_INFO`, `IL_DBG`, `D_*` category wrappers, `il_print_hex_dump`, `il_get_debug_level`.
- RX/TX queue primitives: `struct il_rx_buf`, `struct il_queue`, `struct il_tx_queue`, `struct il_rx_queue`, `il_queue_used`, `il_get_cmd_idx`, queue wrap helpers, stop/wake helpers.
- Firmware command abstractions: `struct il_cmd_meta`, `struct il_device_cmd`, `struct il_device_cmd_huge`, `struct il_host_cmd`, command flags such as `CMD_ASYNC`, `CMD_WANT_SKB`, and `CMD_SIZE_HUGE`.
- EEPROM/regulatory definitions: `struct il_eeprom_channel`, calibration structures, channel-band offsets, SKU flags, and helpers such as `il_eeprom_query16`, `il_init_channel_map`, `il_get_channel_info`.
- Driver state: `struct il_priv` aggregates PCI/mac80211 objects, firmware images, RXON state, scan state, calibration data, station table, queues, work items, timers, debugfs state, LEDs, status bits, and per-family private substructures.
- Hardware abstraction: `struct il_ops` contains callbacks for TX queue handling, uCode loading, EEPROM semaphore access, RXON commit, scanning, station handling, power, LED commands, and hardware dumps.
- Configuration data: `struct il_hw_params`, `struct il_cfg`, `struct il_mod_params`, `struct il_power_mgr`.
- Rate and aggregation state: `struct il_ht_agg`, `struct il_tid_data`, `struct il_lq_sta`, `struct il_scale_tbl_info`, rate masks, PLCP/IEEE mapping constants, table type helpers, antenna masks.
- Register helpers: `_il_rd`, `_il_wr`, `il_rd`, `il_wr`, `_il_rd_prph`, `_il_wr_prph`, `il_set_bits_prph`, `il_clear_bits_prph`, `il_read_targ_mem`, `il_write_targ_mem`.

## Control Flow and Integration
The header does not implement the full driver, but it defines the control surfaces used by the implementation. Probe/configuration code binds a PCI ID to an `il_cfg`, fills `il_priv`, loads firmware through `fw_desc` DMA buffers, initializes RX/TX queues, then transitions status bits through init, alive, ready, scanning, RF kill, and error states. mac80211 callbacks declared here (`il_mac_config`, interface add/remove/change, scan, flush, BSS changes) drive RXON staging/commit, station table updates, queue flow control, and rate setup.

Hardware access is split deliberately. Plain CSR access uses `_il_rd`/`_il_wr` against PCI MMIO. Internal device resources require `il_rd`/`il_wr` or PRPH helpers, which take `reg_lock`, grab NIC access with `CSR_GP_CNTRL_REG_FLAG_MAC_ACCESS_REQ`, perform the access, and release NIC access. This contract is shared with `csr.h` and `prph.h`.

## State and Persistence Behavior
`struct il_priv` is the persistent in-memory state for a device lifetime. It stores firmware images and backup data for reload/recovery, EEPROM contents, regulatory channel tables, station keys and link-quality commands, queue descriptors and DMA memory, calibration accumulators, scan requests, workqueue/timer state, status bits, debugfs settings, traffic/interrupt counters, and LED state. Firmware images and queue memory are DMA coherent allocations and must be freed through matching helpers. EEPROM data is cached in `il->eeprom`; station and key state must be restored after firmware restart.

## Dependencies and Integration Points
The file depends on kernel PCI, DMA, workqueue/timer, LED, waitqueue, and MMIO APIs; on mac80211/cfg80211 types; and on local `commands.h`, `csr.h`, and `prph.h`. It exports contracts used by hw-specific 3945/4965 files, common RX/TX/scan/power/statistics code, debugfs, and rate control modules.

## Risks and Edge Cases
- Queue sizes are power-of-two assumptions; incorrect `n_bd`/`n_win` breaks wrap arithmetic.
- Register access helpers must match CSR versus internal/PRPH address space; using raw MMIO for powered-down internal resources can race sleep states.
- `il_priv` has many lock domains (`lock`, `hcmd_lock`, `reg_lock`, `sta_lock`, `mutex`); ordering mistakes can deadlock or expose stale station/queue state.
- Firmware API version and size limits are enforced through config fields; mismatches risk failed loads or uCode assertions.
- Debug and queue stop wrappers intentionally poison direct `ieee80211_stop_queue`/`wake_queue` use after local helpers, so new code must use refcounted stop/wake paths.

## Test Signals
Useful validation includes kernel build coverage for `CONFIG_IWL3945`, `CONFIG_IWL4965`, debug/debugfs variants, suspend/resume, firmware restart, scan cancel, RF kill/CT kill transitions, TX aggregation setup/teardown, station add/remove, EEPROM/channel-map parsing, and lockdep/KASAN runs around queue reclaim and debugfs reads.
