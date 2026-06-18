
# sources/distributed-fs/ceph-client/drivers/power/supply/mt6370-charger.c

## Purpose
The MT6370 charger driver exposes a USB charger power supply and an OTG VBUS regulator for MediaTek/Richtek MT6370 hardware. It manages BC1.2 attach detection, charger limit programming, MIVR recovery behavior, and ADC-assisted charger fault workarounds.

## Important APIs, Types, and Functions
`struct mt6370_priv` stores regmap fields, IIO ADC channels, ordered workqueue, BC1.2 work, MIVR delayed work, IRQ numbers, attach state, USB type, and power-supply/regulator handles. `mt6370_chg_fields` maps logical fields to `regmap_field` definitions and optional `linear_range` converters. Main functions include `mt6370_chg_probe()`, `mt6370_chg_init_rmap_fields()`, `mt6370_chg_init_setting()`, `mt6370_chg_get_property()`, `mt6370_chg_set_property()`, `mt6370_chg_bc12_work_func()`, `mt6370_chg_pwr_rdy_check()`, `mt6370_mivr_handler()`, and `mt6370_chg_mivr_dwork_func()`.

## Control Flow
Probe gets the parent regmap, allocates all regmap fields, obtains all IIO ADC channels, registers the OTG regulator, registers the power supply, creates the attach mutex and ordered workqueue, sets up work items, initializes hardware, requests three named IRQs, then samples power-ready state. UVP events call `mt6370_chg_pwr_rdy_check()`, which feeds `POWER_SUPPLY_PROP_ONLINE` back into the driver's setter. The setter updates `attach` and queues BC1.2 work. Attach IRQs mark BC1.2 complete and queue work to decode USB type. MIVR IRQs hold a wake reference, mask the IRQ, delay 200 ms, read MIVR state and IBUS, optionally toggle CFO, then re-enable IRQ.

## State and Persistence
Driver state is volatile and guarded by `attach_lock` for attach/USB-type transitions. Regmap fields hold current hardware configuration. Workqueue ordering serializes BC1.2 state transitions. There is no persistent storage, but DT/regulator settings and hardware register defaults are reapplied on probe.

## Dependencies and Integration Points
The driver integrates with regmap, regmap_field, IIO, regulator, GPIO parsing for an optional OTG enable GPIO, power_supply, platform IRQs, and workqueues. It exports USB type values to the core sysfs layer and uses `power_supply_changed()` for notification propagation.

## Risks and Test Signals
Risk areas include property-map/range mistakes, MIVR IRQ masking not being restored on unexpected paths, reliance on ordered workqueue lifetime, IIO channel indexing, and BC1.2 state loops through `power_supply_set_property()`. Tests should exercise attach/detach, SDP/CDP/DCP detection, writable limit attributes, OTG regulator voltage/current/enable behavior, MIVR IRQ handling under low IBUS, and probe deferral/error paths for regmap/IIO/IRQ resources.
