# sources/distributed-fs/ceph-client/drivers/leds/flash/leds-sgm3140.c

## Purpose
This platform driver supports SGMicro SGM3140-compatible charge-pump flash LED circuits, including compatibles for OCP8110 and RT5033 LED. It uses GPIOs and a regulator to switch torch or flash mode and a timer to enforce flash timeout.

## Important APIs, Types, and Functions
`struct sgm3140` stores flash class device, V4L2 handle, timer, flash and enable GPIOs, VIN regulator, enabled state, timeout, and max timeout. LED operations are `sgm3140_brightness_set()`, `sgm3140_strobe_set()`, `sgm3140_strobe_get()`, and `sgm3140_timeout_set()`. Timer callback `sgm3140_powerdown_timer()` turns GPIOs off, disables the regulator, and clears `enabled`.

## Control Flow
Probe obtains `flash` and `enable` GPIOs, gets the `vin` regulator, reads the first child LED node and optional `flash-max-timeout-us`, initializes current timeout and LED flash settings, registers the LED flash class device, and creates a V4L2 flash subdevice. Torch brightness enables the regulator, drives flash GPIO low and enable GPIO high. Flash strobe enables the regulator, drives both flash and enable GPIOs high, and arms the timer. Turning either mode off deletes the timer, clears GPIOs, disables the regulator, and updates `enabled`.

## State and Persistence
The only software state is volatile: `enabled`, current timeout, max timeout, timer state, and V4L2 handle. There is no mutex around `enabled`, timer callback, brightness, and strobe paths, so concurrent LED class operations rely on higher-level serialization and should be considered carefully.

## Dependencies and Integration Points
The driver depends on GPIO consumer APIs, regulator framework, LED flash class, firmware child nodes, and optional V4L2 flash. It binds `ocs,ocp8110`, `richtek,rt5033-led`, and `sgmicro,sgm3140`.

## Risks and Edge Cases
Regulator enable/disable calls can become unbalanced if concurrent brightness and strobe operations race. `sgm3140_init_flash_timeout()` sets the class default value to 250 ms even if `max_timeout` is lower; the separate `priv->timeout` cache is clamped, but the class setting may advertise an out-of-range default. The child fwnode is not put on the successful probe path. Timer callback uses non-cansleep GPIO setters and regulator disable in timer context, which is risky if the regulator operation can sleep.

## Test Signals
Test torch on/off, flash strobe auto-timeout, manual strobe off, regulator balance under repeated operations, V4L2 subdevice creation, missing timeout property defaulting, and remove with active timer. Lockdep or sleep-in-atomic diagnostics are important for the timer callback path.
