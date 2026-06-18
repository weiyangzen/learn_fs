<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-syscon.c -->
# sources/distributed-fs/ceph-client/drivers/gpio/gpio-syscon.c

Purpose: exposes selected bits in shared syscon registers as GPIO lines for simple SoC control registers that do not justify a full hardware-specific GPIO driver.

Important APIs, types, and functions: `struct syscon_gpio_data` describes capabilities, bit count, data/direction offsets, and optional custom set callback. `struct syscon_gpio_priv` holds the gpiochip, regmap, match data, and per-device register offsets. Core callbacks are `syscon_gpio_get()`, `syscon_gpio_set()`, `syscon_gpio_dir_in()`, and `syscon_gpio_dir_out()`. Special writers are `rockchip_gpio_set()` for write-mask registers and `keystone_gpio_set()` for lock-bit set-only behavior.

Control flow: probe obtains match data, resolves a syscon regmap from `gpio,syscon-dev` or the parent node, optionally reads data/direction offsets from phandle arguments, installs callbacks according to feature flags, and registers the gpiochip. Reads and writes translate a logical offset into 32-bit syscon register index and bit position.

State and persistence behavior: no driver-private runtime state beyond offsets and match data. GPIO values and direction live in the shared syscon registers and survive as hardware state until overwritten by this or another syscon consumer.

Dependencies and integration points: integrates with `regmap`, `mfd/syscon`, Device Tree compatibles for Cirrus EP7209 modem-control GPIO, TI Keystone DSP GPIO, and Rockchip RK3328 mute GPIO.

Risks and test signals: shared syscon registers require correct masks and offsets; incorrect DT offsets can corrupt unrelated control bits. Direction update return values are ignored in `dir_in()` and only the final set result is returned in `dir_out()`. Test read/write bit addressing across 32-bit boundaries, parent-regmap fallback, Rockchip write-mask semantics, Keystone set-only behavior, and feature-flag combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpio/gpio-syscon.c -->
