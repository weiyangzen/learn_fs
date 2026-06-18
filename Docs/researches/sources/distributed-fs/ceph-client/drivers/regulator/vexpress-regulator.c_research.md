<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/vexpress-regulator.c -->
# sources/distributed-fs/ceph-client/drivers/regulator/vexpress-regulator.c

Purpose: Provides ARM Versatile Express voltage control through the platform-specific vexpress config regmap.

Important APIs and types: `vexpress_regulator_get_voltage()` reads register offset zero through the regmap and returns microvolts. `vexpress_regulator_set_voltage()` writes the requested minimum voltage to offset zero. Probe allocates a dynamic `struct regulator_desc`, selects read-only or writable ops based on min/max constraints, and registers a continuous-voltage regulator.

Control flow: Probe initializes the vexpress config regmap, creates a descriptor named after the device, reads regulator init data from OF, disables `apply_uV`, chooses set-capable ops only when both min and max constraints are present, then registers the regulator.

State and persistence: No private state beyond devm descriptor/regmap allocation. Hardware voltage state is persisted in the vexpress configuration backend.

Dependencies and integration points: Depends on OF compatible `arm,vexpress-volt`, `devm_regmap_init_vexpress_config()`, regulator OF constraints, and consumers expecting continuous voltage operations.

Risks: The set operation writes `min_uV` without validating it against `max_uV`; validation relies on regulator core constraints. Absence of min/max constraints makes the regulator read-only even if hardware can write. `apply_uV` is cleared, avoiding automatic voltage writes during registration.

Test signals: Read-only vs writable DT constraints, regmap read/write failures, voltage set requests at constraint boundaries, async probe ordering, and consumers using `regulator_get_voltage()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/regulator/vexpress-regulator.c -->
