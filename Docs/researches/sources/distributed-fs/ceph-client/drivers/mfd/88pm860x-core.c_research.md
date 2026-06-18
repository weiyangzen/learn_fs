# sources/distributed-fs/ceph-client/drivers/mfd/88pm860x-core.c

Purpose: MFD core for Marvell 88PM8606/88PM8607 PMICs. It manages paired companion I2C chips, interrupt demultiplexing, oscillator reference voting, child-device registration for regulators, RTC, onkey, touch, power, codec, LEDs, and backlights, plus suspend wake handling.

Important APIs, types, and functions: `pm860x_probe()` allocates `pm860x_chip`, parses platform/DT data, creates primary and optional companion regmaps, and calls `pm860x_device_init()`. `device_8607_init()` verifies chip ID, configures BUCK/MISC registers, initializes IRQs, and registers PMIC children. `device_8606_init()` initializes oscillator, backlight, and LED children. Exported `pm8606_osc_enable()`/`pm8606_osc_disable()` implement vote-based oscillator control. Custom IRQ code includes `pm860x_irq()`, `pm860x_irq_sync_unlock()`, `pm860x_irq_domain_map()`, and `device_irq_init()`.

Control flow: probe requires platform data or DT-derived companion address/IRQ mode. It identifies 8606/8607 by I2C address, optionally creates a dummy companion client and regmap, initializes the primary role, then initializes the companion role if present. IRQ setup masks and clears status registers, allocates legacy IRQ descriptors/domain, and requests the threaded parent IRQ. Remove frees child devices/IRQ and unregisters the companion.

State and persistence: `pm860x_chip` stores primary/companion clients, regmaps, IRQ base/core IRQ, oscillator mutex/vote/status, BUCK3 mode, wake flag, and platform-derived mode. `pm860x_irqs[]` is a static table with mutable `enable` fields, so interrupt enable state is shared globally across device instances. Hardware mask/status and oscillator bits persist in the PMIC.

Dependencies and integration: depends on I2C, regmap, irqdomain, MFD core, charger-manager platform data, regulators, and exported low-level helpers from `88pm860x-i2c.c`. Child device names follow the `88pm860x-*` convention.

Risks: `pm860x_device_init()` returns 0 even if sub-initializers logged failures, so probe can succeed after partial child setup; static IRQ enable/cached mask state is not per-chip; `irq_domain_create_legacy()` return is not stored for removal; child registration failures are mostly logged and ignored; companion handling mixes devm and non-devm regmap lifetime.

Test signals: build with `CONFIG_MFD_88PM860X`, probe 8606, 8607, and paired companion setups; verify child devices, IRQ mask/unmask and nested IRQ dispatch, oscillator vote reference counting, suspend/resume wake IRQ, DT companion parsing, remove cleanup, and error-injection paths for companion/regmap/IRQ failures.
