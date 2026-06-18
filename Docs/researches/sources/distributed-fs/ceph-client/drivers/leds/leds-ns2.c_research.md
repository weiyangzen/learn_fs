# sources/distributed-fs/ceph-client/drivers/leds/leds-ns2.c

Purpose: LaCie Network Space v2 dual-GPIO LED mode driver with optional SATA activity mode.

Important APIs/types/functions: `struct ns2_led_modval` maps mode to command/slow GPIO levels. `struct ns2_led` stores LED class device, GPIOs, mode map, SATA flag, sleep capability, and rwlock. `ns2_led_get_mode()`, `ns2_led_set_mode()`, brightness callbacks, and `sata` sysfs handlers implement mode control.

Control flow: probe allocates one `ns2_led` per child. Registration obtains `cmd` and `slow` GPIOs, parses `modes-map` triples, picks blocking or atomic brightness callback based on `gpiod_cansleep`, reads current GPIO state to infer initial mode, then registers the LED with a `sata` attribute. Brightness selects OFF, ON, or SATA based on value and SATA flag.

State and persistence: `sata` and LED class brightness cache the inferred/requested state; actual mode is encoded in two GPIO levels. Initial state is read from hardware, unlike netxbig.

Dependencies and integration: depends on firmware-node GPIO descriptors, LED class, OF platform binding `lacie,ns2-leds`, and the local `leds.h` header for LED defaults.

Risks: `ns2_led_set_mode()` returns void and silently ignores missing modes. The sleepable GPIO path is called while holding an irqsave rwlock, which is risky if GPIO operations actually sleep. Mode map binary layout relies on packed triples and `fwnode_property_read_u32_array()` into that structure.

Test signals: all mode-map combinations, initial hardware mode detection, SATA sysfs toggling while on/off, sleepable and non-sleepable GPIO controllers, and malformed `modes-map` rejection.
