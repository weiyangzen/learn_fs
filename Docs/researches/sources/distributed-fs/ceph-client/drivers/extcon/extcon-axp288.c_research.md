# sources/distributed-fs/ceph-client/drivers/extcon/extcon-axp288.c

## Purpose
`extcon-axp288.c` handles USB charger-type detection and USB role switching for X-Powers AXP288 PMICs on Intel tablet platforms.

## Important APIs, types, and functions
`struct axp288_extcon_info` tracks PMIC regmap/IRQ data, extcon device, optional INT3496 ID extcon, USB role switch, role work, previous cable, and VBUS state. Core helpers are `axp288_handle_chrg_det_event()`, `axp288_get_vbus_attach()`, `axp288_usb_role_work()`, `axp288_get_id_pin()`, `axp288_extcon_enable()`, and `axp288_extcon_find_role_sw()`.

## Control flow
Probe gets parent AXP20x state, optionally locates the Cherry Trail xHCI role switch and INT3496 ID extcon, blocks P-unit I2C access while reading initial VBUS/reset-source information, registers extcon cables for SDP/CDP/DCP plus USB, maps PMIC IRQs through regmap-irq, registers an ID notifier if present, synchronizes role-switch state, starts BC1.2 detection, and enables wakeup. Interrupts synchronously run charger detection: read VBUS, ensure charger detection completed, decode SDP/CDP/DCP, clear old cable state, set new extcon states, and schedule USB role work if VBUS changed.

## State and persistence behavior
Runtime state includes `previous_cable`, `vbus_attach`, pending role work, and PMIC registers. Reset-source indicator bits are logged and cleared on probe. No durable state is stored.

## Dependencies and integration points
The driver depends on AXP20x MFD/regmap, regmap IRQs, IOSF MBI P-unit I2C locking, extcon, ACPI/software nodes, `usb_role_switch`, x86 CPU matching, and optional INT3496 extcon state.

## Risks and edge cases
PMIC register access must be wrapped with IOSF P-unit I2C blocking to avoid firmware collisions. Role-switch lookup can defer probe. Unknown BC1.2 results fall back to SDP. The driver uses the extcon state of another ACPI device if present, so probe ordering and notifier cleanup matter. Only VBUS rising IRQ is wake-enabled in suspend.

## Test signals
Validate SDP/CDP/DCP/no-VBUS detection, INT3496-present and absent role control, host/device/none role transitions, P-unit lock failure, regmap IRQ mapping failures, suspend wake on charger insertion, reset-source clearing, and probe deferral for the role switch.
