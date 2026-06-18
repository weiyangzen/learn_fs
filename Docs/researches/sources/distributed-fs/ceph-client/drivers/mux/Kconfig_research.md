# sources/distributed-fs/ceph-client/drivers/mux/Kconfig

Purpose: defines the kernel configuration surface for the generic multiplexer subsystem and its controller drivers. `MULTIPLEXER` is an internal bool selected by `MUX_CORE`; `MUX_CORE` exposes the framework; the driver menu is gated by `if MULTIPLEXER`.

Important symbols: `MUX_ADG792A` depends on `I2C`; `MUX_ADGS1408` depends on `SPI`; `MUX_GPIO` depends on `GPIOLIB || COMPILE_TEST`; `MUX_MMIO` depends on `OF` and selects `REGMAP_MMIO`. The help text documents module names (`mux-adg792a`, `mux-adgs1408`, `mux-gpio`, `mux-mmio`) and the core abstraction: muxes controlled by GPIO, MMIO/regmap, or dedicated chips.

Control flow and integration: this file has no runtime flow, but it controls which objects in the sibling Makefile are built and which dependencies are forced into the build. Device-tree users typically need `MUX_CORE` plus one controller driver. `MUX_MMIO`'s `REGMAP_MMIO` select is especially important because `mmio.c` can create a regmap over mapped registers.

State and persistence: Kconfig selections persist in the kernel `.config`; there is no runtime state. Risks are dependency mismatch and hidden build coverage: `MUX_CORE` selects `MULTIPLEXER`, but selecting a leaf driver without the matching bus support is blocked by dependencies. Test signals are `scripts/kconfig` dependency checks, `make olddefconfig`, and build combinations for built-in and module leaf drivers.
