# Research: sources/distributed-fs/eos/mgm/proc/ProcInterface.hh

## Purpose

`ProcInterface.hh` declares the static interface for identifying, authorizing, constructing, and tracking MGM proc commands. Its documentation explains the proc model: clients read `/proc/user` or `/proc/admin`, pass command arguments in CGI keys such as `mgm.cmd` and `mgm.subcmd`, and receive a stream containing stdout, stderr, and return code. It also documents the newer protobuf request path.

## Important APIs, Types, and Functions

- `GetProcCommand()` is the factory entry point for both old CGI commands and new protobuf commands.
- `IsProcAccess()` detects proc paths.
- `ProtoIsWriteAccess()` and `IsWriteAccess()` classify state-changing requests.
- `Authorize()` gates `/proc/admin/` and `/proc/user/` paths.
- `GetSubmittedCmd()`, `SaveSubmittedCmd()`, and `DropSubmittedCmd()` handle async command pickup and disconnection.
- `VidIsAdmin()` centralizes MGM admin privilege checks for legacy path authorization, protobuf dispatch, and defense-in-depth command handlers.
- `sProcThreads` exposes the shared async thread pool.
- Private `IsAdminCmd()` and `HandleProtobufRequest()` keep protobuf command classification and construction internal.

## Control Flow

Callers first use `IsProcAccess()` to detect `/proc/` paths and `Authorize()`/`IsWriteAccess()` to apply access policy. They then call `GetProcCommand()`, which may return a parked async command, a protobuf handler, or a legacy `ProcCommand`. Long-running protobuf handlers can be saved and later retrieved by `tident`.

The header makes `VidIsAdmin()` the single source of truth for admin checks. That is important because command handlers such as `FileRegisterCmd` perform extra checks but should match the central predicate.

## State and Persistence Behavior

The header declares static process state: an async command map, a list of running orphaned commands waiting for deletion, a mutex, a thread-local log id, and the thread pool. This state is runtime-only and protects command lifecycles. Persistent effects are performed by concrete command handlers and the legacy `ProcCommand`.

## Dependencies and Integration Points

The interface depends on `IProcCommand`, `Logging`, `Mapping`, `ThreadPool`, `proc_fs.hh`, `VirtualIdentity`, and `RequestProto` command cases. It is the integration point between the proc filesystem implementation and the command classes under `mgm/proc/user` and `mgm/proc/admin`.

## Risks and Edge Cases

- Static mutable state must remain protected by `mMutexCmds`.
- `VidIsAdmin()` has two protocol sources (`XrdSecEntity` preferred, `vid.prot` fallback), so callers with and without an entity must behave consistently.
- Future protobuf command cases require updates to `IsAdminCmd()` and dispatch construction.
- Async command ownership transfers by `unique_ptr`; incorrect use can drop or leak a command object.

## Test Signals

Compile-level tests should ensure every declared handler has a matching implementation. Runtime tests should cover path detection, authorization, admin predicate combinations, async command parking, protobuf dispatch, and write-access classification. Security tests should verify non-admin users cannot instantiate admin protobuf commands even if they reach the protobuf dispatcher through a user URL.
