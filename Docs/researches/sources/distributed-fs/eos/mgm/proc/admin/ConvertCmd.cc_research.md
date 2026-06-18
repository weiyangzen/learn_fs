# Research: sources/distributed-fs/eos/mgm/proc/admin/ConvertCmd.cc

## Purpose

`ConvertCmd.cc` implements the protobuf command for configuring the converter engine, scheduling file layout conversions, listing pending conversion jobs, and clearing pending jobs.

## Important APIs, Types, and Functions

- `ConvertCmd::ProcessRequest()` validates converter-engine availability, selects JSON output when requested, and dispatches `config`, `file`, `list`, and `clear`.
- `ConfigList()` reports converter threadpool/config/running/pending/failed state in text or JSON.
- `ConfigSubcmd()` lists or sets converter engine configuration.
- `FileSubcmd()` resolves an identifier to a file path, validates metadata, computes target space/checksum/layout, builds a conversion id, and schedules a job.
- `ListSubcmd()` formats pending jobs as JSON or a table.
- `ClearSubcmd()` clears pending jobs; it is additionally root/admin/sudoer gated.
- `PathFromIdentifierProto()` supports path, file id, and container id identifiers.
- `CheckConversionProto()` validates layout, replica count, checksum, and placement policy.
- Static `CheckValidPath()` validates namespace existence and type.
- Static `BuildConversionId()` constructs the converter engine job string.

## Control Flow

Execution starts by requiring `gOFS->mConverterEngine`. Config list/set delegates directly to the engine. File conversion resolves the target path, checks it is a file through `_exists`, reads file metadata and first replica location under namespace locks, validates requested conversion parameters, infers the target space from the replica filesystem if not specified, chooses the requested or existing checksum, builds a conversion id of the form `<fid>:<space>#<layoutid>[~placement]`, and calls `ScheduleJob()`. Listing reads pending jobs and formats them. Clearing is allowed only for root, sudoer, admin uid, or admin gid.

## State and Persistence Behavior

Persistent conversion state is owned by `mConverterEngine` and namespace metadata. This command schedules jobs by file id and conversion id; it does not directly mutate file metadata. It reads namespace metadata under `gOFS->eosViewRWMutex` and filesystem scheduling data under `FsView::gFsView.ViewMutex`.

## Dependencies and Integration Points

The file depends on `XrdMgmOfs`, scheduler placement policy parsing, `FsView`, `ConverterEngine`, namespace view/file/container interfaces, table formatting, layout/file-id helpers, common constants, and JSON. It is centrally admin-gated by `ProcInterface` for `RequestProto::kConvert`, with an extra privilege check for clearing.

## Risks and Edge Cases

- `CheckValidPath()` error text says "path must point to a <actual type>" when `enforce_type` mismatches; that wording may be reversed from what users need.
- `FileSubcmd()` uses the first replica location and rejects files without replicas; conversion of tape-only or empty-location files is unsupported.
- `PathFromIdentifierProto()` accepts container id but `FileSubcmd()` later enforces file existence, so container identifiers lead to type errors.
- `ConfigSubcmd(SET)` has no visible success message, only `retc=0`.
- `ClearSubcmd()` ignores fields in the clear proto and clears all pending jobs.

## Test Signals

Tests should cover missing converter engine, config list text/JSON, config set failures, identifier resolution by path/fid/cid, non-existent paths, directory input, files without replicas, invalid layout/replica/checksum/placement, inferred space from fsview, explicit space, conversion id formatting, schedule failure with engine message, pending list formatting, and clear authorization.
