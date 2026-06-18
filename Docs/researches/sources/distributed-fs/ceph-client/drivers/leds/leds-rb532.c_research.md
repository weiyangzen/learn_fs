# sources/distributed-fs/ceph-client/drivers/leds/leds-rb532.c

Purpose: minimal Routerboard532 user LED driver. It registers one global LED class device named `uled` backed by the RC32434 board latch bit `LO_ULED`.

Important APIs, types, and functions: `rb532_led_set()` writes to latch U5 via `set_latch_u5()`, `rb532_led_get()` reads via `get_latch_u5()`, and `rb532_uled` describes the LED class device with a `nand-disk` default trigger. Platform `probe` and `remove` register and unregister the static class device.

Control flow: the platform driver binds to `rb532-led`; probe simply calls `led_classdev_register()`. Brightness set uses inverted latch semantics: nonzero brightness clears `LO_ULED`, while off sets `LO_ULED`. Brightness get returns `LED_FULL` when the latch bit is set, which mirrors the raw latch state rather than the set path's active-low write direction.

State and persistence: there is no allocated private state; the hardware latch is the source of truth. The class device is static module state, so only one instance is expected.

Dependencies and integration points: depends on MIPS Routerboard532 architecture headers, RC32434 GPIO/latch helpers, platform device registration elsewhere, and the LED trigger subsystem.

Risks and test signals: polarity deserves board-level validation because the set and get paths expose hardware-level inversion. Tests are mostly integration tests: load/unload on supported hardware, verify the NAND trigger toggles the visible LED, and confirm no duplicate platform instances are created.
