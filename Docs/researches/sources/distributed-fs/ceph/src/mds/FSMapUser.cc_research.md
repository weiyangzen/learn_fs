# sources/distributed-fs/ceph/src/mds/FSMapUser.cc

## Purpose

`FSMapUser.cc` implements the compact client-facing filesystem map. It strips the full monitor `FSMap` down to epoch, legacy client filesystem ID, and filesystem `(cid, name)` pairs so clients can resolve filesystem names and IDs without receiving full MDS daemon topology.

## Important APIs, Types, And Functions

`FSMapUser::encode()` writes version 1 with `epoch`, `legacy_client_fscid`, and a vector of `fs_info_t` values built from the `filesystems` map. `decode()` reads the same vector, clears the map, and rebuilds it by `cid`.

`fs_info_t::encode()` and `decode()` persist only `cid` and `name`. `generate_test_instances()` creates a sample map with epoch 2, legacy FSCID 1, and two named filesystems.

`print()` emits a multiline human-readable representation. `print_summary()` emits either formatter fields or a compact stream form like `e<epoch>: name(cid) ...`.

## Control Flow And Data Flow

Monitor code builds an `FSMapUser` from the authoritative `FSMap` when sending `MFSMapUser` messages to client subscribers. The encode path converts the map to a vector because only `fs_info_t` values are transmitted; decode reconstructs the keyed map using each row's embedded `cid`.

Formatting flow is simple: formatter mode dumps `epoch` and repeated `id`/`name` pairs; stream mode emits all filesystem names and IDs on one line. The header helper `get_fs_cid(name)` performs linear lookup by filesystem name.

## State And Persistence Behavior

The encoded state is stable and intentionally small: `epoch`, `legacy_client_fscid`, and each filesystem's `cid`/`name`. No MDS ranks, pools, health, standby state, mirror info, or compat sets persist in this compact map. Because `filesystems` is keyed by `cid` after decode, duplicate CIDs in the encoded vector would collapse to the last decoded value.

Map iteration order is by `fs_cluster_id_t`, so the encoded vector and printed stream are deterministic for a given map. `legacy_client_fscid` may be `FS_CLUSTER_ID_NONE` when no default exists.

## Dependencies And Integration Points

The implementation depends on `FSMapUser.h`, Ceph encoding macros, `common/Formatter.h`, `mds/mdstypes.h` for role/string support, and monitor message code. `MDSMonitor` fills this object and sends it through `MFSMapUser`; clients use it to choose or resolve a CephFS filesystem.

## Risks And Edge Cases

Formatter mode dumps repeated `id` and `name` fields without opening an array or object per filesystem, so consumers expecting strict JSON arrays may need to handle repeated keys according to the formatter backend. `get_fs_cid()` is linear and returns the first matching name; duplicate names should be prevented by monitor validation, not by this class.

The compact encoding intentionally omits topology and health. Callers that need ranks, pools, or MDS states must use full `FSMap`/`MDSMap` paths. Any future fields require versioning without breaking old clients.

## Test Signals

Tests should dencode `FSMapUser` and `fs_info_t`, verify encode/decode round trips preserve epoch, legacy FSCID, names, and IDs, validate `get_fs_cid()` for existing and missing names, and check stream/formatter output for single and multiple filesystems. Integration tests should confirm monitor-generated `MFSMapUser` updates client filesystem name resolution after create, rename if supported, and remove events.
