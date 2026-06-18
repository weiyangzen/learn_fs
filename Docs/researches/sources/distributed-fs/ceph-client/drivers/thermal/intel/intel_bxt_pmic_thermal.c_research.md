# sources/distributed-fs/ceph-client/drivers/thermal/intel/intel_bxt_pmic_thermal.c

## Purpose

`intel_bxt_pmic_thermal.c` handles thermal interrupts from the Broxton Whiskey Cove PMIC and forwards matching PMIC sensor events to Linux thermal zones.

## Important APIs, Types, and Functions

`struct trip_config_map` maps PMIC IRQ/status/enable registers to thermal trip numbers. `struct thermal_irq_map` maps ACPI/thermal-zone names such as `STR0` to trip configs. `pmic_thermal_irq_handler()` resolves active PMIC thermal IRQ bits, updates the named thermal zone, and clears IRQ bits. `pmic_thermal_probe()` maps platform IRQs to regmap IRQ virqs, requests threaded IRQs, and unmasks PMIC thermal interrupt bits.

## Control Flow

Probe obtains parent `intel_soc_pmic`, regmap, and regmap IRQ chip data, then requests every platform IRQ until `-ENXIO`. It then iterates configured thermal maps and clears mask bits to enable thermal interrupts. Runtime IRQ handling walks all maps/trips, reads IRQ registers, reads event status, updates the corresponding thermal zone by name, and clears the matched IRQ.

## State and Persistence Behavior

The driver has static mapping tables and no per-device heap state. PMIC interrupt masks and latched event bits live in PMIC registers and persist until changed/cleared.

## Dependencies and Integration Points

It depends on MFD `intel_soc_pmic`, regmap/regmap-irq, platform IRQ resources, and thermal zones already registered for names like `STR0`. The platform ID `bxt_wcove_thermal` selects mapping data.

## Risks and Test Signals

Risks include thermal zone lookup by fixed string, ignoring `evt_stat` contents after reading, clearing IRQ with `reg_val & mask`, and no cleanup to re-mask interrupts on remove. Test signals include virq mapping, IRQ request count, interrupt unmask register writes, each STR sensor update, and regmap read/write error paths.
