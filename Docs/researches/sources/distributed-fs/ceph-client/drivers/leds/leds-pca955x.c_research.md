# sources/distributed-fs/ceph-client/drivers/leds/leds-pca955x.c

Purpose: PCA9550/51/52/53 and IBM PCA9552 I2C LED driver with LED, blink, and optional GPIO roles.

Important APIs/types/functions: chip definitions provide bit count, address mask, and blink divider. `struct pca955x` tracks mutex, chip definition, active blink bitmap, active pins, and blink period. `pca955x_led_set()`, `pca955x_led_get()`, `pca955x_led_blink()`, GPIO callbacks, `pca955x_get_pdata()`, and `pca955x_probe()` implement behavior.

Control flow: probe validates chip match and I2C address, parses child nodes, reads current LED selector registers, applies default-state changes, registers LED class devices, preserves existing BLINK0 LEDs when requested, initializes blink prescaler/PWM1, and optionally registers a GPIO chip. Brightness uses selector states: on, off, shared PWM1 for variable brightness, and BLINK0 for blink.

State and persistence: `active_blink`, `active_pins`, and `blink_period` cache software ownership and shared blink state. Hardware LED selector, PSC, PWM, and input registers hold device state; probe may preserve existing blink selector state.

Dependencies and integration: depends on I2C SMBus byte and block reads, LED class, fwnode/OF child properties, optional GPIO chip support, and DT binding constants.

Risks: hardware supports only one BLINK0 period for all blinking LEDs, so incompatible blink requests return `-EBUSY`. Variable brightness through PWM1 is shared by all non-full/non-off LEDs. Active pin tracking prevents GPIO from taking LED-owned pins, but type configuration must be correct. Address validation can reject nonstandard wiring.

Test signals: address-mask validation for each chip, default-state off/on/keep, preserving bootloader blink, shared blink conflict handling, PWM brightness sharing, GPIO ownership, and suspend/resume via LED core flags.
