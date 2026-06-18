# sources/distributed-fs/ceph-client/drivers/misc/amd-sbi/rmi-core.h

Purpose: defines shared AMD SB-RMI register constants, mailbox message ids, per-device state, and cross-file function declarations.

Important APIs and types: `enum sbrmi_reg` names revision, control, status, inbound/outbound message, software interrupt, and thread extension registers. `enum sbrmi_msg_id` defines package power read/write/max commands. `struct sbrmi_data` owns the miscdevice, regmap, mutex, cached max power limit, static address, and revision. It declares `rmi_mailbox_xfer`, `create_misc_rmi_device`, and conditional `create_hwmon_sensor_device`.

Control flow: transport probe initializes `struct sbrmi_data`, stores it as drvdata, then calls the declarations here to register hwmon and misc interfaces. Core and hwmon functions share the same mutex and regmap through this structure.

State and persistence: the header describes per-device runtime state but stores none itself. Cached revision and max power limit persist for the lifetime of the probed device.

Dependencies and integration points: depends on miscdevice, mutex, I2C/platform/regmap headers, and AMD APML UAPI structures. It is the coupling point for `rmi-core.c`, `rmi-hwmon.c`, and `rmi-i2c.c`.

Risks: register enum values rely on implicit increments matching the SB-RMI register map. The hwmon stub silently returns success when disabled, so probe behavior changes by config without logging. The include set is broader than needed for some consumers.

Test signals: compile with and without `CONFIG_AMD_SBRMI_HWMON`, static checks of enum addresses against APML documentation, and probe tests validating drvdata fields.
