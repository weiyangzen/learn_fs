# sources/distributed-fs/ceph-client/drivers/regulator/dbx500-prcmu.h

Purpose: Declares the shared data structure and helper prototypes used by UX500/DBX500 PRCMU regulator drivers.

Important APIs, types, and symbols: `struct dbx500_regulator_info` wraps a `regulator_desc` with software state fields: `is_enabled`, `epod_id`, `is_ramret`, and `exclude_from_power_state`. It declares `power_state_active_enable()` and `power_state_active_disable()`. When `CONFIG_REGULATOR_DEBUG` is enabled it declares debug init/exit functions; otherwise inline stubs return success.

Control flow support: DB8500 descriptor entries embed this structure in a global array. Enable/disable paths use the state fields and helper functions, while probe/remove call debug hooks regardless of build configuration.

State and persistence: The header defines the shape of persistent in-memory regulator state but does not allocate it. Its inline debug stubs make debug optional without conditional code at call sites.

Dependencies and integration points: It includes `linux/platform_device.h` and assumes regulator descriptor definitions are visible to C files including it through their own includes.

Risks and test signals: Adding fields changes the shared contract between DB8500 descriptors and debugfs formatting. Test builds with and without `CONFIG_REGULATOR_DEBUG` to ensure both real and stub paths compile.
