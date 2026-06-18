# Research: sources/cloud-native/nydus-snapshotter/pkg/filesystem/config.go

This file defines `NewFSOpt` option functions used by `NewFileSystem`. Options set the nydusd binary path, enabled managers by filesystem driver, cache manager, referrer manager, index manager, tarfs manager, signature verifier, root mountpoint, and optional stargz resolver.

The important behavior is dependency injection. `WithManagers` builds `enabledManagers` keyed by `Manager.FsDriver`, letting the filesystem route fscache, fusedev, blockdev, proxy, and nodev paths. `WithCacheManager`, `WithReferrerManager`, `WithIndexManager`, and `WithTarfsManager` reject nil inputs to fail early. `WithEnableStargz` constructs a `stargz.Resolver` only when enabled. `WithVerifier` allows nil and simply stores the pointer, so callers must ensure mount-time verification can be invoked safely.

There is no persistent state beyond the configured `Filesystem` fields. Integration points are all downstream filesystem operations: daemon startup needs managers and cache, metadata detection needs referrer/index managers, tarfs paths need `tarfs.Manager`, stargz conversion needs a resolver, and signature verification runs during mount. Risks include missing nil checks for verifier and root mountpoint, overwriting duplicate managers by driver, and no direct unit tests for option validation.
