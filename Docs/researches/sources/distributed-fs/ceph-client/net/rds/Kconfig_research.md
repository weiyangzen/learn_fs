# sources/distributed-fs/ceph-client/net/rds/Kconfig

## Purpose
This Kconfig file declares Reliable Datagram Sockets core and transport options. RDS provides reliable sequenced datagram delivery over InfiniBand/RDMA or TCP.

## Important APIs, Types, And Functions
Symbols are `RDS`, `RDS_RDMA`, `RDS_TCP`, `RDS_DEBUG`, and `GCOV_PROFILE_RDS`. `RDS` depends on `INET`; `RDS_RDMA` depends on RDS, InfiniBand, and InfiniBand address translation; `RDS_TCP` depends on RDS and has an IPv6 compatibility dependency; debug and gcov options affect instrumentation.

## Control Flow
No runtime control flow exists here. Configuration controls object selection in the RDS Makefile and whether debug/gcov flags are added.

## State And Persistence
The file affects kernel build configuration only.

## Dependencies And Integration Points
`RDS_RDMA` enables the RDMA-capable transport implemented by the `ib*` and `rdma_transport` files. `RDS_TCP` enables the TCP transport. The core can be built without either transport but then cannot communicate unless transports are loaded separately.

## Risks
Selecting RDS without transports can surprise users at runtime. RDMA support is intentionally gated by InfiniBand and address-translation support. Debug flags change compiled logging behavior.

## Test Signals
Build tests should cover core-only, TCP-only, RDMA-only, combined transports, module/built-in combinations, debug builds, and gcov profile builds.
