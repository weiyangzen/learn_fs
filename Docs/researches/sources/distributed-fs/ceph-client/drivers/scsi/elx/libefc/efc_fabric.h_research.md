# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.h

## Purpose
`efc_fabric.h` declares fabric, namespace, fabric-controller, and P2P state handlers plus topology helpers.

## Important APIs, Types, And Functions
The header exports state functions for FLOGI, FDISC, name-server PLOGI/RFT_ID/RFF_ID/GID_PT, delayed GID_PT, fabric-controller SCR/RSCN, and P2P login/attach paths. It also declares `efc_p2p_setup`, `efc_fabric_set_topology`, and `efc_fabric_notify_topology`.

## Control Flow And State
Declarations mirror the fabric discovery pipeline: login to fabric, attach domain/nport, start namespace/fabric-controller nodes, process name-server and RSCN events, or take the P2P route when FLOGI reveals an N_Port peer. Topology helpers mutate `nport->topology` and notify nodes that were blocked waiting for topology.

## Dependencies And Integration Points
It includes Linux FC ELS/FS/NS headers and depends on `efc_sm_ctx`, `efc_node`, and `efc_nport` from the libefc object model. Device code uses topology helpers when inbound FLOGI/PLOGI indicates P2P behavior.

## Risks And Test Signals
Risks are mostly event-contract risks across multiple state-machine families. Test signals should ensure every declared fabric state is reachable through login/discovery tests and that topology notifications are delivered exactly once to waiting nodes.
