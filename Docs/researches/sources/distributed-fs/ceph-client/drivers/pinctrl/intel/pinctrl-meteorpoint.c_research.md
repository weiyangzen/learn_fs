# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorpoint.c

## Purpose

`pinctrl-meteorpoint.c` provides the Intel Meteor Point-S PCH pin map for the common Intel pinctrl/GPIO driver. It covers 339 pins across GPP_D/R/J, vGPIO, eSPI/DIR_ESPI, GPP_B/C/H/S/E/K/F/I, SPI0, JTAG_CPU, and other platform groups.

## Important APIs, Types, And Functions

The key data is `mtps_soc_data`, built from `mtps_pins` and five explicit community descriptors. `MTP_COMMUNITY()` binds Meteor Point register offsets: PAD_OWN 0x0b0, PADCFGLOCK 0x110, HOSTSW_OWN 0x150, GPI_IS 0x200, and GPI_IE 0x220. ACPI HID `INTC1084` selects the data and probe uses `intel_pinctrl_probe_by_hid()`.

## Control Flow

The platform driver registers via `module_platform_driver()`. Probe is fully delegated to the common Intel core, which maps BARs, copies communities, normalizes pad groups, registers pinctrl/GPIO, requests the shared IRQ, and installs PM callbacks.

## State And Persistence

All state in this file is immutable table data. Runtime state belongs to the common driver. GPIO bases are sparse and range from 0 through 576, with each `INTEL_GPP()` describing the mapping from pin ranges to GPIO offsets.

## Dependencies And Integration Points

The file depends on ACPI `INTC1084`, platform probing, PM, and the `PINCTRL_INTEL` namespace. Hardware integration includes audio, CNV/vGPIO, THC interrupts, eSPI, SPI flash/TPM, USB overcurrent, SATA/PCIe, fuse/sort pins, JTAG, and management/reset pins.

## Risks

Meteor Point's high pin count and sparse GPIO bases make manual table maintenance risky. A wrong GPP range can misroute interrupts or break GPIO descriptor lookup. As with several newer Intel maps, no named function/group mux table is provided, so mux control is limited to generic GPIO and firmware-established pad modes unless future tables are added.

## Test Signals

Probe on `INTC1084` should expose 339 pins and GPIO ranges up to base 576. Tests should cover GPIO and IRQ operations in early, middle, and high-base groups, especially vGPIO and JTAG/GPP_I ranges. Suspend/resume should preserve requested and IRQ lines via the common PM callbacks.
