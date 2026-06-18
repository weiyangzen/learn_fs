# sources/distributed-fs/ceph-client/include/xen/interface/io/xenbus.h

## Purpose
`io/xenbus.h` defines the public Xenbus device-state enumeration used by frontend and backend drivers to coordinate connection, teardown, and reconfiguration through Xenstore.

## Important APIs, Types, and Functions
The key type is `enum xenbus_state` with values from `XenbusStateUnknown` through `XenbusStateReconfigured`, including the normal bring-up sequence `Initialising`, `InitWait`, `Initialised`, `Connected`, the teardown states `Closing` and `Closed`, and reconfiguration states `Reconfiguring` and `Reconfigured`.

## Control Flow
Drivers publish their own state and watch the peer state. A normal device moves from initialization to `Connected`; unplug or error paths move through `Closing` to `Closed`; dynamic changes use `Reconfiguring` and `Reconfigured` before returning to connected operation.

## State and Persistence Behavior
The enum values are persisted as integer Xenstore state nodes for the lifetime of a Xen device. They are a coordination protocol, not kernel memory state by themselves.

## Dependencies and Integration Points
This header is consumed by Linux `xenbus.h`, Xen frontend/backend drivers, and tooling that creates or observes Xenstore device nodes. It must remain stable across guest, backend, and toolstack versions.

## Risks and Test Signals
Risks are state-machine deadlocks, drivers treating a state as stronger than it is, and incompatible tooling assumptions around reconfiguration states. Test signals include Xenbus probe/remove tests, peer-state watch delivery, suspend/resume state replay, and hotplug error-path coverage.
