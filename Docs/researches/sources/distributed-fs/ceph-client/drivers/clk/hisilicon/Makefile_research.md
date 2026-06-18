# sources/distributed-fs/ceph-client/drivers/clk/hisilicon/Makefile

Purpose: selects common and SoC-specific HiSilicon clock/reset objects for kbuild.

Important APIs/types/functions: always builds shared helpers `clk.o`, `clkgate-separated.o`, `clkdivider-hi6220.o`, and `clk-hisi-phase.o`. Conditional objects include `clk-hi3620.o`, `clk-hip04.o`, `clk-hix5hd2.o`, CRG drivers, Hi3660/Hi3670, Hi6220, reset support, and stub clock drivers.

Control flow: build inclusion follows architecture and Kconfig symbols.

State and persistence: no runtime state.

Dependencies and integration points: SoC files in this work item rely on shared Hisilicon helpers and reset code selected here.

Risks: unconditional helper objects increase compile surface for all Hisilicon clock builds. Architecture-specific `obj-$(CONFIG_ARCH_HI3xxx)` gates Hi3620 separately from the `COMMON_CLK_*` options.

Test signals: compile Hi3xxx, Hi3519, Hi3559A, Hi3660, and stub-clock configurations; verify module/built-in combinations do not leave unresolved common helper symbols.
