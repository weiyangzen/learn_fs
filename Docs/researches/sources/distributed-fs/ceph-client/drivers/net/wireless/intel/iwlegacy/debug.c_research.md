# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/debug.c

## Purpose
`debug.c` implements iwlegacy debugfs support and traffic accounting when `CONFIG_IWLEGACY_DEBUGFS` is enabled. It exposes runtime diagnostic files for TX/RX statistics, EEPROM/SRAM dumps, station and queue state, interrupt counters, firmware stats, calibration state, power-save status, force reset, watchdog timeout, missed beacon threshold, and RF calibration toggles.

## Important APIs, Types, and Functions
- `il_update_stats()` classifies TX/RX frame control values into management, control, and data counters and is exported.
- `il_dbgfs_register()` creates the debugfs directory tree and files under the wiphy debugfs directory.
- `il_dbgfs_unregister()` recursively removes the debugfs tree.
- Read handlers include `*_tx_stats_read`, `*_rx_stats_read`, `*_sram_read`, `*_nvm_read`, `*_stations_read`, `*_channels_read`, `*_status_read`, `*_interrupt_read`, `*_qos_read`, `*_tx_queue_read`, `*_rx_queue_read`, `*_sensitivity_read`, `*_chain_noise_read`, and `*_power_save_status_read`.
- Write handlers include clear traffic stats, interrupt stats reset, SRAM offset/length selection, disable HT40, clear firmware stats, missed beacon threshold, force reset, and watchdog timeout.
- `DEBUGFS_*` macros generate file operations and add files/booleans.

## Control Flow and Integration
The register function creates `data`, `rf`, and `debug` subdirectories. Read paths allocate a temporary buffer, format the current `il_priv` fields with `scnprintf`, call `simple_read_from_buffer`, and free the buffer. Write paths copy bounded user input, parse an integer or offset/length tuple, then mutate driver state or call driver operations. Firmware statistic reads dispatch through `il->debugfs_ops` for hardware-specific formatting.

## State and Persistence Behavior
The file reads and mutates live `il_priv` state: packet counters, ISR counters, EEPROM bytes, SRAM dump selection (`dbgfs_sram_offset`, `dbgfs_sram_len`), station aggregation state, channel tables, queue pointers, calibration structures, power state bits, missed beacon threshold, watchdog timeout, and force reset counters. Debugfs state lasts until unregister or device removal. Traffic and ISR counters can be reset through debugfs.

## Dependencies and Integration Points
It depends on `common.h`, mac80211 frame helpers, debugfs, copy-from-user, simple read helpers, and hardware-specific debug operations. It uses common functions such as `il_read_targ_mem`, `il_eeprom_query16`, `il_get_hw_mode`, `il_clear_isr_stats`, `il_send_stats_request`, `il_force_reset`, and `il_setup_watchdog`.

## Risks and Edge Cases
- Many reads traverse live state with minimal locking, so output is diagnostic and can race with device reset/removal.
- `sram_read` can allocate large buffers based on user-selected length and reads target memory; invalid ranges can be expensive or fail depending on device state.
- `disable_ht40` is rejected while associated, but other knobs such as force reset and watchdog updates are intentionally disruptive.
- Several buffer sizes are hand-estimated; future additions must keep `scnprintf` bounds and allocation calculations correct.

## Test Signals
Build with and without `CONFIG_IWLEGACY_DEBUGFS`, mount debugfs, read all files while associated and unassociated, exercise clear/reset writes, validate SRAM/EEPROM dump bounds, check force-reset behavior, run KASAN/lockdep while removing the device during debugfs access, and verify traffic counters with known management/control/data frames.
