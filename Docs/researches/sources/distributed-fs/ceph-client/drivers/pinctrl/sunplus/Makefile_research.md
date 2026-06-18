# sources/distributed-fs/ceph-client/drivers/pinctrl/sunplus/Makefile

## Purpose
This Makefile connects `CONFIG_PINCTRL_SPPCTL` to the Sunplus SP7021 pinctrl build products. It builds a composite object named `sppinctrl` from the generic driver logic and the SP7021 data table.

## Important APIs, Types, And Targets
- `obj-$(CONFIG_PINCTRL_SPPCTL) += sppinctrl.o`: includes the composite object when the Kconfig option is built-in or module.
- `sppinctrl-objs := sppctl.o sppctl_sp7021.o`: links the framework-facing implementation (`sppctl.c`) with the SoC data definitions (`sppctl_sp7021.c`).

## Control Flow
During kbuild, the tristate expansion of `CONFIG_PINCTRL_SPPCTL` determines whether `sppinctrl.o` is omitted, built into `vmlinux`, or prepared as a module object. The composite object layout means exported arrays declared in `sppctl.h` and defined in `sppctl_sp7021.c` are linked with the driver operations in `sppctl.c`.

## State And Persistence
There is no runtime state. The file persists build topology: driver logic and SoC tables must be compiled together.

## Dependencies And Integration Points
- Depends on Kconfig symbol `PINCTRL_SPPCTL`.
- Integrates `sppctl.c`, `sppctl.h`, and `sppctl_sp7021.c`.
- Module naming is aligned with the Kconfig help text's `sppinctrl`.

## Risks
- If new SoC data files are added, this Makefile must be extended or the driver will compile without the needed table definitions.
- If `sppctl.c` remains built-in-only via `builtin_platform_driver`, module builds of `sppinctrl` should be checked carefully.
- Missing object linkage would surface as unresolved externals for `sppctl_list_funcs`, `sppctl_pins_all`, and related size symbols declared in `sppctl.h`.

## Test Signals
- `make drivers/pinctrl/sunplus/` or full kernel builds should produce `sppinctrl.o` when `CONFIG_PINCTRL_SPPCTL=y/m`.
- Link tests catch missing SP7021 table definitions.
- `modinfo`/module alias checks are useful if the option is built as a module in this tree.
