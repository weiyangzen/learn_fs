# sources/distributed-fs/ceph-client/drivers/clk/sifive/Makefile

Purpose: kbuild rule for the SiFive PRCI clock driver.

Important APIs/types/functions: `obj-$(CONFIG_CLK_SIFIVE_PRCI) += sifive-prci.o`.

Control flow: when the Kconfig symbol is enabled, kbuild compiles the PRCI implementation, which includes FU540/FU740 descriptor headers.

State and persistence behavior: no runtime state.

Dependencies/integration points: relies on Kconfig to select reset/WRPLL dependencies.

Risks: adding additional SiFive clock objects requires updating this Makefile; current descriptor headers are compiled into the single object.

Test signals: verify object generation for built-in and module configurations.
