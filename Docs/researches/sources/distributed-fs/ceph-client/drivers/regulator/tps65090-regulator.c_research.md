# sources/distributed-fs/ceph-client/drivers/regulator/tps65090-regulator.c

Purpose: Platform child regulator driver for TPS65090 PMIC rails, including fixed DCDCs, FET switches, and fixed LDO rails.

Important APIs/types/functions: `struct tps65090_regulator` stores per-rail descriptor, rdev, and FET overcurrent wait settings. Descriptor macros define 12 rails. FET enable uses `tps65090_fet_enable`, which retries `tps65090_try_enable_fet` up to 1000 times and checks timeout/power-good bits. DT parsing supports external DCDC control GPIOs and `ti,overcurrent-wait`.

Control flow: probe gets parent MFD data and platform/DT regulator data, allocates per-rail state, optionally configures DCDC external control, registers each regulator with parent regmap and optional OF node, applies overcurrent wait, and enables external control when requested. For FETs, enable sets control bits, polls timeout status, requires power-good, and retries by disabling/re-enabling on recoverable failures.

State and persistence: hardware enable/control bits persist in the MFD regmap. Driver state keeps overcurrent wait values and external-control mode. GPIO descriptors for external control are handed over to the regulator core with `devm_gpiod_unhinge`.

Dependencies and integration points: TPS65090 MFD helpers/regmap, OF regulator matching, GPIO descriptors, regulator core, and platform data.

Risks: FET enable can spin for many attempts and intentionally `WARN_ON(1)` on final failure. External-control ops are empty because GPIO enable is delegated to the core, so descriptor ops change based on DT. Missing regulator node or platform data fails probe.

Test signals: FET retry success/failure, overcurrent wait bounds, external-control GPIO handoff, always-on/boot-on behavior when disabling external control, and DT parsing for every rail.
