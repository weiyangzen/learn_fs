# sources/distributed-fs/ceph-client/arch/arm/mach-aspeed/Kconfig

Purpose: declares Aspeed BMC platform support and generation-specific machine symbols for AST2400, AST2500, and AST2600 families. It selects watchdog, syscon, pinctrl, timers, CPU generation, GIC, and arch timer support as appropriate.

Control flow is Kconfig dependency selection across ARMv5/v6/v7 multi-platform builds. No runtime state exists here. Risks are selecting wrong CPU generation or missing timer/pinctrl dependencies for a SoC generation. Test signals are build coverage for G4/G5/G6 and boot on representative Aspeed DTs.
