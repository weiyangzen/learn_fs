# sources/distributed-fs/ceph-client/net/rds/loop.h

## Purpose
`loop.h` declares the loopback transport object and lifecycle functions used by the RDS core during module and network-namespace setup/teardown.

## Important APIs, Types, and Functions
The header exports `rds_loop_transport`, `rds_loop_net_init()`, `rds_loop_net_exit()`, and `rds_loop_exit()`. It does not define transport internals; those remain private to `loop.c`.

## Control Flow
Core initialization can register per-net operations with `rds_loop_net_init()`, use `rds_loop_transport` when loopback is preferred, and call `rds_loop_exit()`/`rds_loop_net_exit()` during teardown.

## State and Persistence
No state is stored in the header. State lives in `loop.c` globals and per-connection private allocations.

## Dependencies and Integration Points
Consumers include RDS initialization/transport selection code. The declared transport has type `RDS_TRANS_LOOP` and uses the generic `struct rds_transport` shape from `rds.h`.

## Risks
The header is intentionally minimal; the main risk is lifecycle ordering. Calls to `rds_loop_exit()` should occur after new loopback connection creation has stopped.

## Test Signals
Build coverage should ensure declarations match definitions. Runtime coverage should validate loopback transport registration and namespace cleanup.
