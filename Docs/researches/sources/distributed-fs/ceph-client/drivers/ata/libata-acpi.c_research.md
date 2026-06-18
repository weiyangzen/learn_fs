# sources/distributed-fs/ceph-client/drivers/ata/libata-acpi.c

## Purpose
`libata-acpi.c` provides ACPI integration for libata PATA and SATA devices. It binds ATA ports/devices to ACPI namespace objects, handles ACPI dock/bay hotplug notifications, evaluates and applies ACPI timing/taskfile methods (`_GTM`, `_STM`, `_GTF`, `_SDD`), manages ACPI power states for ATA devices, and disables ACPI integration after repeated failures.

## Important APIs, Types, And Functions
The file exposes `ata_dev_acpi_handle()`, `ata_acpi_bind_port()`, `ata_acpi_bind_dev()`, `ata_acpi_dev_manage_restart()`, `ata_acpi_port_power_on()`, `ata_acpi_dissociate()`, `ata_acpi_gtm()`, `ata_acpi_stm()`, `ata_acpi_gtm_xfermask()`, `ata_acpi_cbl_pata_type()`, `ata_acpi_on_resume()`, `ata_acpi_set_state()`, `ata_acpi_on_devcfg()`, and `ata_acpi_on_disable()`. `struct ata_acpi_gtf` models seven ATA taskfile registers returned by `_GTF`; `struct ata_acpi_hotplug_context` attaches libata port/device pointers to ACPI hotplug callbacks.

The `acpi_gtf_filter` module parameter controls filtering of risky `_GTF` commands such as transfer-mode changes, lock/freeze commands, DIPM, and FPDMA feature toggles.

## Control Flow
Binding starts from ACPI companion devices. PATA ports preset a port companion from the host companion and port number; SATA devices preset device companions with `_ADR` values derived from host port and PMP number. Both port and device binding allocate ACPI hotplug contexts when the ACPI object exists and no hotplug context is already installed.

ACPI notifications flow into `ata_acpi_handle_hotplug()`. Bus/device checks mark the port hotplugged and freeze it for EH. Eject requests mark a specific device or all edge-link devices for detach, schedule EH, and wait for EH completion. Separate uevent callbacks emit `BAY_EVENT=<event>` on the SCSI device or ATA port kobject.

Timing support uses `_GTM` to capture BIOS timing values, `_STM` to restore them with IDENTIFY buffers for master/slave, and `_GTM`-derived masks to infer PATA cable type. `_GTF` is evaluated lazily and cached in `dev->gtf_cache`; returned seven-byte taskfiles are converted to `ata_taskfile`, filtered, and executed through `ata_exec_internal()`. SATA configuration also calls `_SDD` with byte-swapped IDENTIFY data before `_GTF`. After any executed `_GTF` command, IDENTIFY data is reread.

Resume restores initial `_GTM` timing through `_STM` where available, refreshes or schedules `_GTF`, and marks devices with `ATA_DFLAG_ACPI_PENDING`. Device configuration runs pending ACPI work, retries once on failures, then sets `ATA_DFLAG_ACPI_DISABLED` after a second failure. Power-state helpers select ACPI D states for SATA devices individually, handle runtime ATAPI/ZPODD D3-cold restrictions, and sequence PATA channel/device power according to ACPI requirements.

## State And Persistence
Runtime state is held in ACPI companion bindings on `ap->tdev` and `dev->tdev`, hotplug contexts allocated per ACPI object, `ap->__acpi_init_gtm`, `ATA_PFLAG_INIT_GTM_VALID`, `dev->gtf_cache`, and device flags such as `ATA_DFLAG_ACPI_PENDING`, `ATA_DFLAG_ACPI_FAILED`, `ATA_DFLAG_ACPI_DISABLED`, and `ATA_DFLAG_DETACH`. Hardware/firmware state is mutated through ACPI power resources, `_STM` timing settings, and ATA taskfile commands from `_GTF`.

## Dependencies And Integration Points
The file depends on ACPI core object evaluation, ACPI power management, ACPI hotplug contexts, libata EH and internal command execution, SCSI device objects for uevents, PCI/libata structures, runtime PM, and ZPODD helpers. It is called from libata probe, resume, device configuration, disable, detach, and power-management paths.

## Risks And Edge Cases
Firmware-provided `_GTF` commands can be harmful; filtering prevents transfer-mode conflicts and lock/security/FPDMA/DIPM surprises by default. `_GTF` cache ownership is manual and must be cleared on disable/resume/error. Partial ACPI failures are tolerated only when no taskfile executed and the port is not frozen; otherwise EH retries and may disable ACPI for the device. `_STM` depends on valid 512-byte IDENTIFY buffers for both device slots. SATA and PATA use different ACPI companion topology and power sequencing, so incorrect `ATA_FLAG_ACPI_SATA` use can target the wrong namespace object. Runtime D3-cold for ATAPI is restricted to ZPODD-ready devices.

## Test Signals
Useful tests include ACPI namespace binding for PATA ports, SATA devices, and PMP devices; dock/bay add/eject notifications; uevent generation; `_GTM` success, not-found, wrong-type, and wrong-length cases; `_STM` execution and restore on dissociate/resume; `_GTF` caching, filtering, command rejection, command failure, and retry-disable behavior; `_SDD` IDENTIFY byte-swapping; PATA cable inference from GTM; SATA/PATA suspend and resume power sequencing; and ZPODD runtime D3-cold behavior.
