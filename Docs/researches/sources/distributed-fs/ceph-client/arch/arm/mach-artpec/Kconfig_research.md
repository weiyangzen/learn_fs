# sources/distributed-fs/ceph-client/arch/arm/mach-artpec/Kconfig

Purpose: declares Axis ARTPEC ARM SoC support and `MACH_ARTPEC6`. ARTPEC-6 selects AMBA, GIC, global/arch timers, PSCI, SCU/TWD, and syscon support.

Control flow is Kconfig selection. The file determines whether `board-artpec6.o` participates in the build and whether secure/cache/timer dependencies are present. Risks are incomplete selects for PSCI or cache controller integration. Test signals are ARTPEC6 build coverage and boot with expected interrupt/timer/PSCI support.
