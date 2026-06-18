# sources/distributed-fs/openafs/src/WINNT/afsd/fs.c

## Purpose

`fs.c` is the Windows OpenAFS `fs` command implementation. It registers dozens of subcommands and translates command-line requests into cache-manager pioctls, VLDB lookups, protection-server lookups, registry/service operations, and formatted diagnostics. It covers ACL editing, cache flushing, volume and quota reporting, mount-point management, server preference management, cell configuration, cache options, tracing/debugging, encryption and data-verification flags, and Unix-like owner/group/mode operations.

## Important APIs, Types, and Functions

`wmain()` initializes Winsock, converts the wide command line to UTF-8, registers command syntaxes via `cmd_CreateSyntax()`, then runs `cmd_Dispatch()`. ACL commands use `SetACLCmd()`, `CopyACLCmd()`, `CleanACLCmd()`, `ListACLCmd()`, `PRights()`, `Convert()`, and helpers from `fs_acl.c`. File/volume commands include `GetCallerAccess()`, `FlushCmd()`, `FlushAllCmd()`, `FlushVolumeCmd()`, `SetVolCmd()`, `ExamineCmd()`, `ListQuotaCmd()`, `WhereIsCmd()`, `DiskFreeCmd()`, `QuotaCmd()`, `GetFidCmd()`, `ChOwnCmd()`, `ChGrpCmd()`, and `ChModCmd()`. Mount/cell/server commands include `ListMountCmd()`, `MakeMountCmd()`, `RemoveMountCmd()`, `CheckServersCmd()`, `CheckVolumesCmd()`, `ListCellsCmd()`, `NewCellCmd()`, `WhichCellCmd()`, `WSCellCmd()`, `SetCellCmd()`, `GetCellCmd()`, `SetPrefCmd()`, and `GetPrefCmd()`. Diagnostics and settings include `SysNameCmd()`, `StoreBehindCmd()`, `SetCryptCmd()`, `GetCryptCmd()`, `TraceCmd()`, `UuidCmd()`, `MemDumpCmd()`, `MiniDumpCmd()`, `CSCPolicyCmd()`, `RxStatProcCmd()`, `RxStatPeerCmd()`, `SmbUnicodeCmd()`, `SetDataVerifyCmd()`, `GetDataVerifyCmd()`, and hidden `TestVolStatCmd()`.

## Control Flow

Most subcommands follow a common pattern: default path lists to `.`, build a `ViceIoctl` with `space` as the shared transfer buffer, optionally prefetch a fid and literal-resolution options with `VIOCGETFID`, call one or more `pioctl_utf8()` operations, print formatted results, and accumulate per-item errors rather than aborting the whole list. ACL commands fetch serialized ACLs with `VIOCGETAL`, parse and normalize them, modify `AclEntry` lists, serialize back with `AclToString()`, and store through `VIOCSETAL`. Volume/quota/status commands exchange `VolumeStatus` plus trailing strings. Mount commands split parent directory and final component, handle Windows UNC/NetBIOS AFS paths and freelance root permissions, and use mount-specific pioctls to create/stat/delete mount points. Server preference commands batch hostname/rank pairs into pioctl buffers, flushing when near `MAXINSIZE`.

## State and Persistence Behavior

The process itself is stateless apart from global command buffer `space`, `uclient`, `gblob`, and `rxInitDone`. It mutates cache-manager state through pioctls: ACLs, cache flush state, volume status/quota messages, mount points, server preferences, cell definitions, setuid cell flags, sysname, store-behind defaults, Rx security level, trace state, UUID generation, data verification, Unicode setting, callback address, and volume-status test hooks. It also mutates Windows registry CSC policy values and can ask the AFSD service to generate a minidump. VLDB checks in `mkmount` are advisory unless `-fast` is omitted and VLDB initialization succeeds.

## Dependencies and Integration Points

The file depends on OpenAFS command parsing, `pioctl_utf8()` and Windows cache-manager ioctl contracts, `fs_utils`, ACL helpers, `parsemode`, cell config, protection server, VLDB/ubik client initialization, host lookup utilities, Rx stats flags, Windows registry/service APIs, Winsock, and admin/root checks. It is the primary administrative CLI surface for the Windows AFS client.

## Risks and Edge Cases

The shared `space` buffer and many hand-packed variable-length pioctl payloads make length accounting critical. Some code still uses old pointer/assignment idioms and fixed buffers, so long names, malformed cache-manager replies, or unexpected pioctl sizes are high-risk. Several admin commands are Windows-only or non-Windows-only behind preprocessor branches. Numeric owner/group parsing treats `atoi()==0` as "name lookup", making true ID 0 ambiguous. `NewCellCmd()` appears to read `-fsport`/`-vlport` from the wrong parameter indexes in its integer conversions. Error reporting sometimes passes pioctl return code instead of `errno` to `fs_Die()`. Mount-point path handling has many Windows UNC and freelance special cases.

## Test Signals

Useful tests include command registration and aliases, UTF-8 command-line conversion, every pioctl payload size and out-size validation, ACL set/list/copy/clean for AFS and DFS ACLs, literal mountpoint options, offline volume status mapping, quota formatting, mount create/list/remove under normal AFS and freelance root, server-preference batching and VL-only mode, cell add/list/status/set, sysname multi-value set/get, store-behind file/default modes, crypt and verify flags, trace/uuid/memdump/minidump/admin denial paths, chown/chgrp name-to-ID resolution, chmod symbolic and octal parsing, and hidden volume-status test inputs.
