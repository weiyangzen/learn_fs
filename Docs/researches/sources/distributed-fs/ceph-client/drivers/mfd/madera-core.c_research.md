# sources/distributed-fs/ceph-client/drivers/mfd/madera-core.c

Purpose: this is the shared MFD core for Cirrus Logic Madera codec families. It handles power rails, reset sequencing, boot polling, chip identification, errata, runtime PM, 32 kHz clock setup, hardware patches, and child device registration.

Important APIs, types, and functions: child arrays define per-codec cells such as `madera-pinctrl`, `madera-irq`, `madera-micsupp`, `madera-gpio`, `madera-extcon`, and codec-specific ASoC children. `madera_name_from_type()` names enum variants. `madera_wait_for_boot_noack()` and `madera_wait_for_boot()` poll/ack boot status. `madera_soft_reset()`, `madera_enable_hard_reset()`, and `madera_disable_hard_reset()` implement reset policy. `madera_runtime_suspend()`/`madera_runtime_resume()` manage DCVDD, hard reset, regcache state, and cache sync. `madera_dev_init()` is the main initializer exported to bus drivers. `madera_dev_exit()` removes children and powers the device down.

Control flow: `madera_dev_init()` initializes shared state, copies platform data, gets optional clocks and reset GPIO, places regmaps in cache-only mode, adds LDO1 early for codecs that may supply DCVDD internally, requests regulators, enables supplies, releases reset, waits for boot, reads silicon ID, selects a patch function and child set, optionally soft-resets, reads revision, applies patch, enables MCLK2-derived 32 kHz clock, enables runtime PM, and registers children. Errors unwind regulators, reset, clock, and children in reverse order.

State and persistence: `struct madera` stores device type/name/revision, regmaps, regulators, clocks, reset GPIO, notifier, runtime-PM state, micbias counts, and reset errata. Register caches preserve state across runtime suspend and are synced on resume. Hardware reset/power state is actively changed.

Dependencies and integration points: I2C/SPI bus frontends, regmap configs and patch functions from codec-specific files, regulators, clocks, GPIO descriptors, MFD core, runtime PM, OF match table, and downstream audio/extcon/gpio/irq drivers.

Risks: power/reset sequencing is intricate and hardware-specific, especially CS47L15 reset errata and optional reset GPIO behavior. Child shutdown order intentionally avoids devm for some resources. Tests should cover each supported type, ID/type mismatch, missing MCLK2 warning, reset GPIO absent/present, LDO1 ordering, patch failure, runtime suspend/resume cache sync, and unwind paths.
