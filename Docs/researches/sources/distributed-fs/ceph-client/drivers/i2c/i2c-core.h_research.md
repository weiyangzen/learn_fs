# sources/distributed-fs/ceph-client/drivers/i2c/i2c-core.h

Purpose: private header for I2C framework implementation files. It exposes shared board-info state, internal helpers, firmware integration hooks, SMBus alert setup, and lock/suspend helpers used by core transfer code.

Important APIs/types: `struct i2c_devinfo` stores board-list entries. Externs include `__i2c_board_lock`, `__i2c_board_list`, and `__i2c_first_dynamic_bus_num`. Helpers include `i2c_check_7bit_addr_validity_strict()`, `i2c_dev_irq_from_resources()`, `i2c_in_atomic_xfer_mode()`, `__i2c_lock_bus_helper()`, `__i2c_check_suspended()`, ACPI/OF registration and matching hooks, and `i2c_setup_smbus_alert()`.

Control flow: transfer callers use `__i2c_lock_bus_helper()` to select trylock behavior for late atomic contexts, then `__i2c_check_suspended()` before dispatch. Adapter registration code calls OF/ACPI/SMBus hook declarations that compile to no-ops when features are disabled.

State and persistence: it centralizes access to board registration globals and adapter locked flags. It does not own storage beyond external declarations.

Dependencies and integration: depends on kconfig conditionals, rwsems, system state/preemption, and feature-specific compilation for ACPI, OF, ACPI opregions, and SMBus.

Risks: private helpers define subtle global behavior. Atomic transfer detection is intentionally narrow and may return `-EAGAIN` instead of sleeping. Suspend warnings are rate-limited by a bit flag so repeated bugs can become quiet.

Test signals: all I2C core files build under OF/ACPI/SMBUS enabled and disabled configs, atomic transfer trylock behavior, and suspended adapter rejection.
