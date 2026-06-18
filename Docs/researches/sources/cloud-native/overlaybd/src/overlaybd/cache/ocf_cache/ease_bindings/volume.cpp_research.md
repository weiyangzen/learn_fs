<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.cpp -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.cpp

## Purpose
Implements the OCF volume type that backs both cache-device IO and core/source-file IO with Photon `IFile` operations.

## Important APIs, Types, And Functions
Defines internal `ease_ocf_volume_io` and `ease_ocf_volume`, `volume_open`, `volume_submit_io`, flush/discard no-op completions, `volume_get_length`, volume data accessors, static `volume_properties`, `volume_init`, and `volume_cleanup`.

## Control Flow
OCF volume open stores UUID and optional cache params. For cache UUIDs, IO is dispatched as `preadv`/`pwritev` to `media_file` at OCF address. For core UUIDs, reads are translated from global cache namespace address to source-file offset, optionally trigger asynchronous prefetch, then read from `OcfSrcFileCtx::src_file`. Writes to core return `ENOSYS`.

## State And Persistence
Cache IO persists to the media file. Core IO reads source files only. Volume-private data stores UUID and cache params; IO-private data stores caller iovecs, OCF offset adjustment, source context, and error state.

## Dependencies And Integration Points
Depends on Photon IO allocation, logging/audit, `IOVector`, OCF volume registration, `ease_ocf_provider`, and `OcfSrcFileCtx`. It is the storage adapter OCF uses for cache and backing core volumes.

## Risks And Test Signals
Core reads reject nonzero data offset and null source context as internal bugs. EOF is treated as invalid because upper layers should truncate reads before OCF. Prefetch spawns a detached Photon thread and ignores useful return data, so failures are logged but do not directly fail the foreground read. Source size reviewed: 210 lines; exercised by OCF perf/manual tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/volume.cpp -->
