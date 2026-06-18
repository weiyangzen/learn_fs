# subset-b-009770 research

Grouped research for `subset-b-009770` covering rclone serve proxy, rc, restic, S3, SFTP, WebDAV, and adjacent command/test helpers. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go

Source read: complete file, 346 lines, 10483 bytes, sha256 `371767e31854fa8feab1d26361e498507bd23e2d6c5cb2a64639890be38a4a09`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go_research.md`.

## Purpose
Implements the programmable authentication proxy used by rclone serve protocols to derive per-user backend configuration from an external command. It lets servers authenticate an incoming password or public key, run a JSON stdin/stdout helper, create a backend from the returned config, and cache a VFS for subsequent requests.

## Important APIs, types, and functions
`OptionsInfo`, `Options`, and global `Opt` register the `auth_proxy` global option. `Proxy` stores the split command line, request context, VFS options, and a `lib/cache.Cache`. `cacheEntry` stores the VFS plus a SHA-256 credential guard. `New`, `run`, `generateCacheKey`, `call`, `Call`, and `Get` are the core API.

## Control flow
`Call` derives a credential-aware HMAC cache key and first checks the VFS cache. On miss, `call` runs the proxy command with either `user/pass` or `user/public_key`, validates returned `type` and `_root`, fills backend defaults, constructs an rclone Fs via `fsInfo.NewFs`, wraps it in VFS, and stores it. `run` obscures any fields named by `_obscure` before backend construction.

## State and persistence behavior
Persistent state is remote backend state created by the returned config; local state is an in-memory VFS cache keyed by username and a process-random HMAC of the auth secret. The raw password is not persisted; only a SHA-256 hash is kept in `cacheEntry` for collision defense. The HMAC key is process local, so cache names are not stable across restarts.

## Dependencies and integration points
Depends on `os/exec`, JSON encoding, `fs`, `fs/cache`, `configmap`, `obscure`, `lib/cache`, and VFS packages. It is integrated by SFTP, WebDAV, S3, and test helpers through `proxy.New`, `Proxy.Call`, and `Proxy.Get`.

## Risks and edge cases
Command parsing uses `strings.Fields`, so quoted paths or arguments are not shell interpreted. Proxy helpers must return complete safe config because environment/CLI config is not merged. The cache key appears in backend names and logs, so the HMAC construction is important. Global `proxy.Opt` checks in some callers can diverge from passed `proxyOpt` if modified carelessly.

## Test signals
`proxy_test.go` exercises command success, helper failure, obscuring, password and public-key calls, cache reuse, and cache miss retrieval. Serve protocol integration tests also run auth-proxy modes through `servetest`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go

Source read: complete file, 41 lines, 613 bytes, sha256 `7cb98b6d26b97a00b617e4cecbaddda33ceeb8f526e4dd39d82bfe4d290c90e0`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go_research.md`.

## Purpose
Provides a build-ignored test auth proxy executable. It reads the proxy protocol JSON from stdin and emits a local backend config suitable for unit tests.

## Important APIs, types, and functions
`main` decodes a `map[string]string`, mutates `user` by appending `-test`, treats an `error` input as fatal, defaults `type` to `local`, defaults `_root` to empty, and writes JSON to stdout.

## Control flow
The test process is launched by `go run`; stdin drives the output config and stdout becomes the config map parsed by `proxy.run`.

## State and persistence behavior
No persistent state. It only transforms one request and exits. Its output may include password/public-key fields from input for proxy cache and obscuring tests.

## Dependencies and integration points
Depends only on standard JSON/log/os packages and the proxy JSON contract from `proxy.go`.

## Risks and edge cases
Because it is build-ignored, it is only valid when explicitly invoked with `go run`. It is intentionally permissive and should not be copied as a production auth proxy.

## Test signals
`proxy_test.go` uses it to validate normal proxy operation, command failure, and obscuring behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_code.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go

Source read: complete file, 269 lines, 8188 bytes, sha256 `42463bf162b44d32ce03fc0bf01ddfb5d1c709e6963683cde7f4dc2575174b15`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go_research.md`.

## Purpose
Tests the auth proxy implementation from helper process invocation through VFS cache behavior for password and public-key authentication.

## Important APIs, types, and functions
`TestRun` covers `Proxy.run` success, failure, and `_obscure`. Later subtests call `Proxy.call`, `Proxy.Call`, and `Proxy.Get` with password and public-key inputs and verify cache keys, VFS creation, and credential mismatch behavior.

## Control flow
The tests build absolute paths to `proxy_code.go`, execute it with `go run`, inspect returned config values, then instantiate `Proxy` with local backend/VFS options. They call the proxy directly and through the cache-facing API.

## State and persistence behavior
State is test-local except for temporary VFS cache entries inside each `Proxy`. It validates that a changed credential gets a different cache path and does not reuse stale VFS state.

## Dependencies and integration points
Depends on the local backend, `configmap`, `obscure`, `vfscommon`, testify assertions, and the ignored helper source.

## Risks and edge cases
Tests manipulate executable paths and process execution, so failures can reflect missing Go toolchain or working-directory assumptions. Coverage is focused on local backend behavior and does not validate production helper security.

## Test signals
Strong test signal for JSON protocol handling, field obscuring, password/public-key cache segregation, and retrieval through cache keys.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxy_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go -->
# sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go

Source read: complete file, 13 lines, 386 bytes, sha256 `38e3d42a240745fe7fd68204a73e35a11a44ed232d68937663d7370955d6674f`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go_research.md`.

## Purpose
Adds auth-proxy command-line flags to serve subcommands that support dynamic backend selection.

## Important APIs, types, and functions
`AddFlags` calls `flags.AddFlagsFromOptions` with `proxy.OptionsInfo` and no prefix.

## Control flow
Serve commands call this during init, causing Cobra/pflag to expose `--auth-proxy` on those commands.

## State and persistence behavior
No state beyond binding command-line values into global proxy options.

## Dependencies and integration points
Depends on `cmd/serve/proxy`, rclone flag helpers, and `pflag`.

## Risks and edge cases
Any subcommand using it shares the same unprefixed flag name, so registration order and global options must stay consistent.

## Test signals
Covered indirectly by serve command construction and auth-proxy integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/proxy/proxyflags/proxyflags.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc.go -->
# sources/user-network-fs/rclone/cmd/serve/rc.go

Source read: complete file, 350 lines, 7986 bytes, sha256 `276cc9160b2a1be8870c194abb34169026ac416ecc42536b85a82514a82d0b86`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/rc.go_research.md`.

## Purpose
Implements the remote-control API for starting, stopping, listing, and enumerating `rclone serve` protocol servers at runtime.

## Important APIs, types, and functions
`Handle` is the protocol server contract. Internal `server` records id, address, rc params, handle, and serve error channel. `Fn` is the registration callback type. `AddRc`, `startRc`, `stopRc`, `serveTypesRc`, `listRc`, and `stopAll` implement rc paths `serve/start`, `serve/stop`, `serve/types`, `serve/list`, and `serve/stopall`.

## Control flow
`startRc` validates the requested type, obtains the Fs from params, copies global config and filters into a background context, creates the protocol server, starts `Serve` in a goroutine, waits briefly for startup failure, then stores it under a random type-prefixed id. Stop paths call `Shutdown`, wait for the serve goroutine, and remove entries.

## State and persistence behavior
State is the process-global `serveFns` registry and `servers` map protected by `serveMu`. Server params are stored for listing. No persistent state is written, but servers keep remote connections/listeners alive until stopped.

## Dependencies and integration points
Depends on `fs/rc`, `fs/filter`, `errcount`, and protocol packages that register via `AddRc` from their init functions.

## Risks and edge cases
Holding `serveMu` while waiting on shutdown/startup can serialize operations and can deadlock if a server callback re-enters serve rc. The 100 ms startup probe may miss late failures. IDs are random but not collision checked beyond map assignment.

## Test signals
`rc_test.go` tests missing types, start errors, immediate stops, start/stop/list/types/stopall behavior. `servetest.TestRc` exercises protocol-specific rc wiring with live TCP checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc_test.go -->
# sources/user-network-fs/rclone/cmd/serve/rc_test.go

Source read: complete file, 180 lines, 4456 bytes, sha256 `98bafb04e516b30c85a7c7049a9ca73c4ccc039de241b516cc818c0cc0f22cc1`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/rc_test.go_research.md`.

## Purpose
Unit-tests the serve rc lifecycle manager using dummy server handles.

## Important APIs, types, and functions
`dummyServer` implements `Handle`. Test helper `newServer` variants simulate normal serve, construction failure, and immediate stop. `resetGlobals` and `newTest` isolate global registries.

## Control flow
Tests register a fake serve type, invoke rc functions directly with `rc.Params`, then inspect outputs, server map contents, and shutdown behavior.

## State and persistence behavior
Mutates the package-global `serveFns` and `servers` maps but resets them around each test. Dummy servers model listener address and error-channel lifetimes without opening sockets.

## Dependencies and integration points
Depends on rc params, net address behavior, and testify-style stdlib testing assertions.

## Risks and edge cases
Because tests are white-box and global-state based, parallelization would be unsafe unless isolation changes. They do not exercise real protocol listeners.

## Test signals
Covers unknown serve type, factory error, immediate stop error path, normal start/stop, nonexistent stop, sorted type/list output, and stopall cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/rc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/cache.go

Source read: complete file, 77 lines, 1399 bytes, sha256 `8ec5a9022f80fa85fff40c3f2e0a88cf69a12d28000b025f8a9d63d2333a96ca`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/cache.go_research.md`.

## Purpose
Implements a small optional in-memory cache of restic repository objects to speed repeated object reads after list operations.

## Important APIs, types, and functions
`cache` contains an RW mutex, `map[string]fs.Object`, and a `cacheObjects` switch. `newCache`, `find`, `add`, `remove`, and `removePrefix` are the public-in-package operations.

## Control flow
Server paths call `find` before `Fs.NewObject`, add objects after successful upload/list discovery, remove on delete, and clear descendants before refreshing directory listings.

## State and persistence behavior
State is process-memory only and disappears on restart. When disabled, all operations become no-ops or misses. `removePrefix("/")` clears the entire cache.

## Dependencies and integration points
Depends on `sync`, string prefix checks, and `fs.Object`.

## Risks and edge cases
Prefix removal intentionally appends `/`, so removing `b` preserves an exact object named `b` while deleting children. Stale objects are possible if external writers mutate the backend outside restic list/delete/upload flows.

## Test signals
`cache_test.go` validates CRUD and prefix-removal semantics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go

Source read: complete file, 55 lines, 1077 bytes, sha256 `89b7efb7cda3956c9611749abf28bdfdbc13310e589c0cb8bf4b0554efdcdd4e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go_research.md`.

## Purpose
Tests the restic object cache implementation.

## Important APIs, types, and functions
Adds a test-only `String` method to expose sorted cache keys. `TestCacheCRUD` covers add/find/remove. `TestCacheRemovePrefix` checks child removal and full clear.

## Control flow
Tests create mock objects, mutate a cache, and compare deterministic comma-joined key listings.

## State and persistence behavior
State is test-local in-memory cache entries guarded by the cache mutex.

## Dependencies and integration points
Depends on `mockobject`, sorting, strings, and testify assertions.

## Risks and edge cases
Only enabled-cache behavior is tested; disabled-cache no-op behavior is not directly asserted here.

## Test signals
Provides direct signal that exact keys are preserved while descendants are removed and `/` clears all.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/cache_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh

Source read: complete file, 36 lines, 606 bytes, sha256 `79c2cf63263c391000670de30adb7e5693171bebc45bb41f38116823dd8d00a8`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh_research.md`.

## Purpose
Shell helper for manually running restic serve integration tests against many configured rclone remotes.

## Important APIs, types, and functions
Defines a list of `Test*:` remotes, loops over them, runs `go test -remote $remote -v -timeout 30m`, tees per-remote logs, and prints ISO timestamps.

## Control flow
Executed manually from the restic serve package directory, commonly inside screen according to the comment.

## State and persistence behavior
Writes `restic-test.$remote.log` files in the current directory. It does not clean them or manage remote state beyond whatever the tests do.

## Dependencies and integration points
Depends on Bash, `go test`, configured rclone test remotes, and package test flags.

## Risks and edge cases
Assumes remote names are configured and that log filenames with colons are acceptable on the platform. It is not used by normal `go test`.

## Test signals
Manual broad compatibility signal across providers; not an automated unit-test input.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic-test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic.go

Source read: complete file, 572 lines, 16585 bytes, sha256 `51f13038acf0109b22c63c6dfe9a2d0b764ad00d44055ce798b1ffa1dc6e5922`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic.go_research.md`.

## Purpose
Implements `rclone serve restic`, an HTTP or HTTP/2-over-stdio server exposing an rclone remote through restic's REST backend API.

## Important APIs, types, and functions
`Options` combines HTTP/auth config with `Stdio`, `AppendOnly`, `PrivateRepos`, and `CacheObjects`. `Command`, `newServer`, `server.Bind`, `WithRemote`, `checkPrivate`, `serveObject`, `postObject`, `deleteObject`, `listObjects`, and `createRepo` are the central APIs. `ContextRemoteKey` carries the translated remote path.

## Control flow
Command startup builds an Fs, creates a server, and either serves HTTP listeners or binds an HTTP/2 server to `StdioConn`. Requests flow through `WithRemote`, which trims URL paths and maps restic `data/<hash>` objects into `data/<prefix>/<hash>`. GET/HEAD serve objects, POST creates repositories or writes objects, DELETE removes objects, and list endpoints require the restic v2 Accept header.

## State and persistence behavior
Repository state is ordinary directories and objects on the backing Fs. Local state includes the HTTP server, optional object cache, request context values, and append-only/private-repo options. Append-only blocks overwrites and most deletes except lock files. Private repos restrict paths to the authenticated username prefix.

## Dependencies and integration points
Depends on chi, rclone `lib/http`, HTTP auth, VFS-independent `fs` operations, `operations.RcatSize`, `walk.ListR`, systemd notification, terminal checks, and `x/net/http2` for stdio mode. Registered both as Cobra command and rc serve type.

## Risks and edge cases
Security depends on correct auth configuration and `checkPrivate` path matching. Append-only mode still allows lock deletion by path pattern. Cache entries can go stale after external mutation. `WithRemote` path rewriting must remain compatible with restic's expected data layout.

## Test signals
`restic_test.go`, append-only/private-repos tests, cache tests, and optional upstream restic integration tests cover path mapping, HTTP errors, overwrite/delete restrictions, private repository auth, rc start, and object cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go

Source read: complete file, 137 lines, 3509 bytes, sha256 `a6b42891dc768371e30461f76f46e09b4a295f4026390141f554f26c534ef0b9`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go_research.md`.

## Purpose
Tests restic server append-only mode, especially overwrite and delete restrictions.

## Important APIs, types, and functions
`createOverwriteDeleteSeq` builds reusable request sequences. `TestResticHandler` creates a local-backed server with `AppendOnly=true`, creates a repo, and runs sequences for config, data objects, and lock files.

## Control flow
Each sequence uses httptest requests directly against the chi router and checks HTTP status/body after POST, GET, and DELETE operations.

## State and persistence behavior
State is a temporary local repository. Append-only should preserve original object contents after forbidden overwrite/delete while allowing lock creation and lock deletion.

## Dependencies and integration points
Depends on `cmd.NewFsSrc`, configfile install, restic request helpers, and HTTP status assertions.

## Risks and edge cases
Random IDs avoid collisions but the test only covers REST handler semantics, not concurrent restic clients.

## Test signals
Strong signal that append-only protects repository data but permits lock cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_appendonly_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go

Source read: complete file, 78 lines, 2802 bytes, sha256 `c5ca6ccdad4a72ff7d66802d1739ca19f1ee7650e9cc3ab4bbf59a5ed7cc02d5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go_research.md`.

## Purpose
Tests `--private-repos` access control for restic serve.

## Important APIs, types, and functions
`newAuthenticatedRequest` wraps test request creation and Basic Auth. `TestResticPrivateRepositories` configures one valid user/password and checks allowed, unauthorized, and forbidden paths.

## Control flow
The test posts and gets under `/test/`, then retries with missing or bad credentials, then requests root and another user's prefix.

## State and persistence behavior
State is a temporary local Fs plus HTTP auth config on the test server. No persistent credentials are written.

## Dependencies and integration points
Depends on lib/http Basic Auth behavior, chi route parameters, and restic request helpers.

## Risks and edge cases
It validates only Basic Auth username matching; proxy/custom auth combinations are not covered here.

## Test signals
Signals that authenticated users can access only their matching repository prefix and all other paths are forbidden.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_privaterepos_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go

Source read: complete file, 183 lines, 4633 bytes, sha256 `dea4ac732a540424c0918db769f126382938a8d3eabe817bfc1dce4b57217958`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go_research.md`.

## Purpose
Provides restic serve integration and handler error tests.

## Important APIs, types, and functions
`newOpt` creates localhost listener options. `TestResticIntegration` optionally runs upstream restic REST backend tests against a live rclone server. `TestMakeRemote`, `TestListErrors`, `TestServeErrors`, and `TestRc` cover path rewriting, error mapping, and rc registration.

## Control flow
The integration test starts a temporary remote-backed server, changes into an external restic source tree, and runs `go test` with `RESTIC_TEST_REST_REPOSITORY`. Unit-style tests invoke the router directly.

## State and persistence behavior
State includes temporary remote content, process working directory changes during upstream tests, and test server listeners. Error wrapper Fs types inject list/NewObject failures.

## Dependencies and integration points
Depends on restic source checkout availability, rclone backend/all imports, servetest, httptest, and rc.

## Risks and edge cases
The integration test is skipped if the restic source tree is absent and mutates cwd, so cleanup correctness matters. Error tests cover HTTP status mapping but not all backend error classes.

## Test signals
Signals compatibility with restic's external server tests when available and deterministic behavior for URL-to-remote mapping and common errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go

Source read: complete file, 53 lines, 1491 bytes, sha256 `9fe21efdaf8f93ba0371b405275b3772a38b18591626a9daa96c5724d0ac1d85`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go_research.md`.

## Purpose
Defines shared HTTP test helpers for restic serve tests.

## Important APIs, types, and functions
`wantFunc`, `newRequest`, `wantCode`, `wantBody`, `checkRequest`, and `TestRequest` make handler tests concise and ensure the restic v2 Accept header is present.

## Control flow
Tests build httptest requests, route them through a handler, and apply a list of response assertions.

## State and persistence behavior
No persistent state. Helpers create request/recorder objects only.

## Dependencies and integration points
Depends on `httptest`, `net/http`, `io`, and testify assertions.

## Risks and edge cases
The helpers compare body bytes exactly and do not close request bodies, appropriate for httptest but not a production pattern.

## Test signals
Used by append-only, private-repo, list-error, and serve-error tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/restic_utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go -->
# sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go

Source read: complete file, 73 lines, 1396 bytes, sha256 `8a6e171648b2bc527949b2c740ba405562191e26d26451a8887a1e45ccb4b89c`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go_research.md`.

## Purpose
Adapts stdin/stdout files to `net.Conn` so restic can start rclone and communicate over HTTP/2 on standard streams.

## Important APIs, types, and functions
`Addr` implements `net.Addr`; `StdioConn` implements `Read`, `Write`, `Close`, address accessors, and deadline methods.

## Control flow
Restic command startup constructs `StdioConn` and passes it to `http2.Server.ServeConn` when `--stdio` is enabled.

## State and persistence behavior
State is the two process file descriptors. `Close` closes stdin and stdout; deadlines are delegated to the files.

## Dependencies and integration points
Depends on `os.File`, `net.Conn`, and `time` deadline APIs.

## Risks and edge cases
Deadline support depends on the underlying file descriptors. Running on a terminal is rejected in `restic.go`, not here.

## Test signals
Exercised indirectly by stdio mode users; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/restic/stdio_conn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/backend.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/backend.go

Source read: complete file, 529 lines, 12864 bytes, sha256 `966d757df7f60c42eda1b934dc942381f6eec85771e0f4345606cc5aa3bbf705`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/backend.go_research.md`.

## Purpose
Implements the `gofakes3.Backend` bridge from S3 buckets/objects to rclone VFS paths and optional streaming multipart support.

## Important APIs, types, and functions
`s3Backend` stores the server pointer, metadata map, multipart upload registry, and fallback warning guard. It implements bucket listing/creation/deletion, object head/get/put/touch/copy/delete, multi-delete, bucket existence, and metadata/modtime helpers.

## Control flow
Bucket operations map top-level VFS directories to buckets. Object operations join bucket and key into a VFS path, stat/open/create/remove VFS nodes, copy data streams, and convert hashes/modtimes/mime types into S3 metadata. Copy to self updates metadata/modtime; copy to another key reads the source and writes via `PutObject`.

## State and persistence behavior
Remote state is directories and files in the backing Fs through VFS. Local state is an in-memory metadata map keyed by full path and multipart upload state held in `multipartUploads`. Metadata is not persisted across process restarts.

## Dependencies and integration points
Depends on `gofakes3`, rclone VFS, `fs.Object`, Swift float-time helpers for mtime metadata, and helper files `utils.go`, `list.go`, `ioutils.go`, and `multipart.go`.

## Risks and edge cases
The metadata map can diverge from remote state after external changes. Directory cleanup after delete is marked unsafe and may remove empty parents unexpectedly. `PutObject` has nuanced mtime handling where fallback to `mtime` is nested under `X-Amz-Meta-Mtime` parsing. Root files are not represented as buckets.

## Test signals
`s3_test.go` runs backend integration through the S3 backend, encoding tests, auth/proxy bucket listing, and rc tests. Multipart behavior is covered separately.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/backend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go

Source read: complete file, 34 lines, 577 bytes, sha256 `249d1cd61518e27aab35a68ffecea20ffd706f89ed78bc63fbcf48b7806f4d8e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go_research.md`.

## Purpose
Provides small `io.ReadCloser` utilities for S3 object responses.

## Important APIs, types, and functions
`noOpReadCloser` is an empty body for HEAD-like responses. `readerWithCloser` wraps a reader plus close callback. `limitReadCloser` combines `io.LimitReader` with a closer for ranged reads.

## Control flow
Get/Head object code returns these wrappers to satisfy gofakes3 object body expectations without leaking underlying file handles.

## State and persistence behavior
No persistent state; close callback ownership is passed from the VFS handle.

## Dependencies and integration points
Depends only on `io`.

## Risks and edge cases
Correct close propagation is important for ranged requests because the limited reader itself does not close the underlying file.

## Test signals
Covered indirectly by S3 GET/HEAD and ranged object integration tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/ioutils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/list.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/list.go

Source read: complete file, 51 lines, 1139 bytes, sha256 `19ff1487f51e40a0aa26328f94c5214c3d34b936cbc3f19a8347da93cbaf62c7`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/list.go_research.md`.

## Purpose
Recursively converts VFS directory entries into a gofakes3 object listing for a bucket and prefix.

## Important APIs, types, and functions
`entryListR` accepts bucket, current directory path, remaining prefix name, delimiter behavior, and the response accumulator.

## Control flow
It stats and reads a directory, filters entries by the remaining prefix component, emits common prefixes when delimiter mode is active, recurses into directories otherwise, and emits content records for files with key, modtime, ETag, size, and storage class.

## State and persistence behavior
No persistent state. It reads VFS directory state and adds to a request-local `ObjectList`.

## Dependencies and integration points
Depends on path helpers, prefix parsing from `utils.go`, `getDirEntries`, ETag hashing, VFS nodes, and `gofakes3` models.

## Risks and edge cases
Filtering is component-based after `prefixParser`; unusual control characters and delimiter semantics are noted by a workaround comment. Recursive listing can be expensive for large buckets.

## Test signals
S3 integration and MinIO client encoding/list tests exercise listing output; `pager_test.go` covers final ordering after listing.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/list.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/logger.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/logger.go

Source read: complete file, 35 lines, 565 bytes, sha256 `f752935f50404f9f2f2fc7e92cc2d0d5d059c30dfea32db41f6855739ec11e3e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/logger.go_research.md`.

## Purpose
Adapts gofakes3 logging into rclone's fs logging levels.

## Important APIs, types, and functions
`logger.Print` joins variadic values into one string and maps error, warning, and info levels to `fs.Errorf`, `fs.Infof`, and `fs.Debugf`.

## Control flow
The server passes this logger when constructing `gofakes3.GoFakeS3`.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends on `gofakes3.LogLevel` and rclone `fs` logging.

## Risks and edge cases
Level mapping is intentionally compressed; gofakes3 info becomes debug, so normal verbosity may hide request details.

## Test signals
Covered indirectly whenever S3 server tests emit gofakes3 logs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/logger.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/multipart.go

Source read: complete file, 388 lines, 11768 bytes, sha256 `6fad721d67310ea5d287be916c34b01fda5b5095d4aaa87123b540bf4e3acb5d`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/multipart.go_research.md`.

## Purpose
Implements streaming S3 multipart uploads so completed objects can be written to backends via `PutStream` without buffering the entire upload in memory.

## Important APIs, types, and functions
`multipartUpload` tracks bucket/key, metadata, pipe writer, MD5s, part sizes, stream buffer, next part, and background PutStream lifecycle. `CreateMultipartUpload`, `UploadPart`, `CompleteMultipartUpload`, `AbortMultipartUpload`, `validate`, `streamPart`, `close`, `abort`, and `multipartETag` implement `gofakes3.MultipartBackend`.

## Control flow
Creation validates bucket and PutStream support, creates parent directories, starts a background `PutStream` reading from an `io.Pipe`, and stores upload state. Each part is copied into a pool-backed buffer while MD5 is computed; the part is streamed when all earlier parts have arrived. Complete validates client ETags/order, ensures contiguous streaming, closes the pipe, invalidates VFS parent cache, stores metadata, applies mtime, and returns the S3 multipart ETag.

## State and persistence behavior
Remote object data is streamed to the underlying Fs before completion. Local upload state is held in `multipartUploads` until complete or abort. Buffered out-of-order parts consume pool storage until their turn. Abort cancels context and closes the pipe with a sentinel error.

## Dependencies and integration points
Depends on `gofakes3`, `uuid`, `fs.Features().PutStream`, `object.NewStaticObjectInfo`, `lib/multipart`, `pool.RW`, Swift mtime helpers, and VFS cache invalidation.

## Risks and edge cases
Requires part numbers to become contiguous; gaps are rejected at completion. Out-of-order clients are tolerated only within memory/disk buffer limits. PutStream bypasses VFS, so parent cache invalidation is essential. Fallback to gofakes3 in-memory buffering can use large memory and is logged once.

## Test signals
`multipart_test.go` covers non-uniform parts, in-memory fallback, concurrent out-of-order parts, non-contiguous rejection, and abort cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go

Source read: complete file, 198 lines, 6949 bytes, sha256 `db6f2165f76840453379787649c0341d49e540889f9a8081359703bf8dcfd5fe`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go_research.md`.

## Purpose
Tests streamed and fallback multipart upload behavior for serve s3 using MinIO's low-level multipart API.

## Important APIs, types, and functions
`newMultipartTestServer`, `readObject`, and `multipartUploadParts` set up local-backed servers and helpers. Tests cover non-uniform parts, out-of-order concurrent uploads, gaps, and aborts.

## Control flow
Each test starts a temporary local Fs, creates a bucket, starts an S3 server, uses `minio.Core` to create/upload/complete/abort multipart uploads, then reads the backing Fs directly.

## State and persistence behavior
State is temporary local object data plus live in-memory multipart state inside the server. Cleanup shuts down the server and client.

## Dependencies and integration points
Depends on MinIO client, rclone local backend/fstest, random data, proxy defaults, and VFS options.

## Risks and edge cases
Local backend tests PutStream behavior available through rclone features; they do not cover every cloud backend's PutStream edge cases. Concurrency test uses one shuffle order.

## Test signals
Strong signal for streaming assembly correctness, ETag validation path, invalid part gaps, and abort leaving no object.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/multipart_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/pager.go

Source read: complete file, 66 lines, 1530 bytes, sha256 `b0c8be0152760c30cd641b2ff0ca2a5bef9eb5b5200a8effe890d04f068e4654`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/pager.go_research.md`.

## Purpose
Implements S3 list pagination and deterministic ordering for gofakes3 object lists.

## Important APIs, types, and functions
`pager` sorts common prefixes and object contents lexicographically, applies marker trimming, fills a response up to MaxKeys, marks truncation, and sets NextMarker.

## Control flow
ListBucket builds a full `ObjectList` first, then calls this function to page it according to gofakes3's `ListBucketPage`.

## State and persistence behavior
No persistent state; it mutates the passed list slices and returns a new response list.

## Dependencies and integration points
Depends on Go `sort` and gofakes3 list structures.

## Risks and edge cases
The truncation check compares original remaining list length to `page.MaxKeys`; when `MaxKeys` is zero, tokens default to 1000 but the check still uses zero, which can mark truncated unexpectedly. Marker handling treats contents and prefixes independently.

## Test signals
`pager_test.go` verifies content sorting by key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go

Source read: complete file, 32 lines, 792 bytes, sha256 `ce698a03ed47914093fe12a2034232923b85f0582ad249eb69ef7c4134495794`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go_research.md`.

## Purpose
Tests S3 pager ordering behavior.

## Important APIs, types, and functions
`TestPagerSortsContentsByKey` creates an unsorted object list, calls `pager`, and asserts lexicographic key order.

## Control flow
The test avoids a full server and invokes the backend helper directly.

## State and persistence behavior
No persistent state.

## Dependencies and integration points
Depends on gofakes3 object list models and testing package.

## Risks and edge cases
Coverage is narrow: it does not check prefix ordering, markers, truncation, or zero MaxKeys behavior.

## Test signals
Provides regression signal that returned contents are sorted by key.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/pager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/s3.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/s3.go

Source read: complete file, 132 lines, 3826 bytes, sha256 `5161da6cd8be1ee70230f5c1f627e0e3c30bf6586ad779b5d8d1759d8b4b3e24`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/s3.go_research.md`.

## Purpose
Defines the `rclone serve s3` Cobra command, options, flags, help embedding, and rc registration.

## Important APIs, types, and functions
`OptionsInfo` exposes path-style, ETag hash, auth key, cleanup, multipart streaming, HTTP, and auth settings. `Options`, global `Opt`, `help`, and `Command` are the main API.

## Control flow
Init registers global options, command flags, VFS flags, proxy flags, the subcommand, and the rc serve factory. Command execution either opens a source Fs or, in auth-proxy mode, expects no remote argument and lets the proxy create backends per request.

## State and persistence behavior
State is command/global option binding and server runtime created by `newServer`. No files are written by this file.

## Dependencies and integration points
Depends on Cobra, embedded markdown help, configstruct, HTTP/VFS/proxy flags, and `serve.AddRc`.

## Risks and edge cases
The `NoCleanup` option is declared but directory cleanup behavior in `utils.go` must honor it elsewhere; mismatch would surprise users. Auth-proxy mode relies on global proxy options and no source Fs.

## Test signals
S3 integration tests and `servetest.TestRc` validate command/rc server startup paths indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go

Source read: complete file, 316 lines, 7935 bytes, sha256 `597dd1c9ea1189e2878b0fcf9a4f5de6da0ecd84b90a4c43af74e47c3cdbcb7a`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go_research.md`.

## Purpose
Runs serve s3 integration tests and MinIO-client behavior checks.

## Important APIs, types, and functions
`serveS3` and `startS3` start an authenticated local S3 server and return backend config. `TestS3`, `TestS3Minio`, `TestEncodingWithMinioClient`, and bucket-list/auth helper tests exercise normal and auth-proxy modes.

## Control flow
Tests launch serve s3, configure rclone's S3 backend or MinIO client to talk to it, then run generic backend tests or explicit list operations.

## State and persistence behavior
State is temporary local or Docker-backed remote content plus live server listeners. Proxy tests temporarily mutate global `proxy.Opt.AuthProxy`.

## Dependencies and integration points
Depends on MinIO client, rclone S3 backend, local backend, servetest, fstest, docker-backed testserver for MinIO, hashes, random credentials, and rc.

## Risks and edge cases
Docker-backed coverage is skipped without Docker. Global proxy option mutation is not parallel-safe. Integration failures can come from the nested backend tests rather than the S3 server alone.

## Test signals
Broad conformance signal for serving S3 over local and MinIO-backed remotes, path encoding, auth keys, auth proxy, and rc startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/server.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/server.go

Source read: complete file, 222 lines, 5230 bytes, sha256 `8db95539e9f15ff840ed77e945ef150e8d060381e79598d506f84ed98e3389c3`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/server.go_research.md`.

## Purpose
Constructs and runs the HTTP S3 server around `gofakes3`, rclone VFS, optional auth proxy, and HTTP listener configuration.

## Important APIs, types, and functions
`Server` stores HTTP server, options, Fs, VFS/proxy, gofakes3 instance, handler, secret, and ETag hash type. `newServer`, `getVFS`, `auth`, `Bind`, `Serve`, `Addr`, `Shutdown`, auth middlewares, `parseAccessKeyID`, `stringToMd5Hash`, and `getAuthSecret` are the key functions.

## Control flow
`newServer` selects ETag hash behavior, parses auth key pairs, builds gofakes3 with v4 auth and integrity checks, then either creates a fixed VFS or wraps the handler with proxy auth middleware. HTTP server routes all paths to the gofakes3 handler. Proxy mode extracts the access key ID from SigV4, calls the auth proxy, stores the VFS in request context, and adds a temporary auth key pair.

## State and persistence behavior
State includes the HTTP listener, one fixed VFS or per-auth proxy VFS cache, gofakes3 auth key registry, and request context values. The proxy path uses MD5(accessKeyID) as proxy username and accessKeyID as password input.

## Dependencies and integration points
Depends on chi, gofakes3, signature parsing, rclone HTTP server, VFS, proxy, hashes, and auth utilities in `utils.go`.

## Risks and edge cases
Anonymous access is allowed if no auth keys are provided. Proxy auth still adds auth keys dynamically and must parse Authorization correctly. `getAuthSecret` uses only the first auth pair secret. Adding auth keys per request may accumulate state in gofakes3.

## Test signals
S3 integration tests exercise fixed auth, proxy auth, rc startup, and real client behavior through this server.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/utils.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/utils.go

Source read: complete file, 139 lines, 2676 bytes, sha256 `50055f971d6f2e846bde1e60141553823cd485c1bcc35a4e2ad26b5d7cb1526e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/utils.go_research.md`.

## Purpose
Contains helper functions for S3 path, hash, directory, cleanup, and auth-pair handling.

## Important APIs, types, and functions
`getDirEntries`, `getFileHashByte`, `getFileHash`, `prefixParser`, `mkdirRecursive`, `rmdirRecursive`, and `authlistResolver` are package helpers used by backend/list/server code.

## Control flow
Directory helpers stat/read VFS nodes, create missing parent chains, and remove empty parent directories recursively. Hash helpers prefer `fs.Object.Hash` but can read VFS cache contents when an upload is still represented by a VFS node without an object entry.

## State and persistence behavior
No durable state. It reads or mutates remote directory structure through VFS mkdir/remove operations.

## Dependencies and integration points
Depends on VFS, gofakes3 errors, rclone hash/multihasher, path/string helpers, and `fs.Object`.

## Risks and edge cases
`mkdirRecursive` uses absolute-looking path construction after trimming and may be sensitive to VFS path conventions. `rmdirRecursive` is intentionally opportunistic and can remove empty parents after object delete. Hashing uploading VFS nodes can be expensive.

## Test signals
Covered indirectly by S3 object operations, listing, upload, and auth tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/serve.go -->
# sources/user-network-fs/rclone/cmd/serve/serve.go

Source read: complete file, 44 lines, 1137 bytes, sha256 `043ef0aa39cd687790343b2ae7fcb7030513c343567af79e3eaeac08fbed85ee`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/serve.go_research.md`.

## Purpose
Defines the top-level `rclone serve` command under which protocol subcommands register.

## Important APIs, types, and functions
`Command` is a Cobra command with help text and a `RunE` that errors when no protocol or an unknown protocol is supplied. `init` adds it to the root command.

## Control flow
The top-level command itself does not serve traffic; protocol packages call `serve.Command.AddCommand` in their init functions.

## State and persistence behavior
No runtime server state. It only contributes CLI registration and help text.

## Dependencies and integration points
Depends on rclone `cmd` root registration and Cobra.

## Risks and edge cases
Help text mentions metadata headers and delegates actual option behavior to subcommands. Unknown protocols produce a generic error.

## Test signals
Covered indirectly by CLI command registration; protocol tests exercise subcommands.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/serve.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go -->
# sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go

Source read: complete file, 35 lines, 554 bytes, sha256 `a87f5eabd427ca106a5c83aca90045852a3c46124f7ab643c6352d38defd1318`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go_research.md`.

## Purpose
Build-ignored auth proxy helper used by serve protocol integration tests.

## Important APIs, types, and functions
`main` expects a root path argument, decodes input JSON, and emits a local backend config with `_root` set to that root and `_obscure` set to `pass`.

## Control flow
Servetest invokes it via `go run` when exercising auth-proxy mode for local-backed protocol tests.

## State and persistence behavior
No persistent state; one request in, one config out.

## Dependencies and integration points
Depends only on standard JSON/log/os packages and the proxy JSON contract.

## Risks and edge cases
Hardcodes `type=local`, so `servetest.RunWithBackend` disables auth-proxy mode for non-local backing remotes.

## Test signals
Used by SFTP, WebDAV, and S3 serve integration tests through `servetest`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/proxy_code.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/rc.go -->
# sources/user-network-fs/rclone/cmd/serve/servetest/rc.go

Source read: complete file, 77 lines, 2005 bytes, sha256 `cefb3e4dea7b541e7475f996bbe92172010b0ad1740c6861a4e8b2ddae49d591`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/servetest/rc.go_research.md`.

## Purpose
Provides reusable tests for serve protocol rc registration and live TCP startup/shutdown.

## Important APIs, types, and functions
`GetEphemeralPort`, `checkTCP`, and `TestRc` allocate a localhost port, call rc `serve/start`, verify the returned id/address, test TCP connectivity, call `serve/stop`, and verify the port closes.

## Control flow
Protocol tests pass required rc params such as type and auth options; this helper adds `fs` and `addr`.

## State and persistence behavior
State is a temporary local directory and a live server registered in the global rc serve map until stopped.

## Dependencies and integration points
Depends on rc call registry, net dial/listen, and testify assertions.

## Risks and edge cases
There is a small race because an ephemeral port is closed then reused by the server. It assumes protocols bind TCP and support `addr` params.

## Test signals
Used by restic, sftp, webdav, and s3 tests to verify rc lifecycle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/rc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go -->
# sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go

Source read: complete file, 165 lines, 4968 bytes, sha256 `b9a1e82cd3fcd4dcf9ec8fc3a39327b1870ecbf0d292a49e897ecc0dcdaded44`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go_research.md`.

## Purpose
Shared integration harness for testing `rclone serve <protocol>` looped back into rclone backend integration tests.

## Important APIs, types, and functions
`StartFn`, `Run`, `RunWithBackend`, internal `run`, and `makeBackingFs` create a backing Fs, start the server, export backend config through environment variables, and execute the matching backend package's `go test`.

## Control flow
Normal mode passes a real Fs to the server. Auth-proxy mode passes nil and sets `proxy.Opt.AuthProxy` to `go run proxy_code.go <root>`. For named backing remotes, it starts the matching testserver and uses a random subremote.

## State and persistence behavior
State includes temporary/backing remote data, process cwd changes into backend package directories, environment variables for generated remote config, and temporary mutation of global proxy options.

## Dependencies and integration points
Depends on fstest, testserver, os/exec, configmap, proxy package, and backend integration test conventions.

## Risks and edge cases
Not parallel-safe around cwd and global proxy option mutation. Backend test failures can be caused by the served protocol, the client backend, or the backing remote.

## Test signals
Central test signal for protocol servers because SFTP, WebDAV, and S3 use it for generic backend conformance.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/servetest/servetest.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/connection.go

Source read: complete file, 385 lines, 10618 bytes, sha256 `26f6d68eb5bca3b87786a96138e87250ed1c77ad98b2323a253e3a994663f3dc`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/connection.go_research.md`.

## Purpose
Handles per-SSH-connection channel requests for serve sftp, including SFTP subsystem service and a constrained exec command surface for rclone compatibility.

## Important APIs, types, and functions
`describeConn`, `shellUnEscape`, `conn`, `execCommand`, `handleHashsumCommand`, `handleChannel`, `handleChannels`, `serveChannel`, `serveStdio`, and `stdioChannel` implement session behavior.

## Control flow
After SSH authentication, each session channel waits for either `subsystem sftp` or `exec`. SFTP sessions are served by `pkg/sftp.NewRequestServer`. Exec supports `df`, several hashsum commands, `rclone hashsum`, limited `xxhsum -H2`, and legacy `echo 'abc' | md5sum/sha1sum` probes, then sends an exit-status request.

## State and persistence behavior
Connection state is the selected VFS, SFTP handlers, and descriptive logging string. Stdio mode adapts stdin/stdout to an SFTP channel without SSH handshake.

## Dependencies and integration points
Depends on `pkg/sftp`, `x/crypto/ssh`, rclone hashes, VFS, terminal checks, and stdio files.

## Risks and edge cases
Exec parsing is intentionally limited and string-based; unsupported commands fail. Hashing an uploading VFS node may read cached file contents. Channel goroutines can block if clients open sessions without sending recognized requests.

## Test signals
`connection_test.go` covers shell unescaping. SFTP backend integration and handler tests exercise subsystem behavior and hash/stat interactions indirectly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go

Source read: complete file, 25 lines, 504 bytes, sha256 `b1db60ba63bddbc300badd8410d915ba0e853b6437dde13f7aaa382a3f4939e5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go_research.md`.

## Purpose
Tests SFTP shell-unescape behavior used for exec command arguments.

## Important APIs, types, and functions
`TestShellEscape` verifies escaping and newline restoration for strings that were shell-escaped by rclone.

## Control flow
The test calls `shellUnEscape` directly with table cases.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends on the regex and string replacement behavior in `connection.go`.

## Risks and edge cases
It covers only argument unescaping, not full exec command parsing.

## Test signals
Regression signal for hashsum paths containing escaped characters or embedded newlines.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/connection_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/handler.go

Source read: complete file, 194 lines, 4185 bytes, sha256 `a1a11939c64570a9c454b6c3cf568760ade1d1d77d8e0f8e6baba26461dbf9c5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/handler.go_research.md`.

## Purpose
Maps `pkg/sftp` file operation interfaces onto rclone VFS operations.

## Important APIs, types, and functions
`vfsHandler` embeds VFS and implements `Fileread`, `Filewrite`, `Filecmd`, `StatVFS`, `Filelist`, plus `listerat.ListAt`.

## Control flow
Read/write open VFS files according to SFTP flags. File commands implement Setstat size/mtime, Rename, Remove/Rmdir, Mkdir, and reject symlink/hardlink. Listing stats directories/files and adapts results to SFTP's `ListerAt` interface.

## State and persistence behavior
State mutations are remote file writes, truncates, modtime changes, renames, removals, and mkdirs through VFS. No extra local persistence.

## Dependencies and integration points
Depends on `pkg/sftp`, VFS node/handle APIs, os flags, syscall errors, and VFS statfs.

## Risks and edge cases
Flag handling must preserve resume semantics: absence of truncate must not zero existing content. Symlink/readlink are unsupported. StatVFS invents inode counts because VFS has no inode model.

## Test signals
`handler_test.go` validates resume without truncate, truncation, Setstat size, StatVFS, and mtime setting. Interface assertions in `sftp_test.go` confirm SFTP contracts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go

Source read: complete file, 217 lines, 6644 bytes, sha256 `6fe40de422d9696712d48c19848525534921ec65db8d168da5f791c7ade615aa`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go_research.md`.

## Purpose
Tests SFTP VFS handler behavior through a real SSH/SFTP client and server.

## Important APIs, types, and functions
`startTestServer` starts a local-backed SFTP server and returns a connected `pkg/sftp.Client`. Tests cover resumed writes, truncate opens, FSETSTAT truncation, StatVFS, and Chtimes/mtime.

## Control flow
Each test writes via the SFTP client, reads back through the client, and asserts file contents, size, statfs values, or modtime.

## State and persistence behavior
State is temporary local filesystem content served through VFS cache modes selected per test.

## Dependencies and integration points
Depends on local backend, x/crypto/ssh client, pkg/sftp client, proxy defaults, VFS options, and testify.

## Risks and edge cases
Build-tagged away on Windows, Darwin, and Plan 9. Tests use insecure host-key checking and are not parallel-safe around shared constants only by convention.

## Test signals
Strong regression signal for upload resume corruption, overwrite truncation, Setstat support, and StatVFS extension behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/server.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/server.go

Source read: complete file, 456 lines, 13791 bytes, sha256 `86d437581d1327e1e1107d5379a1a3ff1017cd19d21d68c80726fb1fb9c698c1`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/server.go_research.md`.

## Purpose
Builds and runs the SSH server for `rclone serve sftp`, including authentication, host key loading/generation, listener setup, and proxy integration.

## Important APIs, types, and functions
`server` stores Fs, options, fixed VFS or proxy, SSH config, listener, and stopped channel. `newServer`, `configure`, `acceptConnections`, `acceptConnection`, `getVFS`, `Serve`, `Shutdown`, key loading, authorized key loading, and RSA/ECDSA/Ed25519 key generation are central.

## Control flow
`configure` rejects conflicting auth-proxy and authorized-keys flags, loads authorized keys, enforces that some auth is configured unless `--no-auth`, builds password and public-key callbacks, loads or generates host keys under the cache dir, then obtains a socket-activation listener or binds TCP. Accepted SSH connections authenticate, map proxy credentials to a cached VFS key when needed, and hand channels to `connection.go`.

## State and persistence behavior
Persistent local state can include generated host key files in the rclone cache directory. Runtime state includes listener, SSH config, fixed VFS or proxy VFS cache, and per-connection permissions extensions.

## Dependencies and integration points
Depends on crypto key generation, `x/crypto/ssh`, rclone config/cache/env/file helpers, sdactivation, proxy, VFS, and server connection handlers.

## Risks and edge cases
Authentication safety depends on flag validation and constant-time user/pass checks. Auto-generated host keys persist and file permissions matter. `proxy.Opt.AuthProxy` is checked globally in places instead of only the passed proxy options, which can surprise tests or embedding. `loadAuthorizedKeys` silently skips parse errors while bytes remain only when no key parsed.

## Test signals
SFTP integration, handler, rc, and auth-proxy tests exercise listener startup, auth, VFS mapping, and shutdown.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/server.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go

Source read: complete file, 206 lines, 7046 bytes, sha256 `d52dc92ec47aea92e6b7583112b9a67d3673fadb9df57d273048e5ca611f8b15`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go_research.md`.

## Purpose
Defines the `rclone serve sftp` command, SFTP options, flags, stdio mode, and rc registration for non-Plan-9 builds.

## Important APIs, types, and functions
`OptionsInfo`, `Options`, global `Opt`, `AddFlags`, and `Command` define listen address, auth credentials, authorized keys, host keys, no-auth, stdio, VFS, and proxy flags.

## Control flow
Init registers options and rc factory. Command execution either serves the remote over stdin/stdout for subsystem mode or constructs `newServer` and accepts SSH connections.

## State and persistence behavior
State is CLI/global option binding plus server runtime. Stdio mode has no listener and serves one process stream.

## Dependencies and integration points
Depends on Cobra, configstruct, VFS/proxy flag helpers, serve rc, terminal/stdin handling in `connection.go`, and `server.go`.

## Risks and edge cases
Plan 9 is excluded. Stdio mode must not run directly on a terminal. Auth-proxy mode changes required arguments because the proxy supplies the backend.

## Test signals
`sftp_test.go`, `handler_test.go`, and `servetest.TestRc` validate command/server behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go

Source read: complete file, 88 lines, 2182 bytes, sha256 `df25fb10c666be8debecea6c5c70e49c8003e36a4d8935e002772624ca4fcd14`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go_research.md`.

## Purpose
Runs serve sftp integration tests and rc lifecycle tests.

## Important APIs, types, and functions
`TestSftp` starts an authenticated SFTP server and returns rclone SFTP backend config for generic backend tests. Interface assertions confirm `vfsHandler` satisfies pkg/sftp contracts. `TestRc` checks rc startup.

## Control flow
Tests launch the server, parse host/port from the listener, run `servetest.Run`, and cleanly shut down afterward.

## State and persistence behavior
State is temporary served remote data and a live SSH listener. Passwords are test constants and obscured in client config.

## Dependencies and integration points
Depends on local backend, servetest, obscure config, rc, VFS options, and pkg/sftp interfaces.

## Risks and edge cases
Build-tagged away on Windows, Darwin, and Plan 9. Generic backend failures can arise from client backend behavior as well as server behavior.

## Test signals
Broad signal that serve sftp can satisfy rclone's SFTP backend test suite in normal and auth-proxy local modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go -->
# sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go

Source read: complete file, 12 lines, 319 bytes, sha256 `b68eac50482246be953190799507e0ba1faf13f3cfeb1d2bed8a7c0c9468326e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go_research.md`.

## Purpose
Provides a Plan 9 stub for the SFTP serve command.

## Important APIs, types, and functions
`Command` is declared as `*cobra.Command` under the `plan9` build tag so imports can compile without a real SFTP server implementation.

## Control flow
No runtime control flow; the real command is absent on Plan 9.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends only on Cobra for the symbol type.

## Risks and edge cases
Users on Plan 9 cannot use serve sftp through this implementation.

## Test signals
Build coverage is the main signal; functional SFTP tests are excluded on Plan 9.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/sftp/sftp_unsupported.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go -->
# sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go

Source read: complete file, 727 lines, 21369 bytes, sha256 `98bf2afbddbab4f0daee8e059136bcdadbd029b8856b68e49ccd6e16e38c276c`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go_research.md`.

## Purpose
Implements `rclone serve webdav`, adapting rclone VFS to Go's WebDAV filesystem interface with optional directory browsing, zip downloads, ETags, gzip compression, and auth-proxy support.

## Important APIs, types, and functions
`Options`, `Command`, `WebDAV`, `newWebDAV`, `getVFS`, `auth`, `ServeHTTP`, `serveDir`, WebDAV filesystem methods (`Mkdir`, `OpenFile`, `RemoveAll`, `Rename`, `Stat`), `Handle`, `FileInfo`, `DeadProps`, `Patch`, `ETag`, and `ContentType` are the important APIs.

## Control flow
Startup resolves ETag hash options, creates either a fixed VFS or proxy-backed custom auth, constructs `lib/http.Server`, wraps routes with compression/range and server headers, registers WebDAV-only methods, and routes all paths to `ServeHTTP`. Directory GET/HEAD can render HTML or zip; other methods are delegated to `webdav.Handler`, followed by X-OC-Mtime postprocessing on successful COPY/MOVE/PUT.

## State and persistence behavior
Remote state is files/directories/modtimes managed through VFS. Runtime state includes HTTP server, WebDAV memory lock system, optional proxy VFS cache, ETag hash type, and template config. Dead properties expose checksums and lastmodified; PROPPATCH can update modtime.

## Dependencies and integration points
Depends on chi, Go `x/net/webdav`, rclone HTTP server/template/auth, VFS, proxy, hash APIs, and HTTP serve directory helpers.

## Risks and edge cases
Compression must skip Range requests to preserve partial content. Auth-proxy relies on lib/http custom auth storing a VFS in context. ETag and checksum generation may be expensive or unavailable. WebDAV rename overwrite semantics depend on VFS/backend behavior. Directory zip can stream large trees.

## Test signals
`webdav_test.go` covers generic WebDAV backend integration, directory/file HTTP behavior with golden output, gzip for text/PROPFIND, Range no-compression, and rc startup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go -->
# sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go

Source read: complete file, 354 lines, 9009 bytes, sha256 `6095bc47dc506979bb4bcaef7bab133733403535ee9b7d35abe3354011348ea1`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go_research.md`.

## Purpose
Tests serve webdav through backend integration, HTTP directory/file behavior, compression, range handling, and rc startup.

## Important APIs, types, and functions
`TestWebDav`, `TestHTTPFunction`, `HelpTestGET`, `startAuthenticatedServer`, compression tests, range test, and `TestRc` are the main tests. Interface assertions validate `FileInfo` WebDAV extensions.

## Control flow
Tests start local-backed WebDAV servers with auth/template/BaseURL/hash options, run generic backend tests, compare HTTP responses to golden files, and inspect gzip/range behavior with real HTTP clients.

## State and persistence behavior
State includes temporary server listeners, configured filter rules, golden files optionally rewritten by `-updategolden`, and local testdata files.

## Dependencies and integration points
Depends on local backend, servetest, filter config, gzip, net/http, WebDAV backend, templates, obscure passwords, and rc.

## Risks and edge cases
Build-tagged away on Windows and Darwin due troublesome character mappings. Golden tests are sensitive to template/output formatting. `-updategolden` writes fixture files when requested.

## Test signals
Strong signal for WebDAV protocol conformance, browser-style directory listing, auth, ETag/hash config, gzip middleware, and range safety.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/webdav/webdav_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/settier/settier.go -->
# sources/user-network-fs/rclone/cmd/settier/settier.go

Source read: complete file, 64 lines, 1827 bytes, sha256 `2a53951c8d05f1b0d45c633419a287dffe95b1eae90b9adbc9c631bdb64d6fe3`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/settier/settier.go_research.md`.

## Purpose
Defines the `rclone settier` command for changing storage class or tier on all objects under a remote path.

## Important APIs, types, and functions
`commandDefinition` is a Cobra command registered in init. Its Run function parses `tier` and `remote:path`, constructs an Fs, checks `Features().SetTier`, and calls `operations.SetTier`.

## Control flow
Execution is straightforward: validate two args, build source Fs, enter `cmd.Run`, reject unsupported backends, then delegate recursive tier mutation to operations.

## State and persistence behavior
Persistent state is remote object storage tier/class changed by the backend. No local state is stored.

## Dependencies and integration points
Depends on rclone command framework, Fs feature flags, and operations tiering.

## Risks and edge cases
Tier changes can make objects unavailable or incur provider costs; command only checks feature presence, not provider-specific tier validity before delegation.

## Test signals
Covered by operation/backend tests rather than a local test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/settier/settier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/sha1sum/sha1sum.go -->
# sources/user-network-fs/rclone/cmd/sha1sum/sha1sum.go

Source read: complete file, 69 lines, 2444 bytes, sha256 `eb2eaeb9acd198b51238a036aeac6dffd41b3af8864e9b9d042b8f96ce588646`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/sha1sum/sha1sum.go_research.md`.

## Purpose
Defines the compatibility `rclone sha1sum` command, equivalent to `rclone hashsum SHA1` with stdin and checksum-file support.

## Important APIs, types, and functions
`commandDefinition` registers hashsum flags and in `RunE` handles stdin hashing, source Fs creation, checksum-file verification, stdout listing, or output-file listing.

## Control flow
Control flow first accepts zero or one arg, lets `hashsum.CreateFromStdinArg` consume stdin when appropriate, then delegates to `operations.CheckSum` or `operations.HashLister` inside `cmd.Run`.

## State and persistence behavior
No persistent state except optional output file selected by hashsum flags. Remote files are read but not modified.

## Dependencies and integration points
Depends on `cmd/hashsum`, rclone hash type `SHA1`, and operations hash/checksum helpers.

## Risks and edge cases
Remote SHA-1 support varies; without `--download`, unsupported backends return empty hashes. Stdin hyphen handling depends on data availability.

## Test signals
Covered by shared hashsum/operations tests outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/sha1sum/sha1sum.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_bsd.go -->
# sources/user-network-fs/rclone/cmd/siginfo_bsd.go

Source read: complete file, 23 lines, 434 bytes, sha256 `55f63c183ae1854e505e3102e678dec4a2103fb84b104009cf78a8952b4ba2be`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/siginfo_bsd.go_research.md`.

## Purpose
Adds SIGINFO handling on BSD-like platforms to print global transfer statistics.

## Important APIs, types, and functions
`SigInfoHandler` creates a signal channel, registers for `syscall.SIGINFO`, and starts a goroutine that prints `accounting.GlobalStats()` for each signal.

## Control flow
Called from command startup on supported platforms; signal delivery triggers asynchronous stats output.

## State and persistence behavior
State is one signal channel and goroutine in the process. No persistent state.

## Dependencies and integration points
Depends on build tags for Darwin/BSD variants, `os/signal`, `syscall`, `fs.Printf`, and accounting stats.

## Risks and edge cases
Multiple registrations would create multiple goroutines if called more than once. Output is asynchronous with ongoing transfers.

## Test signals
Platform build and manual signal behavior are the test signal; no local unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_bsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_others.go -->
# sources/user-network-fs/rclone/cmd/siginfo_others.go

Source read: complete file, 7 lines, 150 bytes, sha256 `bbc2173a42d691d7758d030225eb9989152942c8c5e777d5060a0192f9576cd4`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/siginfo_others.go_research.md`.

## Purpose
Provides a no-op SIGINFO handler for non-BSD platforms.

## Important APIs, types, and functions
`SigInfoHandler` is an empty function under the inverse build tag.

## Control flow
No control flow.

## State and persistence behavior
No state.

## Dependencies and integration points
Depends only on build constraints matching the BSD implementation.

## Risks and edge cases
Users on these platforms do not get SIGINFO stats behavior through this hook.

## Test signals
Build coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/siginfo_others.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/size/size.go -->
# sources/user-network-fs/rclone/cmd/size/size.go

Source read: complete file, 84 lines, 2743 bytes, sha256 `780f08e1b8109d77b2ecb2c771be8bf5e613b7170c470082cf84098be064d452`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/size/size.go_research.md`.

## Purpose
Defines the `rclone size` command to count objects, bytes, and sizeless objects under a remote path.

## Important APIs, types, and functions
`jsonOutput` flag and `commandDefinition` implement CLI registration. Run builds an Fs, calls `operations.Count`, logs sizeless warnings, and prints JSON or human-readable totals.

## Control flow
Execution validates one path, enters `cmd.Run`, collects counts recursively according to global filters/depth, then formats output.

## State and persistence behavior
No remote mutation. Local state is only the command flag and stdout/log output.

## Dependencies and integration points
Depends on command framework, flags, JSON encoder, fs suffix formatting, and operations count.

## Risks and edge cases
Some backends report unknown sizes; the command counts them as empty and warns, so totals may be underestimated.

## Test signals
Covered by operations/count tests outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/size/size.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/sync/sync.go -->
# sources/user-network-fs/rclone/cmd/sync/sync.go

Source read: complete file, 108 lines, 4056 bytes, sha256 `3cf446b70a1c4ae2f04d8b160924b520d7c34ec41e9b577737c3f6aea52df9dd`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/sync/sync.go_research.md`.

## Purpose
Defines the high-risk `rclone sync` command, making destination contents match source and deleting destination-only data when appropriate.

## Important APIs, types, and functions
`createEmptySrcDirs`, logger options, and `commandDefinition` implement flags and command execution. Run parses source/destination with optional single source filename and calls `sync.Sync` or `operations.CopyFile`.

## Control flow
After argument validation, it configures optional loggers, attaches them to context if any logging flags are set, then delegates to sync operations for directory sync or file copy.

## State and persistence behavior
Persistent state is destination remote mutation: creates, updates, deletes, and optional empty source directory creation. Logger config can write external logs depending on flags.

## Dependencies and integration points
Depends on command framework, operations logger flags, `fs/sync`, and operations copy helpers.

## Risks and edge cases
This command can delete data; docs emphasize dry-run/interactive. Overlapping remotes, duplicate objects, filters, metadata root behavior, and delete-on-error safeguards are handled in delegated sync code but are critical risks.

## Test signals
Covered by broader sync/operations test suites outside this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/sync/sync.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go -->
# sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go

Source read: complete file, 57 lines, 1593 bytes, sha256 `d70bdc288c0bbcfa8e85241b5880c843bb06da1472b84a137f8924af893c2540`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go_research.md`.

## Purpose
Defines `rclone test changenotify`, a developer command for logging remote change notifications.

## Important APIs, types, and functions
`pollInterval` flag and `commandDefinition` call the backend `Features().ChangeNotify` callback and then block forever.

## Control flow
The command constructs the Fs, creates a poll channel, starts change notification, sends the poll interval, logs readiness, and waits on an empty select.

## State and persistence behavior
No persistent local state. It may cause backend polling/subscriptions and logs every callback.

## Dependencies and integration points
Depends on test command group, flags, Fs feature detection, and backend change-notify implementations.

## Risks and edge cases
Returns an error if the remote lacks ChangeNotify despite the message naming poll interval. It intentionally runs until interrupted.

## Test signals
Manual diagnostic signal for backend notification support; no unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/changenotify/changenotify.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/histogram/histogram.go -->
# sources/user-network-fs/rclone/cmd/test/histogram/histogram.go

Source read: complete file, 62 lines, 1537 bytes, sha256 `4b69811611d9012bbfe6609047ca39a81dbfafe5c52dd4616538b05bdd93ca67`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/histogram/histogram.go_research.md`.

## Purpose
Defines `rclone test histogram`, which emits a JSON histogram of byte values used in file basenames.

## Important APIs, types, and functions
`commandDefinition` lists objects recursively with `walk.ListR`, counts bytes in `path.Base(entry.Remote())` into a 256-entry array, and encodes it as JSON.

## Control flow
The command builds a directory Fs, uses current config max depth, walks object entries, counts basename bytes, writes JSON to stdout, and prints a trailing newline.

## State and persistence behavior
No remote mutation and no persistent state.

## Dependencies and integration points
Depends on walk.ListR, fs config, JSON encoder, path basename handling, and the test command group.

## Risks and edge cases
Counts UTF-8 bytes rather than runes, which is appropriate for filename compression diagnostics but important to interpret correctly.

## Test signals
Manual developer diagnostic; no direct unit test in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/histogram/histogram.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/all.sh -->
# sources/user-network-fs/rclone/cmd/test/info/all.sh

Source read: complete file, 16 lines, 445 bytes, sha256 `9aad378ec60258ac0f8e21dac309e55ac3ae206577d8f3a2a779e120eabc8e10`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/all.sh_research.md`.

## Purpose
Shell convenience wrapper for running the older `rclone info` checks across a fixed list of remotes.

## Important APIs, types, and functions
Execs `rclone --check-normalization=true --check-control=true --check-length=true info` with a local path and many `Test*:` remotes.

## Control flow
It replaces itself with the rclone process via `exec`; all behavior is delegated to the info command.

## State and persistence behavior
Remote test directories may be created or modified by the info command. The script itself writes no files.

## Dependencies and integration points
Depends on Bash, rclone in PATH, and configured test remotes.

## Risks and edge cases
Remote list includes historical names and may be stale. It is a manual helper, not robust orchestration.

## Test signals
Manual multi-remote signal for filename normalization/control/length support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/all.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/base32768.go -->
# sources/user-network-fs/rclone/cmd/test/info/base32768.go

Source read: complete file, 93 lines, 4933 bytes, sha256 `3e2b9461ed988fbed6e247f9b4fb9f3ab498aaa9e20a022e61adf89ececfc8e5`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/base32768.go_research.md`.

## Purpose
Adds a base32768 filename capability check to the `rclone test info` results.

## Important APIs, types, and functions
`safeAlphabet` is a large rune alphabet and `(*results).checkBase32768` creates many local files with generated Unicode names, syncs them to the remote, checks equality, and records `canBase32768`.

## Control flow
The check writes a temporary local tree, creates a remote test directory under the tested Fs, syncs local to remote, runs `operations.Check`, then purges the remote test directory.

## State and persistence behavior
Persistent remote state is temporary and purged unless purge fails. Local temp directory is removed with defer. The result boolean is stored in the in-memory results object.

## Dependencies and integration points
Depends on fspath, operations, sync, local temp files, and the surrounding `results` type from `info.go`.

## Risks and edge cases
Large Unicode filename sets can stress provider limits and cleanup. Failures are logged and result in false rather than aborting the entire info run.

## Test signals
Covered when `--check-base32768` is used on the info command.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/base32768.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/info.go -->
# sources/user-network-fs/rclone/cmd/test/info/info.go

Source read: complete file, 515 lines, 15058 bytes, sha256 `16b948420baef0886b3e1891346292821750ca1d9959f602d349328d7883a7f2`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/info.go_research.md`.

## Purpose
Implements `rclone test info`, a diagnostic command that probes backend filename/control-character limits, Unicode normalization behavior, streaming upload support, maximum filename lengths, and writes JSON reports.

## Important APIs, types, and functions
`results` captures remote name, control character maps, max lengths, normalization flags, streaming flag, base32768 flag, context, and Fs. Important methods include `newResults`, `Print`, `WriteJSON`, `checkControls`, `findMaxLength`, `checkUTF8Normalization`, `checkStreaming`, and `readInfo`.

## Control flow
Command flags select which probes run. Control checks create filenames with special characters in left/middle/right positions, attempt write/get/list operations, and record errors/presence. Length checks binary-search-ish increasing names. Normalization and base32768 checks sync/check generated local files. Streaming writes an unknown-size object and validates hashes/size.

## State and persistence behavior
The command creates and removes temporary remote test files/directories unless `--keep-test-files` is set. Results are printed and optionally written as JSON for later CSV aggregation.

## Dependencies and integration points
Depends on rclone Fs operations, sync/check/purge, object info, hash verification, Unicode normalization helpers, JSON encoding, and internal report types.

## Risks and edge cases
It intentionally mutates the target remote and can leave test files if interrupted or keep mode is enabled. Results are provider and account dependent. Some checks are expensive and may hit filename, API, or rate limits.

## Test signals
Manual diagnostic output plus `internal/build_csv` aggregation provide test signals; no conventional unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go -->
# sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go

Source read: complete file, 158 lines, 3922 bytes, sha256 `2682cf698135590806c37dbfa264ce1933ad5c00a3aa2eeaae52a3742a9e5e55`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go_research.md`.

## Purpose
Converts multiple `rclone test info` JSON reports into a comparative CSV matrix for control-character behavior.

## Important APIs, types, and functions
`main` parses `-o`, reads each JSON file into `internal.InfoReport`, builds sorted remote/character axes, maps write/get/list results to compact codes, and writes CSV. Helpers `sok` and `pok` convert errors/presence values.

## Control flow
Input files are decoded, reports lacking ControlCharacters are skipped, headers are generated in three rows, rows are emitted per character, and output goes to stdout or a created file.

## State and persistence behavior
Persistent state is the output CSV file when `-o` is not `-`. Inputs are read-only.

## Dependencies and integration points
Depends on CSV/JSON stdlib, sorted maps, strconv quoting, internal report types, and rclone fatal logging.

## Risks and edge cases
Only handles reports with control-character data; other info fields are ignored. Fatal logging exits on malformed inputs or write errors.

## Test signals
Used manually after collecting info JSON outputs to compare providers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/build_csv/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/internal.go -->
# sources/user-network-fs/rclone/cmd/test/info/internal/internal.go

Source read: complete file, 156 lines, 3233 bytes, sha256 `0b854873b214b4807d2748a45742955ebfb0fb9e074448c583655a0a16ab0f8d`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/internal/internal.go_research.md`.

## Purpose
Defines shared data types and JSON/text encodings for `rclone test info` reports.

## Important APIs, types, and functions
`Presence`, `Position`, constants, `PositionList`, `ControlResult`, and `InfoReport` model control-character results and backend capability booleans. `String`, marshal, and unmarshal methods provide stable textual/JSON representations.

## Control flow
Positions marshal as text map keys such as `left,middle`; presence values marshal as JSON strings such as `present` or `renamed`.

## State and persistence behavior
No runtime state beyond values being encoded/decoded.

## Dependencies and integration points
Depends on bytes, JSON, string parsing, and fmt errors.

## Risks and edge cases
Unmarshal errors currently format `%s` with the receiver in some cases, which may not show the raw unknown string clearly. Invalid bitmasks panic in `Position.String`.

## Test signals
Used by info command JSON output and CSV builder; encoding stability is the main compatibility signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/internal/internal.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/test.sh -->
# sources/user-network-fs/rclone/cmd/test/info/test.sh

Source read: complete file, 51 lines, 1136 bytes, sha256 `1afe60f396e63edf8781b709bb2a8b118aec3009f56d506ba1968eaa1b16a284`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/info/test.sh_research.md`.

## Purpose
Zsh helper for running `rclone info` diagnostics across selectable remotes, suitable for parallel execution.

## Important APIs, types, and functions
Defines an associative array of remotes to extra flags, supports `--list`, sets local special-case config, purges the test directory, runs `rclone info -vv --write-json`, and captures logs/listing output.

## Control flow
For each remote, the script constructs a target directory, purges it best-effort, runs info, and then lists the directory into a `.list` file.

## State and persistence behavior
Writes `info-$remote.json`, `info-$remote.log`, and `info-$remote.list` in the current directory. Mutates/purges remote `infotest` directories.

## Dependencies and integration points
Depends on zsh, GOPATH layout, rclone binary, configured test remotes, and optional provider-specific environment variables such as `GCS_BUCKET`.

## Risks and edge cases
It is destructive for the chosen test directory and uses historical remote names/flags. Designed for manual diagnostics rather than CI.

## Test signals
Manual multi-provider data collection signal for `cmd/test/info`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/info/test.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go -->
# sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go

Source read: complete file, 310 lines, 9099 bytes, sha256 `ff975e608d1fabfc728350812cbed7b85f85ff33987b2e12914dd5ce526cef0e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go_research.md`.

## Purpose
Implements developer commands for generating random file trees or fixed-size files for testing.

## Important APIs, types, and functions
`makefilesCmd`, `makefileCmd`, shared flags, `commonInit`, `makefiles`, readers (`zeroReader`, `asciiReader`, `chargenReader`), `fileName`, `dir.createDirectories`, `dir.list`, and `writeFile` are the main functions.

## Control flow
`makefiles` mode builds a random directory tree according to file count, average files per directory, max depth, sizes, and seed, then writes files with selected content source. `makefile` mode parses one size and writes each named file. Common init chooses deterministic/random seed and validates mutually exclusive content flags.

## State and persistence behavior
Persistent state is the generated local filesystem files and directories. Global package variables hold flags, random source, content reader, directory counts, and used filenames for the current command run.

## Dependencies and integration points
Depends on the rclone test command group, fs size suffix flags, file mkdir helpers, random string helpers, pattern readers, and os/filepath IO.

## Risks and edge cases
Global filename uniqueness is process-wide for one run and does not reset between command invocations in the same process. Sparse files rely on filesystem support. Random tree shape can vary widely with parameters; seed controls reproducibility.

## Test signals
Manual test-data generation utility; no unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/test/makefiles/makefiles.go -->
