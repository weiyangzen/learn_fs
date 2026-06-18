# sources/cloud-native/moby/daemon/builder/remotecontext/lazycontext.go

## Purpose
Implements a `builder.Source` backed by a filesystem directory that computes file hashes lazily and caches them by relative path. It is used for build contexts where hashing every file upfront is unnecessary.

## Important APIs, Types, And Functions
Exports `NewLazySource(root string) (builder.Source, error)`. Internal `lazySource` implements `Root`, `Close`, `Hash`, and `prepareHash`. It relies on `normalize`, `NewFileHash`, `pools.Copy`, and path error conversion.

## Control Flow
`Hash` normalizes the requested path under the root, computes the relative path, `Lstat`s the file, and returns the relative path for missing targets to preserve broken-symlink compatibility. Cache misses call `prepareHash`, which creates a tar-compatible file hash and copies file data only for non-empty regular files.

## State And Persistence
Maintains an in-memory `map[string]string` of relative-path hashes. `Close` is a no-op and the root directory is not owned. The type is explicitly not concurrency-safe.

## Dependencies And Integration Points
Integrates with builder cache keys and remotecontext file hashing. It depends on filesystem metadata and file content, but delegates canonical hash format to `NewFileHash`.

## Risks And Test Signals
Stale cache entries are possible if files mutate after first hash. Broken symlinks returning paths is compatibility-sensitive. No direct file in this subset tests it; archive-context hashing tests provide adjacent coverage.
