# subset-b-007033 gRPC gateway and server research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwInterface.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcRestGwInterface.cc

## Purpose
`GrpcRestGwInterface.cc` implements the REST gateway command bridge compiled under `EOS_GRPC_GATEWAY`. It accepts individual REST gateway protobuf command messages, wraps them where useful into `eos::console::RequestProto`, and executes the corresponding EOS MGM command path. The file is the command translation layer behind `GrpcRestGwServer.cc`: the server authenticates or maps the request into a `VirtualIdentity`, then this interface runs the requested EOS console/admin operation and fills a `ReplyProto`.

## Important APIs, types, and functions
The public methods are one method per REST-exposed EOS console command: `AclCall`, `AccessCall`, `ArchiveCall`, `AttrCall`, `BackupCall`, `ChmodCall`, `ChownCall`, `ConfigCall`, `ConvertCall`, `CpCall`, `DebugCall`, `EvictCall`, `FileCall`, `FileinfoCall`, `FindCall`, `FsCall`, `FsckCall`, `GeoschedCall`, `GroupCall`, `HealthCall`, `IoCall`, `LsCall`, `MapCall`, `MemberCall`, `MkdirCall`, `MvCall`, `NodeCall`, `NsCall`, `QuotaCall`, `RecycleCall`, `RmCall`, `RmdirCall`, `RouteCall`, `SpaceCall`, `StatCall`, `StatusCall`, `TokenCall`, `TouchCall`, `VersionCall`, `VidCall`, `WhoCall`, and `WhoamiCall`. Streaming commands use `grpc::ServerWriter<ReplyProto>` for `FindCall`, `FsckCall`, and `LsCall`.

`ExecProcCmd(VirtualIdentity&, ReplyProto*, std::string, bool admin)` is the common helper for string-built proc requests. It opens either `/proc/admin` or `/proc/user` through `ProcCommand`, captures stdout/stderr/retc, and maps that back to `ReplyProto`. The file also defines `FileHelper_EnvFstToFmd`, `FileHelper_GetRemoteAttribute`, and `FileHelper_GetRemoteFmdFromLocalDb` for the `file check` path that compares namespace metadata, FST stat data, xattrs, and local FST FMD.

## Control flow
Most command handlers follow one of three paths. The simplest path logs a JSON representation of the protobuf request, wraps it into `RequestProto`, constructs the existing MGM command object, and calls `ProcessRequest()`; examples include ACL, access, config, convert, debug, fs, group, io, node, ns, quota, recycle, route, token, and rm. A second path manually translates protobuf fields into proc query strings such as `mgm.cmd=file&mgm.subcmd=...`; examples include archive, attr, chmod, chown, map, mkdir, rmdir, touch, version, vid, who, and whoami. A third path performs direct side effects or external queries before returning: `CpCall` uses XRootD checksum/stat/opaque queries, `FileCall` contains a large `FileProto::FileCommand_case()` switch, `GeoschedCall` invokes `gOFS->mGeoTreeEngine`, `HealthCall` runs `HealthCommand`, `StatusCall` runs `popen("eos-status")`, and `StatCall` uses `XrdPosixXrootd::Stat`.

Path resolution is repeated in many handlers. If a request supplies metadata id/inode but no path, the implementation uses `gOFS->eosViewRWMutex`, `eosFileService`, `eosDirectoryService`, and `eosView->getUri()` to recover a namespace path. Failures are reported in the `ReplyProto` with `EINVAL` or the captured errno. Streaming `LsCall` runs `mgm.cmd=ls`, then batches every 100 output lines into a streaming reply; WNC-flavored listing supplements entries with size, mtime, and selected xattrs by reading namespace metadata directly.

`FileCall` is the highest-risk branch. It translates many file subcommands to `/proc/user` (`adjustreplica`, `convert`, `copy`, `drop`, `layout`, `move`, `purge`, `replicate`, `tag`, `verify`, `version`, `versions`, `share`, `workflow`), handles `resync` through `gOFS->QueryResync`, handles symlinks through `gOFS->_symlink`, and implements `check` by first asking MGM for replica locations and then querying each FST with XRootD. `VidCall` similarly builds one or two `/proc/admin` requests depending on whether both UID and GID mapping entries must be removed or changed.

## State and persistence behavior
The class itself is stateless across calls. Persistent effects happen through the called MGM command implementations, `/proc/admin` and `/proc/user` commands, `gOFS` services, `GeoTreeEngine`, `EgroupRefresh`, and XRootD/FST opaque requests. Some commands update namespace metadata (`chmod`, `chown`, `touch`, `mkdir`, file operations), scheduling configuration (`geosched` with `save_config = true`), VID mapping state, recycle/routing/token state, or file replica metadata. `StatusCall` depends on an external `eos-status` executable and does not persist state itself.

## Dependencies and integration points
The file integrates gRPC protobufs with the existing EOS console/MGM command stack. Key dependencies are `proto/eos_rest_gateway/eos_rest_gateway_service.grpc.pb.h`, `console::RequestProto` and `ReplyProto`, many `mgm/proc/admin/*Cmd` and `mgm/proc/user/*Cmd` classes, `ProcCommand`, `gOFS`, namespace interfaces, `Mapping`, `GeoTreeEngine`, `Egroup`, `HealthCommand`, `XrdCl`, `XrdPosixXrootd`, and protobuf JSON utilities for request logging. It is called only by the REST gateway service implementation in `GrpcRestGwServer.cc`.

## Risks and edge cases
Many proc command strings concatenate raw protobuf strings without URL escaping. Paths, keys, values, hosts, map patterns, VID patterns, and workflow/event values containing `&`, `=`, quotes, or control characters can change proc parameters or break parsing. The code has scattered validation for geotags and XRootD URLs, but not for most query-string fields.

The file logs complete request protobufs as JSON at info level. Depending on proto contents, this can expose paths, tokens, authorization headers converted into command fields, or administrative intent. `StatusCall` shells out via `popen("eos-status")`; the command string is constant, which limits injection risk, but availability and PATH/environment still matter.

`EvictCall` appears to call `req.mutable_debug()->CopyFrom(*evictRequest)` before constructing `EvictCmd`; that looks like a copy/paste type mismatch unless generated protobuf overloads make it impossible to compile. This should be verified because the intended field is likely `mutable_evict()`.

Several handlers use root identity for read-style commands (`FileinfoCall`, `WhoCall`, `WhoamiCall`) or direct root-like internal lookups; authorization relies on downstream command behavior and the identity supplied by `GrpcRestGwServer::Vid`. The long `file check` path allocates and deletes raw pointers in several error paths; early returns after allocating `newresult` or XRootD responses deserve leak/regression tests. There is also substantial duplicated logic with `GrpcWncInterface.cc`, so fixes can easily land in one gateway and not the other.

## Test signals
Useful tests would exercise each command translation by asserting the generated proc command or the called command object for representative protobufs. Security tests should cover path/value fields containing `&` and `=`, non-path metadata id resolution failures, geotag sanitization, REST request logging redaction expectations, and privilege behavior for VID/geosched/member commands. Integration tests need an MGM test fixture for `ProcCommand` paths, streaming `find/fsck/ls`, WNC-style `fileinfo` and `ls`, and FST-backed `file check`. A focused regression test should cover `EvictCall` dispatch and `TouchCall` parent creation retry.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcRestGwInterface.cc -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcServer.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcServer.cc

## Purpose
`GrpcServer.cc` implements the main EOS MGM gRPC service under `EOS_GRPC`. It exposes namespace RPCs, command execution, ping, and traffic-shaping monitoring, and maps gRPC authentication material into EOS `VirtualIdentity` objects.

## Important APIs, types, and functions
`RequestServiceImpl` derives from generated `eos::rpc::Eos::Service`. It implements `Ping`, `FileInsert`, `ContainerInsert`, `MD`, `Find`, `NsStat`, `Exec`, and `TrafficShapingRate`. Namespace operations delegate to `GrpcNsInterface`. `TrafficShapingRate` streams `TrafficShapingRateResponse` reports built by `BuildTrafficShapingRateReport`.

Static helpers on `GrpcServer` are `DN`, `IP`, and `Vid`. `DN` reads x509 identity properties from the gRPC auth context. `IP` parses `context->peer()` into an IP address. `Vid` builds an `XrdSecEntity`, selects a non-secret tident (`DN`, `eostoken`, `grpc-key`, or `grpc-anon` plus peer data), optionally attaches the authkey as endorsements, and calls `Mapping::IdMap`.

`GrpcServer::Run` loads TLS material from `EOS_MGM_GRPC_SSL_CERT`, `EOS_MGM_GRPC_SSL_KEY`, and `EOS_MGM_GRPC_SSL_CA`, enforces TLS unless `EOS_MGM_GRPC_ALLOW_INSECURE` is present, configures gRPC credentials, registers the service, starts the server, and waits.

## Control flow
Each RPC logs peer/IP/DN, maps the caller to a `VirtualIdentity`, waits for MGM boot via `WAIT_BOOT` where needed, and delegates. `MD` switches on request type: file/container/stat use `GrpcNsInterface::Stat`, listing uses `GrpcNsInterface::StreamMD`, and unsupported types return `INVALID_ARGUMENT`. `TrafficShapingRate` maps without an auth key, requires root or sudoer, then loops until cancellation, emitting reports roughly every 100 ms.

Startup first attempts to load TLS files when all three TLS environment variables are set. Without TLS, startup is refused unless `EOS_MGM_GRPC_ALLOW_INSECURE` is set; insecure mode binds only `127.0.0.1`. TLS mode binds `0.0.0.0` and normally requires and verifies client certificates, unless `EOS_MGM_GRPC_DONT_REQUEST_CLIENT_CERTIFICATE` downgrades to token-only behavior. The service is registered and `mServer->Wait()` blocks until shutdown.

## State and persistence behavior
The server owns `mServer` and TLS strings. It does not persist data itself. RPCs can mutate namespace state through `GrpcNsInterface::{FileInsert,ContainerInsert,Exec}` and stream live monitoring state through traffic shaping. Identity mapping can depend on EOS mapping configuration and supplied auth keys/tokens.

## Dependencies and integration points
The file integrates generated `proto/Rpc.grpc.pb.h`, `GrpcNsInterface`, `Mapping`, `SymKey`, XRootD `XrdSecEntity`, `TrafficShaping`, gRPC reflection/credentials, and MGM boot macros. It relies on environment variables for transport security and on `Mapping::IdMap` for auth-to-VID conversion.

## Risks and edge cases
Transport security is central. The implementation now refuses public insecure binding unless explicitly allowed, and insecure mode is loopback-only. `EOS_MGM_GRPC_DONT_REQUEST_CLIENT_CERTIFICATE` is a deliberate downgrade and should be rare. `Vid` avoids logging raw auth keys by using a tident sentinel and only debug-level short fingerprints; regression tests should protect this because audit logs are otherwise a credential leakage vector.

`DN` looks for `x509_common_name` first and then SAN, despite the comment noting gRPC prioritization behavior; deployments relying on SAN identity should validate actual auth-context properties. `IP` parsing is duplicated with the REST server and can fail closed to an empty string for unexpected peer formats. `TrafficShapingRate` streams sensitive monitoring data and correctly requires admin/sudoer, but uses an empty authkey, so authorization is certificate/mapping driven only.

## Test signals
Unit tests should cover `DN`, `IP`, and `Vid` for mTLS, EOS token, SSS/shared-secret authkey, no auth, and malformed peer strings. Startup tests should verify TLS load failures, refusal without TLS, loopback-only insecure mode, and client-cert downgrade logging. RPC integration tests should cover MD type dispatch, namespace insert delegation, `Exec`, `Find`, and permission denial for `TrafficShapingRate`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcServer.cc -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncInterface.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcWncInterface.cc

## Purpose
`GrpcWncInterface.cc` implements the EOS Windows native client command bridge under `EOS_GRPC`. It receives `eos::console::RequestProto` messages from `GrpcWncServer.cc`, optionally switches the caller role, dispatches to command-specific handlers, and fills unary or streaming `ReplyProto` responses.

## Important APIs, types, and functions
The entry points are `ExecCmd(VirtualIdentity&, const RequestProto*, ReplyProto*)` for unary commands and `ExecStreamCmd(VirtualIdentity&, const RequestProto*, ServerWriter<ReplyProto>*)` for streaming `find` and `ls`. The object stores per-call pointers in `mVid`, `mRequest`, `mReply`, and `mWriter`, plus `mJsonFormat`.

`RoleChanger` applies requested UID/GID role changes from `request.auth().role()`, permitting roles already in `allowed_uids`/`allowed_gids` or any requested role for sudoers, otherwise dropping to uid/gid 99. `ExecProcCmd` appends `mgm.format=json` when needed, executes `/proc/admin` or `/proc/user`, and populates the reply, using `cmd.GetStdJson()` for JSON output. Command methods mirror the REST gateway implementation: `Access`, `Acl`, `Archive`, `Attr`, `Backup`, `Chmod`, `Chown`, `Config`, `Convert`, `Cp`, `Debug`, `Evict`, `File`, `Fileinfo`, `Find`, `Fs`, `Fsck`, `Geosched`, `Group`, `Health`, `Io`, `Ls`, `Map`, `Member`, `Mkdir`, `Mv`, `Node`, `Ns`, `Quota`, `Recycle`, `Rm`, `Rmdir`, `Route`, `Space`, `Stat`, `Status`, `Token`, `Touch`, `Version`, `Vid`, `Who`, and `Whoami`.

The file also defines `File_EnvFstToFmd`, `File_GetRemoteAttribute`, and `File_GetRemoteFmdFromLocalDb` for the file consistency check path.

## Control flow
`ExecCmd` stores call pointers, determines JSON mode, calls `RoleChanger`, then switches on `RequestProto::command_case()`. Some sensitive commands have extra checks: `Health` and `Vid` require root or selected allowed uid markers (`0`, `2`, or `3`) before dispatch. Unsupported commands return `EINVAL`. `ExecStreamCmd` follows the same setup but only dispatches `Find` and `Ls`.

Most handlers are equivalent to `GrpcRestGwInterface.cc` but read from `mRequest` and write to `mReply`. Some construct existing MGM command classes and call `ProcessRequest`; others build proc command strings. `File` contains the same large file subcommand switch and FST consistency-check logic as the REST interface. `Fileinfo`, `Member`, and `ExecProcCmd` add JSON-specific behavior for WNC clients. `Ls` streams output in batches of 100 lines and augments WNC listings with metadata from `gOFS->eosView`.

## State and persistence behavior
Unlike the REST interface, this class is stateful during a call through member pointers. It is instantiated per request in `GrpcWncServer.cc`, so there is no intended cross-request persistence. Persistent effects are delegated to MGM command classes, `/proc/admin`, `/proc/user`, `gOFS`, `GeoTreeEngine`, `EgroupRefresh`, namespace metadata services, and FST opaque queries. `RoleChanger` mutates the passed `VirtualIdentity` for the duration of downstream command execution.

## Dependencies and integration points
Dependencies include generated `proto/EosWnc.grpc.pb.h`, EOS console command classes, `ProcCommand`, JSON helpers, `HealthCommand`, `gOFS`, namespace interfaces, `Mapping`, `GeoTreeEngine`, `EgroupRefresh`, XRootD `XrdCl`, and `XrdPosixXrootd`. The file is called by `WncService` in `GrpcWncServer.cc`, while identity construction is shared with the main `GrpcServer::Vid`.

## Risks and edge cases
The same raw query-string concatenation risk exists here as in the REST interface. WNC adds `mgm.format=json` by appending to the query, so malformed values containing separators can affect both command parsing and output mode. `RoleChanger` falls back to uid/gid 99 on unauthorized role requests instead of failing immediately, which may be surprising and should be covered by tests. The allowed uid checks for `Health` and `Vid` use magic values `2` and `3`; their meaning is not local to this file.

The class stores request/reply/writer as mutable members, so it is not reentrant or thread-safe if reused concurrently. Current server code constructs a fresh instance per call, which is safe. There is heavy duplication with `GrpcRestGwInterface.cc`, including the long file-check helper logic, increasing divergence risk. As with REST, `Status` uses `popen("eos-status")`, and many handlers rely on downstream authorization.

## Test signals
Tests should verify dispatch for every `RequestProto::command_case()`, JSON output behavior, role switching for allowed, sudoer, and denied role requests, and permission behavior for `Health` and `Vid`. Regression tests should compare WNC and REST command translations for shared commands. Integration tests should exercise streaming `find`/`ls`, WNC `fileinfo` ACL enrichment, JSON `Member`, `Touch` parent retry, and file consistency checks against simulated FST responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncInterface.cc -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncServer.cc -->
# sources/distributed-fs/eos/mgm/grpc/GrpcWncServer.cc

## Purpose
`GrpcWncServer.cc` implements the embedded gRPC service for the EOS Windows native client under `EOS_GRPC`. It receives WNC protobuf requests, maps the gRPC peer/auth material to a `VirtualIdentity` through `GrpcServer`, waits for MGM boot, and delegates command execution to `GrpcWncInterface`.

## Important APIs, types, and functions
`WncService` derives from generated `EosWnc::Service`. It implements `ProcessSingle` for unary commands and `ProcessStream` for streaming commands. Both methods compute a human-readable command name for debug logging, call `GrpcServer::IP`, `GrpcServer::DN`, and `GrpcServer::Vid`, then instantiate `GrpcWncInterface` and call `ExecCmd` or `ExecStreamCmd`.

`GrpcWncServer::RunWnc` loads optional TLS material from `EOS_MGM_WNC_SSL_CERT`, `EOS_MGM_WNC_SSL_KEY`, and `EOS_MGM_WNC_SSL_CA`, initializes `gGlobalOpts.mMgmUri`, configures the gRPC `ServerBuilder`, registers `WncService`, starts `mWncServer`, and waits.

## Control flow
For unary requests, `ProcessSingle` maps the protobuf oneof command case to a string used only for logging, logs peer/IP/DN/command/token length, maps identity using the request authkey, waits for boot, then delegates to `GrpcWncInterface::ExecCmd`. For streaming requests, `ProcessStream` only distinguishes `Find` and `Ls` for logging and delegates to `ExecStreamCmd`.

Startup optionally enables TLS if all WNC TLS environment variables are present. TLS mode uses `GRPC_SSL_REQUEST_CLIENT_CERTIFICATE_AND_VERIFY`; otherwise the server binds `0.0.0.0:<mWncPort>` with `grpc::InsecureServerCredentials()`. The server waits indefinitely until shutdown.

## State and persistence behavior
The server owns `mWncServer` and blocks inside `Wait()`. It sets global console option `gGlobalOpts.mMgmUri` from `EOS_MGM_URL` or `root://localhost` when empty. It does not persist WNC command state itself; all command side effects are delegated to `GrpcWncInterface`.

## Dependencies and integration points
The file depends on generated `proto/EosWnc.grpc.pb.h`, `GrpcWncInterface`, `GrpcServer` identity helpers, `ConsoleMain` global options, MGM boot macros, EOS logging, and gRPC credentials. It reuses the main gRPC identity mapping implementation rather than duplicating DN/IP/authkey handling.

## Risks and edge cases
Unlike `GrpcServer::Run`, insecure WNC mode binds to `0.0.0.0`, exposing the service on all interfaces if TLS env vars are missing. That is a major deployment risk unless external network controls are guaranteed. Debug logging avoids printing the auth key and logs only token length, which is good. Command name mapping is duplicated and incomplete for stream/unary cases; unknown commands still flow to the interface where they may return unsupported.

TLS file load checks set `mSSL = false` if a file load fails, which silently falls back to insecure all-interface binding later. That should probably fail closed. `gGlobalOpts.mMgmUri` mutation is process-global and can affect other console-command behavior.

## Test signals
Startup tests should cover TLS success, TLS file load failure, insecure binding address, and default MGM URI initialization. Security tests should assert whether insecure all-interface binding is intended; if not, add a regression test for loopback-only or fail-closed behavior. Request tests should verify identity mapping receives the authkey, `WAIT_BOOT` precedes execution, and stream/unary dispatch reaches `GrpcWncInterface`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/eos/mgm/grpc/GrpcWncServer.cc -->

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
