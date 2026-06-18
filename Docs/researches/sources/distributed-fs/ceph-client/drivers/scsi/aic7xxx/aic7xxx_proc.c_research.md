# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic7xxx_proc.c

Purpose: `/proc`/host info support for the `aic7xxx` driver. It formats adapter, SEEPROM, negotiation, and per-device queue state for userspace and implements a write path for replacing serial EEPROM configuration.

Important APIs and functions: external functions are `ahc_proc_write_seeprom()` and `ahc_linux_show_info()`. Internal helpers are `ahc_calc_syncsrate()`, `ahc_format_transinfo()`, `ahc_dump_target_state()`, and `ahc_dump_device_state()`. It also carries the SCSI sync-rate exception table used for display formatting.

Control flow: `ahc_linux_show_info()` prints driver version, controller description, controller info, allocated SCBs, SG length, raw SEEPROM words if present, and then iterates targets/channels to dump user/goal/current transfer settings plus active LUN queue statistics. Device lookup is through `scsi_device_lookup_by_target()`. `ahc_proc_write_seeprom()` locks and pauses the adapter, validates buffer size and checksum, prepares a PCI or VL SEEPROM descriptor, acquires the SEEPROM if needed, writes the provided config, rereads it into `ahc->seep_config`, releases resources, unpauses, and returns bytes written or an error.

State and persistence: show path reads runtime negotiation state, `ahc->seep_config`, SCB counts, and `ahc_linux_device` counters. The write path persists data to serial EEPROM hardware and updates the in-memory copy. It mutates adapter pause state while writing.

Dependencies and integration: uses Linux `seq_file` output, SCSI target/device APIs, `aic7xxx_93cx6` SEEPROM helpers, register definitions for PCI/VL SEEPROM control, and host template `.show_info`/`.write_info` hooks from `aic7xxx_osm.c`.

Risks: SEEPROM writes are hardware-persistent and can make adapters misconfigured if the caller supplies wrong but checksummed data. The function requires exact `struct seeprom_config` size and checksum but not semantic validation. Proper pause/unpause and lock handling are critical. `scsi_device_lookup_by_target()` references should normally be paired with put operations; this legacy code does not show that in the loop.

Test signals: read `/proc/scsi/aic7xxx/*` with and without SEEPROM, verify transfer formatting for async/sync/wide/DT modes, exercise multi-channel target iteration, test rejected writes for wrong length/checksum/unsupported adapter/no SEEPROM, and validate successful write/reread on controlled hardware or emulation.
