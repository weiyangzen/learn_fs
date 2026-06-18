# sources/distributed-fs/ceph-client/drivers/pinctrl/starfive/Makefile

## Purpose
This Makefile maps StarFive pinctrl Kconfig symbols to the object files that implement each SoC/controller variant.

## Important APIs, types, and functions
`obj-$(CONFIG_PINCTRL_STARFIVE_JH7100)` builds `pinctrl-starfive-jh7100.o`. `obj-$(CONFIG_PINCTRL_STARFIVE_JH7110)` builds the common `pinctrl-starfive-jh7110.o`. `obj-$(CONFIG_PINCTRL_STARFIVE_JH7110_SYS)` and `obj-$(CONFIG_PINCTRL_STARFIVE_JH7110_AON)` build the SYS and always-on wrappers.

## Control flow
Kbuild evaluates each `obj-*` line from Kconfig state. The common JH7110 object is separate from the two platform-driver wrappers, so SYS/AON share probe, GPIO, pinmux, pinconf, IRQ, and PM logic while supplying different `jh7110_pinctrl_soc_info` tables.

## State and persistence behavior
There is no runtime state. The file controls which translation units exist in the final kernel/module build.

## Dependencies and integration points
It integrates directly with the StarFive Kconfig fragment. The split mirrors the source design: JH7100 is self-contained, while JH7110 has common code plus SYS/AON instance files.

## Risks
If a visible JH7110 driver is enabled without selecting `PINCTRL_STARFIVE_JH7110`, unresolved symbols such as `jh7110_pinctrl_probe()` would result; Kconfig currently handles this. Duplicate symbol or module-loading issues should be watched when common code is built-in but instance drivers are modules.

## Test signals
Build tests should confirm object inclusion for each symbol combination and no unresolved exports between `pinctrl-starfive-jh7110.o` and the SYS/AON objects.
