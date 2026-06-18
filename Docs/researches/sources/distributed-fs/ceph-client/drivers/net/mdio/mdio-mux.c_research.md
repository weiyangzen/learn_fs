<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux.c

Purpose: core framework for MDIO bus multiplexers. It creates child mii_bus instances that switch a shared parent bus before forwarding MDIO operations.

Important APIs/types/functions: exports `mdio_mux_init` and `mdio_mux_uninit`. Internal types are `struct mdio_mux_parent_bus` and `struct mdio_mux_child_bus`; forwarding callbacks include C22/C45 read/write variants.

Control flow: `mdio_mux_init` locates the parent bus via `mdio-parent-bus` or uses a supplied bus, allocates parent state, iterates child nodes, reads each child `reg`, allocates a child bus, installs only the callbacks supported by the parent, registers it with OF MDIO, and returns a mux handle. Child operations lock the parent bus `mdio_lock` with mux nesting, call the driver switch function if needed, update current child, and forward to the parent callback. Uninit unregisters/frees child buses and releases the parent device.

State and persistence: runtime state tracks current child, parent ID counter, parent device reference, child bus list, and driver-provided switch data. No persistent storage exists.

Dependencies/integration: used by GPIO, MMIO, Broadcom, Amlogic, and generic mux drivers. Depends on OF MDIO, phylib, mii_bus locking, and driver-specific switch functions.

Risks and test signals: risks include child registration partial failures, parent reference leaks, `parent_count` global uniqueness only per boot, switch failure leaving current child stale, and callback absence. Tests should cover parent deferral, mixed C22/C45 parents, failed child registration, nested lock behavior, and uninit cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux.c -->
