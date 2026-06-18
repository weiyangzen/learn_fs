# sources/distributed-fs/ceph-client/drivers/mux/Makefile

Purpose: maps mux Kconfig symbols to kernel objects. It builds `mux-core.o` from `core.o` whenever `CONFIG_MULTIPLEXER` is enabled and adds one object per hardware controller driver.

Important build variables: `mux-core-objs := core.o`, `mux-adg792a-objs := adg792a.o`, `mux-adgs1408-objs := adgs1408.o`, `mux-gpio-objs := gpio.o`, and `mux-mmio-objs := mmio.o`. `obj-$(CONFIG_...)` lines tie those aggregate objects to Kconfig symbols. The module names match the Kconfig help text.

Control flow and integration: there is no runtime flow. Build integration is direct: `CONFIG_MUX_*` produces loadable modules or built-ins according to tristate selection, while `CONFIG_MULTIPLEXER` controls the framework object. A driver object relies on exported symbols from `core.c`, so module dependency generation must see `mux-core`.

State and persistence: build state is captured by `.config`, generated `.o` and `.ko` artifacts, and module dependency metadata. Risks include stale Kconfig to Makefile mismatch if a symbol or object name changes. Test signals are `make drivers/mux/`, `make M=drivers/mux`, `modinfo` for module aliases, and allmodconfig build coverage.
