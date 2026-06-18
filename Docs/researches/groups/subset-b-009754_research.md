# subset-b-009754 research

Grouped research report for subset-b-009754. Each section preserves the source path and is bounded by reconciliation markers.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/seafile.go -->
# sources/user-network-fs/rclone/backend/seafile/seafile.go

Purpose: implements the rclone `seafile` backend `fs.Fs` surface, mapping rclone operations onto Seafile libraries and paths. It registers config options for server URL, user/password or saved 2FA token, optional library scoping, encrypted library keys, library creation, and path encoding.

Important APIs/types/functions: `Options` holds remote configuration; `Fs` stores root/library state, REST client, pacer, library cache, feature flags, auth locks, directory creation locks, and encrypted-library renewal. `NewFs` parses config, reveals obscured secrets, checks server version, authenticates, optionally creates/decrypts a selected library, configures feature availability, and handles file-root detection. `Config` is the 2FA state machine. Public rclone methods include `List`, `NewObject`, `Put`, `PutStream`, `Mkdir`, `Rmdir`, `ListR`, `Copy`, `Move`, `DirMove`, `Purge`, `CleanUp`, `About`, `UserInfo`, `PublicLink`, `Shutdown`, plus helpers such as `splitPath`, `buildDirEntries`, `getCachedLibraries`, and `mkMultiDir`.

Control flow: all paths are interpreted as either `library/path` or as paths under the configured library/root directory. Listing root without a configured library returns libraries as directories; otherwise listing resolves a library ID and delegates to API v2/v2.1 helpers. Upload creates a library on demand when possible, then delegates to `Object.Update`. Server-side copy/move ensure destination directories, call Seafile copy/move APIs, then repair Seafile's conflict-renamed target via `adjustDestination`. Directory moves use direct rename when possible, otherwise a random temporary name around Seafile's cross-directory move behavior.

State and persistence: library metadata is cached in `cache.Cache` under `librariesCacheKey`; `createLibraryMutex` serializes global library creation, and `librariesMutex` protects cache access. Encrypted libraries can start a `Renew` loop that periodically re-authorizes the library token. `Config` persists `auth_token` after successful 2FA and clears the password.

Dependencies/integration: depends on rclone `fs`, `configstruct`, `obscure`, `bucket`, `encoder`, `rest`, `pacer`, Seafile API DTOs, and `go-semver`. Implements many optional rclone interfaces and disables unsupported features based on server version and library encryption.

Risks/test signals: path splitting, library cache freshness, concurrent library/directory creation, encrypted library renewal, and Seafile conflict rename semantics are high-risk. Tests in `seafile_internal_test.go` cover path splitting and 2FA states; `seafile_test.go` delegates broad behavior to rclone integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/seafile.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/seafile_internal_test.go -->
# sources/user-network-fs/rclone/backend/seafile/seafile_internal_test.go

Purpose: unit tests private Seafile backend path and configuration behavior that does not require a live Seafile server.

Important APIs/types/functions: `pathData` defines cases for `Fs.splitPath`, combining configured library, configured root, command argument path, and expected library/path output. `TestSplitPath` instantiates minimal `Fs` values and verifies path decomposition. `TestSplitPathIntoSlice` covers the package-level `splitPath` helper used by recursive directory creation. `Test2FAStateMachine` exercises `Config` with `configmap.Simple` and `fs.ConfigIn`.

Control flow: `TestSplitPath` enumerates unrooted and library-rooted remotes, including empty roots, single library names, nested file paths, and configured root prefixes. The 2FA test drives `Config` through initial state, password prompting, password validation, 2FA prompt, blank-code retry, explicit retry after failure, and terminal failure. It does not mock a successful token exchange, so network-dependent `2fa_do` success is intentionally absent.

State and persistence behavior: tests assert mapper mutation indirectly for password entry by following the next state, and use obscured config password for the "ready for token" path. They verify that no output is returned when 2FA is disabled.

Dependencies/integration: uses rclone `fs.ConfigIn`, `configmap.Simple`, `obscure`, and `testify` assertions. It targets private functions in package `seafile`, not external package tests.

Risks/test signals: good coverage for path-root semantics and the interactive 2FA state machine. Missing signals include successful 2FA token persistence, HTTP token failure variants, library cache behavior, encrypted-library authorization, and Seafile object operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/seafile_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/seafile_test.go -->
# sources/user-network-fs/rclone/backend/seafile/seafile_test.go

Purpose: external integration test entry point for the Seafile backend.

Important APIs/types/functions: `TestIntegration` invokes `fstests.Run` with `RemoteName: "TestSeafile:"` and `NilObject: (*seafile.Object)(nil)`.

Control flow: when the rclone test harness is configured with a `TestSeafile` remote, the generic filesystem test suite performs create, list, update, copy/move, delete, directory, and feature checks according to the backend's advertised capabilities. This file contains no backend logic itself.

State and persistence behavior: all persistent effects are on the configured live Seafile remote and the rclone test framework. The test relies on external configuration and credentials.

Dependencies/integration: imports the backend package as an external consumer and `github.com/rclone/rclone/fstest/fstests`. This verifies public interface conformance rather than private helper behavior.

Risks/test signals: broad live coverage is valuable for API drift, auth, library handling, and object operations, but it is environment-dependent and not deterministic in ordinary unit runs. It does not isolate specific failure paths; those require targeted unit tests or mocked REST tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/seafile_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/webapi.go -->
# sources/user-network-fs/rclone/backend/seafile/webapi.go

Purpose: low-level Seafile Web API adapter used by `seafile.go` and object code. It translates backend actions into REST calls, encodes/decodes names and paths, maps selected HTTP statuses to rclone errors, and handles upload/download link mechanics.

Important APIs/types/functions: constants `APIv20` and `APIv21` select Seafile API roots; `ErrorInternalDuringUpload` signals retryable single-use upload-link failure. Functions cover account auth, server/account info, library CRUD/decrypt/trash cleanup, directory list/detail/create/rename/move/delete, file detail/delete/download/upload/share-link/copy/move/rename, and `decodeFileInfo`.

Control flow: most functions build `rest.Opts`, call through `f.pacer`, and use `f.shouldRetry`. JSON APIs use `CallJSON`; form-only Seafile endpoints manually build URL-encoded bodies. `getAuthorizationToken` is intentionally callable without an `Fs` for configuration-time 2FA. Upload first gets a single-use upload URL elsewhere, posts multipart data, and treats HTTP 500 as `ErrorInternalDuringUpload` so callers can fetch a new link. Download accepts absolute or relative download links and compensates when encrypted libraries ignore HTTP range requests by discarding bytes client-side and wrapping a limited reader.

State and persistence behavior: this file mostly has no durable state, but it mutates decoded API result fields into rclone standard encoding and relies on the shared pacer. It consumes auth headers already installed on `f.srv`.

Dependencies/integration: depends on rclone `rest`, `fs`, `readers`, Seafile API DTOs, `net/url`, `net/http`, and `encoder` behavior via `f.opt.Enc`. It is tightly integrated with `seafile.go` path/library resolution and `Object` upload/download.

Risks/test signals: high-risk areas are undocumented API v2.1 endpoints, inconsistent status mapping, form-body encoding, single-use upload URLs, and client-side range emulation for encrypted libraries. No direct tests are listed for this file; integration tests are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/seafile/webapi.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp.go -->
# sources/user-network-fs/rclone/backend/sftp/sftp.go

Purpose: implements rclone's SFTP backend on top of `github.com/pkg/sftp`, supporting internal Go SSH or an external `ssh` binary, connection pooling, directory/object operations, optional hardlink copy, remote-shell hashing, quota discovery, and platform-specific path handling.

Important APIs/types/functions: `Options` exposes host/auth/key/certificate/agent/proxy/cipher/hash/shell/path/chunk/concurrency settings. `Fs` stores root paths, SSH config, feature flags, connection pool, token dispenser, pacer, hash cache, and session count. `Object` caches stat data and checksums. Core functions include `NewFs`, `NewFsWithConnection`, `sftpConnection`, `getSftpConnection`, `putSftpConnection`, `drainPool`, `newSftpClient`, `List`, `Put`, `Mkdir`, `Rmdir`, `Move`, `Copy`, `DirMove`, `run`, `Hashes`, `About`, `remotePath`, `remoteShellPath`, `quoteOrEscapeShellPath`, `parseHash`, `parseUsage`, `Open`, `Update`, and `Remove`.

Control flow: initialization builds SSH auth methods from agent, key files/PEM, certs, password, or ask-password callback; configures host-key validation; applies cipher/KEX/MAC options; opens an early connection; auto-detects remote shell type; canonicalizes root; and detects file-root remotes. Operations borrow pooled connections, return reusable ones, and validate questionable connections after non-ordinary errors. Uploads hold a connection for the full file write, clear cached hashes, remove failed partial uploads, then set or infer modtime. Reads open an SFTP file and pump it through a pipe reader with session accounting.

State and persistence behavior: connection pool and idle timer are in-memory; `connections` uses a token dispenser. Shell type and autodetected hash commands are persisted back to the config mapper. `cachedHashes` avoids repeated command probing. `mkdirLock` serializes recursive creation per path. `savedpswd` caches prompted password for reconnects.

Dependencies/integration: integrates rclone `fs` interfaces, `accounting.LimitTPS`, `pacer`, `encoder`, env/proxy helpers, `ssh-agent`, `x/crypto/ssh`, `knownhosts`, and `pkg/sftp`. Implements `Fs`, `PutStreamer`, `Mover`, `Copier`, `DirMover`, `DirSetModTimer`, `Abouter`, `Shutdowner`, and `Object`.

Risks/test signals: risks include deadlocks with low connection limits, external SSH non-reuse, shell command injection/quoting, Windows path conversion, server-specific SFTP extensions, hash command autodetection, partial failed uploads, and stale pooled connections. Unit tests cover shell escaping, path encoding/override, hash and `df` parsing; integration tests exercise OpenSSH/rclone SFTP remotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp_internal_test.go -->
# sources/user-network-fs/rclone/backend/sftp/sftp_internal_test.go

Purpose: unit tests private helpers in the non-Plan 9 SFTP backend, focusing on shell safety, path encoding, and parser correctness.

Important APIs/types/functions: tests cover `quoteOrEscapeShellPath` for Unix, cmd, and PowerShell; `Fs.remotePath`; `Fs.remoteShellPath`; `parseHash`; and `parseUsage`.

Control flow: shell escaping cases verify harmless paths, command-substitution-like strings, newlines, quotes, Windows cmd quote rejection, and PowerShell single-quote doubling. Path tests instantiate minimal `Fs` values with `encoder.Display | encoder.EncodeColon`, asserting encoded colon handling and `PathOverride` behavior, including `@` root-prefix mode. Parser tests check standard hash command output and multiple `df` layouts.

State and persistence behavior: no persistent state. The tests instantiate only enough `Fs` state to validate deterministic helper output.

Dependencies/integration: uses `testify/assert` and rclone `encoder`. Build tag `!plan9` matches the backend implementation.

Risks/test signals: strong targeted signal for command injection boundaries and shell path construction, which are security-sensitive. It does not test SSH auth, connection pooling, actual command execution, or upload/read behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp_test.go -->
# sources/user-network-fs/rclone/backend/sftp/sftp_test.go

Purpose: external integration test entry points for the SFTP backend.

Important APIs/types/functions: `TestIntegration` runs against `TestSFTPOpenssh:`; `TestIntegration2` runs against `TestSFTPRclone:` unless a global `-remote` is supplied; `TestIntegration3` runs against `TestSFTPRcloneSSH:` under the same condition. All pass `NilObject: (*sftp.Object)(nil)` to `fstests.Run`.

Control flow: each test delegates to rclone's generic backend suite, which exercises filesystem semantics according to advertised backend features. The variants cover an OpenSSH server, rclone's SFTP server, and rclone over SSH configuration.

State and persistence behavior: relies on configured live remotes and may create/delete files on those remotes. It has no local state beyond test harness configuration.

Dependencies/integration: imports backend as an external package plus `fstest` and `fstests`. Build tag `!plan9` excludes unsupported platforms.

Risks/test signals: broad integration coverage for real SFTP behavior, but it depends on external fixtures and cannot pinpoint private helper regressions. It complements `sftp_internal_test.go` and `ssh_external_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp_unsupported.go -->
# sources/user-network-fs/rclone/backend/sftp/sftp_unsupported.go

Purpose: placeholder file for unsupported platforms, currently `plan9`, so the package has buildable Go source and Go tooling does not report "no buildable Go source files".

Important APIs/types/functions: contains only package declaration and comments under build tag `plan9`.

Control flow: none at runtime. The build constraint selects this file instead of the main `!plan9` SFTP implementation.

State and persistence behavior: none.

Dependencies/integration: no imports. It integrates only with Go build tags.

Risks/test signals: low implementation risk, but important for cross-platform package hygiene. There are no tests needed beyond build selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/sftp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh.go -->
# sources/user-network-fs/rclone/backend/sftp/ssh.go

Purpose: defines abstraction interfaces that let the SFTP backend use either Go's internal SSH client or an external `ssh` binary behind the same connection/session API.

Important APIs/types/functions: `sshClient` requires `Wait`, `SendKeepAlive`, `Close`, `NewSession`, and `CanReuse`. `sshSession` requires environment setup, command/subsystem start, stdin/stdout pipes, `Run`, `Close`, and stdout/stderr writer setters.

Control flow: no executable logic. `sftp.go` consumes these interfaces when creating SFTP clients, running shell commands, detecting shell type, and managing pooled connections. `ssh_internal.go` and `ssh_external.go` provide implementations.

State and persistence behavior: none in this file; state belongs to concrete implementations.

Dependencies/integration: imports only `io` for stream interfaces. The abstraction is central to connection pooling because `CanReuse` determines whether a borrowed connection can return to the pool.

Risks/test signals: interface drift is the main risk: new behavior added to one implementation must satisfy both. Tests for external wait/close and integration tests indirectly validate the contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh_external.go -->
# sources/user-network-fs/rclone/backend/sftp/ssh_external.go

Purpose: implements SFTP's SSH abstraction using an external `ssh` command configured by the `ssh` option.

Important APIs/types/functions: `sshClientExternal` stores the backend and first session; `newSSHClientExternal` creates the client wrapper; `Wait`, `Close`, `NewSession`, and `CanReuse` coordinate the process-backed session. `sshSessionExternal` wraps `exec.Cmd`, cancellation, start state, SFTP-vs-command mode, and `sync.Once`-guarded wait result. `requestSubsystem` is a sentinel prefix translated into `ssh -s <subsystem>`.

Control flow: each session creates a cancellable `exec.CommandContext` from configured args. `Start` appends either `-s subsystem` or a remote command and starts the process. `RequestSubsystem` uses the sentinel path. `Run` starts then waits. `Close` cancels context and waits. `CanReuse` returns true only while the first external session is still running the SFTP subsystem.

State and persistence behavior: process state is in memory. `waitOnce` prevents duplicate waits and associated zombie/process-state hazards. Environment setting is deliberately unsupported and returns an error.

Dependencies/integration: uses `os/exec`, `context`, `slices.Clone`, `sync`, and rclone logging. It plugs into `sftp.go` connection creation and command execution; user must configure passwordless external SSH and keepalives themselves.

Risks/test signals: risks include argument construction, external process lifecycle, inability to set env vars, and different reuse semantics from internal SSH. `ssh_external_test.go` verifies repeated `Wait`/`Close` safety.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh_external.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh_external_test.go -->
# sources/user-network-fs/rclone/backend/sftp/ssh_external_test.go

Purpose: regression tests for external SSH process lifecycle behavior.

Important APIs/types/functions: `TestSSHExternalWaitMultipleCalls` creates an external session using `echo test`, starts a quick command, and calls `Wait` three times. `TestSSHExternalCloseMultipleCalls` uses `sleep 10`, starts a long command, closes it, then calls `Wait` repeatedly.

Control flow: both tests instantiate a minimal `Fs` with only `Options.SSH`, call `newSSHSessionExternal`, and assert no panic or inconsistent wait behavior. The close test skips if the local `sleep` command cannot start.

State and persistence behavior: no persistent state. The tests validate that `waitOnce` caches the process wait result and that `exited()` reflects process completion.

Dependencies/integration: uses local system commands (`echo`, `sleep`), rclone `fs.SpaceSepList`, and `testify/assert`. Build tag `!plan9`.

Risks/test signals: targeted coverage for zombie-process/double-wait regressions. It does not test real SSH, subsystem mode, command quoting, or external SFTP data transfer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh_external_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh_internal.go -->
# sources/user-network-fs/rclone/backend/sftp/ssh_internal.go

Purpose: implements SFTP's SSH abstraction using `golang.org/x/crypto/ssh`.

Important APIs/types/functions: `sshClientInternal` wraps `*ssh.Client`; `newSSHClientInternal` dials through direct, SOCKS5, or HTTP CONNECT proxy paths and completes the SSH handshake. Methods implement waiting, OpenSSH keepalive request, close, reuse allowance, and session creation. `sshSessionInternal` embeds `*ssh.Session` and adapts stdout/stderr setters.

Control flow: `newSSHClientInternal` builds a dialer from rclone HTTP config, chooses proxy behavior from backend options, calls `ssh.NewClientConn`, logs connection metadata, and returns a reusable client. Sessions are thin wrappers over `srv.NewSession`.

State and persistence behavior: no persistence. Internal clients are reusable and therefore eligible for the SFTP connection pool.

Dependencies/integration: uses rclone `fshttp`, proxy helpers, `x/crypto/ssh`, and `net`. It is the default path when `Options.SSH` is empty.

Risks/test signals: risks include proxy dialing behavior, host-key/auth config supplied by `sftp.go`, and keepalive failures being only logged. Integration tests provide most coverage; no dedicated unit tests are present for this wrapper.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/ssh_internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/stringlock.go -->
# sources/user-network-fs/rclone/backend/sftp/stringlock.go

Purpose: provides a keyed mutex used by the SFTP backend to serialize operations for the same path, notably recursive directory creation.

Important APIs/types/functions: `stringLock` stores a global mutex and a map from string IDs to channels. `newStringLock` initializes the map. `Lock(ID)` waits while a channel exists for the ID, then installs a new channel. `Unlock(ID)` closes and removes the channel, panicking if the ID was not locked.

Control flow: waiters release the global mutex before blocking on the per-ID channel, then re-check the map after wakeup. Different IDs can proceed independently; same-ID callers serialize.

State and persistence behavior: all state is in-memory and scoped to one `Fs` instance. Channels act as one-shot broadcast notifications on unlock.

Dependencies/integration: uses only `sync`. `sftp.go` uses this for `mkdir` to avoid concurrent creators racing on the same directory tree.

Risks/test signals: improper unlock order or missing unlock can deadlock same-ID operations; unlocking an unknown ID intentionally panics. `stringlock_test.go` stress-tests per-key serialization.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/stringlock.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/stringlock_test.go -->
# sources/user-network-fs/rclone/backend/sftp/stringlock_test.go

Purpose: concurrency test for `stringLock`.

Important APIs/types/functions: `TestStringLock` creates three counters, one shared lock, and many goroutines that repeatedly lock by counter ID, read-modify-write, then unlock.

Control flow: `outer` and `inner` constants create 1000 increments per key. Each critical section sleeps briefly to amplify race windows. After `WaitGroup` completion, the test asserts all counters reached the expected total.

State and persistence behavior: only in-memory counters and lock map. The test relies on deterministic final counts to prove same-ID serialization while allowing different IDs to run concurrently.

Dependencies/integration: uses `sync`, `time`, `fmt`, and `testify/assert`.

Risks/test signals: good signal for keyed mutual exclusion under contention, but it does not test panic behavior for invalid unlock or fairness/starvation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sftp/stringlock_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/api/types.go -->
# sources/user-network-fs/rclone/backend/shade/api/types.go

Purpose: JSON data transfer types for the Shade backend.

Important APIs/types/functions: `ListDirResponse` models file/directory attributes returned by Shade FS list and attr endpoints, including type, path, inode, millisecond timestamps, size, hash, and draft flag. `PartURL` models a presigned multipart part upload URL plus optional required headers. `CompletedPart` records ETag and part number for multipart completion.

Control flow: no behavior. `shade.go` consumes `ListDirResponse` for `List`, `NewObject`, root file detection, and directory existence checks. `upload.go` consumes `PartURL` and `CompletedPart` during multipart upload.

State and persistence behavior: none; these are transient JSON payload structures.

Dependencies/integration: package `api` is imported by `shade.go` and `upload.go`.

Risks/test signals: JSON field names must match Shade API. `CompletedPart` lacks explicit JSON tags, relying on Go field names (`ETag`, `PartNumber`) matching the expected completion body. Integration tests are the main validation signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/shade.go -->
# sources/user-network-fs/rclone/backend/shade/shade.go

Purpose: implements the rclone backend for Shade FS, including token acquisition, file/directory operations, reads via direct or presigned URLs, server-side move, and integration with multipart upload support.

Important APIs/types/functions: constants define Shade endpoints, pacer timing, and upload limits. `Options` stores drive ID, API key, endpoint, chunk settings, concurrency, and cached token values. `Fs` holds REST clients, drive/root, pacer, token cache/mutex, config mapper, and created-directory cache. `Object` and `Directory` implement rclone object/directory surfaces. Key functions include `refreshJWTToken`, `callAPI`, `NewFS`, `Move`, `DirMove`, `NewObject`, `Put`, `List`, `ensureParentDirectories`, `ensureDirectoryPath`, `Mkdir`, `Rmdir`, `buildFullPath`, `Object.Open`, `Object.Update`, and `Object.Remove`.

Control flow: initialization parses options, creates clients, sets features, validates chunk size, restores token expiry if present, refreshes a JWT, and detects file-root remotes. `refreshJWTToken` returns a still-valid token or fetches a new one from the Shade API, decodes JWT expiry, and persists token fields to config. `callAPI` wraps authenticated Shade FS requests through the pacer. Listing filters draft entries and makes API paths relative to the configured root. Reads first call `/fs/download`; HTTP 200 returns the body directly, while 307 body is treated as a presigned URL and fetched with range options. Directory creation walks parents and treats conflict/unprocessable as existing.

State and persistence behavior: JWT token and expiry are persisted in the config mapper; `createdDirs` is an in-memory cache guarded by RW mutex. No content hashes or modtimes are set through the API.

Dependencies/integration: integrates rclone `fs`, `rest`, `fshttp`, `pacer`, `encoder`, `object.NewStaticObjectInfo`, and Shade API DTOs. Advertises empty directories, move, dir move, and chunk writer.

Risks/test signals: risks include token expiry parsing, status handling when responses are nil, directory-cache staleness, query escaping/unescaping, unsupported hashes/modtime, and presigned URL range behavior. `shade_test.go` supplies live integration coverage only.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/shade.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/shade_test.go -->
# sources/user-network-fs/rclone/backend/shade/shade_test.go

Purpose: external integration test entry point for the Shade backend.

Important APIs/types/functions: `TestIntegration` runs `fstests.Run` against remote `TestShade:` with `NilObject: (*shade.Object)(nil)`, skips invalid UTF-8 tests, and sets `eventually_consistent_delay` to 7.

Control flow: the generic rclone test suite exercises backend operations on a configured Shade drive. The extra config acknowledges eventual consistency in the service.

State and persistence behavior: creates/deletes remote Shade objects and may interact with backend token persistence through normal initialization. Local state is owned by the test harness.

Dependencies/integration: imports `shade` as an external package and rclone `fstests`.

Risks/test signals: useful broad signal for API behavior, but depends on live credentials/service availability and does not isolate token, directory cache, or multipart edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/shade_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/upload.go -->
# sources/user-network-fs/rclone/backend/shade/upload.go

Purpose: implements Shade multipart uploads via rclone's `fs.OpenChunkWriter` / `multipart.UploadMultipart` infrastructure.

Important APIs/types/functions: `shadeChunkWriter` stores the upload token, chunk size, source size, backend/object pointers, and completed parts guarded by a mutex. `Object.uploadMultipart` delegates to generic multipart upload. `Fs.OpenChunkWriter` computes chunk sizing, ensures parents, initiates multipart upload, and returns writer metadata. `WriteChunk` reads a chunk, fetches a presigned part URL, PUTs the bytes, records ETag/part number, and returns bytes written. `Close` sorts parts and completes the upload. `Abort` asks Shade to abort the multipart token. `warnStreamUpload` logs the unknown-size upload ceiling once.

Control flow: for known sizes, `chunksize.Calculator` adjusts part size to stay under max parts; for unknown sizes, configured chunk size is used. Each part obtains a fresh JWT, then a part URL, then uploads to that URL with any returned headers. Completion sends sorted parts to the complete endpoint; abort deliberately avoids retrying failures.

State and persistence behavior: multipart state is remote via the init token and local via `completedParts`. The writer updates `Object.size` from the writer's source size after upload. No resumable local state is stored.

Dependencies/integration: uses rclone `multipart`, `chunksize`, `rest`, Shade API DTOs, and the backend token/directory helpers. Exposed through `Fs.Features().OpenChunkWriter`.

Risks/test signals: memory use is one full chunk per concurrent upload because chunks are buffered; unknown-size uploads are capped by chunk size times max parts; ETag presence and JSON field names must match service expectations; error message for failed upload formats the chunk buffer instead of part number. Integration tests are the main coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/shade/upload.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/api/types.go -->
# sources/user-network-fs/rclone/backend/sharefile/api/types.go

Purpose: DTO and error types for the ShareFile backend API.

Important APIs/types/functions: `ListRequestSelect` defines the OData projection for child listing. `ListResponse` wraps `odata.count` and `[]Item`. `Item` models files/folders with names, dates, hidden flag, size, OData type, ID, and hash. `Error` implements Go's `error` interface for OData error responses. `DownloadSpecification`, `UploadRequest`, `UploadSpecification`, and `UploadFinishResponse` model download and upload negotiation/completion. `UploadFinishResponse.ID` returns the first uploaded item ID or a clear error. `Parent`, `Zone`, and `UpdateItemRequest` support item updates/moves.

Control flow: behavior is limited to `Error.Error` string formatting and `UploadFinishResponse.ID` validation. Other types are marshaled/unmarshaled by backend REST calls.

State and persistence behavior: no persistent state. Timestamps and IDs are transient API payloads.

Dependencies/integration: imports `time`, `fmt`, and `errors`. It is intended to be consumed by the ShareFile backend implementation for OData listing, upload, download, patch, and error handling.

Risks/test signals: risks are schema drift, OData field naming, pointer optional fields, and upload completion responses with no `Value`. No direct tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/api/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/generate_tzdata.go -->
# sources/user-network-fs/rclone/backend/sharefile/generate_tzdata.go

Purpose: `go:build ignore` generator for embedding ShareFile timezone data into the `sharefile` package.

Important APIs/types/functions: `main` creates `AssetDir` from local `./tzdata` and calls `vfsgen.Generate` with package name `sharefile`, build tags `!dev`, and variable name `tzdata`.

Control flow: when invoked manually with `go run`, it reads the `tzdata` directory and generates Go source through `vfsgen`. On generation failure it logs fatally.

State and persistence behavior: produces generated files in the working directory according to `vfsgen` behavior. It is not part of normal builds due to the ignore build tag.

Dependencies/integration: depends on `github.com/shurcooL/vfsgen`, `net/http`, and `log`. It supports the ShareFile backend's timezone lookup assets.

Risks/test signals: generator assumes `./tzdata` relative to invocation directory. There are no tests in this subset; build/generation success is the validation path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/sharefile/generate_tzdata.go -->
