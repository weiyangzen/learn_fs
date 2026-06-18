# sources/distributed-fs/ceph-client/arch/arm/mach-meson/Kconfig

Purpose: Kconfig menu for Amlogic Meson ARMv7 platforms.

Important APIs/types/functions: Defines `ARCH_MESON` plus `MACH_MESON6`, `MACH_MESON8`, `MACH_MESON8B`, and `MACH_MESON8M2`, selecting GIC, arch timer, SMP, and Meson SMP support as appropriate.

Control flow: No runtime flow; it controls which Meson machine and SMP objects build.

State and persistence: No runtime state.

Dependencies and integration points: Integrates with ARM multi-v7, GIC, timer, DT, and Meson-specific SMP code.

Risks: Selecting SMP support for families depends on matching firmware/register support; configuration mistakes show as secondary CPU boot failures.

Test signals: Build Meson6/8 variants and verify selected SMP/timer/irq symbols.
