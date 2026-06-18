# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_fabric.c

## Purpose
`efc_fabric.c` implements fabric, fabric-controller, name-server, and point-to-point node state machines. It is responsible for FLOGI/FDISC login, topology detection, domain attach initiation, SCR/RSCN processing, GID_PT discovery, and P2P winner setup.

## Important APIs, Types, And Functions
Important state handlers include `__efc_fabric_init`, FLOGI/FDISC waits, fabric wait/idle, namespace PLOGI/RFT_ID/RFF_ID/GID_PT states, fabric-controller SCR/RSCN states, P2P FLOGI/PLOGI/domain/node attach states, and `__efc_fabric_wait_attach_evt_shutdown`. Helpers include `efc_fabric_set_topology`, `efc_fabric_notify_topology`, `efc_p2p_setup`, and internal GID_PT/RSCN processors.

## Control Flow And State
The physical fabric node sends FLOGI. If the response is an F_Port, topology becomes fabric, pending topology waiters are notified, and `efc_domain_attach` uses the returned FC_ID. If the response is N_Port, P2P winner logic assigns local/remote IDs and either attaches the domain or waits for the peer's PLOGI path. After domain/nport attach, the code starts a name-server node and optional fabric-controller node. Name-server flow logs into directory services, registers FC4 types/features, issues GID_PT, creates missing remote nodes, marks absent nodes missing, and handles RSCN-driven rediscovery with optional target delay. Fabric-controller flow sends SCR, accepts RSCN, and forwards it to name-server.

## Dependencies And Integration Points
This file depends on ELS/CT helpers, node allocation and attach, domain/nport attach APIs, FC well-known IDs, xarray node lookup, timers for delayed GID_PT, and backend node/device state machines for discovered peers.

## Risks And Test Signals
Risks include P2P winner comparison correctness, topology notification timing for nodes waiting on PLOGI, GID_PT payload parsing, RSCN coalescing delays, and repeated discovery during shutdown. Test signals include FLOGI to F_Port and N_Port, FDISC vport login, SCR/RSCN acceptance, GID_PT with new/missing/refound nodes, target-only delayed RSCN, P2P loopback and winner/loser paths, and fabric shutdown while attach is pending.
