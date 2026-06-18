<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/interface.h -->
# sources/distributed-fs/ceph-client/include/linux/ulpi/interface.h

Purpose: declares the provider-side ULPI bus interface used by controllers that can read and write ULPI PHY registers.

Important APIs and types: `struct ulpi_ops` supplies `read(struct device *, u8 addr)` and `write(struct device *, u8 addr, u8 val)` callbacks. `ulpi_register_interface()` creates a `struct ulpi` from a parent device and ops; `ulpi_unregister_interface()` removes it.

Control flow: a USB controller or glue driver registers ULPI access ops, the ULPI core enumerates/identifies the PHY, and matched PHY drivers call through `ulpi_read()`/`ulpi_write()` to these ops.

State and persistence: this header owns no state; provider implementations keep bus/register access state and the ULPI core owns the created device.

Dependencies and integration points: depends on `linux/types.h` and forward declarations of `struct device`/`struct ulpi`. It bridges host/device controller drivers to ULPI PHY drivers.

Risks and test signals: risks include ops that sleep in invalid contexts, bad register address handling, and unregistering while a PHY driver is active. Test interface registration failure paths, read/write error returns, and remove ordering with active USB controllers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/ulpi/interface.h -->
