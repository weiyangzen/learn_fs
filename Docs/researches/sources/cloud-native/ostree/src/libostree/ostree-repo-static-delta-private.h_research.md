# sources/cloud-native/ostree/src/libostree/ostree-repo-static-delta-private.h

## Purpose

This private header defines static delta constants, wire-format strings, opcodes, shared helper prototypes, execution stats, analysis structs, and endian helpers used by static delta generation, parsing, execution, dumping, and indexing.

## Important APIs, Types, and Functions

- `OSTREE_STATIC_DELTA_PART_MAX_SIZE_BYTES` and `OSTREE_STATIC_DELTA_OBJTYPE_CSUM_LEN` define part sizing and packed object entry width.
- `OSTREE_STATIC_DELTA_PART_PAYLOAD_FORMAT_V0`, `OSTREE_STATIC_DELTA_META_ENTRY_FORMAT`, `OSTREE_STATIC_DELTA_FALLBACK_FORMAT`, `OSTREE_STATIC_DELTA_SUPERBLOCK_FORMAT`, and `OSTREE_STATIC_DELTA_SIGNED_FORMAT` define serialized `GVariant` layouts.
- `OSTREE_STATIC_DELTA_SIGNED_MAGIC` marks signed static delta containers.
- `OstreeStaticDeltaOpenFlags` controls checksum skipping and trusted variant parsing.
- `OstreeStaticDeltaOpCode` enumerates the bytecode consumed by the executor: open-splice-close, open, write, set/unset read source, close, and bspatch.
- `OstreeDeltaExecuteStats` records operation counts.
- `OstreeDeltaContentSizeNames` represents content similarity analysis records.
- Prototypes connect compilation analysis, part opening/execution, object-existence checks, dump/delete/reindex helpers, and endian detection.

## Control Flow

The header does not implement control flow, but it defines the contracts shared by the `.c` files. The compiler emits payloads using the part payload format and opcode enum. The core reader validates meta-entry and fallback layouts from the superblock. The processing layer interprets the opcodes in the same order they are declared here. Endian helper functions are used when generating or displaying non-native-endian numeric fields.

## State and Persistence Behavior

The formats declared here are persistent ABI for static delta artifacts on disk and in summaries. A superblock includes metadata, timestamp, source and target checksums, target commit object, recursive delta references, part metadata, and fallback entries. A signed delta stores magic, raw superblock bytes, and signature metadata. Any change to these strings affects compatibility with existing delta files.

## Dependencies and Integration Points

The header depends on public OSTree core types and is included by static delta core, compilation, compilation analysis, and processing sources. It also exposes `_ostree_repo_static_delta_reindex()` and related internals used by repo summary and command code. The `OSTREE_SUMMARY_STATIC_DELTAS` key links static delta indexes to summary metadata.

## Risks and Edge Cases

Format strings are dense and easy to break. Numeric fields in historical deltas may be non-canonical endian, so callers must use `maybe_swap_endian_u32()` and `maybe_swap_endian_u64()` when appropriate. `OSTREE_STATIC_DELTA_N_OPS` must remain in sync with the opcode enum and stats indexing. The signed format intentionally signs raw superblock bytes; any transformation before verification would invalidate signatures.

## Test Signals

Format compatibility tests should parse old and new superblocks, signed containers, fallback entries, empty object arrays, and cross-endian deltas. Opcode tests should verify the stats index remains aligned with `OSTREE_STATIC_DELTA_N_OPS`. ABI tests should ensure generated artifacts can be opened by the core reader and executed by the processing layer.
