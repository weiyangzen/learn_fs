# sources/distributed-fs/ceph-client/drivers/md/dm-cache-metadata.h

## Purpose
`dm-cache-metadata.h` exposes the persistent metadata API used by the DM cache target and policies. It defines metadata device sizing limits, feature flag masks, the opaque metadata handle, statistics, and all mapping, discard, dirty, hint, commit, and recovery operations.

## Important APIs, Types, and Functions
The header defines `DM_CACHE_METADATA_BLOCK_SIZE`, maximum metadata-device sector constants, supported feature masks, opaque `struct dm_cache_metadata`, callback types `load_discard_fn` and `load_mapping_fn`, `struct dm_cache_statistics`, and declarations for open/close, cache resize, discard bitset resize/load/set, mapping insert/remove/load, dirty bit import, stats get/set, commit, metadata-space queries, hint writing, needs-check/read-only/read-write/abort controls, and clean-open query.

## Control Flow
The intended flow is: open or format metadata, resize structures to match cache/discard geometry, load discards and mappings into runtime target and policy state, perform mapping/dirty/discard mutations while I/O runs, write policy hints and stats, and call `dm_cache_commit()` at transaction boundaries or clean shutdown. Recovery paths may set needs-check, switch read-only/read-write, or abort back to the last good transaction.

## State and Persistence
The header describes persistent metadata but stores no state itself. API comments clarify that policy hints are persistent only across clean operation with matching policy identity, and may be lost after crashes or policy changes.

## Dependencies and Integration Points
It includes cache block types, policy internals, and persistent-data metadata space-map sizing. It is the contract between `dm-cache-target.c` and the metadata implementation, and it also depends on policy APIs for hint sizing and hint extraction.

## Risks and Edge Cases
The maximum metadata size constants impose a hard cap and warning threshold. Feature masks are all zero in this version, so any future on-disk feature flag must update the masks correctly. `dm_cache_set_dirty_bits()` requires the caller's bitset to match cache size for version 2 metadata.

## Test Signals
Compile tests should exercise all target call sites. Runtime signals come from the implementation: correct load callbacks, commit/reopen persistence, clean-open reporting, needs-check behavior, and safe handling of read-only or abort states.
