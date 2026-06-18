# sources/distributed-fs/ceph-client/drivers/acpi/tiny-power-button.c

## Purpose

This tiny ACPI power-button driver sends a configured signal to init when an ACPI power-button event occurs. It is a minimal alternative to the larger ACPI button input path for configurations that want power button delivery through `kill_cad_pid()`.

## Important APIs, types, and functions

The module parameter `power_signal` defaults to `CONFIG_ACPI_TINY_POWER_BUTTON_SIGNAL`. The ACPI ID table matches both regular and fixed power-button HIDs. Event handling is split between `acpi_tiny_power_button_notify()` for device notify events, `acpi_tiny_power_button_event()` for fixed hardware events, and `acpi_tiny_power_button_notify_run()` to run fixed events in ACPI notify-handler context. Probe/remove install and remove either a fixed event handler or a device notify handler.

## Control flow

Probe obtains the ACPI companion. If the ACPI device type is the fixed power button, it installs `acpi_tiny_power_button_event()` for `ACPI_EVENT_POWER_BUTTON`; otherwise it installs an ACPI device notify handler. Fixed event callbacks schedule notify work with `acpi_os_execute()` and return `ACPI_INTERRUPT_HANDLED`. The common notify path calls `kill_cad_pid(power_signal, 1)`. Remove unregisters the matching handler and waits for pending ACPI events to complete.

## State and persistence

The only persistent module state is the configurable signal number. Handler registration is per probed platform device and removed on driver detach.

## Dependencies and integration points

The driver depends on ACPI button HIDs, ACPI fixed-event and notify-handler APIs, ACPICA deferred execution, platform-device matching, and the kernel CAD/init signaling helper.

## Risks

Every notify event for the matched device sends the signal; there is no filtering by event code. An invalid or surprising `power_signal` value changes user-visible init behavior. Remove must wait for pending ACPI callbacks to avoid executing after driver detach.

## Test signals

Test fixed and namespace power-button devices, signal delivery to init, module parameter changes, handler removal with pending events, and coexistence expectations with other ACPI button handling in tiny configurations.
