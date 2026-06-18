# sources/distributed-fs/ceph-client/drivers/acpi/dptf/dptf_power.c

## Purpose
Implements Intel DPTF platform power and battery participant support. It exposes platform power-source/limit/adapter telemetry and DPTF battery electrical telemetry through sysfs, and notifies userspace when firmware reports changed values.

## Important APIs, Types, And Functions
`DPTF_POWER_SHOW()` defines read-only sysfs attributes backed by ACPI integer methods: `PMAX`, `PSRC`, `ARTG`, `PBSS`, `CTYP`, `PROP`, `RBHF`, `VBNL`, and `CMPP`. `prochot_confirm_store()` writes a sequence number to `PBOK`. `dptf_participant_type()` reads `PTYP`.

Two attribute groups exist: `dptf_power` for platform participant type `0x11`, and `dptf_battery` for battery participant type `0x0C`. `dptf_power_notify()` maps ACPI notification codes to changed attribute names and calls `sysfs_notify()`. Probe/remove are `dptf_power_add()` and `dptf_power_remove()` in a platform driver matching `INT3407`, `INT3532`, and multiple newer `INTC` IDs.

## Control Flow
Probe obtains the ACPI companion, reads `PTYP`, chooses the matching attribute group, installs an ACPI device notify handler, creates the sysfs group, and stores the ACPI device in platform data. Reads evaluate AML methods on demand and print integer values. `prochot_confirm` writes `PBOK`. Notifications for power source, power properties, max power, steady-state power, impedance, and voltage/current choose the relevant attribute and notify either the `dptf_battery` or `dptf_power` group based on current `PTYP`. Remove unregisters the notify handler and removes the appropriate sysfs group.

## State And Persistence
The driver keeps only the ACPI device pointer as platform data. All telemetry and control state is firmware-owned and read or written through AML methods. Sysfs notifications are transient events for userspace pollers.

## Dependencies And Integration Points
Depends on ACPI platform-device binding, AML integer method evaluation, ACPI notify handlers, sysfs groups/notifications, and DPTF participant firmware. It integrates with userspace thermal/power managers through `dptf_power` and `dptf_battery` sysfs directories.

## Risks
Participant type determines the sysfs ABI; firmware reporting an unexpected or changing `PTYP` can prevent binding or remove the wrong group. Notification mapping covers only known event codes and logs unsupported events. Attributes return `-EINVAL` on AML failure, so transient firmware errors surface directly to userspace. The attribute name `current_discharge_capbility_ma` preserves a misspelling, which is ABI once exposed.

## Test Signals
Signals include correct binding for `PTYP` `0x11` and `0x0C`, correct sysfs group selection, valid reads for all AML-backed attributes, successful `PBOK` writes, `sysfs_notify()` wakeups on supported ACPI events, and clean unbind. Negative tests should cover wrong `PTYP`, failed methods, unsupported notifications, and notification routing for battery versus platform participants.
