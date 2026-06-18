<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwServer.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcRestGwServer.cc

## Purpose
`GrpcRestGwServer.cc` implements the embedded REST gateway gRPC server under `EOS_GRPC_GATEWAY`. It binds an internal gRPC service and spawns an HTTP-to-gRPC gateway sidecar, mapping REST-originated calls to `GrpcRestGwInterface` command handlers.

## Important APIs, types, and functions
`GrpcRestGwServer::IP` decodes `ServerContext::peer()` into an address, with special handling for bracketed IPv6 peers. `GrpcRestGwServer::Vid` builds a `VirtualIdentity` from gRPC metadata headers (`client-name`, `client-tident`, `client-authorization`) after ensuring the peer is loopback. `EosRestGatewayServiceImpl` derives from the generated `EosRestGatewayService::Service` and implements one method per REST command, each creating a `VirtualIdentity`, constructing `GrpcRestGwInterface`, and delegating to the matching interface method. `GrpcRestGwServer::Run` creates the gRPC server, registers reflection, registers the service, binds loopback, spawns the HTTP gateway through `SpawnGrpcGateway`, and waits for shutdown.

## Control flow
At startup, `Run` logs that the REST gateway server is insecure and loopback-only, constructs the service, initializes reflection, and binds the gRPC listener to `127.0.0.1:<mGrpcGwPort>` using `grpc::InsecureServerCredentials()`. It also builds the HTTP gateway address `127.0.0.1:<mHttpGwPort>`, calls `SpawnGrpcGateway(http_addr, "tcp", grpc_addr, path)`, then waits on `mRestGwServer`. After the gRPC server exits, it waits for the gateway process or handle with `WaitForGrpcGateway`.

Per request, the service method path is uniform: `Vid(context, vid)` maps the caller, then a local `GrpcRestGwInterface` handles the command. Streaming methods (`FindRequest`, `FsckRequest`, `LsRequest`) pass the `ServerWriter` through.

## State and persistence behavior
The server stores its `grpc::Server` in `mRestGwServer`, managed by `GrpcRestGwServer.hh` destruction. It does not persist application data itself. It does create a long-running HTTP gateway companion and exposes the command surface to whatever can reach the loopback ports. Request state is transient, except for command side effects performed by `GrpcRestGwInterface`.

## Dependencies and integration points
The file depends on generated REST gateway protobuf service code, `EosGrpcGateway.h` for spawning and waiting on the HTTP gateway, `GrpcRestGwInterface`, gRPC reflection, gRPC credentials, EOS logging and string conversion, XRootD security entities, and `Mapping::IdMap`. The identity mapping is tightly coupled to XRootD `XrdSecEntity` semantics.

## Risks and edge cases
The REST gateway transport is explicitly unauthenticated and relies on loopback binding plus trusted metadata headers. `Vid` refuses non-loopback peers and falls back to `VirtualIdentity::Nobody`, which is an important security control; tests should ensure IPv4, IPv6, and IPv4-mapped IPv6 loopback formats are accepted and other peers are rejected. If a deployment exposes loopback through a proxy or container network incorrectly, the metadata headers become an impersonation mechanism.

`Vid` synthesizes a non-null tident if the metadata header is absent to avoid `Mapping::IdMap` crashes. That is a stability fix, but the authorization model still depends on optional metadata supplied by the local gateway. `Run` has a logging format issue: the message contains `grpc_port=i` instead of a `%i` placeholder, so the logged gRPC port may be wrong. The hard-coded gateway proto path `../../../../protos/examplepb` is fragile relative to working directory/install layout. `mSSL` and SSL fields exist in the class but are not used here; the implementation always binds insecure loopback.

## Test signals
Tests should cover `IP` parsing for IPv4, IPv6, malformed peers, and curl-escaped values. Unit tests around `Vid` should verify loopback-only metadata trust, fallback to nobody on remote peers, non-null tident synthesis, metadata mapping, and endorsement forwarding. Startup tests should verify loopback binding, gateway spawn arguments, graceful shutdown, and behavior when `BuildAndStart()` fails. Service dispatch tests can mock `GrpcRestGwInterface` or inspect that each generated RPC delegates to the intended `*Call`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwServer.cc -->
