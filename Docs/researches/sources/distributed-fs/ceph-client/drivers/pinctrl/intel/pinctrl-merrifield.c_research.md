# sources/distributed-fs/ceph-client/drivers/pinctrl/intel/pinctrl-merrifield.c

## Purpose

`pinctrl-merrifield.c` defines Intel Merrifield SoC pinctrl data for the Tangier-family pinctrl core, not the modern `pinctrl-intel.c` core. It maps 233 pins into functional families and exposes mux functions for SDIO, I2S, SPI, UART, and PWM.

## Important APIs, Types, And Functions

The file uses `struct tng_pinctrl`, `struct tng_family`, `TNG_FAMILY()`, `TNG_FAMILY_PROTECTED()`, `PIN_GROUP()`, and `FUNCTION()`. `mrfld_soc_data` is the main descriptor. The driver matches ACPI HID `INTC1002` and probes through `devm_tng_pinctrl_probe()`.

## Control Flow

`subsys_initcall()` registers `pinctrl-merrifield`. ACPI matching passes `&mrfld_soc_data` to the Tangier probe. The Tangier core, defined outside this work item, consumes pins, families, groups, and functions to register pinctrl/GPIO behavior. Module exit unregisters the platform driver.

## State And Persistence

This source is static topology. Families describe contiguous pin ranges; family 7 and family 12 are protected, which likely instructs the Tangier core to restrict access or preserve firmware-controlled regions. Runtime state and persistence are handled by the Tangier core.

## Dependencies And Integration Points

The driver depends on `pinctrl-tangier.h` and imports namespace `PINCTRL_TANGIER`. It also includes `pinctrl-intel.h` for shared Intel pin group/function macros. Integration points include ACPI `INTC1002`, platform driver registration, and Tangier pinctrl consumers.

## Risks

Protected family boundaries are important: moving pins between normal and protected families can expose firmware/PMIC-sensitive pins to kernel consumers. Group/function mode values are all mode 1, so any hardware function needing different per-pin mode values would not be represented. Pin names include legacy GP numbers and functional aliases; consumers may depend on exact names.

## Test Signals

Probe on Merrifield hardware should register Tangier pinctrl data, expose 233 pins, and list SDIO/I2S/SPI/UART/PWM functions. Tests should verify protected families cannot be misused according to Tangier policy and that muxing each declared function selects the expected hardware mode.
