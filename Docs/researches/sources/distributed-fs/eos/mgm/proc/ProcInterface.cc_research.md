# Research: sources/distributed-fs/eos/mgm/proc/ProcInterface.cc

## Purpose

`ProcInterface.cc` implements the MGM proc-command factory, protobuf dispatcher, async command parking map, write-access classifier, and authorization predicates. It is the bridge between XRootD `/proc/...` access and either legacy `ProcCommand` objects or newer protobuf command handler classes such as `FsCmd`, `AccessCmd`, `ConvertCmd`, and `FileRegisterCmd`.

## Important APIs, Types, and Functions

- Static state includes `mMutexCmds`, `mMapCmds`, `mCmdToDel`, thread-local `tlLogId`, and `sProcThreads`.
- `GetProcCommand()` returns a previously submitted async command, a protobuf handler, or a legacy `ProcCommand`.
- `GetSubmittedCmd()`, `SaveSubmittedCmd()`, and `DropSubmittedCmd()` manage per-client async commands by `tident`.
- `HandleProtobufRequest(const char*, vid)` base64-decodes and deserializes `mgm.cmd.proto`, then delegates to `HandleProtobufRequest(RequestProto&, vid)`.
- `HandleProtobufRequest(RequestProto&, vid)` logs the request, enforces admin gating for admin-only command cases, and constructs the concrete handler class.
- `ProtoIsWriteAccess()` parses a protobuf request and classifies whether it modifies MGM/namespace state.
- `IsProcAccess()`, `IsWriteAccess()`, `Authorize()`, `VidIsAdmin()`, and `IsAdminCmd()` implement path detection, write classification, and access control.

## Control Flow

`GetProcCommand()` first installs a thread-local log id for the current user and connection. It then checks `mMapCmds` for a completed/stalled async command belonging to the same `tident`. If no command exists and the caller lacks a path or opaque string, it returns a legacy `ProcCommand`. Otherwise it parses the opaque CGI environment; if `mgm.cmd.proto` exists, it dispatches to protobuf handling, otherwise it also returns legacy `ProcCommand`.

The protobuf path decodes base64, parses `RequestProto`, logs the JSON representation, checks `IsAdminCmd(req.command_case()) && !VidIsAdmin(vid)`, and returns null on refusal. The dispatcher then switches over `RequestProto::CommandCase` and constructs the matching command object. User-callable commands include ACL/find/rm/df/token/evict/route/recycle/quota; admin-only commands include filesystem, namespace, space, node, group, config, access, IO, scheduler, devices, monit, record/register, fsck, debug, and convert.

Write detection has separate paths. Protobuf requests are parsed and classified by command/subcommand. Legacy CGI requests are classified by `mgm.cmd` and `mgm.subcmd` string lists. `Authorize()` gates legacy `/proc/admin/` by `VidIsAdmin()` and allows `/proc/user/`.

## State and Persistence Behavior

The interface stores live/completed async command objects in static containers protected by `mMutexCmds`. `DropSubmittedCmd()` tries to kill orphaned commands; commands that cannot be killed immediately move to `mCmdToDel` and are retried later. The thread pool is a static MGM-wide execution resource sized from hardware concurrency with minimum/maximum values.

No namespace or config state is persisted here. Persistence is delegated to handler classes. Security state is derived from `VirtualIdentity`, `XrdSecEntity`, and constants such as daemon/admin uid/gid.

## Dependencies and Integration Points

This file includes every protobuf command handler it can construct, user handlers (`AclCmd`, `DfCmd`, `NewfindCmd`, `RecycleCmd`, `RmCmd`, `RouteCmd`, `TokenCmd`), admin handlers (`FsCmd`, `NsCmd`, `SpaceCmd`, `AccessCmd`, `FileRegisterCmd`, etc.), `SymKey` base64 helpers, protobuf JSON conversion, XRootD CGI parsing, and common constants. It is called from proc filesystem access code and supplies the shared `sProcThreads` pool used by long-running commands.

## Risks and Edge Cases

- Admin security depends on `IsAdminCmd()` staying in sync with future `RequestProto` command cases. The default is closed, which is safe but may break newly added user commands until classified.
- `ProtoIsWriteAccess()` parses the same protobuf later parsed again by command dispatch, which is noted as a TODO and can create duplicated parse cost or inconsistent error handling.
- Legacy write classification is a manual string list and can miss newer state-changing CGI commands.
- `ProtoIsWriteAccess()` returns false for all access-control commands so global stalls/write bans can still be removed; that intentional exception is security-sensitive.
- `DropSubmittedCmd()` keeps non-killable commands in a cleanup list; handlers must implement `KillJob()` correctly to avoid accumulating dead commands.

## Test Signals

Tests should cover protobuf base64 parse failures, unknown command cases, admin refusal for admin-only protobuf commands from non-admin VIDs, allowance for user-callable commands, `VidIsAdmin()` protocol/entity combinations, legacy `/proc/admin` versus `/proc/user` authorization, legacy and protobuf write-detection matrices, async save/get/drop behavior, and no duplicate `tident` insertion. Security regression tests should add a new command case and verify default admin gating.
