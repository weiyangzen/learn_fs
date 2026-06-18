<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/iio/industrialio-acpi.c

Purpose: ACPI helper functions for IIO drivers. It reads Microsoft-style ACPI sensor mount matrices and provides a legacy helper for retrieving ACPI device names plus match data.

Important APIs/functions: exported `iio_read_acpi_mount_matrix()` evaluates an ACPI method such as `ROTM`, validates a 3-string package, parses each row as three integers, and fills `struct iio_mount_matrix` with canonical string pointers for `-1`, `0`, and `1`. Exported `iio_get_acpi_device_name_and_data()` matches the device against its driver's ACPI table, optionally returns `driver_data`, and returns `dev_name(dev)`.

Control flow: mount-matrix read silently returns false when the device has no ACPI handle or method; evaluation/format/value errors log and return false after freeing the ACPI buffer. The legacy name helper returns NULL for no ACPI handle or no match.

State and persistence: no persistent state. The orientation matrix stores pointers to string literals, not allocated row strings. ACPI evaluation buffer is freed before return.

Dependencies and integration: depends on ACPI core helpers, device model, IIO mount matrix type, export symbols, and is used by drivers such as `st_lsm6dsx_core.c` before falling back to generic firmware mount matrix parsing.

Risks: `sscanf()` only accepts integer triplets and rejects any non-orthogonal value outside -1/0/1. The `acpi_status` is logged with `%d`, which may not be ideal for all status representations. The name/data helper is explicitly documented as backward compatibility and should not be used by new drivers.

Test signals: ACPI devices with valid `ROTM`, missing method, malformed package count/type, invalid matrix values, dual-method callers such as `ROMK`/`ROMS`, and ACPI match data retrieval.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/industrialio-acpi.c -->
