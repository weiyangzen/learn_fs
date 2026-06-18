<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7360.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7360.c

## Purpose
`gpio-max7360.c` exposes two GPIO-style functions of the Maxim MAX7360 MFD: normal port GPIOs and keypad-column pins reused as general-purpose outputs.

## Important APIs, types, and functions
Match data selects `MAX7360_GPIO_PORT` or `MAX7360_GPIO_COL`. Helpers include `max7360_get_available_gpos()`, `max7360_gpo_init_valid_mask()`, `max7360_set_gpos_count()`, `max7360_gpio_reg_mask_xlate()`, regmap IRQ descriptors, and `max7360_handle_mask_sync()`. Probe builds a `gpio_regmap_config`.

## Control flow
Probe gets the parent regmap and match data. For port GPIOs it optionally creates a custom regmap IRQ chip when `interrupt-controller` is present, enables interrupt edge configuration on all port pins, and applies optional constant-current output configuration. For column GPOs it calculates how many columns are not used by the keypad, updates the debounce register's GPO/keypad split, and installs a valid mask. It then registers through gpio-regmap.

## State and persistence behavior
State is in the parent MAX7360 regmap. Port outputs use PWM duty-cycle registers with 0 or 255 values, requiring custom mask translation. Column GPO availability is derived from the parent keypad column count and stays fixed after probe.

## Dependencies and integration points
It is an MFD child binding to `maxim,max7360-gpio` or `maxim,max7360-gpo`, depends on parent properties such as `keypad,num-columns`, named IRQ `inti`, gpio-regmap, and regmap-irq.

## Risks and edge cases
Column GPO valid-mask math must match keypad column allocation, or keypad pins could be exposed as GPIO outputs. Interrupt-controller setup requires parent IRQ lookup and writes edge bits for all lines. PWM registers as GPIO outputs need the custom full-byte mask translator.

## Test signals
Test both compatibles, keypad column counts and valid masks, output via PWM registers, constant-current property writes, optional interrupt-controller setup, mask sync to `PWMCFG`, and missing parent regmap/IRQ/property failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-max7360.c -->
