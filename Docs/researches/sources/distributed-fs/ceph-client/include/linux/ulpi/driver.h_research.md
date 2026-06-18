<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/driver.h -->
# sources/distributed-fs/ceph-client/include/linux/ulpi/driver.h

Purpose: defines the Linux device/driver wrapper for ULPI USB PHY devices.

Important APIs and types: `struct ulpi` embeds a `struct device`, an `ulpi_device_id`, and bus I/O ops. `struct ulpi_driver` carries an ID table, `probe()`/`remove()` callbacks, and the underlying `device_driver`. Helpers include `to_ulpi_dev()`, `to_ulpi_driver()`, `ulpi_set_drvdata()`, `ulpi_get_drvdata()`, `ulpi_register_driver()`, `ulpi_unregister_driver()`, `module_ulpi_driver()`, `ulpi_read()`, and `ulpi_write()`.

Control flow: interface providers register a ULPI device, ULPI PHY drivers match on the device ID table, probe configures the PHY via register reads/writes, and remove unwinds device-specific state.

State and persistence: state is device-model lifetime data plus driver private data and hardware PHY register state. Nothing is persisted by the header.

Dependencies and integration points: depends on `mod_devicetable.h`, `device.h`, and `struct ulpi_ops` from the interface layer. It connects USB controller glue code, PHY drivers, module autoloading, and ULPI register access.

Risks and test signals: risks include missing module ownership, accessing ULPI registers after unregister, wrong ID matching, and unsynchronized PHY register changes during controller role/power transitions. Test probe/remove, module autoload aliases, register read/write error propagation, suspend/resume, and controller integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/driver.h -->
