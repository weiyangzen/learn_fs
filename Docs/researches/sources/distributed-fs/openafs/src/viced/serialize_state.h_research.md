# sources/distributed-fs/openafs/src/viced/serialize_state.h

## Purpose

`serialize_state.h` defines the on-disk and runtime contracts for demand-attach fileserver state serialization. It is the schema used by `serialize_state.c`, the host package, the callback package, and `state_analyzer.c`.

## Important APIs, Types, And Functions

- Magic/version constants define independent format stamps for the main fs state, host state, callback state, callback timeout/hash blocks, callback entries, active-volume state, and active-volume hash blocks.
- `struct fs_state_header` is the main 1024-byte header carrying timestamp, sysname, server UUID, validity, endianness, detailed-statistics flag, offsets for active volumes, host, callback, and VLRU state, plus a version string.
- Host schema: `host_state_header`, `host_state_entry_header`, and `hostDiskEntry` encode host records, interfaces, CPS data lengths, callback list index, and activity timestamps.
- Callback schema: `callback_state_header`, timeout/FE-hash headers, `callback_state_entry_header`, `FEDiskEntry`, and `CBDiskEntry` encode FileEntry and CallBack arrays plus index values for remapping.
- Active volume schema: `active_volume_state_header`, `active_volume_state_avehash_header`, `active_volume_state_avehash_entry`, and `AVDiskEntry` reserve layout for active-volume salvage support.
- `struct idx_map_entry_t` and `struct fs_dump_state` describe runtime restore maps and file/mmap cursors.
- Prototypes expose fs-state I/O helpers and host/callback save/restore/verify/index-remap hooks.

## Control Flow

This header does not implement control flow, but it dictates the flow order: write/read the main header, then use offsets to locate host and callback subheaders, then process variable-length host entries and callback FE/CB entries while building old-to-new index maps. Restore uses `h_OldToNew`, `fe_OldToNew`, and `cb_OldToNew` mappings to reconnect references serialized from the old process.

## State And Persistence Behavior

The header is explicitly an on-disk ABI. Structures include reserved expansion fields and fixed-size headers, so changing sizes, field order, magic, or version values affects dump compatibility. The `valid` bit is the primary persistence cursor. The index-map valid states distinguish populated entries from skipped entries, allowing restore to tolerate records that were omitted during save due to inconsistent/busy runtime state.

## Dependencies And Integration Points

The schema references fileserver host/callback structures such as `struct host`, `struct FileEntry`, and `struct CallBack`, and OpenAFS primitive types such as `afs_uint32`, `afs_uint64`, `afsUUID`, `VolumeId`, and `byte`. It is included by `serialize_state.c` and `state_analyzer.c`, and its host/callback prototypes are implemented outside this file.

## Risks And Edge Cases

- The disk structures embed native C types such as `time_t`; portability is guarded mostly by endianness/version checks, not by a canonical XDR format.
- `FS_STATE_H_MAX_LIST_LEN` is intentionally huge, so sanity checks elsewhere must still prevent memory exhaustion from corrupt record counts.
- Active-volume offsets exist in `fs_state_header`, but the current serializer file in this subset only drives host/callback state.
- Any consumer must respect `HOST_STATE_VALID_WINDOW` or stale callbacks can be revived.

## Test Signals

Useful validation includes static layout/size checks for the documented header sizes, dump compatibility tests after structure changes, magic/version mismatch tests, index-map old-to-new remap tests, and analyzer/serializer agreement tests over generated dumps.
