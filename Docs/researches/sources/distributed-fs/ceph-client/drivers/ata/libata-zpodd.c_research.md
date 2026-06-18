# sources/distributed-fs/ceph-client/drivers/ata/libata-zpodd.c

## Purpose
`libata-zpodd.c` implements Zero Power Optical Disk Drive support for SATA ATAPI optical drives that firmware/ACPI can power off. It detects supported slot/drawer mechanisms, determines when the drive is zero-power-ready, enables ACPI wake for powered-off runtime suspend, handles ACPI wake notifications, and restores user-visible media polling/eject behavior after power-on.

## Important APIs, Types, And Functions
Public libata-internal entry points are `zpodd_init`, `zpodd_exit`, `zpodd_on_suspend`, `zpodd_zpready`, `zpodd_enable_run_wake`, `zpodd_disable_run_wake`, and `zpodd_post_poweron`. Internal helpers include `eject_tray`, `zpodd_get_mech_type`, `zpready`, `zpodd_wake_dev`, `ata_acpi_add_pm_notifier`, and `ata_acpi_remove_pm_notifier`.

The main private state is `struct zpodd`, containing mechanism type, owning `ata_device`, `from_notify`, `zp_ready`, `last_ready`, `zp_sampled`, and `powered_off`. The module parameter `zpodd_poweroff_delay` controls how long the drive must stay ready before poweroff is allowed.

## Control Flow
Initialization checks whether the ATA transport device has an ACPI companion capable of poweroff, queries the ATAPI removable media feature descriptor with GET CONFIGURATION, accepts only supported slot or drawer mechanisms, allocates `struct zpodd`, installs an ACPI system notify handler, exposes PM QoS flags, and stores the pointer in `dev->zpodd`. Exit removes the notify handler, frees state, and clears the pointer.

Suspend readiness flow calls `zpready`, which issues TEST UNIT READY and REQUEST SENSE through ATAPI EH helpers. A slot drive is considered ready when sense reports no media; a drawer drive additionally requires the no-media/door-closed qualifier. `zpodd_on_suspend` samples this condition and only sets `zp_ready` after it remains true for `zpodd_poweroff_delay` seconds. `zpodd_zpready` returns the cached decision.

Poweroff flow disables SCSI disk events to prevent polling from waking the drive, marks `powered_off`, and enables ACPI wake on the ATA transport device. Wake notification flow handles `ACPI_NOTIFY_DEVICE_WAKE` while the SCSI generic device is runtime suspended: it records `from_notify` and requests runtime resume. Post-poweron flow clears powered-off state, ejects the tray for drawer drives when the wake came from a user button notification, clears readiness sampling flags, and re-enables disk events.

## State And Persistence
All state is in memory and synchronized by the PM core according to the file comments. `struct zpodd` persists for the life of the ATA device. Runtime transitions mutate `from_notify`, `zp_ready`, `last_ready`, `zp_sampled`, and `powered_off`; ACPI wake state and SCSI disk-event polling are changed while the drive is powered down. No disk or firmware persistent settings are written.

## Dependencies And Integration Points
The file depends on ATAPI command execution (`ata_exec_internal`, TEST UNIT READY, REQUEST SENSE), libata device/taskfile helpers, SCSI device disk-event controls, ACPI companion and wake APIs, ACPI notify handlers, runtime PM, PM QoS exposure, jiffies/time helpers, and CD-ROM command definitions. It is compiled behind `CONFIG_SATA_ZPODD`; `libata.h` provides no-op stubs otherwise.

## Risks And Edge Cases
Sense-code interpretation is device-specific and conservative; unsupported or malformed GET CONFIGURATION data disables ZPODD. Drawer wake behavior sends an eject command after link recovery, so failures there should not block resume but affect UX. Notification install/remove assumes a valid ACPI handle once initialization accepted the companion. `zpodd_exit` calls remove unconditionally for initialized devices; callers must only use it after successful init state exists. Delayed readiness avoids rapid power cycling but can leave power savings disabled if media polling or transient sense changes reset sampling.

## Test Signals
Test with ACPI-poweroff-capable slot and drawer optical drives, unsupported optical mechanisms, media present/absent and drawer open/closed states, runtime suspend with `zpodd_poweroff_delay` boundaries, ACPI wake notification from eject button, resume path with tray ejection for drawer drives, media polling suppression/restoration, module parameter changes, and builds with `CONFIG_SATA_ZPODD` enabled and disabled.
