# sources/distributed-fs/ceph-client/drivers/pinctrl/meson/Makefile

## Purpose
This Makefile maps Meson/Amlogic Kconfig symbols to pinctrl driver objects. It is the build integration layer for the folder.

## Important Rules
`obj-$(CONFIG_PINCTRL_MESON)` builds the common `pinctrl-meson.o`. Hidden mux backends build `pinctrl-meson8-pmx.o` and `pinctrl-meson-axg-pmx.o`. SoC object rules build Meson8, Meson8b, GXBB, GXL, AXG, G12A, A1, S4, A4, C3, and T7 drivers under their matching Kconfig symbols. `CONFIG_PINCTRL_AMLOGIC_A4` maps directly to `pinctrl-amlogic-a4.o`.

## Control Flow And Integration
There is no runtime flow. Build flow is Kconfig-driven: selected symbols expand to object list entries compiled into built-in code or modules depending on the symbol type. Since A4 is a bool symbol, its object is built-in when enabled.

## State And Persistence
Build state is held in kernel configuration and generated build artifacts. The Makefile itself has no runtime persistence.

## Dependencies
The rules depend on symbol names in `Kconfig` matching source filenames. Common objects must be present when SoC drivers reference shared symbols such as Meson pinctrl probe or PMX ops.

## Risks
The main risk is symbol/object drift: a renamed source file or Kconfig symbol would silently drop driver coverage or cause link failures. Because A4 does not use the older Meson common object in the same way as other drivers, dependency assumptions should be checked when refactoring.

## Test Signals
Use `make drivers/pinctrl/meson/` or broader kernel builds with each relevant config enabled. Check that `CONFIG_PINCTRL_AMLOGIC_A4=y` includes `pinctrl-amlogic-a4.o`, while AXG-family configs also include `pinctrl-meson-axg-pmx.o`.
