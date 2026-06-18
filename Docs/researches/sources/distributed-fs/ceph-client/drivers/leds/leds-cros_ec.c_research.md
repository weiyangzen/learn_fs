# sources/distributed-fs/ceph-client/drivers/leds/leds-cros_ec.c

Purpose: ChromeOS EC LED driver that discovers EC-managed LEDs via `EC_CMD_LED_CONTROL` and exposes them as Linux multicolor LED class devices with an automatic EC hardware trigger.

Important APIs/types/functions: `struct cros_ec_led_priv` stores `led_classdev_mc`, EC device pointer, and EC LED id. Mapping tables translate EC LED ids to LED functions and EC colors to Linux color ids. `cros_ec_led_send_cmd()` wraps `cros_ec_cmd()`. `cros_ec_led_brightness_set_blocking()` computes multicolor components and sends EC brightness values. `cros_ec_led_probe_one()` queries one EC LED and registers it if supported.

Control flow: platform probe obtains the parent `cros_ec_device`, registers trigger `chromeos-auto`, iterates all `EC_LED_ID_COUNT` ids, queries each with `EC_LED_FLAGS_QUERY`, skips unsupported ids, validates uniform brightness ranges for multicolor API compatibility, allocates subleds, names devices as `chromeos:<color>:<function>`, and registers multicolor classdevs.

State and persistence: color intensities and brightness are maintained by the LED core and EC firmware. The driver keeps only per-device id and EC pointer. The hardware trigger activation sends `EC_LED_FLAGS_AUTO`, returning control to firmware policy.

Dependencies/integration: integrates with ChromeOS EC protocol, LED multicolor framework, LED trigger framework, platform MFD device `"cros-ec-led"`, and EC command definitions.

Risks: inconsistent EC brightness ranges cause `-EINVAL` because Linux multicolor expects one max brightness. `-EOPNOTSUPP` aborts all probing, while `-EINVAL` for a single id is treated as unknown and skipped. Mapping arrays rely on compile-time `static_assert()` against EC enum sizes.

Test signals: use EC emulation or hardware to exercise query, unsupported ids, auto trigger activation, single-color vs multicolor naming, and component-to-EC color mapping for all supported colors.
