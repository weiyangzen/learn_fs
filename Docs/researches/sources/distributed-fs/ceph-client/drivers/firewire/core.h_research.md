# sources/distributed-fs/ceph-client/drivers/firewire/core.h

### Purpose
`core.h` is the private cross-module header for the FireWire core. It declares card-driver operations, shared constants, internal function prototypes, topology node structures, helpers for tcode classification, and small inline utilities used across card, cdev, device, ISO, topology, and transaction files.

### Important APIs, Types, And Functions
The most important type is `struct fw_card_driver`, the controller-driver callback table for enable/disable, PHY register access, config ROM update, async packet send/cancel, physical DMA authorization, CSR access, and ISO context operations. The header also defines PHY/CSR constants, broadcast-channel defaults, `struct fw_node`, `fw_node_get/put()`, `fw_node_get_device/set_device()`, `fw_device_get/put()`, exported globals such as `fw_device_rwsem`, `fw_device_xa`, and `fw_cdev_major`, and prototypes for card, cdev, device, ISO, topology, and transaction entry points.

### Control Flow, State, And Persistence
There is little executable flow besides inline refcount helpers and classifiers. `fw_node` objects persist topology state across bus resets: node id, color, link/reset flags, beta path, speeds, hop/depth metrics, kref, tree/list links, optional associated `fw_device`, and flexible port pointers. Inline helpers establish conventions such as generation successor comparison with 8-bit wraparound, block/read/tlink-internal tcode classification, OHCI timestamp conversion, ping-packet detection, and FCP address range recognition.

### Dependencies, Integration Points, Risks, And Test Signals
This header couples all FireWire core compilation units and controller/protocol-facing internal APIs. Dependencies include Linux device, DMA, file operations, xarray, rwsem, refcount, slab, and FireWire public headers pulled by users. Risks include struct/callback contract drift between OHCI and core, inline `release_node()` being private but used by `fw_node_put()`, assumptions that `read_csr()` is not called after dummy driver replacement except best-effort checks, and generation wrap logic being central to stale-transaction handling. Test signals include full core build, OHCI implementing every required callback, topology refcounting under reset/removal, tcode helper behavior in packet tests, and correct cdev/device integration through declared globals.
