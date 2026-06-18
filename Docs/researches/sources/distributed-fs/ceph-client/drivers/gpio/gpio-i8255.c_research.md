<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.c

## Purpose
`gpio-i8255.c` is a reusable gpio-regmap library for Intel 8255 Programmable Peripheral Interface chips. It registers one or more 24-line PPIs as one gpiochip and translates gpiolib offsets into port and control-register masks.

## Important APIs, types, and functions
The exported API is `devm_i8255_regmap_register()`. Helpers include `i8255_ppi_init()` to set mode 0 and initialize outputs, `i8255_direction_mask()` to map lines to control bits, and `i8255_reg_mask_xlate()` for gpio-regmap register/mask translation.

## Control flow
Callers provide an `i8255_regmap_config` with parent device, regmap, PPI count, optional names, and optional IRQ domain. Registration validates required fields, initializes each PPI at `i * 4`, fills a `gpio_regmap_config`, and calls `devm_gpio_regmap_register()`.

## State and persistence behavior
State is primarily in the regmap cache and hardware control ports. Initialization configures all ports as mode 0 outputs and sets data ports to zero. Direction is represented by cached control-register bits, which is why the header requires the control registers not be marked volatile.

## Dependencies and integration points
This file exports symbol namespace `I8255` and depends on `gpio-regmap` and a caller-supplied regmap implementation. It can attach an IRQ domain supplied by a wrapper driver.

## Risks and edge cases
The 8255 Port C direction is nibble-granular, so requesting a single Port C line direction effectively affects four lines. Marking control registers volatile breaks direction tracking. Initialization forces outputs low, which can be unsafe for boards that need bootloader-preserved states.

## Test signals
Wrapper-driver tests should verify PPI count validation, all three ports per PPI, Port C upper/lower nibble direction behavior, regmap cache direction reads, optional IRQ-domain mapping, and reset-time output-low effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-i8255.c -->
