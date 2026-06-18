# sources/distributed-fs/ceph-client/drivers/regulator/tps6586x-regulator.c

Purpose: Platform child regulator driver for TPS6586x PMIC variants, registering SYS, SM, and LDO regulators with variant-specific voltage tables.

Important APIs/types/functions: `struct tps6586x_regulator` wraps a descriptor plus two possible enable bit locations. Macros define table-based, linear, fixed, DVM, and SYS regulators. `find_regulator_info` overlays variant-specific descriptors on the base table. `tps6586x_regulator_preinit` normalizes dual enable-bit state so the driver controls one bit. DT parsing maps regulator child names to IDs and patches SYS supply names for LDO5/LDO_RTC.

Control flow: probe gets platform data or parses DT, identifies parent PMIC version, loops all regulator IDs, finds descriptor info, preinitializes enable bits, registers each regulator with optional OF node, and applies board slew-rate settings for SM0/SM1. Version-specific tables override SM2/LDO voltage data for TPS658623/624/640/643 variants.

State and persistence: hardware enable and voltage state lives in the parent MFD. Driver state is static descriptor tables and parent platform data. Preinit may actively rewrite enable bits while preserving an already-on rail.

Dependencies and integration points: TPS6586x MFD register helpers, regulator core, OF regulator matching, platform data, and parent version detection.

Risks: probe loops every possible ID and expects `reg_init_data` array indexing to match IDs. Static descriptor tables are reused globally. Preinit changes live enable bits and must not create brownouts. Slew rate is valid only for SM0/SM1.

Test signals: each PMIC version override, DT parsing and SYS supply propagation, dual enable-bit normalization, SM0/SM1 slew programming, fixed/read-only regulators, and missing platform-data failure.
