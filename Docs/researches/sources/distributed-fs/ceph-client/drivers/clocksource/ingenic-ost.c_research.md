# sources/distributed-fs/ceph-client/drivers/clocksource/ingenic-ost.c

Purpose: registers the Ingenic JZ operating system timer as a continuous clocksource and sched_clock.

Important APIs/types/functions: `struct ingenic_ost_soc_info`, `struct ingenic_ost`, low/high counter read helpers, `ingenic_ost_probe()`, suspend/resume PM ops, and the built-in platform driver probe.

Control flow: probe matches SoC data, allocates state, maps registers, obtains the parent TCU regmap, enables the `ost` clock, clears counter registers, configures non-reset-on-compare mode, enables TCU channel 15, registers the clocksource, and registers sched_clock using the appropriate counter half.

State and persistence: global `ingenic_ost` supplies lockless sched_clock reads; device state stores MMIO base, clock, and embedded clocksource. The TCU regmap controls shared timer registers.

Dependencies and integration points: depends on MFD Ingenic TCU definitions, syscon/regmap, platform device probing, CCF, PM sleep ops, clocksource, and sched_clock.

Risks: for 64-bit SoCs the driver still registers a 32-bit mask and reads the low half; for older SoCs it uses the high register. Global singleton design assumes one OST. `dev_get_drvdata()` in PM callbacks requires driver data to be set, but probe does not call `platform_set_drvdata()`.

Test signals: JZ4725B versus JZ4760B/JZ4770 compatibles, regmap access, suspend/resume clock gating, sched_clock monotonicity, and probe with missing parent regmap or clock.
