# sources/distributed-fs/ceph-client/drivers/scsi/elx/libefc/efc_device.h

## Purpose
`efc_device.h` exposes the remote device node state-machine entry points and helper functions used by node dispatch, fabric/P2P flows, and device login handling.

## Important APIs, Types, And Functions
The header declares `efc_node_init_device`, PRLI processing, deferred PRLI response, deferred LS_ACC setup, and all `__efc_d_*` state functions for loop waiting, PLOGI handling, domain/topology/node attach waits, shutdown, logged-in, ready, gone, ADISC wait, and LOGO wait.

## Control Flow And State
The declarations reveal the main state chain: init, wait for login response or inbound login, wait for domain/topology/attach, transition to logged-in/ready, and route shutdown through attach-wait, delete, ELS quiesce, node-free, and I/O-drain states. The header itself holds no data but assumes `struct efc_node` fields in `efclib.h` carry the mutable login and shutdown state.

## Dependencies And Integration Points
It depends on `struct efc_sm_ctx`, `enum efc_sm_event`, `struct efc_node`, and FC frame headers from the umbrella include path. Fabric code calls device helpers for P2P PRLI acceptance and topology integration.

## Risks And Test Signals
Risks are interface-level: all state handlers share the same callback signature, so mismatched events or callback payload types can compile but fail at runtime. Test signals are state traces entering every declared `__efc_d_*` handler, plus login/shutdown scenarios that confirm the headers and implementations stay synchronized.
