# sources/distributed-fs/ceph-client/drivers/ata/libata.h

## Purpose
`libata.h` is libata’s internal subsystem header. It collects private constants, configuration-dependent stubs, inline helpers, and cross-file function declarations for libata core, SATA, ACPI, SCSI translation, error handling, port multipliers, SFF, and ZPODD. It is the local contract between the libata implementation files rather than the public kernel ATA API.

## Important APIs, Types, And Functions
The header defines `DRV_NAME`, `DRV_VERSION`, the `ATA_DNXFER_*` selector constants, `ATA_PORT_TYPE_NAME`, and helpers such as `ata_sstatus_online`, `ata_dev_is_zac`, and `ata_port_eh_scheduled`. It declares core functions for taskfile/LBA conversion, read/write taskfile construction, internal command execution, readiness waits, IDENTIFY/revalidation/configuration, power state taskfiles, resource freeing, transfer mask limiting, queued-command issue/complete/free, ATAPI DMA checks, byte swapping, link online/offline checks, device/link initialization, ioctl handlers, speed strings, and log-page reads.

Subsystem sections declare optional SATA host helpers, ACPI bind/resume/power helpers with no-op stubs when disabled, SCSI translation and hotplug functions from `libata-scsi.c`, EH functions and reporting helpers, optional SATA PMP helpers with `-EINVAL`/`-EOPNOTSUPP` stubs, optional SFF init/flush helpers, and optional ZPODD functions with stubs when disabled.

## Control Flow
The header has no standalone runtime flow, but it defines compile-time control flow through `#ifdef CONFIG_*` sections. Callers can invoke ACPI, PMP, SFF, or ZPODD helpers without scattering feature checks throughout implementation files; disabled configurations resolve to inline no-ops or error-returning stubs.

## State And Persistence
The header declares global module parameters and shared objects such as `atapi_passthru16`, `libata_fua`, `libata_noacpi`, `libata_allow_tpm`, `ata_port_type`, and `ata_dev_phys_link`. It does not own persistent storage itself. Inline helpers inspect live fields such as SATA status, ATA device class/IDENTIFY data, and port EH flags.

## Dependencies And Integration Points
This file is included by libata implementation units to share private interfaces. It bridges libata core with SCSI (`struct scsi_device`, `struct scsi_cmnd`, `struct Scsi_Host`), block queue limits, ACPI, SATA/PMP, SFF, EH, and ZPODD code. `DRV_VERSION` is consumed by the SCSI VPD ATA information page in `libata-scsi.c`, and `ATA_PORT_TYPE_NAME` is used by the transport class.

## Risks And Edge Cases
Because this is an internal umbrella header, declaration drift can break builds or subtly change feature behavior across many files. Stub return values matter: callers may treat `-EINVAL`, `-EOPNOTSUPP`, `false`, or no-op differently. Inline helper changes can affect hot paths and EH decisions globally. The four-character `DRV_VERSION` constraint is explicitly documented and used in fixed-size response data.

## Test Signals
The main signal is matrix build coverage across `CONFIG_ATA_ACPI`, `CONFIG_SATA_HOST`, `CONFIG_SATA_PMP`, `CONFIG_ATA_SFF`, and `CONFIG_SATA_ZPODD` enabled/disabled combinations. Runtime smoke tests should cover SCSI queueing, EH scheduling, SFF init/exit, PMP absence stubs, ACPI disabled behavior, and ZPODD disabled no-op behavior.
