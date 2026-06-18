# sources/distributed-fs/ceph-client/drivers/leds/leds-pca963x.c

Purpose: PCA9632/33/34/35 I2C PWM LED driver with optional shared hardware blink and power management.

Important APIs/types/functions: `struct pca963x_chipdef` describes GRPPWM/GRPFREQ/LEDOUT layout and LED count. `pca963x_brightness()` writes individual PWM and LEDOUT state. `pca963x_blink_set()` maps delays to group duty/frequency. `pca963x_power_state()` sleeps/wakes the oscillator based on active LEDs. Probe and `pca963x_register_leds()` configure MODE2 and register children.

Control flow: probe picks chip definition from I2C ID, validates child count, allocates flexible state, turns off LEDOUT registers, powers down MODE1, then registers children. Registration configures output driver polarity from properties, optionally enables blink callback, and registers each child with fallback labels. Brightness changes update PWM/LEDOUT and then MODE1 sleep state.

State and persistence: `leds_on` bitmap tracks whether the chip should be awake; each LED caches blink flag and group duty/frequency values. Hardware registers hold PWM, group blink, LEDOUT, and sleep state.

Dependencies and integration: depends on I2C SMBus, LED class, fwnode/OF properties `nxp,hw-blink`, `nxp,totem-pole`, `nxp,inverted-out`, `nxp,period-scale`, and simple PM ops.

Risks: hardware blink is global, so the last blink settings affect all blinking LEDs. `pca963x_brightness()` reads registers into `u8` without checking negative SMBus errors. `pca963x_power_state()` uses LED core brightness cache, which must remain synchronized with requested writes.

Test signals: child count/reg validation, output mode polarity properties, brightness off/full/PWM, shared blink delay mapping and bounds, suspend/resume sleep bit, and all supported chip register layouts.
