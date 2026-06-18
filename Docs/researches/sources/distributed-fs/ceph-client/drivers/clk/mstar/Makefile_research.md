# sources/distributed-fs/ceph-client/drivers/clk/mstar/Makefile

Purpose: maps MStar clock Kconfig symbols to object files.

Important APIs/types: `obj-$(CONFIG_MSTAR_MSC313_CPUPLL)` builds `clk-msc313-cpupll.o`; `obj-$(CONFIG_MSTAR_MSC313_MPLL)` builds `clk-msc313-mpll.o`.

Control flow: Kbuild includes objects conditionally according to boolean Kconfig symbols.

State and persistence: build-system metadata only.

Dependencies and integration: paired with `drivers/clk/mstar/Kconfig` and included from the parent clock-driver build.

Risks: adding new MStar clock files requires both Kconfig and Makefile updates. Since drivers use builtin platform registration, object inclusion directly controls runtime availability.

Test signals: kernel build with each config enabled and disabled, and checking `drivers/clk/mstar/` object list.
