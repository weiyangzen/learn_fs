# sources/distributed-fs/ceph-client/drivers/pinctrl/sunxi/Makefile

## Purpose

This Makefile maps the sunxi pinctrl Kconfig symbols to the common core objects and the per-SoC controller object files. It is the build integration point that turns enabled `CONFIG_PINCTRL_*` symbols into compiled drivers.

## Important APIs, Types, And Functions

The always-built core entries are `pinctrl-sunxi.o` and `pinctrl-sunxi-dt.o`. Per-SoC `obj-$(CONFIG_...)` rules build files such as `pinctrl-sun4i-a10.o`, `pinctrl-sun20i-d1.o`, `pinctrl-sun50i-a100.o`, `pinctrl-sun50i-h616.o`, and `pinctrl-sun55i-a523-r.o`.

## Control Flow

There is no runtime flow. Kbuild evaluates each `obj-y` and `obj-$(CONFIG_...)` assignment. Because `PINCTRL_SUNXI` is selected by every SoC symbol, the directory always includes the common core when any sunxi pinctrl support is enabled. The matching SoC object is then linked into the kernel or module set according to its config value.

## State And Persistence

Build state is limited to generated Kbuild outputs and object files. This file does not own runtime state or hardware configuration.

## Dependencies And Integration Points

This file depends on the Kconfig symbols defined in the adjacent `Kconfig` file and on source files with matching basenames. It integrates SoC tables with the shared sunxi core and with the top-level kernel build system.

## Risks

The primary risk is drift between Kconfig symbols and object names. A new symbol without an `obj-*` line silently produces no driver, while an object rule referencing a missing file breaks builds. The common `obj-y` core assumes this directory is only entered when sunxi pinctrl is selected; build-system changes should preserve that relationship.

## Test Signals

Validation should include allmodconfig/allnoconfig-style compile coverage, targeted builds for each `CONFIG_PINCTRL_*` symbol, and a check that every Kconfig SoC symbol has exactly one intended object rule.
