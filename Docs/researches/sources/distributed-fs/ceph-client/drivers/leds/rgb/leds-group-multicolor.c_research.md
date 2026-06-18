# sources/distributed-fs/ceph-client/drivers/leds/rgb/leds-group-multicolor.c

Purpose: creates one multicolor LED class device from several already-registered monochrome LED devices. It keeps grouped color state consistent and disables direct writes to the underlying LEDs while the group exists.

Important APIs, types, and functions: `struct leds_multicolor` stores the multicolor class device and array of monochrome classdev pointers. `leds_gmc_set()` scales group brightness and per-subled intensity to each monochrome LED's max brightness. `leds_gmc_probe()` obtains referenced LEDs with `devm_of_led_get_optional()`, builds subled metadata, registers a multicolor device, initializes output, and disables individual LED sysfs write access. `restore_sysfs_write_access()` reverses that on devm cleanup.

Control flow: probe repeatedly fetches LED phandles until none remain, records common suspend/resume flags, allocates subleds, derives color from each source LED, registers the group, applies initial brightness, then disables each source LED's sysfs access under `led_access`.

State and persistence: the grouped class device stores subled intensities; underlying LEDs remain separate class devices but their sysfs write access is disabled for consistency. State persists only in LED core devices and hardware behind the monochrome LEDs.

Dependencies and integration points: OF LED lookup, LED class internals (`led_sysfs_disable/enable`), LED multicolor class, and compatible `leds-group-multicolor`.

Risks and test signals: test zero referenced LEDs, scaling with differing max brightness values, sysfs access restoration on probe failure/remove, suspend flag propagation, and interactions with triggers already attached to child monochrome LEDs.
