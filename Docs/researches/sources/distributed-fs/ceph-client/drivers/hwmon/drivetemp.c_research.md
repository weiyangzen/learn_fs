## sources/distributed-fs/ceph-client/drivers/hwmon/drivetemp.c

### Purpose

`drivetemp.c` registers a SCSI class interface that creates hwmon devices for SATA disks and zoned block disks with temperature reporting. It prefers ATA SCT Command Transport temperature data and limits, falling back to SMART attributes 194 or 190 when SCT is unavailable or unsafe for a known model family.

### Important APIs, types, and functions

`struct drivetemp_data` stores the SCSI device, owning device, hwmon device, ATA/SCT sector buffer, selected temperature-read callback, optional-attribute flags, and static limit values. Core helpers are `drivetemp_scsi_command()`, `drivetemp_ata_command()`, `drivetemp_get_smarttemp()`, `drivetemp_get_scttemp()`, `drivetemp_sct_avoid()`, `drivetemp_identify_sata()`, `drivetemp_identify()`, `drivetemp_read()`, `drivetemp_is_visible()`, `drivetemp_add()`, and `drivetemp_remove()`.

### Control flow

Module init registers a SCSI `class_interface`. On add, the driver rejects devices without inquiry data and non-disk/non-ZBC types, then reads ATA Information VPD page 0x89 under RCU to confirm SAT, ATA, and SATA. If SCT is supported and not blocked by the avoid list, it reads the SCT status log, validates version/current temperature, records history flags, optionally reads the SCT temperature-history table for limits, and installs `drivetemp_get_scttemp()`. Otherwise SMART fallback requires SMART support and a readable SMART temperature attribute.

### State and persistence behavior

Temperatures are not cached; each sysfs read sends ATA commands through SCSI. SCT limit values are captured once at probe. The selected read method persists as a function pointer. A global device list tracks instances for class-interface removal.

### Dependencies and integration points

Dependencies include SCSI class interfaces, SAT ATA pass-through via `ATA_16`, `scsi_execute_cmd()`, ATA identify helpers, RCU-protected `sdev->vpd_pg89`, and hwmon info registration. It integrates under each SCSI disk's generic device and exposes temperature files plus `HWMON_C_REGISTER_TZ`.

### Risks

Polling drive firmware can be unsafe; TOSHIBA DT01ACA* avoids SCT because polling can freeze drives under heavy writes. SMART attributes are vendor-defined. The global device list has no explicit lock and relies on class-interface serialization. Static SCT limits can become stale. SAT bridges may reject ATA pass-through.

### Test signals

Cover SCT-capable drives, SCT data-table limits, SMART-only fallback, non-SATA SCSI devices, SAT bridges without VPD 0x89, avoid-list models, SMART checksum failures, invalid `0x80` temperatures, and remove while hwmon exists.
