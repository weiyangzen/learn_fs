# sources/distributed-fs/ceph-client/net/ipv4/udp_tunnel_stub.c

## Purpose
This tiny file defines and exports the global `udp_tunnel_nic_ops` indirection used by UDP tunnel code and NIC offload management.

## Important APIs, Types, and Functions
The only symbol is `const struct udp_tunnel_nic_ops *udp_tunnel_nic_ops`, exported GPL. The concrete ops table is installed by `udp_tunnel_nic.c` at late init and cleared at module exit.

## Control Flow
There is no runtime control flow beyond external modules reading or assigning the pointer under their own synchronization, normally RTNL in the NIC manager.

## State and Persistence Behavior
The pointer is process-global kernel state. NULL means no UDP tunnel NIC offload manager is registered; non-NULL points to the active ops.

## Dependencies and Integration Points
It depends on `net/udp_tunnel.h` for the ops type and allows tunnel core code to compile independently from the NIC manager implementation.

## Risks
Consumers must tolerate NULL and must synchronize against updates. Misordered module exit could expose stale ops if users do not follow the RTNL/registration contract.

## Test Signals
Build with UDP tunnel NIC support as built-in and modular, verify ops are NULL before init and cleared on exit, and confirm tunnel drivers handle absent ops.
