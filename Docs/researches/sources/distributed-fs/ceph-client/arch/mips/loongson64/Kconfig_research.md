<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Kconfig -->
# sources/distributed-fs/ceph-client/arch/mips/loongson64/Kconfig

Purpose: Defines Loongson64-specific configuration for the RS780/SBX00 HPET timer.

Important APIs/types/functions: `RS780_HPET` is a bool under `MACH_LOONGSON64`, depends on `BROKEN`, and selects `MIPS_EXTERNAL_TIMER`.

Control flow: The option is hidden from normal use because of `BROKEN`; help warns that the driver performs dangerous hacks and should be enabled only on RS780E systems.

State and persistence: Build configuration only.

Dependencies and integration: Enables `hpet.o` through the Loongson64 Makefile.

Risks: The option manipulates chipset registers before PCI init; enabling it on wrong hardware is unsafe.

Test signals: With the option enabled manually, `setup_hpet_timer()` and HPET clocksource registration should compile and run on RS780E.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson64/Kconfig -->
