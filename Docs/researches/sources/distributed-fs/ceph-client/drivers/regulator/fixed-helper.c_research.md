# sources/distributed-fs/ceph-client/drivers/regulator/fixed-helper.c

Purpose: Provides a small helper for registering a fixed always-on regulator backed by a platform device, primarily for board/setup code that needs to create a fixed supply programmatically.

Important APIs, types, and functions: `struct fixed_regulator_data` bundles `fixed_voltage_config`, `regulator_init_data`, and an embedded `platform_device`. `regulator_fixed_release()` frees the duplicated supply name and containing allocation. `regulator_register_always_on()` allocates and initializes the bundle, marks constraints always-on, assigns consumer supplies, configures platform data for `"reg-fixed-voltage"`, registers the platform device, and returns it.

Control flow: Callers provide an ID, name, consumer supply array, count, and microvolt value. The helper allocates state, duplicates the name with `kstrdup_const()`, fills fixed regulator config and init data, sets the platform release callback, calls `platform_device_register()`, and returns the embedded platform device pointer.

State and persistence: The platform device owns the allocated bundle. The fixed regulator config points to embedded init data, and release frees both the constant-or-allocated supply name and the bundle.

Dependencies and integration points: It integrates with the fixed voltage regulator platform driver (`fixed.c`), platform device core, and regulator machine constraints.

Risks and test signals: Test allocation failure, supply name lifetime, platform registration failure behavior, release callback execution, always-on constraints, and consumer supply propagation. The helper currently returns the platform device even if `platform_device_register()` fails; callers should be checked for error handling expectations.
