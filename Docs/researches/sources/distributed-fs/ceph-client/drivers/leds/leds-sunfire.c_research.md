# sources/distributed-fs/ceph-client/drivers/leds/leds-sunfire.c

Purpose: Sun Fire clockboard and FHC board LED driver for Ultra Enterprise systems. It registers three LEDs per board and manipulates UPA/FHC control register bits.

Important APIs, types, and functions: `struct sunfire_led` stores a class device and MMIO register pointer. `struct led_type` maps LED name, set handler, and optional trigger. `__clockboard_set()` and `__fhc_set()` implement per-bit polarity rules. `sunfire_led_generic_probe()` handles allocation and registration for both board types. Two platform drivers bind to `sunfire-clockboard-leds` and `sunfire-fhc-leds`.

Control flow: module init registers both platform drivers. Each probe requires exactly one resource, allocates a three-LED container, assigns the resource start as the register address for each LED, and registers the three class devices. Brightness callbacks read-modify-write the shared register, with left LEDs active-low and other positions active-high.

State and persistence: LED state is the hardware register. The driver does not lock register updates, so concurrent LED writes could race on shared read-modify-write operations.

Dependencies and integration points: SPARC UPA accessors, FHC/clockboard register bit definitions, platform resources provided by architecture code, and the LED trigger subsystem. Right LEDs use `heartbeat` default triggers.

Risks and test signals: test resource-count validation, polarity for left/middle/right bits, multi-driver registration/unregistration, and concurrent updates to LEDs on the same register. Architecture-level integration is required because the register pointer is not ioremap-managed in this file.
