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
