# sources/distributed-fs/openafs/src/viced/serialize_state.c

## Purpose

`serialize_state.c` implements demand-attach fileserver state dump and restore for host and callback state. It creates, invalidates, loads, commits, reads, writes, maps, syncs, and verifies the state dump file at `AFSDIR_SERVER_FSSTATE_FILEPATH`. The implementation is compiled only under `AFS_DEMAND_ATTACH_FS`.

## Important APIs, Types, And Functions

- Public entry points `fs_stateSave()` and `fs_stateRestore()` orchestrate full save/restore under `H_LOCK`.
- Public I/O helpers `fs_stateWrite`, `fs_stateRead`, `fs_stateWriteV`, `fs_stateReadV`, `fs_stateWriteHeader`, `fs_stateReadHeader`, `fs_stateIncEOF`, `fs_stateSeek`, `fs_stateSync`, and `fs_stateFileOpen` are used by host/callback serialization code.
- Internal lifecycle helpers `fs_stateCreateDump`, `fs_stateLoadDump`, `fs_stateInvalidateDump`, `fs_stateCommitDump`, and `fs_stateCloseDump` manage dump-file validity.
- Mmap helpers `fs_stateSizeFile`, `fs_stateResizeFile`, `fs_stateTruncateFile`, `fs_stateMapFile`, `fs_stateUnmapFile`, `fs_stateIncCursor`, and `fs_stateCheckIOSafety` provide fast sequential I/O on non-Windows platforms.
- Header helpers `fs_stateFillHeader` and `fs_stateCheckHeader` encode/check magic, format version, sysname, endianness, stats mode, timestamp, server UUID, and version string.

## Control Flow

Save flow: take `H_LOCK`, allocate `fs_dump_state`, optionally run `h_stateVerify` and `cb_stateVerify`, create a new dump after renaming any existing file to `.old`, write an invalid header, serialize host state, serialize callback state, and commit by truncating/syncing data before writing a valid header. If pre-save verification failed, `state.bail` keeps the final header invalid even though the dump file was written.

Restore flow: take `H_LOCK`, allocate state, open and mmap the dump, read/check the main header, immediately invalidate the dump so it cannot be replayed after a failed restore, skip host/callback restore if the dump timestamp is older than `HOST_STATE_VALID_WINDOW`, otherwise restore host and callback tables and remap their indices, optionally verify both tables, log elapsed milliseconds and restored FE/CB counts, then invalidate and close the file on exit.

## State And Persistence Behavior

The file persists process-local host and callback structures so DAFS can restart without forcing all clients through full callback reinitialization. The validity protocol is two-phase: header `valid = 0` while a dump is in progress or consumed, and `valid = 1` only after all data has been synced and the final header is rewritten. The header is tied to this server by `FS_HostUUID`, endianness, `FS_STATE_MAGIC`, `FS_STATE_VERSION`, and detailed-statistics mode. Old dumps can be loaded only for limited host/callback restore; older than 30 minutes means restore continues with host restore disabled.

## Dependencies And Integration Points

This file sits between `viced.c` shutdown/startup and the `host.c`/`callback.c` serializers declared in `serialize_state.h`. It depends on global `fs_state.options`, `FS_HostUUID`, `cml_version_number`, `H_LOCK`, `ViceLog`, OpenAFS integer macros, and platform file/mmap APIs. `viced.c` invokes `fs_stateRestore()` before Rx request service starts and invokes `fs_stateSave()` after shutdown quiesces background host/callback threads.

## Risks And Edge Cases

- Restore exits the process on host/callback corruption paths, preventing a partially corrupted in-memory server from continuing.
- `msync` return value is ignored in the mmap `fs_stateSync` implementation, so sync failures may be invisible.
- Mmap `fs_stateSeek` does not bounds-check the target offset; callers must validate offsets.
- Header version mismatch is fatal, but component version-string mismatch is warning-only.
- Host/callback restore is skipped when the dump is too old; tests must distinguish "restore succeeded without host restore" from full restore.

## Test Signals

Strong signals include save/restore round trips, invalid-header rejection, wrong UUID/endian/version rejection, old timestamp skip behavior, pre-save verification failure producing an invalid dump, forced mmap resize while writing large callback tables, and recovery behavior after a crash between data sync and valid-header rewrite.
