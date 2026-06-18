# sources/distributed-fs/ceph-client/drivers/extcon/extcon-max8997.c

## Purpose
MAX8997 MUIC extcon provider for Samsung-era micro-USB accessory and charger detection. It maps MAX8997 MUIC and PMIC charge insert/remove interrupts into extcon states for USB device, USB host, SDP/CDP/DCP/fast/slow chargers, MHL, dock, and JIG.

## Important APIs, Types, and Functions
`struct max8997_muic_info` stores the MUIC I2C client, extcon device, previous ADC/charger type, two-byte status cache, current IRQ, work item, mutex, platform data, delayed cold-plug work, and default USB/UART switch paths. `max8997_muic_set_debounce_time()` programs ADC debounce. `max8997_muic_set_path()` programs CONTROL1 switch routing and CONTROL2 low-power/charge-pump bits. `max8997_muic_get_cable_type()` classifies ADC or charger groups and preserves previous values for detaches. `max8997_muic_handle_usb()`, `_handle_dock()`, and `_handle_jig_uart()` apply switch paths and extcon notifications. `max8997_muic_probe()` binds to the parent MFD, requests IRQ-domain mappings, registers extcon, applies platform initialization data, and schedules delayed initial detection.

## Control Flow
Probe obtains `struct max8997_dev` and optional platform MUIC data, registers threaded IRQs for ADC, VBVolt, charger-detect, OVP, and PMIC charger insert/remove lines, then registers extcon. If platform data exists, the driver writes board-provided initial register values and uses board-provided USB/UART paths and detect delay; otherwise defaults are used. It reads current STATUS1/2 to route UART JIG early, sets ADC debounce, and queues delayed detection. At runtime the threaded IRQ stores the virtual IRQ in `info->irq` and schedules work. `max8997_muic_irq_work()` maps that virtual IRQ back to a logical MUIC/PMIC interrupt, reads STATUS1/2, dispatches ADC or charger handling, and logs unsupported interrupts.

## State and Persistence
The only persistent effects are MUIC register programming and extcon state. Previous cable and charger types are per-device fields used to classify detach after open/no-charger statuses. `info->irq` is a transient one-slot pending IRQ field, so simultaneous IRQs before work runs can overwrite each other; the regmap/IRQ domain may still latch source state, but this worker only dispatches one stored IRQ type.

## Dependencies and Integration Points
Uses extcon provider, MAX8997 MFD register helpers (`max8997_update_reg`, `max8997_bulk_read`, `max8997_write_reg`), IRQ domain mapping, platform data, and workqueues. It integrates with board data through `struct max8997_muic_platform_data` for initial register writes, routing, and cold-plug delay.

## Risks
The single `info->irq` field is a race-prone compression of interrupt sources. The PMIC charger insert/remove IRQs share the charger handler, so charger classification depends on fresh STATUS2 reads. Unsupported ADC accessories return `-EAGAIN`, producing error logs during boot cold-plug detection. Probe has no remove callback to cancel delayed work, though devm work autocancel is used only for `irq_work`; the delayed work is initialized manually. Board-specific path values and init data can change core routing behavior.

## Test Signals
Check extcon uevents for USB host, USB device plus SDP, CDP, DCP, fast/slow chargers, MHL, dock, and JIG. Validate platform-data defaults versus custom USB/UART paths. Exercise ADC open detach after each attach type, PMIC charger insert/remove, cold-plug after the configured delay, and failures from STATUS reads or IRQ mapping.
