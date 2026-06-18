# sources/distributed-fs/ceph-client/drivers/mfd/tqmx86.c

## Purpose
`tqmx86.c` is the MFD core for TQ-Systems x86 module PLDs discovered through DMI. It maps LPC I/O registers, identifies board and PLD revisions, configures optional GPIO and I2C interrupt routing, creates watchdog/GPIO child devices, and conditionally creates an `ocores-i2c` child plus onboard EEPROM description when a soft I2C controller is detected.

## Important APIs, Types, And Functions
Module parameters are `gpio_irq` and `i2c1_irq`, accepting IRQ 7, 9, 12, or 0. Resource arrays are `tqmx_i2c_soft_resources[]`, `tqmx_watchdog_resources[]`, and `tqmx_gpio_resources[]`. Child cells are `tqmx86_i2c_soft_dev[]` and `tqmx86_devs[]`. Helpers include `tqmx86_board_id_to_name()`, `tqmx86_board_id_to_clk_rate()`, `tqmx86_setup_irq()`, `tqmx86_probe()`, and `tqmx86_create_platform_device()`.

## Control Flow
Module init checks DMI vendor/product matches and creates a platform device from the DMI callback before registering the platform driver. Probe maps I/O base `0x180`, reads board ID, SAUC, and revision, logs a human-readable board name, reads the I2C soft-controller detect register via `inb()`, optionally programs GPIO IRQ selection and fills the GPIO IRQ resource, sets the ocores clock rate based on board ID, optionally programs I2C1 IRQ and registers the ocores child, then registers watchdog and GPIO cells.

## State, Persistence, And Dependencies
Persistent effects include PLD interrupt routing register writes and child platform devices. Static resource arrays are mutated at probe to add IRQ resources and update clock rate. Dependencies include DMI, I/O port mapping/accessors, platform devices, MFD core, ocores I2C platform data, I2C board info for a 24c32 EEPROM, and module parameters.

## Integration Points
Child drivers are `tqmx86-wdt`, `tqmx86-gpio`, and optionally `ocores-i2c`. The ocores child receives I/O and optional IRQ resources plus platform data describing the onboard EEPROM. Resource conflicts are ignored for watchdog/GPIO cells because the PLD I/O range overlaps.

## Risks
Static mutable resources make multiple-device support unsafe. Invalid IRQ module parameters fail setup but do not abort probe for GPIO/I2C; the corresponding resource is simply not filled. `tqmx86_create_platform_device()` allocates a platform device from a DMI callback without retaining a pointer for explicit unregister. Unknown board IDs assume a 24 MHz LPC clock, which may be wrong. Direct `inb()` is used outside the mapped range by design.

## Test Signals
Test DMI match/no-match behavior, board ID name and clock-rate mapping, GPIO/I2C IRQ parameter validation and readback mismatch handling, soft I2C detect path, ocores child resources and EEPROM info, watchdog/GPIO child creation, and unknown-board fallback logging.
