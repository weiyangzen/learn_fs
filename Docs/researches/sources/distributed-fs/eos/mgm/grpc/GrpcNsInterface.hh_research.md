# sources/distributed-fs/eos/mgm/grpc/GrpcNsInterface.hh

## Purpose
Declares the static gRPC namespace interface class used by the MGM gRPC server to expose namespace metadata and command operations.

## Important APIs, types, and functions
`GrpcNsInterface` declares filtering for files and containers, metadata methods (`GetMD`, `Stat`, `StreamMD`, `Find`, `NsStat`), sudo-only insert APIs, generic command dispatch (`Exec`), individual namespace command handlers, recycle handlers, ACL/token/quota handlers, and `Access()` for permission checks.

## Control flow
The class is a stateless static facade. Server handlers pass a `VirtualIdentity`, request protobuf, and response/writer object. The implementation performs identity remapping, permission checks, namespace locking, and command delegation.

## State and persistence
The header stores no state. It declares methods that can read and mutate namespace state, quota state, ACL/xattr metadata, recycle state, and process stats through the implementation.

## Dependencies and integration points
Guarded by `EOS_GRPC`, it includes identity mapping, logging, MGM namespace macros, namespace metadata interfaces, `GrpcServer.hh`, generated `Rpc.grpc.pb.h`, and gRPC C++ headers.

## Risks and test signals
Because every method is static, test isolation depends on controlling global `gOFS` and namespace services. Tests should validate method dispatch, compile guards, protobuf compatibility, and permission behavior at the public API boundary.
