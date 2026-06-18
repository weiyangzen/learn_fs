# sources/distributed-fs/ceph-client/arch/arm/mach-at91/Makefile

Purpose: selects AT91/Microchip platform objects based on SoC and PM Kconfig symbols, and generates PM data offset headers needed by suspend assembly/C code.

Control flow is build-time: SoC objects such as `at91rm9200.o`, `at91sam9.o`, `sam9x60.o`, `sam9x7.o`, `sama5.o`, `sama7.o`, and `samv7.o` are conditionally added; PM builds include `pm.o` and `pm_suspend.o`; `pm_data-offsets.h` is generated from `pm_data-offsets.s`. Dependencies are Kbuild `filechk`, FORCE rules, and PM code including the generated header. Risks are stale generated offsets, missing clean-files, and SoC object omissions. Test signals are clean rebuilds with PM on/off and each SoC selected.
