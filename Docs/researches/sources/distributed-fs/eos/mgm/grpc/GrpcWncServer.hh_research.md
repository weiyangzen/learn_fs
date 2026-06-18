<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncServer.hh -->
# sources/distributed-fs/eos/mgm/grpc/GrpcWncServer.hh

## Purpose
`GrpcWncServer.hh` declares the server wrapper for the EOS Windows native client gRPC service. It owns port/TLS configuration, the assisted server thread, and the gRPC server pointer.

## Important APIs, types, and functions
`GrpcWncServer(int port = 50052)` sets the WNC gRPC port and starts with SSL disabled. `RunWnc(ThreadAssistant&)` starts and waits on the gRPC service. `StartWnc()` launches `RunWnc` in the `AssistedThread`. The destructor logs shutdown, calls `mWncServer->Shutdown()` when available, and joins the thread.

## Control flow
The owner constructs `GrpcWncServer`, calls `StartWnc`, and later destroys it to shut down the server. The implementation in `.cc` performs the blocking server wait and handles optional TLS setup.

## State and persistence behavior
Members include `mWncPort`, SSL flags and loaded certificate/key/CA strings and paths, an `AssistedThread`, and `std::unique_ptr<grpc::Server>` under `EOS_GRPC`. There is no durable state in the wrapper.

## Dependencies and integration points
The header includes MGM namespace macros, `AssistedThread`, logging, and `GrpcWncInterface`. It conditionally includes gRPC headers under `EOS_GRPC`. The class is embedded in the MGM lifecycle alongside the main gRPC server and REST gateway server.

## Risks and edge cases
The destructor joins after shutdown; if `RunWnc` is blocked before assigning `mWncServer` or outside `Server::Wait()`, destruction can hang. TLS configuration is environment-driven in the implementation, not through constructor arguments. Copy/move semantics are not explicitly deleted even though the class owns a thread/server resource.

## Test signals
Build tests should cover `EOS_GRPC` enabled/disabled. Lifecycle tests should verify start, shutdown, and destruction. Configuration tests should validate the default port and TLS member behavior through `RunWnc` integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncServer.hh -->
