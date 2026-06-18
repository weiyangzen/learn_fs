<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/refs.go -->
# sources/cloud-native/stargz-snapshotter/store/refs.go

## Purpose
Caches image manifest/config metadata by reference for stargz-store and manages reference lifetimes around that metadata.

## Important APIs, Types, And Functions
- `newRefPool` creates `<root>/pool` and an LRU cache with eviction cleanup.
- `loadRef` reads manifest/config from disk or fetches and writes them.
- `use` and `release` pin references in the LRU cache while layers are in use.
- `readManifestAndConfig`, `writeManifestAndConfig`, and `fetchManifestAndConfig` handle metadata I/O and remote resolution.
- Path helpers derive digest-based metadata dirs.

## Control Flow
`loadRef` first attempts disk reuse; on failure it resolves the image using registry hosts restricted to the reference host, fetches the platform manifest and config, writes both JSON files, adds an LRU reference, and schedules release after 120 seconds unless pinned.

## State And Persistence
Manifest/config JSON are stored under `pool/metadata--<digest(ref)>`. LRU eviction removes metadata directories only after reference counts drop to zero.

## Dependencies And Integration Points
Uses containerd Docker resolver, platform selection, `containerdutil.FetchManifestPlatform`, `cacheutil.LRUCache`, and `source.RegistryHosts`. Consumed by `LayerManager`.

## Risks And Edge Cases
Platform is hardcoded to default. Disk cache read failures always trigger fetch. Timed goroutine release relies on clients calling returned done functions and reference counters staying balanced. Eviction removes entire metadata dirs.

## Test Signals
Signals include disk reuse after first fetch, metadata JSON correctness, LRU eviction cleanup after done, pin/unpin behavior through use/release, and host mismatch rejection in the temporary resolver.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/store/refs.go -->
