# sources/distributed-fs/ceph-client/drivers/mfd/palmas.c

## Purpose
`palmas.c` is the TI Palmas/TWL603x/TPS659xx family I2C MFD core. It creates multiple I2C clients/regmaps, configures interrupt handling, decodes pad mux state for child GPIO/PWM/LED users, writes PMU power-control policy, and populates DT children.

## Important APIs, Types, And Functions
`palmas_regmap_config[]` defines three client register windows. `palmas_irq_chip` and `tps65917_irq_chip` describe variant-specific regmap IRQ layouts. `palmas_ext_control_req_config()` is exported for regulator/resource consumers to assign external request lines. `palmas_dt_to_pdata()`, `palmas_set_pdata_irq_flag()`, `palmas_power_off()`, and `palmas_i2c_probe()` drive setup. `struct palmas_driver_data` selects features and IRQ chip.

## Control Flow
Probe obtains platform data or derives it from DT, allocates `struct palmas`, creates dummy I2C clients for secondary addresses, attaches regmaps, optionally configures IRQ polarity and clear-on-read behavior, registers a regmap IRQ chip, writes or reads pad mux registers, derives GPIO/PWM/LED mux masks, writes `PALMAS_POWER_CTRL`, populates DT children, and optionally registers `pm_power_off`. Remove tears down IRQs, dummy clients, and global poweroff state.

## State And Persistence
Persistent hardware state includes pad mux registers, interrupt polarity/clear behavior, external request assignments, power-control masks, and DEV_ON poweroff writes. Driver state stores regmaps, dummy clients, mux masks, IRQ data, feature flags, and a global `palmas_dev` for poweroff.

## Dependencies And Integration Points
It depends on I2C, regmap, regmap-irq, MFD core, OF child population, `linux/mfd/palmas.h`, IRQ trigger metadata, and DT properties such as `ti,mux-pad1`, `ti,mux-pad2`, `ti,power-ctrl`, `ti,system-power-controller`, and `ti,palmas-override-powerhold`.

## Risks
Global `pm_power_off` ownership is single-device and must be cleared on remove. Dummy client creation and of-node references must remain balanced. IRQ cleanup is called even when IRQ setup may have been skipped, so changes around no-IRQ paths need care. Pad mux interpretation is bitfield-heavy and drives child behavior. External request configuration silently ignores invalid IDs or missing `PALMAS_EXT_REQ`.

## Test Signals
Boot supported compatibles (`ti,palmas`, `ti,tps659038`, `ti,tps65917`), verify child devices, regmap IRQ delivery, IRQ polarity from DT/firmware, pad mux masks, exported external request control, system poweroff behavior, no-IRQ probe, and dummy-client error cleanup.
