# sources/distributed-fs/ceph-client/drivers/net/ethernet/rdc/Makefile

Purpose: Connects RDC Kconfig symbols to build outputs.

Important rule: `obj-$(CONFIG_R6040) += r6040.o` builds the RDC R6040 driver when its config is enabled.

Control flow and integration: The parent networking Makefile descends into this vendor directory; this Makefile contributes `r6040.o` according to `CONFIG_R6040`.

State and persistence: No runtime state. Build output depends on the config value.

Risks and test signals: The main risk is stale object naming if the source file is renamed or split. Build tests with `CONFIG_R6040=y` and `m` validate the mapping.
