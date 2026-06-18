# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-lakefield.c

## Purpose

`pinctrl-lakefield.c` defines the Intel Lakefield PCH pinctrl/GPIO layout. It maps 267 pins into EAST, NORTHWEST, WEST, and SOUTHEAST communities and delegates all runtime behavior to the common Intel core.

## Important APIs, Types, And Functions

The central data object is `lkf_soc_data`, with `lkf_pins` and four `lkf_communities`. `LKF_COMMUNITY()` binds Lakefield's register offsets. Explicit `INTEL_GPP()` entries describe subgroups and GPIO bases. ACPI HID `INT34C4` selects the driver data for `intel_pinctrl_probe_by_hid()`.

## Control Flow

The platform driver registers through `module_platform_driver()`. Probe is HID-based and calls into `intel_pinctrl_probe()`. The common core maps one BAR per Lakefield community, creates GPIO ranges from the pad groups, registers pinctrl and GPIO, and handles shared IRQs and PM save/restore.

## State And Persistence

Static state defines the hardware topology only. Runtime state such as pad register pointers, requested GPIOs, IRQ enable masks, and saved PM contexts is owned by `pinctrl-intel.c`. Community boundaries map pins 0-59, 60-148, 149-237, and 238-266.

## Dependencies And Integration Points

The driver depends on ACPI `INT34C4`, platform-device probing, the common Intel pinctrl namespace, and PM callbacks. Pin coverage includes touch/display/eSPI/SPI, LPSS I2C/I3C/audio, UART/SSP/UFS/eMMC/PCIe/display sideband, and PMIC/type-C/southeast platform pins.

## Risks

Lakefield has large contiguous ranges split into multiple GPPs. Incorrect base assignment affects both GPIO numbering and IRQ domain hwirq mapping. No explicit mux function tables are provided, so named pinmux selection is not available from this source. Table comments are useful but not authoritative; numeric ranges control behavior.

## Test Signals

Hardware boot should show four mapped communities under `INT34C4`, expected line names, and GPIO ranges starting at 0, 64, 96, 128, 160, 192, 224, and 256. GPIO/IRQ tests across each community boundary and suspend/resume on requested LPSS or PMIC lines provide meaningful coverage.
