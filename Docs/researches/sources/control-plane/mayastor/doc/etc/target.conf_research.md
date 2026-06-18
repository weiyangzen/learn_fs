# sources/control-plane/mayastor/doc/etc/target.conf

## Purpose
Example SPDK iSCSI target configuration exposing two malloc-backed disks.

## Important Sections
`[Malloc]` creates two 64 MiB LUNs with 4096-byte block size. `[iSCSI]` sets node base `iqn.2019-05.io.openebs`. `PortalGroup1` listens on `0.0.0.0:3261`; `InitiatorGroup1` allows any initiator/netmask. `TargetNode0` and `TargetNode1` expose `disk0` and `disk1` with queue depth 128; the first explicitly sets `AuthMethod None`.

## Control Flow
SPDK target initialization creates malloc bdevs, configures portal/initiator groups, and exposes target nodes mapping LUN0 to each malloc disk.

## State and Persistence
Static config. Runtime state includes in-memory malloc disks and iSCSI sessions; data is not persistent across process restart.

## Dependencies and Integration Points
Designed to pair with `doc/etc/nexus.conf` iSCSI initiator URLs. Requires SPDK iSCSI target support and port 3261 availability.

## Risks
Allows any initiator and no authentication, so it is only safe for isolated test environments. Malloc disks are volatile. Binding `0.0.0.0` exposes the target on all interfaces.

## Test Signals
Start the target in an isolated environment and use an iSCSI initiator or Mayastor nexus config to connect to `disk0` and `disk1`.
