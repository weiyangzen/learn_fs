## sources/distributed-fs/ceph-client/arch/mips/ath79/Makefile

Purpose: builds the common ATH79 platform objects.

Important build entries: `obj-y := prom.o setup.o common.o clock.o` always includes firmware command-line parsing, platform setup, shared reset/DDR helpers, and clock registration. `obj-$(CONFIG_EARLY_PRINTK) += early_printk.o` optionally adds early UART output.

Control flow: none at runtime. The included objects provide MIPS platform hooks, clock providers, reset helpers, and early console support.

State and persistence: none directly.

Dependencies and integration: uses Kbuild and `CONFIG_EARLY_PRINTK`. The object list assumes device-tree-based board descriptions will drive devices while these files provide common low-level services.

Risks: omitting `clock.o` or `setup.o` would break timer initialization and SoC detection. Early printk support is optional and not available in non-early builds.

Test signals: built kernels should expose `prom_init`, `plat_mem_setup`, `plat_time_init`, `arch_init_irq`, ATH79 reset helpers, and DT clock provider declarations.
