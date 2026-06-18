# sources/distributed-fs/ceph-client/drivers/leds/leds-lp3944.c

Purpose: I2C driver for LP3944 funlight chip, exposing selected outputs as LED class devices with on/off and shared hardware blink support.

Important APIs/types/functions: `struct lp3944_data` holds mutex and eight LED slots. `lp3944_dim_set_period()` and `lp3944_dim_set_dutycycle()` program DIM prescaler/PWM. `lp3944_led_set()` read-modify-writes selector registers `LS0/LS1` with optional inversion. `lp3944_led_set_blink()` maps delay_on/off to DIM0 period/duty. `lp3944_configure()` consumes platform LED descriptors.

Control flow: probe requires platform data and SMBus byte-data support, allocates private data, initializes mutex, and registers configured LED or inverted LED outputs. Default status is written to hardware after registration. Remove unregisters all configured LEDs.

State and persistence: software stores id/type/client per LED. Hardware selector and DIM registers store output/blink state. DIM0 is shared by all blinking LEDs, so a new blink request changes the pattern for every LED using DIM0.

Dependencies/integration: platform data `leds-lp3944.h`, I2C SMBus byte data, LED blink API, mutex for selector RMW.

Risks: blink always uses DIM0, limiting independent blink patterns. `lp3944_led_set()` does not check read error before using `val`. Strings in platform data must remain valid. Manual unregister unwind is complex.

Test signals: normal and inverted LEDs, LS0/LS1 bit placement, blink period/duty conversion and max validation, shared DIM0 behavior, platform-data error paths, and removal cleanup.
