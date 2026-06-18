# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max77693.c

## Purpose
`extcon-max77693.c` supports the Maxim MAX77693 MUIC, reporting USB, host, charger, MHL, jig, and dock extcon states while handling dock button input events and programming MUIC switch paths.

## Important APIs, types, and functions
`struct max77693_muic_info` stores parent MFD state, extcon, previous ADC/GND/charger/button classifications, status bytes, current IRQ, work items, mutex, dock input device, and USB/UART paths. Major helpers are `max77693_muic_get_cable_type()`, `max77693_muic_set_path()`, `max77693_muic_adc_ground_handler()`, `max77693_muic_jig_handler()`, `max77693_muic_dock_handler()`, `max77693_muic_dock_button_handler()`, `max77693_muic_adc_handler()`, `max77693_muic_chg_handler()`, `max77693_muic_irq_work()`, and `max77693_muic_detect_accessory()`.

## Control flow
Probe initializes or reuses the MUIC regmap, registers a dock input device, maps and requests all nested MUIC IRQs, registers extcon, applies platform or default MUIC initialization registers, sets USB/UART paths and delayed detection time, routes UART jig early if present, reads device ID, configures ADC debounce, and queues delayed initial detection. IRQ handler records the virq and schedules work. Work maps the virq back to a MUIC interrupt type, reads STATUS1/STATUS2 under a mutex, dispatches ADC-family events to accessory/dock/jig/button handling, and dispatches charger-family events to charger and composite MHL/dock charging handling.

## State and persistence behavior
The driver keeps previous ADC, ADC-ground, charger, and button classifications so detach and button release can be reported after hardware returns open states. Hardware registers store path, low-power/charge-pump, debounce, and interrupt-mask configuration. There is no persistent storage.

## Dependencies and integration points
It depends on MAX77693 MFD/regmap/irq-domain support, extcon provider APIs, Linux input for dock keys, workqueues, mutexes, platform data or OF match, and EDAC-independent MFD initialization.

## Risks and edge cases
The global `muic_irqs[]` stores virqs and is shared across device instances, so multiple devices would overwrite IRQ mappings. Work records only one `info->irq`, so rapid different IRQs before work runs can collapse or be misclassified. Composite MHL/dock plus charger cases have ordering assumptions between ADC and charger IRQs. The default initial detection delay is 20 seconds, so early consumers may see stale state.

## Test signals
Test USB host, USB SDP, DCP, CDP, Apple slow/fast chargers, MHL with/without VBUS, smart/audio docks, jig USB/UART, dock buttons, simultaneous ADC/charger IRQ ordering, delayed initial detection, multiple-instance behavior, and regmap/input allocation failures.
