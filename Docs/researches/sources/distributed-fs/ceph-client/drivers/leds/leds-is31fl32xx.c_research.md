# sources/distributed-fs/ceph-client/drivers/leds/leds-is31fl32xx.c

Purpose: I2C LED controller driver for ISSI/Si-En IS31FL32xx families, including 16/18/28/36-channel 8-bit devices and IS31FL3293 12-bit RGB device.

Important APIs/types/functions: `struct is31fl32xx_chipdef` defines channel count, optional registers, PWM layout, brightness steps, reset and shutdown callbacks. `is31fl32xx_brightness_set()` writes one or two PWM registers and pokes the update register. `is31fl3216_reset()` and `is31fl3293_reset()` handle chips without generic reset registers. `is31fl32xx_parse_dt()` registers LEDs from child nodes and detects channel conflicts.

Control flow: probe obtains chipdef from OF match, counts available child nodes, allocates flexible private data, parses children, registers classdevs with fwnode naming, then initializes/reset registers, enables channel-control bits, exits software shutdown, and applies optional global control.

State and persistence: private data stores immutable chipdef, client, and LED channel list. Hardware PWM and enable registers hold runtime state. Remove resets registers to a known state but does not maintain software brightness cache.

Dependencies/integration: I2C SMBus byte-data writes, OF child nodes, LED class extended registration, chip-specific current/reset macros from headers.

Risks: no mutex is used by design; correctness depends on independent writes and I2C bus serialization. `is31fl3293_reset()` uses max rather than min for `max_microamp`, which merits scrutiny against hardware limits. Some chipdefs rely on default-initialized fields, so missing `brightness_steps` would break brightness registration.

Test signals: exercise 256-step and 4096-step brightness writes, reversed PWM registers on IS31FL3216, reset/shutdown callbacks, `issi,22khz-pwm`, duplicate channel rejection, and remove-time reset error logging.
