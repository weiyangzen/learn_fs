# sources/distributed-fs/ceph-client/drivers/leds/rgb/Makefile

Purpose: build map from RGB LED Kconfig symbols to object files.

Important APIs, types, and functions: not executable code; it lists `obj-$(CONFIG_...) += ...` for group multicolor, KTD202x, LP5812, NCP5623, PWM multicolor, Qualcomm LPG, and MT6370 RGB drivers.

Control flow: Kbuild includes an object when the corresponding configuration symbol is built in or modular. Module names follow object names without `.o`.

State and persistence: build-system state only. It does not create runtime state.

Dependencies and integration points: integrates the RGB driver directory with Kbuild and the Kconfig symbols defined in the sibling `Kconfig`.

Risks and test signals: build tests should confirm each listed object exists in the tree and each object has a corresponding reachable Kconfig symbol. Allmodconfig and per-symbol module builds are the relevant validation.
