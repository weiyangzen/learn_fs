<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncInterface.hh -->
# sources/distributed-fs/eos/mgm/grpc/GrpcWncInterface.hh

## Purpose
`GrpcWncInterface.hh` declares the command bridge used by the EOS Windows native client gRPC service. It exposes a compact public API that accepts a full `RequestProto` and dispatches internally to command-specific private methods.

## Important APIs, types, and functions
The public entry points are `ExecCmd` for unary commands and `ExecStreamCmd` for streaming commands. Private state includes `mJsonFormat`, pointers to the active `VirtualIdentity`, request, reply, and stream writer. Private helpers are `RoleChanger` and `ExecProcCmd`. The private command methods cover the same broad EOS command set exposed to WNC clients.

## Control flow
The header establishes a stateful dispatch pattern: `ExecCmd`/`ExecStreamCmd` set member pointers, then private methods read the current request and write the current reply/writer. The command methods are not externally callable, so the switch in `ExecCmd` is the central dispatch table.

## State and persistence behavior
The class holds per-call state but does not own it. It should be treated as single-use or at least single-call-at-a-time. Persistent state changes happen in the implementation through MGM commands and services, not through members declared here.

## Dependencies and integration points
The header is compiled under `EOS_GRPC` and includes `VirtualIdentity`, namespace macros, and generated WNC protobuf/gRPC definitions. It uses `grpc::ServerWriter` for streaming replies. `GrpcWncServer.cc` is the primary caller.

## Risks and edge cases
Because request, reply, writer, and identity are raw pointers stored on the object, null pointer safety and object lifetime depend on disciplined caller behavior. The class is not thread-safe if reused. The large private method list must stay synchronized with `RequestProto` command cases and the `.cc` dispatch switch.

## Test signals
Build tests should compile with `EOS_GRPC` enabled/disabled. API tests should confirm `ExecCmd` handles unary command cases and `ExecStreamCmd` handles only stream command cases. Static analysis should flag accidental object reuse across threads or calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncInterface.hh -->
