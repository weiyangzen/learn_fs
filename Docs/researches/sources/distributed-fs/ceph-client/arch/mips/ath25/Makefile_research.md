## sources/distributed-fs/ceph-client/arch/mips/ath25/Makefile

Purpose: controls compilation of ATH25 platform objects. It always includes shared board, PROM, and device registration code, then conditionally includes early printk and SoC-family implementations.

Important build entries: `obj-y += board.o prom.o devices.o` provides core platform hooks. `obj-$(CONFIG_EARLY_PRINTK) += early_printk.o` adds early UART output. `obj-$(CONFIG_SOC_AR5312) += ar5312.o` and `obj-$(CONFIG_SOC_AR2315) += ar2315.o` link the family-specific setup.

Control flow: none at runtime. Build selection determines whether the inline stubs in `ar5312.h`/`ar2315.h` are replaced by real implementations.

State and persistence: none directly.

Dependencies and integration: depends on Kbuild and local Kconfig symbols. It integrates with MIPS architecture boot through `plat_mem_setup`, `arch_init_irq`, `plat_time_init`, initcalls, and early printk objects supplied by the compiled files.

Risks: disabling one SoC family while booting that hardware leaves the dispatch path with no-op stubs or missing setup. Shared code still selects runtime behavior by CPU type, so build coverage should match target hardware.

Test signals: compile all selected combinations, check linked symbols for target SoCs, and boot with/without `CONFIG_EARLY_PRINTK` to verify console behavior.
