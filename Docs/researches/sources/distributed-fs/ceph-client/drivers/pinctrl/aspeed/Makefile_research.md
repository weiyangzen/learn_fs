# sources/distributed-fs/ceph-client/drivers/pinctrl/aspeed/Makefile

Purpose: Lists the Aspeed pinctrl objects built for the selected Kconfig symbols and applies a local compiler warning flag useful for table-heavy pinmux initialization.

Important APIs and types: `ccflags-y += -Woverride-init` enables diagnostics for overridden initializers in this directory. `obj-$(CONFIG_PINCTRL_ASPEED)` builds the common `pinctrl-aspeed.o` and `pinmux-aspeed.o` objects. `obj-$(CONFIG_PINCTRL_ASPEED_G4)`, `obj-$(CONFIG_PINCTRL_ASPEED_G5)`, and `obj-$(CONFIG_PINCTRL_ASPEED_G6)` add the generation-specific object files.

Control flow: Kbuild expands the `obj-*` assignments according to `.config`. When a generation symbol selects `PINCTRL_ASPEED`, both common objects and the matching generation object are compiled and linked into the kernel build. There is no runtime control flow.

State and persistence: No runtime state. The file affects build artifacts and warning behavior for this directory. Generated object inclusion persists only in the build output selected by the active kernel configuration.

Dependencies and integration points: Tightly coupled to `drivers/pinctrl/aspeed/Kconfig` symbols and to source files named by the object rules. The common objects provide shared infrastructure used by G4/G5/G6 files, while generation objects carry SoC-specific pin tables.

Risks: Object-rule drift can produce link failures if Kconfig symbols are renamed or source files move. If a new generation config selects `PINCTRL_ASPEED` but the Makefile omits its object, the option will build only the common code and no matching device support. `-Woverride-init` may expose intentional duplicate initializer patterns as warnings, but that is useful for detecting table mistakes in pinmux data.

Test signals: Build each `CONFIG_PINCTRL_ASPEED_G4/G5/G6` combination, verify the expected object files appear in the build log, run `make W=1` or equivalent warning builds, and check that common objects are included whenever any generation-specific symbol is enabled.
