# sources/distributed-fs/openafs/src/viced/state_analyzer.c

## Purpose

`state_analyzer.c` is an interactive diagnostic tool for demand-attach fileserver state dumps. It mmaps a dump file, decodes the serialized headers, host entries, FileEntry records, CallBack records, timeout queues, and file-entry hash buckets, and lets an operator navigate or search those structures.

## Important APIs, Types, And Functions

- `main`, `openFile`, `initState`, `banner`, and `prompt` implement program startup and the REPL.
- `dump_hdr`, `dump_h_hdr`, `dump_cb_hdr`, `dump_cb_timeout`, `dump_cb_fehash`, `dump_he`, `dump_fe`, `dump_cb`, and related navigation wrappers render decoded structures.
- `get_hdr`, `get_h_hdr`, `get_cb_hdr`, `get_cb_timeout_hdr`, `get_cb_timeout`, `get_cb_fehash_hdr`, `get_cb_fehash`, `get_he`, `get_fe`, and `get_cb` lazily decode and cache memory-map positions.
- `find_fe_by_index`, `find_fe_by_fid`, and `find_cb_by_index` provide linear searches over decoded records.
- Static cursor/cache structs hold current host, FE, and CB positions and decoded data.

## Control Flow

Startup opens either the provided path or `AFSDIR_SERVER_FSSTATE_FILEPATH`, mmaps it read-only, then enters a prompt with global, host, FE, and CB modes. Commands switch modes, dump headers, dump current/next/previous/first/last/all records, hex-dump raw bytes, or search by index/FID. Decoding is lazy: top-level headers are read once, variable-length record offsets are cached as the user walks to specific indices, and CB navigation is relative to the currently selected FE.

## State And Persistence Behavior

The analyzer does not persist new state. It consumes the dump schema from `serialize_state.h` and reconstructs enough pointer-like state from offsets and record lengths to inspect the dump. Host records include optional interface and CPS arrays; callback records include FE headers followed by one FE disk entry and then that FE's CB disk entries. The analyzer validates magic/version values during display and performs bounds checks for major top-level offsets before copying structures out of the mmap.

## Dependencies And Integration Points

The tool depends directly on the same `viced.h`, `host.h`, `callback.h`, and `serialize_state.h` definitions used by the serializer. It includes volume, vnode, RX, partition, ACL, PT, and utility headers because the serialized structures embed fileserver types. Its output is a troubleshooting bridge between production dumps and source-level host/callback structures.

## Risks And Edge Cases

- It opens the dump with `O_RDWR` even though it maps with `PROT_READ`; this may unnecessarily fail for read-only dump copies.
- Top-level offset checks are present, but many later `memcpy` operations rely on record counts/lengths from the file and do not fully revalidate every variable-length record boundary.
- The REPL parser uses fixed-size input and simple tokenization; malformed commands are rejected but not robustly quoted.
- `get_h_hdr` copies the host header but does not set `hdrs.h_hdr_valid`, so repeated calls may recopy it.

## Test Signals

Tests should run analyzer commands against a small synthetic valid dump, corrupt magic/version fields, bad top-level offsets, zero-record dumps, host records with/without interfaces and CPS arrays, FE records with multiple CBs, and `find by fid` / `find by index` paths. Fuzzing record lengths would be valuable because this tool is commonly used on suspect dumps.
