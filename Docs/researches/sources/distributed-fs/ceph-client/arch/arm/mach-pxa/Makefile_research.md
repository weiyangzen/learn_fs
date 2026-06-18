<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Makefile -->
# sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Makefile

Purpose: build manifest for PXA machine support objects.

Important entries: always links `devices.o generic.o irq.o reset.o`; adds `pm.o sleep.o standby.o` under `CONFIG_PM`; selects SoC-specific objects for `PXA25x`, `PXA27x`, `PXA3xx`, `CPU_PXA300`, and `CPU_PXA320`; adds `pxa-dt.o` for DT machine symbols; adds legacy Gumstix and EPD files for their config symbols.

Control flow: link ordering matters. Common support is explicitly linked before board-specific support, which matches comments in `generic.c` and SoC files that rely on early default initcalls.

State and persistence: build-only; no runtime state.

Dependencies and integration: maps Kconfig symbols to object files. Some objects such as `smemc.o`, `sleep.o`, and Sharp board files are outside this subset but are part of the same architecture build.

Risks and test signals: object ordering and duplicate inclusion matter for weak carrier initializers and shared MFP objects. Build tests should cover `CONFIG_PXA25x`, `CONFIG_PXA27x`, `CONFIG_PXA3xx`, DT-only builds, and legacy Gumstix carrier choices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-pxa/Makefile -->
