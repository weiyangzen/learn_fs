<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_cl_bus.h -->
# sources/distributed-fs/ceph-client/include/linux/mei_cl_bus.h

## Purpose
This header defines the Intel MEI client bus interface, including MEI client device/driver types, registration helpers, synchronous I/O, callbacks, DMA mapping, and GSC command support.

## Important APIs, types, and functions
`struct mei_cl_device` links a Linux device to the MEI bus, ME host client, MEI client handle, name, RX and notification work/callbacks, match/add flags, and driver private data. `struct mei_cl_driver` provides an ID table and probe/remove callbacks. APIs include driver register/unregister, `mei_cldev_send`, `mei_cldev_recv`, timeout and vtag variants, callback registration, UUID/version/MTU queries, drvdata helpers, enable/disable/enabled, `mei_cldev_send_gsc_command`, and DMA map/unmap helpers.

## Control flow
Drivers register with `mei_cldev_driver_register` or `module_mei_cl_driver`, bind to matching MEI clients, enable the client, send/receive messages synchronously or with timeouts, and register asynchronous RX/notification callbacks executed from work items. Remove disables I/O and clears driver state.

## State and persistence
Runtime state includes bus list membership, match/add flags, RX/notification work, callbacks, MEI client handles, private data, enable state, and DMA mappings. Firmware client identity persists in ME firmware but not in this header.

## Dependencies and integration points
It depends on Linux device model, UUIDs, module device tables, workqueues, scatterlists, and MEI core internals. It integrates MEI host-client protocols, GSC command paths, and ME firmware notifications with client drivers.

## Risks and test signals
Risks include callbacks racing device removal, send/receive timeout mismatches, vtag misuse, DMA buffer leaks, MTU violations, and enable/disable ordering errors. Test probe/remove, enable failure, blocking and timeout I/O, RX and notification callbacks, vtag round trips, GSC scatterlist commands, and DMA map/unmap cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mei_cl_bus.h -->
