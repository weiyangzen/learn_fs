# sources/distributed-fs/ceph-client/drivers/misc/mei/bus.c

## Purpose
`bus.c` implements the MEI client bus. It exports MEI client send/receive APIs, callback registration, enable/disable, client DMA mapping, GSC scatter-gather command support, MEI bus device matching/probing/removal, sysfs attributes, uevents, and firmware-client rescanning.

## Important APIs, Types, and Functions
Exported APIs include `mei_cldev_send*()`, `mei_cldev_recv*()`, `mei_cldev_register_rx_cb()`, `mei_cldev_register_notif_cb()`, `mei_cldev_enable()`, `mei_cldev_disable()`, `mei_cldev_dma_map/unmap()`, `mei_cldev_send_gsc_command()`, driver registration helpers, and bus init/exit. Internal foundations include `__mei_cl_send_timeout()`, `__mei_cl_recv()`, `mei_cl_bus_rescan()`, and `mei_cl_bus_dev_alloc/setup/add/destroy()`.

## Control Flow
Send validates bus state, connection, vtag support, MTU, and TX queue limits, allocates a write callback, copies data or extended headers, and calls `mei_cl_write()`. Receive starts flow control if no completed read exists, optionally waits, copies normal or GSC extended data, and frees the read callback. Device rescans allocate `mei_cl_device` wrappers for active firmware clients, run fixups, and add matching devices to the Linux device model. Driver probe matches UUID/name/version and invokes the MEI client driver.

## State and Persistence
State spans `mei_cl_device`, its embedded `mei_cl`, bus/device refs, callback work items, `do_match`, `is_added`, sysfs-visible firmware client properties, and driver-private data. No persistence beyond runtime device model state.

## Dependencies and Integration Points
Depends on `client.c` state machine, MEI HBM support, Linux driver core bus APIs, sysfs/uevent modaliases, scatterlist DMA addresses, runtime PM through lower layers, and MEI client drivers such as GSC proxy, HDCP, and PXP.

## Risks
Locking is split between `device_lock`, `cl_bus_lock`, read-completion spinlocks, and workqueues. Send/receive error paths must free callbacks exactly once. GSC command validation relies on DMA-mapped scatterlists and matching fence/client IDs. Bus references must outlive client devices.

## Test Signals
Signals are successful MEI bus registration, sysfs attributes (`name`, `uuid`, `version`, `modalias`, `max_conn`, `fixed`, `vtag`, `max_len`), client driver autoload via modalias, blocking/nonblocking send/recv behavior, callback invocation, enable/disable connect lifecycle, DMA map/unmap lifecycle, GSC command round trips, and clean rescan/removal.
