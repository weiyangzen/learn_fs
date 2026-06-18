# sources/cloud-native/nydus-snapshotter/pkg/cache/manager.go

Purpose: manages disk cache files for nydus fusedev-style blob caching, including usage accounting and blob cache removal.

Important APIs and functions: suffix constants for image disk, layer disk, chunk map, blob metadata, and v2.1 blob data. `Manager` stores `cacheDir`, `period`, and an event channel; `Opt` includes disabled/cache dir/period/database fields; `NewManager`, `CacheDir`, `CacheUsage`, `RemoveBlobCache`, and `ExtractBlobIDFromFilename`.

Control flow: `NewManager` ensures the cache directory exists and returns a manager. `CacheUsage` builds all possible cache file paths for a blob ID, including backward-compatible unsuffixed and suffixed forms, sums `fs.DiskUsage` for existing paths, and ignores missing files. `RemoveBlobCache` removes chunk maps and metadata before data files, skipping missing files. `ExtractBlobIDFromFilename` strips known suffixes in an order that handles `.blob.data.chunk_map` before shorter suffixes.

State and persistence: cache files live in `cacheDir`; manager state is otherwise simple in-memory configuration. `eventCh`, `period`, `Disabled`, and `Database` are not used in this file, suggesting broader manager behavior is elsewhere or planned.

Dependencies and integration points: integrates with containerd snapshot usage accounting, continuity `fs.DiskUsage`, containerd logging, and cache file names produced by nydusd.

Risks: `RemoveBlobCache` is not atomic and may leave partial state if one removal fails after earlier files are removed. It uses `path.Join`, which assumes Unix-like paths. Cache usage can double-count if alternate legacy/current names are hard links or aliases. Directory traversal is not relevant if blob IDs are trusted digest hex, but arbitrary input would be joined directly.

Test signals: `manager_test.go` tests suffix stripping for many filename forms; usage and deletion are not tested here.
