# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-scmi.c

Purpose: ACPI SMBus CMI adapter driver. It exposes an SMBus-only I2C adapter by calling ACPI control methods (`_SBI`, `_SBR`, `_SBW`, or IBM alternate names) on firmware-described SMBus controllers.

Important APIs/types/functions: `struct acpi_smbus_cmi` stores ACPI handle, adapter, read/write/info capability bits, and method-name table. `acpi_smbus_cmi_access()` is the SMBus transfer implementation. `acpi_smbus_cmi_func()` advertises functions based on discovered methods. `acpi_smbus_cmi_add_cap()` evaluates the info method and records method capabilities. `acpi_smbus_cmi_query_methods()` is the namespace walker callback. `smbus_cmi_probe()` and remove manage adapter lifetime.

Control flow: probe allocates state, gets the ACPI match data method table, walks one namespace level for ACPI methods, requires the info method, fills adapter metadata, and registers it. Transfers map Linux SMBus sizes to ACPI protocol constants and method arguments. Reads call the read method with protocol/address/command; writes call the write method with protocol/address/command/length/value-or-buffer. Returned ACPI packages are validated, status is mapped to Linux errno, and read payloads are copied into `union i2c_smbus_data`.

State and persistence: capability bits persist after probe. There is no hardware state in the driver; firmware methods own serialization and controller state. ACPI result buffers are allocated per transfer and freed before return.

Dependencies/integration: ACPI namespace/method evaluation, platform driver ACPI match table, I2C SMBus algorithm, HWMON class scanning, and firmware-specific CMI package contracts.

Risks: correctness depends entirely on firmware package shape and status values. Block-read protocol validates returned length but returns `-EPROTO` before freeing the ACPI buffer in one invalid-length path, which is a leak risk. The expression in functionality setup relies on operator precedence for read/write capability quick support. Unsupported ACPI status codes collapse to `-EIO`. Method discovery tolerates unsupported names but requires the info method.

Test signals: ACPI devices with standard, IBM, and Microsoft HIDs; absent info method; read-only/write-only capability sets; all supported SMBus sizes; malformed package/object types; status mappings for busy/timeout/DNAK/failure; block length zero/overflow; and adapter cleanup after registration failure.
