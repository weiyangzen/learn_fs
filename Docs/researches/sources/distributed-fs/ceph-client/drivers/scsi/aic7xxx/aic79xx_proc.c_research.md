# sources/distributed-fs/ceph-client/drivers/scsi/aic7xxx/aic79xx_proc.c

## Purpose

`aic79xx_proc.c` implements procfs-style reporting and SEEPROM write support for the AIC79xx Linux driver. It formats controller, SEEPROM, target negotiation, and per-device queue state into a `seq_file`, and it accepts a full `struct seeprom_config` image for NVRAM updates.

## Important APIs, Types, and Functions

- `ahd_calc_syncsrate()` converts SCSI sync period factors to kHz, using exception entries for FAST-160/80/40/20 and a standard factor fallback.
- `ahd_format_transinfo()` formats `struct ahd_transinfo` as transfer speed, frequency, width, and PPR options.
- `ahd_dump_target_state()` prints user/goal/current negotiation state for one target and iterates LUN devices under the Linux `scsi_target`.
- `ahd_dump_device_state()` prints per-LUN queue counters from `struct ahd_linux_device`.
- `ahd_proc_write_seeprom()` validates size and checksum, pauses the controller, switches to SCSI mode, acquires SEEPROM access, writes the provided config, rereads it into `ahd->seep_config`, and restores mode/pause/lock state.
- `ahd_linux_show_info()` prints driver version, adapter description/controller info, allocated SCBs, S/G length, raw SEEPROM words, and target state for all targets.

## Control Flow and State

Read/display flow starts from Linux SCSI host info callback `show_info`, retrieves `ahd_softc` from `shost->hostdata`, emits high-level adapter data, dumps NVRAM if available, then loops through 8 or 16 targets depending on `AHD_WIDE`. Each target report fetches AHD transinfo and, when Linux target state exists, reports goal/current negotiation and all attached LUN queue counters.

Write flow is conservative: it locks the adapter, pauses if needed, saves register modes, switches to SCSI mode, validates the exact buffer length and checksum, acquires SEEPROM, ensures `seep_config` storage exists, writes the words at the channel-specific offset, rereads the data, releases SEEPROM, restores modes, resumes if this function paused the card, and unlocks.

## State and Persistence Behavior

`ahd_linux_show_info()` is read-only. `ahd_proc_write_seeprom()` is persistent: it writes serial EEPROM hardware, updates the in-memory `ahd->seep_config`, and affects future boots/probes. It returns either the byte count written or `-EINVAL` for validation/access failures.

## Dependencies and Integration Points

The file depends on Linux `seq_file`, SCSI target/device lookup, AHD core transinfo/SEEPROM helpers, `aic79xx_osm.h` platform structures, and `aic79xx_inline.h` pause/mode helpers. Its entry points are referenced by `aic79xx_osm.h` and installed in `aic79xx_driver_template`.

## Risks

- SEEPROM writes require a complete valid image; partial or wrong-sized writes are rejected, but a valid checksum with semantically bad settings can persist bad bus policy.
- The code uses atomic allocation while the adapter is locked/paused; allocation failure leaves the write rejected.
- Device lookup in the target dump must be balanced by the SCSI core semantics; if kernel APIs change, reference handling should be reviewed.
- Reporting assumes `struct ahd_linux_device` exists for each found `scsi_device`.

## Test Signals

- `/proc` or host show-info output should include driver version, controller info, SEEPROM words, and target transfer settings.
- Valid SEEPROM write should return exactly `sizeof(struct seeprom_config)` and reread matching data.
- Invalid length/checksum/no-SEEPROM writes should fail with diagnostic logs and restore controller pause/mode state.
