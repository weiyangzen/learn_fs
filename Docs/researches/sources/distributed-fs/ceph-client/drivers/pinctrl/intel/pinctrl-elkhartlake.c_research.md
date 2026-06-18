# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-elkhartlake.c

## Purpose

`pinctrl-elkhartlake.c` describes the Intel Elkhart Lake PCH GPIO/pinctrl topology. Unlike single-descriptor devices, it exposes six ACPI `_UID`-selected community devices, each with its own pin table, pad groups, and `intel_pinctrl_soc_data`.

## Important APIs, Types, And Functions

The file defines `EHL_COMMUNITY()` from the Elkhart Lake register offsets and uses `PINCTRL_PIN()`, `INTEL_GPP()`, and `INTEL_COMMUNITY_GPPS()` to build six SoC-data records. `ehl_soc_data_array` is a NULL-terminated table passed as ACPI match data for `INTC1020`. The platform driver uses `.probe = intel_pinctrl_probe_by_uid`, so the shared helper chooses the table entry whose `.uid` matches ACPI `_UID`.

## Control Flow

`module_platform_driver()` registers `elkhartlake-pinctrl`. On `INTC1020`, `intel_pinctrl_probe_by_uid()` calls `intel_pinctrl_get_soc_data()`, iterates `ehl_soc_data_array`, compares `_UID` against `"0"` through `"5"`, and then invokes `intel_pinctrl_probe()`. The common core performs MMIO mapping, pad-group normalization, pinctrl registration, GPIO chip registration, IRQ setup, and PM context allocation for that UID's community.

## State And Persistence

The static data separates community0 GPP_B/T/G, community1 GPP_V/H/D/U/vGPIO, community2 DSW, community3 CPU/GPP_S/GPP_A/vGPIO_3, community4 GPP_C/F/HVCMOS/GPP_E, and community5 GPP_R. Runtime state is not stored here; the common core owns register locks, GPIO chip state, interrupt masks, and suspend/resume snapshots.

## Dependencies And Integration Points

The driver depends on ACPI `_UID` correctness. It integrates with the common Intel core through `PINCTRL_INTEL`, `intel_pinctrl_probe_by_uid()`, and `intel_pinctrl_pm_ops`. The exposed hardware areas include embedded controller/eSPI, RGMII, SD/eMMC, I2C/UART/SPI/I2S, vGPIO, DSW, CPU, HVCMOS, and HDA pins.

## Risks

UID mismatches are the highest risk because a valid ACPI HID can still select no SoC data or the wrong community. GPIO base values are set to match pin bases in each UID-local controller, so consumers must not assume a global SoC-wide pin number across separate platform devices. Register offsets and GPP ranges must match hardware documentation or IRQ/status and ownership operations will be displaced.

## Test Signals

Probe should instantiate separate devices for `_UID` values 0-5. Debugfs should show only the pins for the matched UID. GPIO line counts should match each community's highest mapped GPP range. Regression tests should cover GPIO input/output, interrupt setup on non-ACPI-owned pads, and suspend/resume on DSW or wake-capable pins.
