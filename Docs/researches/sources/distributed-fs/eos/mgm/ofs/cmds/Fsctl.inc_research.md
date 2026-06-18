# Research: sources/distributed-fs/eos/mgm/ofs/cmds/Fsctl.inc

## Purpose

`Fsctl.inc` implements XRootD filesystem-control operations for EOS. It handles locate and statfs-like requests, the richer `FSctl` plugin dispatcher used by FUSE and EOS clients, fusex protobuf injection, and a small PLUGIO dispatch path.

## Important APIs, Types, and Functions

- `XrdMgmOfs::fsctl(cmd,args,error,client)` handles older `SFS_FSCTL_LOCATE` and `SFS_FSCTL_STATLS`.
- `XrdMgmOfs::FSctl(cmd,args,error,client)` validates and copies path/opaque arguments, maps identity, handles locate, PLUGIO, plugin commands, fusex commands, and `mgm.pcmd` dispatch.
- `dispatchSFS_FSCTL_PLUGIO()` currently handles `Arg1 == "tgc"` through `mTapeGc->handleFSCTL_PLUGIO_tgc()` and rejects unknown PLUGIO commands.
- Plugin command dispatch maps `mgm.pcmd` to functions such as `Access`, `AdjustReplica`, `Checksum`, `Chmod`, `Chown`, `Commit`, `Drop`, `Event`, `Getfmd`, `GetFusex`, `IsMaster`, `Mkdir`, `Open`, `Readlink`, `Redirect`, `FuseStat`, `Statvfs`, `Symlink`, `Utimes`, and `Version`.

## Control Flow

The simple `fsctl` path masks the opcode. Locate returns this MGM's manager host or IP/port as an XRootD locate data response. Statls parses path/opaque, chooses a space from `eos.space`, `EOS_MGM_STATVFS_DEFAULT_SPACE`, root/default behavior, or quota-only settings, sums space free/capacity from `FsView` or quota stats, scales by layout size factor, and writes an `oss.*` response string.

`FSctl` copies `Arg1` and `Arg2` into fixed buffers with length checks, detects `fusex:` protobuf payloads before treating Arg2 as CGI, maps identity with `AOP_Stat`, performs namespace mapping and illegal-name checks, and allows `is_master`/`version` without the usual `BOUNCE_NOT_ALLOWED`. Locate verifies the path is an existing file and returns manager location. PLUGIO dispatch is separate. Non-plugin commands return `EOPNOTSUPP`. Plugin `fusex:` requests are tagged as app `fuse` and delegated to `Fusex`. Other plugin commands use `lookupFsctl()` and switch to the corresponding command handler.

## State and Persistence Behavior

Locate/statls are read-only. Plugin dispatch can invoke mutating commands that persist namespace state, schedule operations, update replicas, or alter metadata. The file itself updates log id and MGM stats for identity mapping. Statls reads global space views and quota state but does not persist.

## Dependencies and Integration Points

Dependencies include XRootD FSctl constants, identity mapping, namespace mapping macros, `FsView`, `Policy`, `LayoutId`, `Quota`, FUSE/fusex, tape GC, and the broad set of MGM command handlers. It is one of the central command buses for EOS clients and FUSE.

## Risks and Edge Cases

- Path and opaque buffers are fixed at 16384 bytes; longer inputs fail with `EINVAL`.
- `fusex:` detection treats Arg2 as binary protobuf and skips CGI copying; parsing errors are delegated.
- Many plugin commands are identity-mapped as `AOP_Stat` before command-specific handlers run; command handlers must enforce their own mutation authorization.
- `is_master` and `version` bypass `BOUNCE_NOT_ALLOWED` by design for discovery.
- Statls behavior changes with environment variables and may return space-wide or quota-specific values.
- Locate marks results read-only even for write-capable files.

## Test Signals

Tests should cover locate host/IP formatting, IPv4 mapped formatting, statls by space and by quota path, layout scaling, env-variable branches, long Arg1/Arg2 rejection, fusex binary dispatch, PLUGIO `tgc`, unknown PLUGIO, every `mgm.pcmd` dispatch target, unauthenticated/version discovery behavior, and command-specific authorization after FSctl dispatch.
