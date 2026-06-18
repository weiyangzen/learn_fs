# sources/cloud-native/buildkit/source/git/source.go

## Purpose
Implements BuildKit's `git://` source backend: it turns LLB source attributes into `GitIdentifier` values, resolves refs to stable commit metadata, caches remote bare repositories and checked-out snapshots, supports submodules, `.git` retention, bundle-backed fetches, signature verification, and deterministic mtime/file-mode compatibility behavior.

## Important APIs, Types, And Functions
- `Opt`, `Source`, `NewSource`, `Supported`, `Schemes`, `Identifier`, and `Resolve` are the source registration boundary used by `source.Manager`.
- `Metadata` and `MetadataOpts` model resolved Git refs, checksums, optional raw commit/tag objects, and signature-verification inputs.
- `gitSourceHandler` is the per-source instance with parsed identifier, cache key state, auth args, SHA256 object-format flag, session manager, and staged bundle cleanup.
- `ResolveMetadata`, `resolveMetadata`, `resolveMetadataFromURL`, and `addGitObjectsToMetadata` implement metadata-only resolution and optional object retrieval.
- `CacheKey`, `Snapshot`, `remoteFetch`, `tryRemoteFetch`, `checkout`, and `mountRemote` are the main cache/snapshot pipeline.
- Helper functions handle signatures (`verifyGitSignature`), auth (`authSecretNames`, `getAuthToken`, `mountSSHAuthSock`, `mountKnownHosts`, `tokenScope`), default branch discovery, commit mtimes, file-mode compatibility, metadata indexing, and subdir safety.

## Control Flow
`Identifier` starts from `NewGitIdentifier`, applies source attrs, validates refs and bundle constraints, then `Resolve` creates a `gitSourceHandler`. `CacheKey` resolves metadata via direct SHA, fetch-by-commit, bundle staging, resolver cache, or `ls-remote`; it then shapes cache keys based on commit/tag SHA, `.git` retention, subdir, submodule skipping, mtime mode, and checkout bundle mode. `Snapshot` reuses a cached immutable snapshot when present; otherwise it performs `remoteFetch`, checks out either a worktree or bundle, stamps metadata, and commits an immutable ref.

`remoteFetch` serializes by remote URL, retries with reset when tags or refs conflict, and verifies that the fetched ref still matches the cache-commit chosen by `CacheKey`. `checkout` creates a mutable snapshot, handles `.git`-preserving clone/fetch versus plain tree checkout, updates submodules unless skipped, safely extracts subdirs only through directory components, normalizes compatibility file modes for old solver compatibility, optionally resets mtimes to commit time, remaps ownership for idmapped mounts, and commits the snapshot.

## State And Persistence
Persistent state is held in BuildKit cache refs. Shared bare repositories are mutable refs indexed by `git-remote::<remote>`. Snapshots are immutable refs indexed by `git-snapshot::<cacheKey>:<subdir>`. Resolver cache can store per-job `Metadata`. Temporary state includes SSH sockets, known-hosts files, bundle staging dirs, and checkout temp dirs; release paths are carefully deferred on error.

## Dependencies And Integration Points
Integrates with BuildKit cache, snapshot, solver job context, session/secrets/SSH forwarding, provenance attrs, `gitutil`, `gitobject`, `gitsign`, `pgpsign`, docker registry hosts for bundle blobs, and platform-specific `runWithStandardUmask`. It consumes many `pb.Attr*` source attrs and is routed by `source.Manager` using `srctypes.GitScheme`.

## Risks And Edge Cases
High-risk areas are ref mutability between cache-key and snapshot, annotated tag versus commit SHA semantics, bundle cleanup ownership, auth-secret scoping, file-protocol hardening, subdir traversal through symlinks, idmap ownership remapping, and shallow fetch behavior for unadvertised commits. Fetch-by-commit requires a full checksum. Checksum prefixes are accepted in some paths, so mismatch checks must remain consistent. `MTime` only affects cache keys when not `"checkout"`.

## Test Signals
`source_test.go` covers repeated fetches, SHA1/SHA256 repos, direct SHA and fetch-by-commit modes, stale branch pins, moved/deleted refs, mutated tags, annotated tags, `.git` retention, signatures, credential redaction, subdir extraction, submodule removal, bundle ref shape/SHA256 detection, commit mtime reset, and compatibility file modes.
