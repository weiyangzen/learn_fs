# sources/distributed-fs/ceph-client/include/linux/fsi.h

Purpose: defines the public device/driver interface for IBM FSI devices, including FSI device identity, driver registration, device I/O helpers, direct slave range access, and minor allocation for FSI character devices.

Important APIs and types: `struct fsi_device` embeds `struct device` and records engine type, version, unit, slave pointer, address, and size. `struct fsi_device_id` plus `FSI_DEVICE()` and `FSI_DEVICE_VERSIONED()` support driver matching. `struct fsi_driver` contains probe/remove callbacks, a generic `device_driver`, and an id table. Helpers include `fsi_get_drvdata()`, `fsi_set_drvdata()`, `fsi_device_read()`, `fsi_device_write()`, `fsi_device_peek()`, `fsi_driver_register()`, `fsi_driver_unregister()`, `module_fsi_driver()`, `fsi_slave_claim_range()`, `fsi_slave_release_range()`, `fsi_slave_read()`, `fsi_slave_write()`, `fsi_get_new_minor()`, and `fsi_free_minor()`.

Control flow: bus discovery creates `fsi_device` instances; FSI drivers register an id table and probe matching devices; drivers issue address-relative reads/writes or claim direct slave ranges for broader access. Character device users obtain minors by FSI device type.

State and persistence: state is runtime bus/device binding, driver data, claimed slave address ranges, and allocated device minors. Hardware register contents persist in external FSI-attached devices but are not modeled here.

Dependencies and integration points: depends on Linux driver core and integrates with FSI bus core, OCC/SBEFIFO/SCOM/cfam character devices, module aliasing, and platform firmware discovery.

Risks and test signals: risks include overlapping slave range claims, size/address validation gaps, minor leaks, version matching mistakes, and unsafe direct access. Tests should cover driver bind/unbind, read/write sizes and alignment, peek behavior, range claim conflicts, minor allocation/free, and module auto-loading from FSI ids.
