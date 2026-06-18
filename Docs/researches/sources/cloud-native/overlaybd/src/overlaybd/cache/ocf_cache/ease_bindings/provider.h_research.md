<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.h -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.h

## Purpose
Declares the C++ wrapper that owns an Open CAS Framework context, cache, core, queues, volume configuration, and read path for OverlayBD's OCF-backed cache filesystem.

## Important APIs, Types, And Functions
`ease_ocf_provider` exposes `start`, `stop`, `ocf_pread`, and `prefetch_unit`. It publishes `SectorSize` and keeps OCF identifiers for cache/core names and UUIDs. The private `alignment` struct plus `prepare_aligned_iov` and `copy_aligned_iov` support sector-aligned submissions for unaligned caller reads.

## Control Flow
Callers construct the provider with `ease_ocf_volume_params` and a prefetch size, call `start(reload_media)` to initialize OCF, and then call `ocf_pread` with a logical file offset plus namespace block base. Reads may be aligned with padding before submission to OCF and copied back afterward.

## State And Persistence
State is process-local OCF handles plus externally owned cache media parameters. Persistent cache media and namespace metadata are managed through the volume and namespace layers, not in this header.

## Dependencies And Integration Points
Includes Photon filesystem and `IOVector`, local OCF context/queue/volume bindings, and `OcfSrcFileCtx`. It is used by `ocf_cache.cpp` as the cache engine behind a Photon `IFileSystem`.

## Risks And Test Signals
The header documents that callers must avoid EOF-overrun reads; `OcfTruncateFile` in `ocf_cache.cpp` is the main guard. Alignment code depends on 512-byte sectors while cache line size is independently configured. Manual/perf coverage comes from `ocf_perf_test.cpp`; source size reviewed: 77 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/ocf_cache/ease_bindings/provider.h -->
