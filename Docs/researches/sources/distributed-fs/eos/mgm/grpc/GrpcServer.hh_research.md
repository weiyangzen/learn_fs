<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcServer.hh -->
# sources/distributed-fs/eos/mgm/grpc/GrpcServer.hh

## Purpose
`GrpcServer.hh` declares the main embedded EOS MGM gRPC server wrapper. It owns runtime configuration, TLS material, the gRPC server instance, the server thread, and a traffic shaping manager pointer used by the service implementation.

## Important APIs, types, and functions
The constructor defaults the service port to `50051` and starts with SSL disabled. `Start()` runs `Run(ThreadAssistant&)` in an `AssistedThread`. The destructor shuts down `mServer` when `EOS_GRPC` is enabled and joins the thread. Static helper declarations under `EOS_GRPC` expose `DN`, `IP`, and `Vid` for request identity mapping.

## Control flow
The owner creates `GrpcServer`, calls `Start()`, and later destroys it or otherwise triggers shutdown. `Run` performs blocking startup and wait. Request methods in `GrpcServer.cc` use the static helper functions rather than storing per-request state in the server wrapper.

## State and persistence behavior
Members store the configured port, TLS enabled flag, loaded certificate/key/CA contents and filenames, a `std::unique_ptr<grpc::Server>`, the assisted thread, and a shared `TrafficShapingManager`. No durable persistence is owned here.

## Dependencies and integration points
The header depends on `AssistedThread`, `Mapping`, MGM namespace macros, and `mgm/shaping/TrafficShaping.hh`. gRPC types are visible only under `EOS_GRPC`. The object is intended to be embedded into the MGM process lifecycle.

## Risks and edge cases
The class has thread/server ownership and should not be copied; this is probably prevented by non-copyable members but is not explicitly documented with deleted copy/move operations. TLS configuration is environment-driven in the `.cc`, so constructor arguments only select the port. The traffic shaping manager member is declared but not visibly initialized in this file; service code relies on global/helper functions instead.

## Test signals
Build tests should compile with and without `EOS_GRPC`. Lifecycle tests should cover startup/shutdown/destruction without hanging. API tests should check that static helper signatures stay compatible with service code and that default port behavior remains stable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcServer.hh -->
