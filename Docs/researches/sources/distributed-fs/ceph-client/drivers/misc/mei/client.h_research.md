# sources/distributed-fs/ceph-client/drivers/misc/mei/client.h

## Purpose
`client.h` declares the internal MEI client API shared by core, bus, interrupt, HBM, and debugfs code.

## Important APIs, Types, and Functions
It declares firmware-client list/ref helpers, host-client allocation/linking, callback allocation/enqueue/flush, vtag helpers, connect/disconnect/read/write IRQ paths, notification conversion/request/event helpers, DMA map/unmap helpers, and debug print macros. Inline helpers expose client UUID, version, MTU, fixed address, host address, and connection state.

## Control Flow
Callers use the declarations to move clients through allocation, link, connect, I/O, notification, DMA, disconnect, queue flush, and unlink phases. Inline helpers centralize state/property interpretation.

## State and Persistence
The header owns no storage. It defines access patterns for state in `struct mei_device`, `struct mei_cl`, and `struct mei_me_client`.

## Dependencies and Integration Points
Includes `<linux/mei.h>` and `mei_dev.h`, and is consumed by `client.c`, `bus.c`, `bus-fixup.c`, `debugfs.c`, interrupt/HBM code, and MEI hardware paths.

## Risks
Prototype changes affect many MEI core files. Inline assumptions, such as fixed clients using host address zero, are protocol-significant.

## Test Signals
Signals are successful compilation of all MEI core objects and behavior parity for all call paths that use these shared declarations.
