# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/atomisp_gmin_platform.c

## Purpose
This file provides legacy ACPI/EFI/DMI platform glue for AtomISP sensors on Intel gmin systems. It discovers/synthesizes sensor platform data, controls GPIOs, clocks, and power rails, registers sensor subdevices, and applies board quirks.

## Important APIs and Functions
`atomisp_platform_get_subdevs()` returns the legacy subdevice table. `atomisp_register_i2c_module()` registers gmin-managed sensors and records CSI data. `atomisp_gmin_remove_subdev()` and `atomisp_unregister_subdev()` remove entries and resources. `gmin_camera_platform_data()` allocates per-sensor state and returns PMIC-backed or ACPI-backed callback tables. Power callbacks control GPIOs, rails, ACPI power, and PMC clocks. `gmin_get_var_int()` reads DMI, DSM, or EFI variables. `isp_pm_cap_fixup()` disables broken BYT PCI runtime PM capability.

## Control Flow
Sensor drivers request platform data during probe. The driver detects PMIC, reserves a `gmin_subdev` slot, stores CSI format/bayer data, reads clock/port/lane/GPIO/regulator/PMIC config, and returns callbacks. Sensor registration records the subdev in `pdata_subdevs[]`. Removal shifts table entries and releases GPIO/regulator resources.

## State and Persistence
Global state includes `gmin_subdevs[]`, `pdata_subdevs[]`, `pmic_id`, shared PMIC address, shared 1.8V/2.8V regulator enable counts, and a PMC clock-name buffer. Each `gmin_subdev` tracks subdev, clock, GPIOs, regulators, CSI metadata, rail/clock booleans, PMIC address, and AXP overrides.

## Dependencies and Integration Points
Depends on I2C, ACPI, EFI variables, DMI, common clock, regulator, GPIO, Intel SoC PMIC helpers, and AtomISP platform headers. Exports symbols used by sensor drivers and overlaps with newer CSI2 bridge parsing.

## Risks
Fixed global slots can overflow. Shared regulator counters must stay balanced. PMIC writes use Intel opregion helpers. Firmware sources can conflict; DMI overrides win, DSM may be ignored for `CamClk`, and EFI fallback can be stale. `gmin_camera_platform_data()` assumes a free slot exists.

## Test Signals
Validate DMI/DSM/EFI parsing, PMIC detection for AXP/TI/Crystal Cove/regulator cases, balanced rail enables with multiple sensors, clock rate enable/disable, GPIO acquisition, CSI hostdata allocation/free, table overflow handling, and BYT PM-cap fixup.
