# sources/distributed-fs/ceph-client/include/linux/soc/cirrus/ep93xx.h

Purpose: This Cirrus Logic EP93xx header shares SoC helper declarations and platform constants for legacy EP93xx ARM systems.

Important APIs/types/functions: It defines `enum ep93xx_soc_model` for 9301/9307/9312 variants, chip revision constants D0 through E2, `struct ep93xx_regmap_adev`, and `to_ep93xx_regmap_adev`. The auxiliary-device wrapper carries a `regmap`, raw base pointer, shared spinlock, and provider-specific `write`/`update_bits` hooks.

Control flow: EP93xx platform code can expose syscon/regmap-backed auxiliary devices; consumers recover the containing `ep93xx_regmap_adev`, then perform locked register writes or masked updates through the provided callbacks.

State and persistence: The auxiliary device stores pointers to the mapped register block and synchronization primitive. Actual state is in EP93xx system registers and persists until reset or later writes.

Dependencies and integration: Includes auxiliary bus, compiler attributes, and container macros. Integrates with EP93xx syscon/regmap providers, clock, reset, pinctrl, and peripheral drivers needing shared register access.

Risks and test signals: Callback locking must be consistent with all users of the same regmap. Test auxiliary-device probe/remove, concurrent `update_bits` users, revision-specific behavior, and boot on each declared SoC model.
