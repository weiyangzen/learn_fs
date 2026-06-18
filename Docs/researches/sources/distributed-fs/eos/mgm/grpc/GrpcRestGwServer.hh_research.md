<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwServer.hh -->
# sources/distributed-fs/eos/mgm/grpc/GrpcRestGwServer.hh

## Purpose
`GrpcRestGwServer.hh` declares the embedded REST gateway server wrapper. It owns the assisted thread and gRPC server instance used to expose EOS console commands through an HTTP REST gateway backed by a loopback gRPC service.

## Important APIs, types, and functions
`GrpcRestGwServer` derives from `LogId`. Under `EOS_GRPC_GATEWAY`, it declares static helpers `IP(grpc::ServerContext*, std::string*, std::string*)` and `Vid(grpc::ServerContext*, VirtualIdentity&)`. The constructor defaults the internal gRPC gateway port to `50054`; the HTTP gateway port member defaults to `40054`. `Run(ThreadAssistant&)` performs server startup and blocking wait. `Start()` launches `Run` on `AssistedThread`. The destructor shuts down `mRestGwServer` if present and joins the thread.

## Control flow
Callers construct `GrpcRestGwServer`, optionally with a gRPC port, then call `Start()`. `Start()` resets the assisted thread to execute `Run`. Destruction requests gRPC shutdown before joining the thread, so `Run` must be blocked in `Server::Wait()` or otherwise responsive to shutdown.

## State and persistence behavior
The class holds runtime configuration (`mHttpGwPort`, `mGrpcGwPort`, unused SSL fields), the `AssistedThread`, and a `std::unique_ptr<grpc::Server>`. It has no persistent storage. Command effects are delegated to the service implementation and interface layer.

## Dependencies and integration points
The header includes namespace macros, assisted threading, mapping/logging helpers, and `GrpcRestGwInterface`. gRPC headers and the server pointer are compiled only with `EOS_GRPC_GATEWAY`. Lifecycle integration is with the MGM process that owns this object and starts/stops the assisted thread.

## Risks and edge cases
Only the gRPC port is configurable through the constructor; the HTTP gateway port is fixed at `40054` unless modified internally. SSL fields are present but unused by the `.cc`, which can mislead operators or future maintainers. The destructor joins unconditionally after shutdown; if `Run` is blocked outside `mRestGwServer->Wait()` or gateway shutdown handling, destruction can hang. Copy/move behavior is not explicitly deleted even though the class owns a thread and server pointer; accidental copying is likely prevented by members but not made explicit.

## Test signals
Build tests should cover `EOS_GRPC_GATEWAY` enabled/disabled. Lifecycle tests should instantiate, start, shutdown, and destroy without hanging. Configuration tests should confirm selected ports and loopback binding. Static helper tests belong with the `.cc` implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwServer.hh -->
