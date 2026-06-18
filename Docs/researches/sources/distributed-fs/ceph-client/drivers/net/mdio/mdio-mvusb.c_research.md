<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mvusb.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mvusb.c

Purpose: USB-to-MDIO adapter driver for Marvell Link Street development-board adapters.

Important APIs/types/functions: `struct mvusb_mdio` stores the USB device, mii_bus, and small command buffer. Key functions are `mvusb_mdio_read`, `mvusb_mdio_write`, probe, and disconnect. USB ID is vendor `0x1286`, product `0x1fa4`.

Control flow: probe allocates a devm mii_bus/private object, initializes reversed command preamble words, assigns C22 read/write callbacks, stores USB interface data, and registers with OF MDIO. Read writes a command to bulk OUT endpoint 2 then reads a 16-bit value from bulk IN endpoint 6. Write sends preamble/address/value over bulk OUT endpoint 2. Disconnect unregisters the bus.

State and persistence: runtime state is the USB device pointer and command buffer; no persistent storage exists.

Dependencies/integration: depends on USB core, OF MDIO, phylib, and hardware-specific bulk endpoint protocol.

Risks and test signals: risks include undocumented USB command format, fixed endpoints/timeouts, no Clause 45 support, and disconnect during transfers. Tests require the adapter or USB emulation to validate read/write commands, timeout handling, and unplug cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mvusb.c -->
