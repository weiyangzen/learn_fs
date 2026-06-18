<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas_ata.h -->
# sources/distributed-fs/ceph-client/include/scsi/sas_ata.h

## Purpose
This header gates SATA-over-SAS support for libsas. It exposes helpers for identifying SAS domain devices that are SATA/STP targets and for scheduling ATA reset, aborting ATA links, executing ATA FIS commands, and exposing SAS ATA SCSI-device attributes.

## Important APIs, Types, And Functions
When `CONFIG_SCSI_SAS_ATA` is enabled, `dev_is_sata()` returns true for `SAS_SATA_DEV`, `SAS_SATA_PENDING`, `SAS_SATA_PM`, and `SAS_SATA_PM_PORT`. The header declares `sas_ata_schedule_reset()`, `sas_ata_device_link_abort()`, `sas_execute_ata_cmd()`, `smp_ata_check_ready_type()`, and `sas_ata_sdev_attr_group`. When disabled, it provides no-op or success-returning inline stubs and an empty attribute-group macro.

## Control Flow
The active path lets libsas and LLDD code branch on `dev_is_sata()` and call ATA-specific recovery or FIS execution helpers. The disabled path compiles out SATA behavior while preserving callers, so control flow continues without scheduling resets or aborting links.

## State And Persistence
No state is owned by this header. It operates on `struct domain_device`, `struct ata_link`, and libata-backed state embedded in `struct sata_device`.

## Dependencies And Integration Points
It includes `linux/libata.h` and `scsi/libsas.h`, connecting SAS discovery/EH to libata error handling and sysfs attributes. It is an integration point for STP/SATA devices discovered behind SAS expanders.

## Risks
The disabled stubs returning success can hide missing SATA support if callers assume an ATA command actually executed. `dev_is_sata()` must track `enum sas_device_type` changes. Link abort/reset calls must be coordinated with libata EH and SAS domain teardown.

## Test Signals
Build both with and without `CONFIG_SCSI_SAS_ATA`, verify SATA device detection, run ATA reset/link-abort paths through libsas, check SMP ATA readiness, and confirm sysfs attribute presence only when support is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/scsi/sas_ata.h -->
