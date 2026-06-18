# sources/distributed-fs/ceph-client/net/rds/Makefile

## Purpose
The Makefile defines RDS core, RDMA transport, and TCP transport object composition.

## Important APIs, Types, And Functions
`rds.o` includes core socket, bind, congestion, connection, info, message, receive, send, stats, sysctl, thread, transport, loopback, page, and RDMA helper objects. `rds_rdma.o` includes RDMA transport, IB CM/send/recv/ring/stats/sysctl/RDMA/FRMR pieces. `rds_tcp.o` includes TCP transport implementation files. `ccflags-$(CONFIG_RDS_DEBUG)` adds `-DRDS_DEBUG`; `CONFIG_GCOV_PROFILE_RDS` enables gcov.

## Control Flow
No runtime flow exists, but link composition determines initialization ordering through module init calls in the object files.

## State And Persistence
The file affects build artifacts only.

## Dependencies And Integration Points
Core RDS exports transport registration APIs consumed by `rds_rdma` and `rds_tcp`. RDMA object composition shows `ib_frmr.o` and `ib_mr.h` belong to memory-registration support.

## Risks
Object omissions or modular dependency issues can break transport registration. Debug/gcov flags may alter performance and coverage behavior.

## Test Signals
Build tests should verify all configured object groups link, RDS debug builds compile, gcov flag propagation works, and modular transports resolve core symbols.
