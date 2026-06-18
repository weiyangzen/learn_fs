# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-moorefield.c

## Purpose

`pinctrl-moorefield.c` defines Intel Moorefield SoC pinctrl topology for the Tangier-family core. It maps 251 pins into contiguous families but does not define explicit function/group mux tables in this file.

## Important APIs, Types, And Functions

The file uses `struct tng_pinctrl`, `TNG_FAMILY()`, `PINCTRL_PIN()`, and `devm_tng_pinctrl_probe()`. `mofld_soc_data` contains the pin descriptors and 15 family ranges. ACPI HID `INTC1003` carries the SoC data to the platform driver.

## Control Flow

`subsys_initcall()` registers `pinctrl-moorefield`. On ACPI match, the platform driver invokes `devm_tng_pinctrl_probe()`, which consumes `mofld_soc_data` and registers Tangier-family pinctrl behavior. Module exit unregisters the driver.

## State And Persistence

This file contains immutable pin and family tables. Runtime state, GPIO registration, mux behavior, and any suspend/resume handling are owned by the Tangier core. Family ranges cover ULPI, eMMC, SDIO, HSI, SSP, I2C, UART, GPIO south/north, camera, clock, PMIC, keyboard, and PTI areas.

## Dependencies And Integration Points

The driver depends on `pinctrl-tangier.h`, ACPI `INTC1003`, platform probing, and namespace `PINCTRL_TANGIER`. It is separate from the modern `PINCTRL_INTEL` core and does not include `pinctrl-intel.h`.

## Risks

Because no named functions are supplied, behavior depends on what the Tangier core can infer from family data or what firmware already configured. Pin names contain repeated GP labels in PTI and GPIO North ranges, so users of names must tolerate aliases that reflect hardware documentation. Family boundary errors can expose or hide broad blocks of pins.

## Test Signals

Probe should expose 251 Moorefield pins and all 15 families. Tangier-core tests should validate GPIO access and any default mux handling across each family boundary. Hardware validation should focus on eMMC/SDIO/UART/I2C and PMIC-sensitive pins.
