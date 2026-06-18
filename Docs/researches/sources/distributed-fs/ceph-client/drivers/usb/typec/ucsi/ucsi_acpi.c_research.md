# sources/distributed-fs/ceph-client/drivers/usb/typec/ucsi/ucsi_acpi.c

Purpose: Implements the ACPI transport for UCSI devices exposed as a memory operation region plus ACPI `_DSM` read/write methods.

Important APIs/types/functions: `struct ucsi_acpi` stores device, UCSI core instance, mapped base address, quirk state, DSM GUID, and last command. Transport ops include `ucsi_acpi_read_version`, `ucsi_acpi_read_cci`, `ucsi_acpi_poll_cci`, `ucsi_acpi_read_message_in`, `ucsi_acpi_async_control`, and either `ucsi_sync_control_common` or LG Gram-specific `ucsi_gram_sync_control`. Probe/remove/resume are `ucsi_acpi_probe`, `ucsi_acpi_remove`, and `ucsi_acpi_resume`.

Control flow and state: probe defers if ACPI dependencies are unmet, maps the memory resource, parses the DSM GUID, selects quirk ops via DMI, creates/registers UCSI, installs an ACPI notify handler, and stores platform data. Reads copy from the mapped UCSI memory area, while async control writes the command to `UCSI_CONTROL`, remembers it, and evaluates the write DSM. Notifications read CCI and call `ucsi_notify_common`. Resume queues generic UCSI resume.

Persistence behavior: state is in memory plus the ACPI operation region owned by firmware. The driver does not persist host state; notification masks are restored by the UCSI core on resume.

Dependencies/integration points: ACPI platform device `PNP0CA0`, `_DSM` UUID `6f8398c2-7ca4-11e4-ad36-631042b5008f`, DMI matching for LG gram, platform memory resources, UCSI core, and ACPI notify handlers.

Risks: firmware DSM failures block reads/writes. Memory-region layout must match UCSI offsets. LG gram quirk clears a bogus power-level/PDO change event after partner source PDO reads; incorrect quirk matching would hide legitimate events or leave bogus loops. Remove unregisters/destroys before removing the notify handler, so handler ordering should be considered under concurrent ACPI notifications.

Test signals: ACPI probe on PNP0CA0, DSM read/write return status, notify-to-CCI delivery, DMI quirk behavior on affected LG systems, suspend/resume notification restoration, and hotplug/role events through the generic UCSI core.
