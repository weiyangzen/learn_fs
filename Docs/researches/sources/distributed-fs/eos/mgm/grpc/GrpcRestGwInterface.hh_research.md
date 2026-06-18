<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwInterface.hh -->
# sources/distributed-fs/eos/mgm/grpc/GrpcRestGwInterface.hh

## Purpose
`GrpcRestGwInterface.hh` declares the REST gateway command bridge class under `EOS_GRPC_GATEWAY`. It exposes a typed C++ method for each REST gateway protobuf endpoint and hides the fallback proc-command execution helper used by the implementation.

## Important APIs, types, and functions
`GrpcRestGwInterface` derives from `eos::common::LogId`. Its public API accepts a mutable `VirtualIdentity&`, a command-specific protobuf pointer, and either a `ReplyProto*` or `ServerWriter<ReplyProto>*`. The method list mirrors the REST gateway service surface: ACL, access, archive, attr, backup, chmod, chown, config, convert, copy helpers, debug, evict, file, fileinfo, find, fs, fsck, geosched, group, health, io, ls, map, member, mkdir, move, node, namespace, quota, recycle, rm, rmdir, route, space, stat, status, token, touch, version, vid, who, and whoami.

The private `ExecProcCmd` method centralizes `/proc/admin` versus `/proc/user` execution for handlers that are not implemented through dedicated `*Cmd` classes.

## Control flow
The header defines no runtime control flow, but it establishes the dispatch contract used by `GrpcRestGwServer.cc`: for each incoming gRPC method, the server constructs a `VirtualIdentity`, creates a short-lived `GrpcRestGwInterface`, and calls the matching `*Call` method. Streaming methods are identifiable from their `ServerWriter` argument.

## State and persistence behavior
The class declares no member variables, so instances are intended to be short-lived and stateless. State changes are performed by implementation calls into MGM command classes, `ProcCommand`, `gOFS`, or other services. The `VirtualIdentity&` parameter is supplied by the caller and is not owned by the interface.

## Dependencies and integration points
The header depends on EOS namespace macros, logging, virtual identities, and the generated REST gateway protobuf service header. It also imports a large number of protobuf command types with `using` declarations. The compile guard means no declarations are emitted unless REST gateway support is enabled.

## Risks and edge cases
The public surface is wide and easy to desynchronize from the protobuf service implementation or from `GrpcWncInterface`. Any new REST endpoint requires updates in generated protobufs, this header, the `.cc` implementation, and the server dispatch class. The header uses global `using` declarations in a header file, which can pollute includers when `EOS_GRPC_GATEWAY` is enabled. Duplicate `using eos::console::ConfigProto;` appears twice and is harmless but suggests manual maintenance.

## Test signals
Build coverage should compile with `EOS_GRPC_GATEWAY` both enabled and disabled. Interface/API tests should verify every service method in `GrpcRestGwServer.cc` has a corresponding declared and defined `GrpcRestGwInterface` method with the expected streaming or unary signature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwInterface.hh -->
