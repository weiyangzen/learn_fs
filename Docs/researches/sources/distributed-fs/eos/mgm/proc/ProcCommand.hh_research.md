# Research: sources/distributed-fs/eos/mgm/proc/ProcCommand.hh

## Purpose

`ProcCommand.hh` declares the legacy proc-command implementation used by EOS MGM for `/proc/user` and `/proc/admin` CGI-style commands. It also declares the `IFilter` interface used by archive/backup tree scans. The `ProcCommand` class is the old command surface behind `IProcCommand`: it opens a proc command, stores stdout/stderr/return code and optional temporary file results, streams results through `read()`/`stat()`, and exposes many user/admin command entry points implemented across `mgm/proc/user` and `mgm/proc/admin`.

## Important APIs, Types, and Functions

- `IFilter::FilterOutFile()` and `IFilter::FilterOutDir()` define a reusable exclusion contract for archive and backup traversal.
- `ProcCommand::open()`, `read()`, `stat()`, and `close()` implement the XRootD file-like command lifecycle.
- `ProcessRequest()` returns an empty `ReplyProto` by default, making legacy raw commands compatible with the protobuf-oriented `IProcCommand` interface.
- `AddOutput()`, `MakeResult()`, `KeyValToHttpTable()`, `CallJsonFormatter()`, and output getters assemble or expose command output.
- `OpenTemporaryOutputFiles()` and `GetResultFn()` support commands such as `find` that avoid keeping large output in memory.
- Public command methods include user commands such as `Archive`, `Backup`, `Find`, `Fileinfo`, `Rm`, `UserQuota`, and admin commands such as `Access`, `AdminQuota`, `Ns`, `Vid`, `Fusex`, `GeoSched`, and `Rtlog`.
- Archive/backup helpers include `ArchiveExecuteCmd`, `ArchDirStatus`, `ArchiveCreate`, `ArchiveAddEntries`, immutable subtree helpers, ACL checks, archive listing formatting, and `BackupCreate`.

## Control Flow

Callers obtain an `IProcCommand` through `ProcInterface`, then legacy commands run through `ProcCommand::open()`. The class parses CGI keys from `pOpaque`, selects a user or admin command, fills `stdOut`, `stdErr`, `stdJson`, `retc`, and finally builds a result stream. Later reads stream `mResultStream` or a temporary result file to the client. `close()` finalizes the command and frees/records transient command state.

The header also defines the call surface for archive and backup flows. Archive/backup commands gather namespace entries through `ArchiveAddEntries`, optionally filter them with `IFilter`, create local metadata files, and communicate with external archive machinery through `ArchiveExecuteCmd`.

## State and Persistence Behavior

`ProcCommand` itself is per-request state. It owns parsed command strings (`mCmd`, `mSubCmd`, `mArgs`, `mPath`), output buffers, format flags, the input `XrdOucEnv`, caller identity pointer `pVid`, temporary file names/handles, and the result stream. It does not persist command state directly; individual command implementations may mutate MGM configuration, namespace metadata, access-control config, archive metadata, or backup files. The `mClosed` guard makes `GetResult()` return no stream after close.

Temporary output files are runtime artifacts for large outputs. The archive/backup helpers can create local temporary files and copy generated metadata into EOS/remote destinations, while state changes are delegated to other subsystems.

## Dependencies and Integration Points

The class depends on `IProcCommand`, `VirtualIdentity`, `XrdOucEnv`, XRootD error/file offset types, namespace metadata interfaces, JSON, and many command implementation files. It is integrated by `ProcInterface` as the fallback for non-protobuf requests and as the base for older proc admin/user commands. Archive and backup helpers integrate with namespace views, archive daemon JSON commands, ACL/immutability behavior, and XRootD copy machinery in implementation files.

## Risks and Edge Cases

- The legacy command surface is broad and command selection is distributed across many implementation files, so adding/removing a command requires updates outside this header.
- `pVid`, `pOpaque`, `mError`, and temporary file handles are raw pointers/handles; lifecycle errors can cause leaks or stale access if open/close paths diverge.
- Large outputs split between memory streams and temporary files; tests need to cover both paths.
- Format flags (`mFuseFormat`, `mJsonFormat`, `mHttpFormat`, `mSendRetc`) affect client-visible output and can regress compatibility.
- `IFilter` is generic but currently tied to archive/backup, with a comment noting it should move to archive-specific code.

## Test Signals

Useful signals include legacy proc command integration tests for `open/read/stat/close`, result formatting with stdout/stderr/retc/json/http, temporary-file streaming for large `find`-style output, archive/backup filter behavior, and command dispatch coverage for admin/user commands. Regression tests should verify no result is returned after `mClosed`, that `GetCmd()` handles missing `mgm.cmd`, and that archive/backup failures set `retc`/`stdErr` consistently.
