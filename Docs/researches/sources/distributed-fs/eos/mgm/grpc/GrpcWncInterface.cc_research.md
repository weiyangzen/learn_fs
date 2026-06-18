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
