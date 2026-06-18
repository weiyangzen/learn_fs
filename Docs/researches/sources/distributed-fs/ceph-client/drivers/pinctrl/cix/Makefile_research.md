# sources/distributed-fs/ceph-client/drivers/pinctrl/cix/Makefile

Purpose: Kbuild rules for Cix Sky1 pinctrl drivers.

Important APIs/types/functions: builds `pinctrl-sky1-base.o` for `CONFIG_PINCTRL_SKY1_BASE` and `pinctrl-sky1.o` for `CONFIG_PINCTRL_SKY1`.

Control flow: the SoC-specific driver depends on the base helper object exported from `pinctrl-sky1-base.c`.

State and persistence: compile-time only.

Dependencies/integration: paired with Cix Kconfig and the shared header `pinctrl-sky1.h`.

Risks: if a future SoC uses the base without selecting the base symbol, exported probe linkage fails. Object order is simple but both pieces must agree on structure definitions.

Test signals: build with `PINCTRL_SKY1=m/y`, inspect linked objects, and run modpost for exported symbol resolution.
