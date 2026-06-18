# sources/distributed-fs/ceph-client/drivers/regulator/max8907-regulator.c

Purpose: registers the MAX8907 PMIC regulator set: main battery pseudo-rail, SD regulators, 20 LDOs, fixed rails, OUT5V/OUT33V, and backup battery charger voltage control.

Important APIs/types/functions: descriptor macros build the regulator table. `max8907_regulator_parse_dt()` matches child regulators. Probe copies descriptors into per-device storage so it can adjust MAX8907B SD1 voltage metadata and switch ops to hardware-control variants. `match_init_data()` and `match_of_node()` bridge DT parsing.

Control flow: platform probe parses DT, allocates per-device descriptors, reads the revision register, adjusts SD1 for revision B, establishes MBATT as a supply name for BBAT/SDBY/VRTC, detects hardware-controlled LDO/OUT5V rails by reading control registers, and registers every descriptor.

State and persistence: per-device descriptor copies are mutable state. Hardware control status determines whether software enable/disable ops are exposed.

Dependencies and integration: depends on MAX8907 MFD regmaps/platform data, OF regulator matching, and regulator core.

Risks and test signals: when no init data exists, BBAT/SDBY/VRTC paths dereference `idata` while assigning `supply_regulator`. Test DT-only configurations, revision B SD1 values, hardware-control op switching, MBATT naming, platform-data init data arrays, and all regulator registrations.
