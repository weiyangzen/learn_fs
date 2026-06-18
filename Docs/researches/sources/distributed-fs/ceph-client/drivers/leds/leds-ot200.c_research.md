# sources/distributed-fs/ceph-client/drivers/leds/leds-ot200.c

Purpose: Bachmann OT200 board LED driver for three back-panel and seven front-panel LEDs.

Important APIs/types/functions: static `leds[]` lists names, I/O ports, and bit masks. `ot200_led_brightness_set()` updates shadow bytes and writes ports under a spinlock. Probe registers all LEDs and initializes front/back panel output bytes.

Control flow: platform probe registers ten LED class devices, then writes initial state with all front LEDs off and the init LED on. Brightness writes select the shadow byte by port, set/clear the LED mask, and write the whole byte to the hardware port.

State and persistence: `leds_front` and `leds_back` are required shadow registers because the hardware state cannot be read with `inb()`. Hardware state is initialized on every probe.

Dependencies and integration: depends on platform device, direct I/O port access, LED class, and a global spinlock.

Risks: uses static global descriptors and shadow state, so multiple instances are not supported. `BUG()` is used for impossible port values. No I/O region request is made here.

Test signals: probe initial port values, each LED bit on/off, shadow preservation across multiple LEDs on the same port, and platform unload/reload behavior.
