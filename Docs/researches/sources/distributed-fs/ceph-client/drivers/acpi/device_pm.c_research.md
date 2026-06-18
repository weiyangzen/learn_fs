# sources/distributed-fs/ceph-client/drivers/acpi/device_pm.c

## Purpose
Provides ACPI device power-management primitives and the generic ACPI PM domain. It discovers and changes ACPI D-states, manages power resources, handles wakeup GPEs and wake power, installs PM notification handlers, chooses sleep/runtime target states, and attaches ACPI PM callbacks to devices with ACPI companions.

## Important APIs, Types, And Functions
State helpers include `acpi_power_state_string()`, `acpi_device_get_power()`, `acpi_device_set_power()`, `acpi_bus_set_power()`, `acpi_bus_init_power()`, `acpi_device_update_power()`, and `acpi_bus_update_power()`. Fixup helpers include `acpi_device_fix_up_power()`, `acpi_device_fix_up_power_extended()`, `acpi_device_fix_up_power_children()`, and `acpi_dev_power_up_children_with_adr()`.

Wakeup helpers include `acpi_pm_wakeup_event()`, `acpi_add_pm_notifier()`, `acpi_remove_pm_notifier()`, `acpi_bus_can_wakeup()`, `acpi_pm_device_can_wakeup()`, and `acpi_pm_set_device_wakeup()`. Sleep-state selection is handled by `acpi_dev_pm_get_state()` and exported `acpi_pm_device_sleep_state()`.

Runtime/system PM entry points include `acpi_dev_suspend()`, `acpi_dev_resume()`, `acpi_subsys_runtime_suspend()`, `acpi_subsys_runtime_resume()`, `acpi_subsys_prepare()`, `acpi_subsys_complete()`, `acpi_subsys_suspend()`, `acpi_subsys_suspend_late()`, `acpi_subsys_suspend_noirq()`, `acpi_subsys_freeze()`, `acpi_subsys_restore_early()`, and `acpi_subsys_poweroff()`. `acpi_dev_pm_attach()` and `acpi_dev_pm_detach()` manage the `acpi_general_pm_domain`. `acpi_storage_d3()` and `acpi_dev_state_d0()` are exported policy/query helpers.

## Control Flow
Power discovery combines power-resource inference with `_PSC` when available. Setting power validates state support and parent state, handles D3cold as `_PS3` plus power-resource removal, executes `_PSx` in ACPI 6 order, updates power resources, and records `device->power.state`. Initialization sets unknown state, skips absent devices, references active power resources, and defaults to D0 when firmware provides no readable state.

Wake notifications install an ACPI system notify handler that responds to `ACPI_NOTIFY_DEVICE_WAKE`, signals a wakeup source, and optionally runs a registered callback. Wake enablement acquires `acpi_wakeup_lock`, enables wake power, enables the GPE, and maintains `enable_count`; disable reverses those steps.

Runtime suspend runs generic runtime suspend and then ACPI low-power transition with wake enabled. Runtime resume powers to D0, disables wake, then runs generic resume. System sleep callbacks coordinate with smart suspend, runtime-suspended devices, wake settings, `_SxD/_SxW/_S0W`, PM QoS, firmware-resume expectations, and driver callback ordering. PM domain attach installs the wake notifier and assigns `acpi_general_pm_domain` only to the first physical node for a companion and skips special IDs such as ACPI fans.

## State And Persistence
Persistent runtime state lives in each `struct acpi_device`: `power.state`, valid power-state descriptors, power-resource flags, wakeup context, wake GPE, wakeup source, notifier flags, and enable counters. Global mutexes serialize notifier installation, notifier callbacks, and wake GPE/power operations. Device PM domain assignment persists until detach. There is no persistent storage.

## Dependencies And Integration Points
Depends on ACPI power-resource helpers, ACPICA `_PSC/_PSx/_SxD/_SxW/_S0W` evaluation, Linux PM core, runtime PM, PM QoS, wakeup sources, suspend-to-idle logic, ACPI companion relationships from the bus layer, ACPI fan special IDs, fwnode properties, and platform storage-D3 quirks.

## Risks
Incorrect D-state choice can break enumeration, runtime PM, wakeup, or resume. Parent/child power ordering and shared power resources make inferred state differ from actual device state. Wake enable counts must stay balanced across repeated suspend/resume paths. Firmware may power devices during system sleep, requiring resume correction. PM-domain attachment to secondary physical nodes sharing a companion would double-apply ACPI PM, so the first-node check is essential.

## Test Signals
Signals include correct `power_state` and `real_power_state` sysfs values, successful runtime suspend/resume through ACPI PM domain, wake GPE enable/disable logs, wake from device events, proper behavior with PM QoS `NO_POWER_OFF`, storage D3 policy detection, non-D0 probe checks, and no resume regressions after firmware-assisted sleep. Tests should cover devices with only `_PSx`, only power resources, both `_PSC` and resources, wake-capable `_PRW`, wake IRQs, and shared ACPI companions.
