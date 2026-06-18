# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-meteorlake.c

## Purpose

`pinctrl-meteorlake.c` describes Intel Meteor Lake PCH GPIO/pinctrl variants for the shared Intel core. It supports Meteor Lake-P and Meteor Lake-S with distinct pin tables, register offsets, communities, and ACPI IDs.

## Important APIs, Types, And Functions

The file defines `MTL_P_*` and `MTL_S_*` register offsets, community macros `MTL_P_COMMUNITY()` and `MTL_S_COMMUNITY()`, `mtlp_soc_data`, and `mtls_soc_data`. ACPI IDs `INTC105E` and `INTC1083` select Meteor Lake-P data; `INTC1082` selects Meteor Lake-S data. The platform driver delegates to `intel_pinctrl_probe_by_hid()`.

## Control Flow

`module_platform_driver()` registers `meteorlake-pinctrl`. On matching ACPI HID, the common Intel probe maps each community BAR, discovers capabilities, normalizes explicit pad groups, registers pinctrl and GPIO, and installs shared IRQ and PM callbacks. There are no file-local runtime callbacks beyond module registration.

## State And Persistence

Meteor Lake-P statically defines 289 pins across five communities; Meteor Lake-S defines 148 pins across three communities. Runtime state is held by `pinctrl-intel.c`. Sparse GPIO bases extend up to 448 on P and 224 on S, so GPIO offsets are hardware-facing and not simply pin numbers.

## Dependencies And Integration Points

The driver depends on ACPI HID selection, `PINCTRL_INTEL`, and common PM ops. Hardware integration spans CPU/platform pins, vGPIO, eSPI, SPI0, JTAG, HDA, CNV, I3C, THC, UFS, display, and management pins. The P and S variants use different HOSTSW_OWN/PADCFGLOCK offsets, making variant selection critical.

## Risks

This is a large declarative map with sparse GPIO bases; table edits can break firmware GPIO resources or interrupt routing. Variant register offsets differ, so assigning the wrong ACPI ID to the wrong data object would be severe. No mux groups/functions are declared, so consumers cannot request named alternate functions through this driver unless another mechanism configures them.

## Test Signals

Probe should select P or S by ACPI ID and expose the expected pin count. GPIO range tests should cover the high sparse bases and community boundaries. Debugfs should show correct pin names and lock/ownership state. IRQ tests should validate the `GPI_IS`/`GPI_IE` offsets for both P and S variants.
