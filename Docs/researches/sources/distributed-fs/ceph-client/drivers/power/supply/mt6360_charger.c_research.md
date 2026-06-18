
# sources/distributed-fs/ceph-client/drivers/power/supply/mt6360_charger.c

## Purpose
MT6360 charger support registers a USB-type power supply plus an OTG VBUS regulator for the MediaTek/Richtek MT6360 PMU charger block. It exposes charger online/status/type and tunable current/voltage limits through the generic `power_supply` API while driving hardware through the parent MFD regmap.

## Important APIs, Types, and Functions
`struct mt6360_chg_info` owns the device, regmap, copied `power_supply_desc`, regulator device, BC1.2 detection state, USB type cache, and charger-detect work item. Linear charge ranges are encoded in `mt6360_chg_range` and used by getter/setter helpers. Important entry points are `mt6360_charger_probe()`, `mt6360_chg_init_setting()`, `mt6360_chg_irq_register()`, `mt6360_charger_get_property()`, `mt6360_charger_set_property()`, `mt6360_pmu_attach_i_handler()`, and `mt6360_handle_chrdet_ext_evt()`.

## Control Flow
Probe allocates state, initializes `chgdet_lock`, creates autocancel work, reads optional `richtek,vinovp-microvolt`, obtains the parent regmap, applies charger defaults, registers the power supply, registers `attach_i` and `chrdet_ext_evt` IRQs, registers the OTG regulator, then schedules an initial charger-detect work pass. Property reads translate regmap fields into power_supply values. Property writes update the force-sleep bit, charge current, regulation voltage, input current, MIVR, precharge current, or termination current. VBUS events enable or disable BC1.2 detection; attach IRQs decode `USB_STATUS1` and update `psy_usb_type`.

## State and Persistence
State is volatile driver memory plus hardware registers. `pwr_rdy`, `bc12_en`, and `psy_usb_type` cache interrupt-derived state and are protected by `chgdet_lock`. Hardware settings persist only as programmed PMU register values until reset or driver reconfiguration. There is no disk persistence.

## Dependencies and Integration Points
The driver depends on platform/MFD instantiation, parent `regmap`, `linux/power_supply.h`, regulator framework regmap ops, device properties, IRQ names `attach_i` and `chrdet_ext_evt`, and `devm_work_autocancel`. The power-supply descriptor exposes USB type availability for sysfs formatting in `power_supply_sysfs.c`. The OTG regulator is matched as `usb-otg-vbus-regulator`.

## Risks and Test Signals
Risk areas include register field mistakes, especially `mt6360_charger_set_mivr()` updating `MT6360_PMU_CHG_CTRL3` with `MT6360_VMIVR_MASK` while the getter reads `CHG_CTRL6`; BC1.2 race handling around detach/attach; and IRQ trigger assumptions. Test by probing with a DT node, checking sysfs values for online/status/usb_type, writing current/voltage limit attributes, validating VBUS attach/detach uevents, confirming regulator enable/voltage control, and fault-injecting regmap/IRQ failures.
