# subset-b-000029 research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source.go -->
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
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_darwin.go -->
# sources/cloud-native/buildkit/source/git/source_darwin.go

## Purpose
Provides Darwin-specific process attributes for the Unix reexec wrapper used to run Git commands with BuildKit's expected umask and process-group behavior.

## Important APIs, Types, And Functions
- `reexecSysProcAttr` is a package-level `unix.SysProcAttr` with `Setpgid: true`.

## Control Flow
This file has no functions. On `unix && !linux` builds, `source_unix_nolinux.go` uses this variable when reexecing the actual Git process.

## State And Persistence
No persistent state. It only configures process spawning behavior.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and is compiled only on Darwin. It integrates with `gitMain` in the non-Linux Unix helper.

## Risks And Edge Cases
Darwin lacks the FreeBSD `Pdeathsig` setting used in `source_freebsd.go`, so cancellation relies on process-group signal forwarding in the wrapper.

## Test Signals
Indirectly covered by non-Windows Git source tests when run on Darwin; no dedicated unit test targets this tiny platform shim.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_freebsd.go -->
# sources/cloud-native/buildkit/source/git/source_freebsd.go

## Purpose
Provides FreeBSD-specific process attributes for the Unix Git reexec wrapper.

## Important APIs, Types, And Functions
- `reexecSysProcAttr` sets `Setpgid: true` and `Pdeathsig: unix.SIGTERM`.

## Control Flow
The non-Linux Unix wrapper imports this variable, attaches it to the child Git command, and then forwards process-group signals on cancellation.

## State And Persistence
No persisted data. The file affects runtime process lifecycle only.

## Dependencies And Integration Points
Depends on `golang.org/x/sys/unix` and integrates with `source_unix_nolinux.go`.

## Risks And Edge Cases
Correctness depends on FreeBSD honoring `Pdeathsig` and process-group signaling as expected; platform drift can leave Git children alive after BuildKit cancellation.

## Test Signals
Covered indirectly by Git source tests on FreeBSD; there is no file-local test.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_linux.go -->
# sources/cloud-native/buildkit/source/git/source_linux.go

## Purpose
Runs Git subprocesses on Linux with a standard `0022` umask while isolating filesystem attributes from other goroutines and ensuring cancellation kills the whole process group.

## Important APIs, Types, And Functions
- `runWithStandardUmask(ctx, cmd)` launches a locked goroutine and delegates to `unshareAndRun`.
- `unshareAndRun` calls `syscall.Unshare(CLONE_FS)`, sets `Umask(0022)`, and runs the process group.
- `runProcessGroup` sets `Setpgid` and `Pdeathsig`, starts the command, and escalates from SIGTERM to SIGKILL after 10 seconds on context cancellation.

## Control Flow
`gitCLI` in `source.go` injects `runWithStandardUmask` as the executor. Each Git invocation is executed in its own process group; when the context is canceled, a goroutine signals the negative PID to terminate the group and starts a delayed kill fallback.

## State And Persistence
No cache state. It mutates only the child-thread umask after `CLONE_FS`, avoiding global process umask leakage.

## Dependencies And Integration Points
Uses `runtime.LockOSThread`, `syscall`, `os/exec`, `time`, and `x/sys/unix`. It is critical to Git snapshot mode tests that assume host test umask is reset to zero but Git output still uses standard permissions.

## Risks And Edge Cases
`CLONE_FS` failure aborts the Git command. Signal handling assumes process groups were created successfully. The SIGKILL fallback runs asynchronously after `Wait` coordination, so command implementations that spawn detached children remain a residual risk.

## Test Signals
Indirectly tested by the broad Git source suite and specifically by compatibility/file-mode tests that depend on stable Git-created permissions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_test.go -->
# sources/cloud-native/buildkit/source/git/source_test.go

## Purpose
Provides comprehensive integration-style tests for the Git source implementation across SHA1/SHA256 object formats, ref kinds, cache reuse, mutation races, submodules, signature verification, bundle handling, mtime normalization, and compatibility file modes.

## Important APIs, Types, And Functions
- Test helpers: `setupGitSource`, `setupGitRepo`, `serveGitRepo`, `runShell`, `runShellEnv`, `logProgressStreams`, `gitSnapshotMode`, and `gitRevParse`.
- Fixture types: `gitRepoFixture` and `testJobContext`.
- Major test families cover repeated fetch, fetch-by-SHA, fetch-by-commit, tags/refs/branches, race scenarios, multiple repos/tags, metadata objects, signatures, subdirs, bundle detection, mtimes, and compatibility modes.

## Control Flow
Tests build temporary Git repositories, often served through `git http-backend` via `httptest`. They construct `GitIdentifier` values, call `Resolve`, `CacheKey`, and `Snapshot`, mount resulting refs, and assert content, cache keys, pins, file modes, mtimes, and `.git` state. Race tests mutate remote refs after cache-key calculation and verify snapshot still uses the pinned commit or returns explicit errors if the pinned commit becomes unreachable.

## State And Persistence
Each test creates an isolated containerd/native snapshot cache and metadata DB. Temporary repos include branches, tags, annotated tags, signed commits/tags when fixture env is set, submodules, special refs, and generated bundles. Tests release refs and close snapshot/cache stores via cleanup.

## Dependencies And Integration Points
Exercises containerd metadata/content stores, native snapshotter, BuildKit cache manager, lease manager, progress logging, git CLI, CGI smart HTTP serving, signature fixtures (`BUILDKIT_TEST_SIGN_FIXTURES`), and solver compatibility versions.

## Risks And Edge Cases
Many tests are skipped on Windows due to missing bind-mount support. Signature tests are fixture-dependent. CGI smart HTTP tests depend on local `git` supporting requested object formats and bundle commands. Some assertions use exact cache-key strings and request counts, which catch regressions but can require updates when serialization changes intentionally.

## Test Signals
This file is itself the main signal for `source.go`: it validates deterministic cache reuse, mutation race protection, tag/branch ambiguity handling, fetch-by-commit semantics, credential redaction, submodule removal, signature policy behavior, bundle ref shape and SHA256 detection, mtime reset, and v0.13/v0.14 file-mode compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_unix_nolinux.go -->
# sources/cloud-native/buildkit/source/git/source_unix_nolinux.go

## Purpose
Implements the non-Linux Unix strategy for running Git with a standard umask by reexecing BuildKit itself as a small wrapper process.

## Important APIs, Types, And Functions
- `gitCmd` names the reexec entrypoint.
- `init` registers `gitMain` with `reexec`.
- `gitMain` sets umask, starts the real Git command, forwards signals, mirrors exit status, and exits.
- `runWithStandardUmask` rewrites the command path/args to invoke the reexec wrapper and applies cancellation signaling.

## Control Flow
Callers invoke `runWithStandardUmask`; it starts `reexec.Self()` with `umask-git` plus original args. The wrapper sets `Umask(0022)`, starts Git with OS-specific `reexecSysProcAttr`, forwards incoming signals to the child or child process group, waits, and exits with the child status where possible. Cancellation sends SIGTERM to the process group and escalates to SIGKILL after 10 seconds.

## State And Persistence
No persisted state. It affects per-process umask and process-group lifecycle.

## Dependencies And Integration Points
Depends on `github.com/moby/sys/reexec`, `os/signal`, `syscall`, and `x/sys/unix`. It uses `reexecSysProcAttr` supplied by Darwin/FreeBSD platform files.

## Risks And Edge Cases
Exit status translation depends on platform `WaitStatus` type. Signal forwarding treats SIGKILL like a forwarded signal even though SIGKILL cannot be caught by the wrapper. Detached grandchildren may survive if not in the process group.

## Test Signals
Indirectly covered by the Git source tests on supported non-Linux Unix platforms; `source_unix_test.go` creates a hostile umask baseline to expose regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_unix_nolinux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_unix_test.go -->
# sources/cloud-native/buildkit/source/git/source_unix_test.go

## Purpose
For non-Windows test runs, resets the process umask to zero so Git source tests cannot accidentally pass because of the host's normal umask.

## Important APIs, Types, And Functions
- `init` calls `syscall.Umask(0)`.

## Control Flow
The init function executes before tests in the package. Git subprocess wrappers are then responsible for applying `0022`, making file-mode tests meaningful.

## State And Persistence
Changes process-global test umask for the test binary lifetime.

## Dependencies And Integration Points
Depends on `syscall` and complements `runWithStandardUmask` implementations.

## Risks And Edge Cases
Because umask is process-global, any tests in the same package that expect host umask semantics would be affected. In this package that is intentional.

## Test Signals
Supports `TestCompatibility014FileModes` and ordinary checkout mode assertions by forcing a strict baseline.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_unix_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_windows.go -->
# sources/cloud-native/buildkit/source/git/source_windows.go

## Purpose
Provides a Windows-specific Git executor shim for the source backend.

## Important APIs, Types, And Functions
- `runWithStandardUmask(ctx, cmd)` starts the command, kills it on context cancellation, and waits.

## Control Flow
The function starts the Git process and spawns a goroutine that either kills the process when the context is done or returns when wait completes.

## State And Persistence
No persistent state and no umask manipulation; Windows does not use POSIX umask.

## Dependencies And Integration Points
Used by `gitCLI` in `source.go` on Windows builds. Depends only on `context` and `os/exec`.

## Risks And Edge Cases
Unlike Unix implementations, this kills only the direct process rather than a process group. Many Git source tests skip on Windows due to snapshotter bind-mount limitations, so Windows behavior has weaker direct coverage.

## Test Signals
Indirect coverage is limited; Windows-specific runtime is mostly guarded by compile-time build tags and broader package behavior where supported.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/git/source_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/identifier.go -->
# sources/cloud-native/buildkit/source/http/identifier.go

## Purpose
Defines the identifier model for BuildKit HTTP/HTTPS sources and their provenance capture behavior.

## Important APIs, Types, And Functions
- `NewHTTPIdentifier(str, tls)` prefixes `http://` or `https://` around the source ref.
- `HTTPIdentifier` stores URL, TLS mode, optional checksum, output filename, mode/owner, auth secret, allowed headers, and PGP signature verification options.
- `HTTPSignatureVerifyOptions` carries armored public key and detached signature bytes.
- `HeaderField` stores user-defined headers.
- `Scheme` returns `http` or `https`.
- `Capture` parses the pin digest and records an HTTP provenance source.

## Control Flow
`source/http.Source.Identifier` constructs this type, then applies attrs. During solve, `Source.Resolve` requires this concrete identifier and passes it to `httpSourceHandler`.

## State And Persistence
No persistence in this file. It is a value object copied into handler state.

## Dependencies And Integration Points
Uses BuildKit provenance capture, `source.Identifier`, source type constants, OCI digest parsing, and errors. It integrates with `source.Manager` via `Scheme`.

## Risks And Edge Cases
`NewHTTPIdentifier` unconditionally prepends the protocol to the `ref` portion supplied by `source.Manager`; callers must pass the post-scheme ref. `Capture` fails if the solver pin is not a valid digest.

## Test Signals
HTTP source tests indirectly validate pins, cache keys, and default naming; provenance capture is not deeply tested in the assigned files.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/identifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/source.go -->
# sources/cloud-native/buildkit/source/http/source.go

## Purpose
Implements the HTTP/HTTPS source backend: resolves remote or session-provided artifacts to digest metadata, caches downloaded bodies as immutable refs, reuses ETag-indexed refs, verifies optional signatures, computes optional metadata checksums, and materializes snapshots as single-file roots.

## Important APIs, Types, And Functions
- `Opt`, `Source`, `NewSource`, `Schemes`, `Identifier`, `Resolve`, and `ResolveMetadata` expose the BuildKit source boundary.
- `Metadata`, `MetadataOpts`, `MetadataChecksumRequest`, and `MetadataChecksumResponse` are metadata API objects.
- `httpSourceHandler` holds source identifier, cached resolution, cache accessor, transport, and session manager.
- `resolveMetadata`, `resolveMetadataStatic`, `resolveMetadataRef`, `CacheKey`, `Snapshot`, `save`, `newHTTPRequest`, `getFileName`, `verifySignature`, and `computeChecksumResponse` are the core operations.
- `cacheRefMetadata` stores `http.checksum`, `etag`, and `http.modtime` on cache refs.

## Control Flow
Identifier parsing applies digest, filename, permissions, ownership, auth, signature, and supported header attrs. Metadata resolution short-circuits when a checksum is pinned; otherwise it computes a URL/options hash, tries resolver cache, searches cache metadata, performs conditional HEAD/GET with known ETags, saves new responses when needed, validates pinned checksums, and records `resolved.refID`. `CacheKey` formats filename, digest, mtime, ownership, auth, and headers into a stable JSON digest. `Snapshot` returns the resolved ref when available, falls back to resolver-cache ref lookup, or performs a new GET/save and checks digest consistency.

## State And Persistence
Downloaded content is persisted in immutable refs with a single sanitized filename. ETags and Last-Modified values are stored as metadata, with ETag search indexed by a digest of URL and relevant source options. Job cleanup retains refs across cache-key/snapshot flow until the job releases them. File mtimes are set from Last-Modified or Unix zero, and UID/GID are mapped through idmapped mounts.

## Dependencies And Integration Points
Uses BuildKit cache/snapshot/session/secrets/solver APIs, source attrs from `pb`, tracing default transport, `pathutil.SafeFileName`, `cachedigest`, PGP verification, and version user agent. `transport.go` adds a special `buildkit-session` host for session uploads.

## Risks And Edge Cases
Only `Accept` and `User-Agent` user headers survive. Auth secret lookup through `hs.sm.Any` assumes a session manager is available; implicit host-based secrets are ignored on missing secret unless an explicit auth secret was requested. Some servers mishandle conditional requests, so the code uses HEAD first and falls back to GET. `etagValue` only strips weak prefixes and does not parse comma lists. Signature/checksum requests force a real cached ref even when static checksum metadata exists.

## Test Signals
`source_test.go` covers ETag reuse, default filename fallback, invalid HTTP status, pinned checksum mismatch and success, PGP detached signature verification, and cache retention after `CacheKey` while a job cleanup holds the ref.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/source_test.go -->
# sources/cloud-native/buildkit/source/http/source_test.go

## Purpose
Tests the HTTP source backend's digest/cache-key behavior, ETag cache reuse, filename fallback, checksum pinning, signature verification, and job-context retention through pruning.

## Important APIs, Types, And Functions
- `TestHTTPSource`, `TestHTTPDefaultName`, `TestHTTPInvalidURL`, `TestHTTPChecksum`, `TestHTTPSignatureVerification`, and `TestPruneAfterCacheKey`.
- Helpers `readFile`, `newHTTPSource`, `newCacheManager`, `simpleJobContext`, and `readSignFixture`.

## Control Flow
Tests create an in-memory HTTP test server, resolve a source, call `CacheKey`, assert request counters and expected digest strings, call `Snapshot`, mount refs, and read payload files. The prune test holds cleanup functions in `simpleJobContext`, prunes the cache, mutates server content, and verifies the original ref is still used until the job context releases it.

## State And Persistence
Each test uses a temporary BuildKit cache manager backed by native snapshotter, containerd metadata/content stores, bbolt, and metadata DB. HTTP server route state is mutated to simulate changed ETags/content. Signature tests depend on optional signing fixtures.

## Dependencies And Integration Points
Exercises BuildKit cache, snapshots, leases, source interfaces, test HTTP server, identity ETags, OCI digests, and winlayers wrappers.

## Risks And Edge Cases
Expected cache-key strings are tied to JSON serialization shape. Signature tests skip without `BUILDKIT_TEST_SIGN_FIXTURES`. The checksum test demonstrates that static checksum metadata avoids network during `CacheKey` but still requires network during `Snapshot`.

## Test Signals
Strong regression signals around conditional-request counts, digest mismatch errors, retained refs after prune, and filename `download` fallback.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/source_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/transport.go -->
# sources/cloud-native/buildkit/source/http/transport.go

## Purpose
Wraps an HTTP transport so URLs with host `buildkit-session` can be served from BuildKit client session uploads instead of the network.

## Important APIs, Types, And Functions
- `newTransport(rt, sm, g)` returns a `sessionHandler`.
- `sessionHandler.RoundTrip` delegates ordinary hosts to the wrapped transport and intercepts `buildkit-session` GET requests.

## Control Flow
For non-session hosts, `RoundTrip` calls `rt.RoundTrip`. For `buildkit-session`, it rejects non-GET methods, selects a session caller with `sm.Any`, creates an `upload.New` reader for the URL, pipes upload content into an `io.Pipe`, and returns a synthetic `200 OK` response with streaming body.

## State And Persistence
No persisted state. It streams data from the session and does not set cache metadata itself.

## Dependencies And Integration Points
Integrates HTTP source downloads with BuildKit session upload service and the source handler's session group.

## Risks And Edge Cases
Uses `context.TODO` for session selection and upload creation rather than the request context. Response lacks headers such as filename, length, etag, or last-modified, so normal HTTP metadata reuse is unavailable for session uploads.

## Test Signals
No dedicated tests in the assigned file set; it is indirectly used if HTTP sources address `buildkit-session`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/http/transport.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/identifier.go -->
# sources/cloud-native/buildkit/source/identifier.go

## Purpose
Defines the common interface all BuildKit source identifiers implement.

## Important APIs, Types, And Functions
- `Identifier` requires `Scheme()` for routing and `Capture(*provenance.Capture, pin)` for provenance recording.
- Package errors `errInvalid` and `errNotFound` are used by the manager for parse and scheme failures.

## Control Flow
Concrete source packages implement `Identifier`; `Manager.Resolve` uses `Scheme()` to find the registered source, and solver/provenance paths call `Capture` after a source pin is known.

## State And Persistence
No runtime state beyond static error values.

## Dependencies And Integration Points
Imports BuildKit provenance and pkg/errors. Used by `source.Manager`, git/http/local identifiers, and other source backends outside this subset.

## Risks And Edge Cases
The interface keeps source contracts small; errors are unexported, so callers match wrapped messages/types only within package usage.

## Test Signals
Indirectly tested by all source manager and backend resolution tests; no local unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/identifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/local/identifier.go -->
# sources/cloud-native/buildkit/source/local/identifier.go

## Purpose
Defines the identifier for local/session-provided source trees and provenance capture for local sources.

## Important APIs, Types, And Functions
- `LocalIdentifier` stores name, session ID, include/exclude/follow patterns, shared key hint, differ mode, metadata-only transfer flag, and metadata exceptions.
- `NewLocalIdentifier` creates a name-only identifier.
- `Scheme` returns `local`.
- `Capture` records a provenance local source by name.

## Control Flow
`localSource.Identifier` populates this struct from source attrs. The handler uses it to generate cache keys and configure file sync.

## State And Persistence
No persistence in this file. The struct controls cache-key and sync behavior in `source.go`.

## Dependencies And Integration Points
Uses provenance types, source interface, source type constants, and `fsutil.DiffType`.

## Risks And Edge Cases
Local provenance captures only the logical source name, not include/exclude patterns or session identity. More detailed state is encoded in cache keys by the handler.

## Test Signals
No direct tests in this subset; behavior is exercised through local source integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/local/identifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/local/source.go -->
# sources/cloud-native/buildkit/source/local/source.go

## Purpose
Implements BuildKit's local source backend, synchronizing files from a client session into a cache ref and producing immutable snapshots for local contexts.

## Important APIs, Types, And Functions
- `Opt`, `NewSource`, `localSource`, `Schemes`, `Identifier`, and `Resolve` expose the source implementation.
- `localSourceHandler.CacheKey` hashes session ID and transfer filters into a session cache key.
- `Snapshot`, `snapshotWithAnySession`, and `snapshot` perform session selection and file sync.
- `newProgressHandler` reports transfer progress.
- `cacheUpdater` bridges fsutil content hashing into BuildKit contenthash cache.
- `searchSharedKey` and `cacheRefMetadata` persist and find reusable mutable refs by local shared key.

## Control Flow
`Identifier` parses attrs for session ID/name prefixing, include/exclude/follow patterns, shared key hints, differ mode, metadata-only transfer, and metadata exceptions. `CacheKey` chooses an explicit session or the next available session from the job group and hashes transfer options. `Snapshot` prefers an explicit session with a 5-second lookup and falls back to any session if unavailable or invalid. `snapshot` reuses or creates a mutable ref, mounts it, obtains contenthash context, configures `filesync.FSSendRequestOpt`, applies metadata-only exception and idmap filters, runs `filesync.FSSync`, persists contenthash context and shared-key metadata, then commits the mutable ref.

## State And Persistence
Mutable refs are reused using `local.sharedKey:<name>:<hint>:<caller.SharedKey()>[:metadata]`. Content hash state is stored with the mutable ref to support incremental file sync. On sync errors, cache policy is reset to default, contenthash context is cleared, and the mutable ref is released asynchronously.

## Dependencies And Integration Points
Depends on BuildKit cache/contenthash/session/filesync/snapshot/solver/progress, `pb` attrs, `patternmatcher`, `fsutil`, and idmap utilities. Integrates tightly with client sessions rather than remote transports.

## Risks And Edge Cases
`CacheKey` requires `jobCtx` and a session when `SessionID` is absent. Fallback from explicit session to any session may hide stale session IDs but improves robustness. Metadata-only exceptions rely on pattern matching and return false on matcher errors. Reusing mutable refs is sensitive to shared-key uniqueness and caller shared-key stability.

## Test Signals
No assigned local tests. Coverage is likely in broader BuildKit local source/file sync tests; this subset has no direct assertions for metadata-only transfer or shared-key reuse.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/local/source.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/manager.go -->
# sources/cloud-native/buildkit/source/manager.go

## Purpose
Provides the registry and router for BuildKit source implementations.

## Important APIs, Types, And Functions
- `Source` interface defines `Schemes`, `Identifier`, and `Resolve`.
- `SourceInstance` interface defines `CacheKey` and `Snapshot`.
- `Manager` stores a mutex-protected scheme-to-source map.
- `NewManager`, `Register`, `Identifier`, and `Resolve` are the public operations.

## Control Flow
Backends register themselves by scheme. For an LLB `Op_Source`, `Identifier` splits `scheme://ref`, finds the backend, and delegates identifier construction with attrs and platform. Later, `Resolve` routes the concrete identifier by `id.Scheme()` to create a source instance.

## State And Persistence
In-memory map only. Register overwrites duplicate schemes with the latest source.

## Dependencies And Integration Points
Imports BuildKit cache, session, solver, protobuf ops, and pkg/errors. All source backends in this subset implement these interfaces.

## Risks And Edge Cases
Parsing requires `://`; opaque identifiers without that separator fail. The manager trusts `id.Scheme()` on resolve, so mismatched identifier objects can route unexpectedly if a custom identifier lies about its scheme.

## Test Signals
No direct tests in this subset, but every source backend depends on this contract.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/types/types.go -->
# sources/cloud-native/buildkit/source/types/types.go

## Purpose
Centralizes string constants for supported source schemes.

## Important APIs, Types, And Functions
- Constants include docker image, docker image blob, git, local, http, https, oci-layout, and oci-layout blob schemes.

## Control Flow
No control flow. Source backends import these constants to advertise and validate schemes.

## State And Persistence
No state.

## Dependencies And Integration Points
Used by git, HTTP, local, OCI, and blob-fetch related code to keep scheme strings consistent.

## Risks And Edge Cases
Changing these string constants is a compatibility break for LLB source identifiers and frontend attrs.

## Test Signals
Indirectly tested by source parsing and backend registration tests across the codebase.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/types/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/util/pathutil/pathutil.go -->
# sources/cloud-native/buildkit/source/util/pathutil/pathutil.go

## Purpose
Sanitizes untrusted filename strings for source backends that need to materialize a single file.

## Important APIs, Types, And Functions
- `SafeFileName(s string) string` trims whitespace, converts slash paths to OS paths, takes the base name, rejects empty/dot/dotdot names and names containing NUL or Unicode control characters, and falls back to `"download"`.

## Control Flow
The function applies `filepath.Base(filepath.FromSlash(strings.TrimSpace(s)))`, validates simple unsafe cases, scans runes for NUL/control characters, and returns either the sanitized base or default.

## State And Persistence
No state. Used at file creation time by HTTP source.

## Dependencies And Integration Points
Depends on `filepath`, `strings`, and `unicode`. `http.getFileName` uses it for manual filenames, `Content-Disposition`, URL path basenames, and default fallback.

## Risks And Edge Cases
Backslash path handling is OS-dependent: on Unix, backslashes remain literal; on Windows, `filepath.Base` treats them as separators. It does not reject reserved Windows device names or path names with ordinary separators after basename extraction.

## Test Signals
`pathutil_test.go` covers unicode preservation, whitespace trimming, Unix paths, traversal-ish inputs, control/NUL rejection, and OS-specific Windows backslash behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/util/pathutil/pathutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/source/util/pathutil/pathutil_test.go -->
# sources/cloud-native/buildkit/source/util/pathutil/pathutil_test.go

## Purpose
Tests filename sanitization behavior for HTTP/local source utility code.

## Important APIs, Types, And Functions
- `TestSafeFileName` uses table-driven cases with parallel subtests.

## Control Flow
The test builds common cases, appends OS-specific cases for Windows or non-Windows, then asserts `SafeFileName` output for each input.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses `runtime.GOOS`, `testing`, and `testify/require`.

## Risks And Edge Cases
The test intentionally documents OS-specific behavior for backslashes, so cross-platform changes to path handling will surface as test changes.

## Test Signals
Validates default `"download"` fallback and safe preservation of Unicode and spaces while rejecting empty, dot, dotdot, NUL, and control-character names.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/source/util/pathutil/pathutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/engine.go -->
# sources/cloud-native/buildkit/sourcepolicy/engine.go

## Purpose
Implements BuildKit's source policy evaluator, allowing policies to allow, deny, or convert source operations before normal source resolution.

## Important APIs, Types, And Functions
- Errors `ErrSourceDenied` and `ErrTooManyOps`.
- `Engine` stores policies and a selector cache map.
- `NewEngine`, `selectorCache`, `Evaluate`, `evaluatePolicies`, and `evaluatePolicy`.

## Control Flow
`Evaluate` returns immediately for no policies or nil ops. Otherwise it repeatedly evaluates policies, because convert rules mutate the source and may trigger more rules. It stops when no mutation occurs or errors after more than 20 iterations. `evaluatePolicy` walks rules in order, matches selectors and constraints, tracks allow/deny with last matching allow/deny winning, short-circuits on conversion mutation, and returns `ErrSourceDenied` if the final deny flag is set.

## State And Persistence
State is in-memory only. Selector regex/wildcard compilation is cached in `sources` behind `sourcesMu`. Source ops are mutated in place.

## Dependencies And Integration Points
Uses solver `pb.SourceOp`, sourcepolicy protobuf types, matcher/mutator helpers, BuildKit logging, pkg/errors, and logrus fields.

## Risks And Edge Cases
Selector cache keys ignore attr constraints, as noted by TODO; this is safe for compiled identifier patterns but not a place to cache constraint regexes. Convert loops rely on the fixed 20-iteration limit. If a mutation occurs and a later evaluation denies, callers receive both `mutated=true` and an error.

## Test Signals
`engine_test.go` covers deny all, allow/deny order, conversion chains, exact/regex/wildcard conversion, HTTP attr conversion, loops, multiple policies, and last-rule-wins behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/engine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/engine_test.go -->
# sources/cloud-native/buildkit/sourcepolicy/engine_test.go

## Purpose
Tests source policy evaluation semantics across allow, deny, conversion, loop protection, multiple policies, and match types.

## Important APIs, Types, And Functions
- `TestEngineEvaluate` orchestrates subtests.
- Helper subtests include `testDenyAll`, `testAllowDeny`, `testConvert`, `testConvertExact`, `testConvertDeny`, `testAllowConvertDeny`, `testConvertLoop`, `testConvertHTTP`, `testConvertRegex`, `testConvertWildcard`, `testConvertMultiple`, `testMultiplePolicies`, and `testLastRuleWins`.

## Control Flow
Each subtest builds protobuf policy rules and source ops, evaluates with `NewEngine`, and asserts mutation booleans, errors, and final identifiers/attrs. Conversion tests rely on repeated evaluation after mutation; loop tests expect `ErrTooManyOps`.

## State And Persistence
No persistence. Source ops are intentionally mutated in memory during assertions.

## Dependencies And Integration Points
Uses solver protobuf source ops, sourcepolicy protobufs, BuildKit logger, logrus, and `testify/require`.

## Risks And Edge Cases
Tests document important policy semantics: last allow/deny rule wins within a policy, multiple policies are evaluated sequentially, and conversion can be followed by denial.

## Test Signals
Strong coverage for engine orchestration but does not directly test selector-cache concurrency.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/engine_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/formatter.go -->
# sources/cloud-native/buildkit/sourcepolicy/formatter.go

## Purpose
Caches selector-specific compiled matchers and formats converted destination identifiers using exact, regex, or wildcard capture semantics.

## Important APIs, Types, And Functions
- `selectorCache` embeds `*spb.Selector` and lazily caches regex and wildcard compilers.
- `newSelectorCache` initializes `sync.OnceValues` closures.
- `(*selectorCache).Format` applies format rules.
- `wildcardCache` caches wildcard matches by input ref.
- `(*wildcardCache).Match` is mutex-protected.

## Control Flow
Exact format returns the target string. Regex format compiles the selector regex once and uses `ReplaceAllString`. Wildcard format compiles the wildcard once, matches the current ref, and formats placeholders from captured groups; if the ref no longer matches, it returns the original match string.

## State And Persistence
In-memory compiled regex/wildcard and per-ref wildcard match cache only.

## Dependencies And Integration Points
Used by `mutate` for convert rules and by `match` for wildcard/regex selector behavior. Depends on BuildKit wildcard utility and protobuf enum values.

## Risks And Edge Cases
Regex replacement uses Go regexp replacement syntax, so policy authors must use supported placeholder syntax. Returning the original match when wildcard formatting does not match can hide unexpected non-matches if callers do not already ensure matching.

## Test Signals
Engine tests cover regex and wildcard conversion formatting; matcher tests cover matching behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/formatter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/matcher.go -->
# sources/cloud-native/buildkit/sourcepolicy/matcher.go

## Purpose
Determines whether a source operation matches a policy selector and its attribute constraints.

## Important APIs, Types, And Functions
- `match(src, ref, constraints, attrs)` returns a boolean match or error.

## Control Flow
The function first validates all attr constraints: equality, inequality, and regex matching against the op attrs. Any failed constraint returns false. Then it checks direct identifier equality, exact mode, regex mode via cached selector regex, wildcard mode via cached wildcard matcher, or errors on unknown match type.

## State And Persistence
No persistence. Regex constraints are compiled per call; selector identifier regex/wildcard compilers are cached in `selectorCache`.

## Dependencies And Integration Points
Used by `Engine.evaluatePolicy`. Depends on `regexp`, sourcepolicy protobufs, and pkg/errors.

## Risks And Edge Cases
Nil constraints and unknown enum values are errors. Missing attrs behave as empty string, so `NOTEQUAL` constraints can match missing keys when the value is non-empty. Constraint regexes are not cached despite the engine TODO.

## Test Signals
`matcher_test.go` covers exact, wildcard, scheme-sensitive matches, attr equality/inequality/regex constraints, missing attrs, multiple constraints, and invalid condition errors.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/matcher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/matcher_test.go -->
# sources/cloud-native/buildkit/sourcepolicy/matcher_test.go

## Purpose
Tests source policy selector matching and attribute constraint behavior.

## Important APIs, Types, And Functions
- `TestMatch` defines table-driven cases for `match`.

## Control Flow
Each case constructs a selector, ref, optional attrs, expected boolean, and expected error flag. The test wraps the selector with `newSelectorCache`, calls `match`, and asserts the result.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Uses sourcepolicy protobuf selector/constraint enums and `testify/require`.

## Risks And Edge Cases
The table documents that wildcard `*` can match full source identifiers, scheme mismatch prevents more specific wildcard matches, default constraint condition is equality, and unknown attr conditions are errors.

## Test Signals
Provides focused coverage for matching before engine-level allow/deny/convert behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/matcher_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/mutate.go -->
# sources/cloud-native/buildkit/sourcepolicy/mutate.go

## Purpose
Applies a source policy convert rule to a BuildKit source operation.

## Important APIs, Types, And Functions
- `mutate(ctx, op, rule, selector, ref)` changes `op.Identifier` and/or `op.Attrs`.

## Control Flow
The function requires `rule.Updates`, chooses the update identifier or falls back to the selector identifier, formats it through the selector cache, updates the source identifier if changed, ensures the attrs map exists, writes changed attr values, logs conversions and attr updates, and returns whether anything changed.

## State And Persistence
Mutates the supplied protobuf `SourceOp` in place. No persisted state.

## Dependencies And Integration Points
Called by `Engine.evaluatePolicy` for `CONVERT` rules. Uses BuildKit logging and sourcepolicy protobuf update fields.

## Risks And Edge Cases
Missing `Updates` is an error. Empty destination falls back to selector identifier, so rules that only set attrs still may format a selector-derived identifier. Existing attrs are overwritten without delete support.

## Test Signals
`mutate_test.go` covers identifier rewrites, digest replacement, HTTP checksum attr insertion, and proto equality after mutation.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/mutate.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/mutate_test.go -->
# sources/cloud-native/buildkit/sourcepolicy/mutate_test.go

## Purpose
Tests convert-rule mutation of BuildKit source ops.

## Important APIs, Types, And Functions
- `TestMutate` table drives `mutate` against `pb.Op_Source` wrappers and expected protobuf results.

## Control Flow
Each case extracts the source op, calls `mutate` with a selector cache and current identifier, asserts the mutation boolean and either an expected error or protobuf equality with the expected op.

## State And Persistence
No persistence. The input op is modified in place.

## Dependencies And Integration Points
Uses solver protobuf ops, sourcepolicy protobuf rules, `proto.Equal`, and `testify/require`.

## Risks And Edge Cases
The tests cover overwriting an already resolved image digest and adding HTTP checksum attrs, but do not cover nil updates despite the production error path.

## Test Signals
Focused signal that mutation correctly rewrites identifiers and initializes/updates attrs maps.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/mutate_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/json.go -->
# sources/cloud-native/buildkit/sourcepolicy/pb/json.go

## Purpose
Adds custom JSON marshal/unmarshal behavior for sourcepolicy enum types so policies can use readable enum names.

## Important APIs, Types, And Functions
- `PolicyAction.MarshalJSON` / `UnmarshalJSON`.
- `AttrMatch.MarshalJSON` / `UnmarshalJSON`.
- `MatchType.MarshalJSON` / `UnmarshalJSON`.

## Control Flow
Marshal calls BuildKit's gogo proto JSON enum helper with enum name maps. Unmarshal accepts string or numeric JSON, validates that the decoded numeric value exists in the enum name map, and assigns it.

## State And Persistence
No persistent state. It uses generated enum name/value maps.

## Dependencies And Integration Points
Used whenever policies are JSON encoded/decoded. Depends on `util/gogo/proto` helpers and pkg/errors.

## Risks And Edge Cases
`MatchType.UnmarshalJSON` validates against `AttrMatch_name` instead of `MatchType_name`, which works only because both enums currently have values 0..2; adding divergent enum values would incorrectly reject/accept values.

## Test Signals
`json_test.go` round-trips all current enum values by string and number, but would not catch the wrong validation map while enum numeric ranges remain identical.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/json.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/json_test.go -->
# sources/cloud-native/buildkit/sourcepolicy/pb/json_test.go

## Purpose
Tests JSON string and numeric round-tripping for sourcepolicy enum types.

## Important APIs, Types, And Functions
- `TestActionJSON`, `TestAttrMatchJSON`, and `TestMatchTypeJSON`.

## Control Flow
Each test iterates the generated enum name map, marshals enum values to JSON strings, unmarshals strings back, marshals numeric values, and unmarshals numbers back to equivalent enum values.

## State And Persistence
No state.

## Dependencies And Integration Points
Uses Go `encoding/json`, generated protobuf enum maps, and `testify/require`.

## Risks And Edge Cases
The tests do not exercise invalid enum values. Because current enum numeric ranges align, they do not detect `MatchType.UnmarshalJSON` validating against the wrong enum map.

## Test Signals
Confirms human-readable JSON compatibility for all currently generated enum values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/json_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/policy.pb.go -->
# sources/cloud-native/buildkit/sourcepolicy/pb/policy.pb.go

## Purpose
Generated Go bindings for the source policy protobuf schema.

## Important APIs, Types, And Functions
- Enums `PolicyAction`, `AttrMatch`, and `MatchType` with name/value maps and descriptor methods.
- Messages `Rule`, `Update`, `Selector`, `AttrConstraint`, and `Policy` with protobuf reflection methods and getters.
- File descriptor globals, raw descriptor compression, dependency indexes, and `TypeBuilder` initialization.

## Control Flow
Runtime control flow is generated boilerplate: enum string/descriptor methods delegate to `protoimpl`, message methods manage protobuf reflection state, getters return zero defaults on nil receivers, and init builds the file descriptor once.

## State And Persistence
Generated descriptor globals are initialized once in memory. Message structs carry protobuf state, unknown fields, and size cache.

## Dependencies And Integration Points
Consumed by sourcepolicy engine, matcher, mutator, JSON helpers, and policy readers. Depends on `google.golang.org/protobuf` reflection/runtime packages.

## Risks And Edge Cases
Manual edits would be overwritten by regeneration. Schema/default changes affect policy semantics because nil or omitted enum fields default to `ALLOW`, `EQUAL`, and `WILDCARD`.

## Test Signals
Covered indirectly by engine/matcher/mutate/json tests. Regeneration consistency is tied to `policy.proto`.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/policy.pb.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/policy.proto -->
# sources/cloud-native/buildkit/sourcepolicy/pb/policy.proto

## Purpose
Defines the source policy protobuf schema used to allow, deny, or convert BuildKit source operations.

## Important APIs, Types, And Functions
- `Rule` has `action`, `selector`, and `updates`.
- `Update` has destination `identifier` and attr map.
- `Selector` has source `identifier`, `match_type`, and repeated attr constraints.
- `AttrConstraint` has key, value, and condition.
- `Policy` has version and repeated rules.
- Enums: `PolicyAction` (`ALLOW`, `DENY`, `CONVERT`), `AttrMatch` (`EQUAL`, `NOTEQUAL`, `MATCHES`), and `MatchType` (`WILDCARD`, `EXACT`, `REGEX`).

## Control Flow
The proto itself has no runtime flow, but generated code and engine logic interpret rules in order. Defaults matter: zero values mean allow action, wildcard matching, and equality constraints.

## State And Persistence
Policies serialized from this schema are the durable policy representation. `version` is documented as currently 1.

## Dependencies And Integration Points
The `go_package` maps generated bindings to `github.com/moby/buildkit/sourcepolicy/pb;moby_buildkit_v1_sourcepolicy`. Engine, matcher, mutator, and JSON helpers consume the generated Go types.

## Risks And Edge Cases
Typos in comments (`due`, `litteral`) are harmless but visible in generated docs. Adding enum values requires updating JSON validation tests and fixing enum-specific validation logic.

## Test Signals
All sourcepolicy tests exercise generated types from this schema; JSON tests validate enum serialization for current values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/sourcepolicy/pb/policy.proto -->
