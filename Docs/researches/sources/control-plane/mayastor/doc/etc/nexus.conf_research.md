# sources/control-plane/mayastor/doc/etc/nexus.conf

## Purpose
Example SPDK/Mayastor nexus configuration that composes a nexus device from two iSCSI children.

## Important Sections
`[Nexus]` defines `Dev e5dc0d39-ffa2-4917-b404-e3a0ed8c2409 512 64 iscsi0 iscsi1`, indicating a nexus UUID/device with block size/size parameters and two child bdev aliases. `[iSCSI_Initiator]` maps two iSCSI URLs to `iscsi0` and `iscsi1`.

## Control Flow
When consumed by the relevant SPDK/Mayastor config loader, iSCSI initiator bdevs are established first and the nexus device is assembled from them.

## State and Persistence
Static config only. Runtime use would create initiator sessions and a nexus device in process memory.

## Dependencies and Integration Points
Depends on reachable iSCSI targets at the hard-coded IPs/ports and Mayastor/SPDK support for these config sections.

## Risks
Hard-coded private IPs and IQNs make it example-specific. No authentication is configured. If used accidentally in production, it points to fixed test endpoints.

## Test Signals
Use only in a lab where the target config is active, then verify both iSCSI children connect and the nexus appears.
