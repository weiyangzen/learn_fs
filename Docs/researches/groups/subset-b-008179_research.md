# Research: subset-b-008179

Grouped source-tree-aligned research for the assigned MinIO Client and MinIO server files. Each section preserves the source path in its title and is delimited for reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/undo-main.go -->
## sources/object-store/minio-mc/cmd/undo-main.go

Purpose: implements `mc undo`, a versioned-bucket recovery command that removes the newest object versions or delete markers to reverse recent PUT/DELETE operations. Important surfaces include `undoCmd`, `undoFlags`, `undoMessage`, `parseUndoSyntax`, `undoURL`, `undoLastNOperations`, `checkIfBucketIsVersioned`, and `mainUndo`.

Control flow validates one target, positive `--last`, `--recursive --force`, optional `--dry-run`, and an `--action` filter limited to single-object undo. `mainUndo` checks bucket versioning before `undoURL` lists versions with delete markers, groups by object path, filters Glacier entries, and calls `Client.Remove` with selected versions. State is remote S3 version metadata; local state is only output. Dependencies are mc `Client`, alias expansion, versioning APIs, `probe`, and color/json output. Risks include destructive deletes, action filtering relying on latest-version ordering, and dry-run still printing success-like messages. Test signal in this subset is indirect; functional coverage would need versioned bucket undo cases.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/undo-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update-main.go -->
## sources/object-store/minio-mc/cmd/update-main.go

Purpose: implements `mc update`, release discovery, checksum/signature verification, download, and in-place binary replacement. Key APIs are `mcVersionToReleaseTime`, `releaseTagToReleaseTime`, `GetCurrentReleaseTime`, environment detectors, `getUserAgent`, `DownloadReleaseData`, `parseReleaseData`, `getUpdateInfo`, `getUpdateTransport`, `getUpdateReaderFromURL`, `doUpdate`, `updateMessage`, and `mainUpdate`.

Control flow compares current release time from `Version` or executable mtime with official sha256sum metadata, builds an archive URL or Docker pull message, and applies `selfupdate` with SHA256. Optional minisign verification is enabled by `MC_UPDATE_MINISIGN_PUBKEY`. State touched is the running executable; release state is fetched over HTTPS using `globalRootCAs`. Integration points include terminal coloring, proxy/TLS transport, progress reader, env, and `selfupdate`. Risks are high because failed writes affect the executable; permission, rollback, checksum, custom URL, FIPS URL, and source-build semantics need careful tests. Existing direct tests are absent here.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update-notifier.go -->
## sources/object-store/minio-mc/cmd/update-notifier.go

Purpose: formats the user-facing "new mc version available" notice used by update checks. Important functions are `prepareUpdateMessage` and `colorizeUpdateMessage`.

Control flow returns no message if no download URL or non-positive age is supplied; otherwise it converts the age to a human-readable relative duration and renders either a boxed terminal notice or a two-line fallback when the terminal is too narrow. State is none beyond terminal width probing. Dependencies include `go-humanize`, `pb.GetTerminalWidth`, runtime OS checks, and color functions from `update-main.go`. Integration is through `getUpdateInfo`. Risks include Unicode box rendering on non-Windows terminals, ANSI-length calculations, and width fallback behavior. There are no direct tests in the subset; validation is mostly visual and terminal-dependent.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update-notifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update_fips.go -->
## sources/object-store/minio-mc/cmd/update_fips.go

Purpose: selects the FIPS release metadata endpoint for `mc update` builds compiled with the `fips` build tag. It defines `mcReleaseInfoURL` as `mcReleaseURL + "mc.fips.sha256sum"`.

Control flow is compile-time only: the Go build constraint `//go:build fips` ensures this file replaces the non-FIPS URL definition. State and persistence are absent; it only influences network fetches made by `DownloadReleaseData`. Dependencies are the package-level `mcReleaseURL` constant from `update-main.go`. Integration risk is mis-building a FIPS binary with the wrong tag, which would fetch ordinary checksums. Test signal would require build-tag-specific compile or unit checks.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update_fips.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update_nofips.go -->
## sources/object-store/minio-mc/cmd/update_nofips.go

Purpose: selects the standard release metadata endpoint for `mc update` builds without the `fips` build tag. It defines `mcReleaseInfoURL` as `mcReleaseURL + "mc.sha256sum"`.

Control flow is entirely compile-time through `//go:build !fips`. Runtime state is absent; the variable is consumed by `DownloadReleaseData` unless the caller supplies a custom release URL or Windows uses the `.exe.sha256sum` variant. Dependencies are limited to `mcReleaseURL`. The main risk is configuration drift with the FIPS file, because exactly one of the two URL definitions must compile. Test signal is build-matrix oriented rather than behavioral in normal unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/update_nofips.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/urls.go -->
## sources/object-store/minio-mc/cmd/urls.go

Purpose: defines `URLs`, the source/target transfer descriptor used by copy/sync-style operations. It carries aliases, `ClientContent` records, total counts and sizes, multipart and MD5 flags, checksum type, encryption key database, and non-serialized error/difference fields.

Important APIs are `WithError`, which returns a copy with `Error` set, and `Equal`, which compares source and target URL identity while tolerating nil content sides. State is in-memory operation metadata; JSON output omits `Error` and `ErrorCond`. Dependencies include `probe`, `minio.ChecksumType`, `prefixSSEPair`, and `differType`. Risks are value-copy semantics: callers expecting mutation from `WithError` must use the returned value. `Equal` compares URL structs directly, so canonicalization must happen before population. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/urls.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/utils.go -->
## sources/object-store/minio-mc/cmd/utils.go

Purpose: shared mc command utilities for error classification, random names, TLS debug output, S3 config construction, truncation, object age filters, bucket lookup mode, URL containment, filesystem metadata parsing, terminal text centering, admin client creation, HTTP client construction, Prometheus JWT generation, and conservative filenames.

Important functions include `isErrIgnored`, `UTCNow`, `randString`, `NewS3Config`, `isOlder`, `isNewer`, `parseAtimeMtime`, `parseAttribute`, `httpClient`, and `getPrometheusToken`. State comes from globals such as `globalDebug`, `globalInsecure`, root CAs, transfer limits, and alias config. Dependencies include minio-go, madmin, JWT, ieproxy, TLS, and `probe`. Risks include fatal parsing in age filters, metadata grammar ambiguity around slash/colon separators, insecure TLS being global, and random string shortening to half the requested length. `utils_test.go` covers attribute parsing only.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/utils_test.go -->
## sources/object-store/minio-mc/cmd/utils_test.go

Purpose: unit tests for `parseAttribute` in `utils.go`, focused on metadata strings stored in `X-Amz-Meta-Mc-Attrs` or the s3cmd-compatible metadata key.

Control flow uses table-driven cases for empty strings, whitespace, slash-only input, incomplete `atime:/`, key-only attributes, key-colon attributes, and a valid multi-attribute string. It asserts both returned maps and exact sentinel error identity with `ErrInvalidFileSystemAttribute`. State is local to the test. Dependencies are Go `testing` and `reflect.DeepEqual`. The test signal is useful but narrow: it does not cover `parseAtimeMtime`, alternate metadata keys, duplicate attributes, or malformed colon counts beyond the listed cases. Risk is exact error comparison, which depends on returning the package sentinel.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/utils_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-enable.go -->
## sources/object-store/minio-mc/cmd/version-enable.go

Purpose: implements `mc version enable`, including optional excluded prefixes and folder-object exclusion for versioned buckets. Key surfaces are `versionEnableCmd`, `versionEnableFlags`, `versionEnableMessage`, `checkVersionEnableSyntax`, and `mainVersionEnable`.

Control flow requires exactly one `ALIAS/BUCKET`, splits `--excluded-prefixes` by comma, reads `--exclude-folders`, creates a client, and calls `client.SetVersion(ctx, "enable", excludedPrefixes, excludeFolders)`. State is remote bucket versioning metadata; no local persistence. Dependencies include cli, console color, JSON output, and the mc `Client` abstraction. Integration points include MinIO/S3 versioning APIs and shared globals set by `setGlobalsFromContext`. Risks include no trimming/validation of comma-separated prefixes in this layer and an apparent JSON tag typo for `ExcludeFolders`. No direct tests here.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-enable.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-info.go -->
## sources/object-store/minio-mc/cmd/version-info.go

Purpose: implements `mc version info`, reporting bucket versioning status, MFADelete, excluded prefixes, and folder exclusion. Important surfaces are `versionInfoCmd`, `versioningInfoMessage`, `checkVersionInfoSyntax`, and `mainVersionInfo`.

Control flow requires one target, initializes a client, calls `client.GetVersion`, copies returned status fields into the output message, and prints either JSON or colored text. State is read-only remote bucket metadata. Dependencies include cli, colorjson, console, and the client versioning API. Integration points are the `version` command group and global output settings. Risks are mostly reporting drift: empty status is rendered as un-versioned, and excluded prefix structs are flattened to strings. Test signal is absent in this subset; useful coverage would include enabled, suspended, and unconfigured buckets.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-main.go -->
## sources/object-store/minio-mc/cmd/version-main.go

Purpose: registers the top-level `mc version` command and its `enable`, `suspend`, and `info` subcommands. Important symbols are `versionSubcommands`, `versionCmd`, and `mainVersion`.

Control flow delegates all real behavior to subcommands; invoking `mc version` without a valid subcommand calls `commandNotFound`. State and persistence are absent. Dependencies are the local subcommand variables and `github.com/minio/cli`. Integration is purely CLI routing with global flags and `setGlobalsFromContext`. Risks are minimal but include forgetting to add new subcommands to `versionSubcommands`, which would make them unreachable. Test signal is indirect through CLI command table tests, not present in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-suspend.go -->
## sources/object-store/minio-mc/cmd/version-suspend.go

Purpose: implements `mc version suspend`, changing an existing bucket's versioning state to suspended. Key surfaces are `versionSuspendCmd`, `versionSuspendMessage`, `checkVersionSuspendSyntax`, and `mainVersionSuspend`.

Control flow requires exactly one target, constructs a client, and calls `client.SetVersion(ctx, "suspend", nil, false)`, then prints a success message. State is remote bucket versioning metadata. Dependencies include cli, console, colorjson, `probe`, and the client abstraction. Integration points are the top-level `version` command and S3/MinIO versioning APIs. Risks include server-side constraints not visible here, such as object lock or replication preventing suspension; this layer relies on the server/client error. No direct tests are included.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/version-suspend.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/watch-main.go -->
## sources/object-store/minio-mc/cmd/watch-main.go

Purpose: implements `mc watch`, a CLI for streaming object notification events from S3-compatible targets or local paths. Important surfaces are `watchCmd`, `watchFlags`, `watchMessage`, `checkWatchSyntax`, and `mainWatch`.

Control flow validates one target, parses event/prefix/suffix/recursive filters, creates a client, calls `Client.Watch`, and starts a goroutine that selects over global cancellation, event batches, and errors. Each event is converted to `watchMessage` for JSON or colored text. State is streaming only; no persistence. Dependencies include minio notification types, `probe`, humanized sizes, console colors, and global context. Risks include long-running goroutine lifecycle, closing `DoneChan` on cancellation, and event filter semantics delegated to client implementations. Functional test script covers `test_watch_object` only outside Mint mode.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/watch-main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/watch.go -->
## sources/object-store/minio-mc/cmd/watch.go

Purpose: reusable watch fan-in primitives independent of CLI formatting. It defines `EventInfo`, `WatchOptions`, `WatchObject`, and `Watcher`.

Control flow exposes event/error channels on `WatchObject`; `NewWatcher` creates aggregate channels and a wait group; `Join` calls `client.Watch` with put/delete/bucket creation/removal events, appends the watch object, and starts a goroutine to forward child events/errors into aggregate channels until `DoneChan` closes. `Stop` closes every child `DoneChan` and waits. State is in-memory channel and goroutine coordination. Dependencies are `Client`, `probe`, context, sync, time, and notification event types. Risks include sending to unbuffered aggregate channels without a receiver and close ordering if multiple stop paths close the same child channel. Tests are indirect.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/watch.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/contributors.sh -->
## sources/object-store/minio-mc/contributors.sh

Purpose: regenerates `CONTRIBUTORS.md` from git commit authors. The script changes to the repository directory, writes a fixed markdown header, then appends unique sorted `git log --format='%aN <%aE>'` entries as bullets.

Control flow is linear under `set -e`; any git/sort/sed failure aborts. State and persistence are the generated `CONTRIBUTORS.md` file in the mc repo. Dependencies are bash, `readlink -f`, git history, UTF-8 sort, and sed. Integration point is release or maintenance automation; it relies on `.mailmap` for author normalization. Risks include portability because `readlink -f` is not universal on macOS, and generated output depends on complete git history. Test signal is operational, not unit-tested.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/contributors.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/docker-buildx.sh -->
## sources/object-store/minio-mc/docker-buildx.sh

Purpose: release helper for publishing multi-architecture mc Docker images to Docker Hub and Quay. It disables IPv6, derives the release tag from `git describe --abbrev=0 --tags`, builds/pushes standard and old-CPU images, prunes buildx cache between builds, then re-enables IPv6.

State changes include host sysctl IPv6 settings, remote pushed images, and Docker build cache pruning. Dependencies are bash, sudo, git tags, Docker buildx, Dockerfiles `Dockerfile.release` and `Dockerfile.release.old_cpu`, and registry credentials. Risks are significant because host networking is modified and images are pushed with `latest` tags; failures before the final sysctl can leave IPv6 disabled. Test signal is manual/release-pipeline execution, not unit tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/docker-buildx.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/functional-tests.sh -->
## sources/object-store/minio-mc/functional-tests.sh

Purpose: end-to-end functional test suite for the `mc` binary, usable directly against play.min.io or under Mint with provided endpoint credentials and JSON result output. It exercises buckets, objects, recursive copy/mirror, find, watch, presigned share, metadata, storage class, SSE-C, alias config, and admin user/policy workflows.

Important helpers include `assert`, `mc_cmd`, `check_md5sum`, setup/teardown, and many `test_*` functions. Control flow initializes temp config/data, creates 0B/1MB/65MB files, sets aliases, runs `run_test`, then cleans temp paths. State includes remote random buckets/objects/users and local temp data/config. Dependencies are bash, `mc`, jq, curl, md5sum, base64, MinIO/S3 credentials, and optional Mint env. Risks include live-server flakiness, random-name collisions, destructive `rb --force --dangerous`, SSE tests requiring HTTPS, and partial cleanup after failures. Test signal is broad integration coverage rather than isolated unit proof.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/functional-tests.sh -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/main.go -->
## sources/object-store/minio-mc/main.go

Purpose: minimal process entry point for the mc command binary. It imports `github.com/minio/mc/cmd` as `mc`, calls `mc.Main(os.Args)`, and terminates through `console.Fatalln` if an error is returned.

Control flow is a single delegation from package `main`; all CLI registration, globals, and command behavior live in `cmd`. State is limited to process arguments and exit behavior. Dependencies are `os`, the mc command package, and MinIO console output. Integration is the build target import path `github.com/minio/mc`. Risks are low; the main concern is that any returned error is fatal and formatting is controlled by console. Test signal is normally covered by command package tests or binary smoke tests, not this file directly.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/main.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn.go -->
## sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn.go

Purpose: wraps `net.Conn` to set per-read and per-write deadlines immediately before each operation. Important APIs are `DeadlineConn`, `Read`, `Write`, `WithReadDeadline`, `WithWriteDeadline`, and `New`.

Control flow is simple: `Read` calls `setReadDeadline` when configured and delegates to the embedded connection; `Write` does the same for writes. State is the wrapped connection plus configured durations. Dependencies are `net` and `time`. Integration points are network clients needing idle-operation timeouts without changing callers that expect `net.Conn`. Risks include ignoring `SetReadDeadline`/`SetWriteDeadline` errors, data races if deadlines are mutated concurrently, and the deadline being relative to call start rather than total request lifetime. `deadlineconn_test.go` verifies read deadlines are refreshed across delayed reads.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn_test.go -->
## sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn_test.go

Purpose: integration-style unit test for `DeadlineConn` timeout behavior using a real local TCP listener and client.

Control flow starts a listener, accepts one TCP connection, wraps it, sets one-second read/write deadlines, reads `message one`, sleeps three seconds, reads `message two`, then writes a response. The client writes both messages and expects `messages received`. State is local sockets and a wait group. Dependencies are `net`, `io`, `bufio`, `sync`, and `testing`. The signal is specifically that read deadlines are reset before every read, so processing delays between reads do not permanently expire the connection. Risks include timing flakiness under extremely slow CI and no explicit negative timeout assertion.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/deadlineconn/deadlineconn_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_darwin.go -->
## sources/object-store/minio-mc/pkg/disk/stat_darwin.go

Purpose: Darwin implementation of `GetFileSystemAttrs`, serializing filesystem metadata into the mc metadata attribute string used by preserve-attributes copy flows.

Control flow calls `syscall.Stat`, then appends `atime`, `gid`, optional `gname`, `mode`, `mtime`, `uid`, and optional `uname` using Darwin `Atimespec` and `Mtimespec` fields. State is read-only local filesystem metadata. Dependencies are `syscall`, `os/user`, `strconv`, and `strings.Builder`. Integration is with `mc cp -a` and `parseAttribute`/`parseAtimeMtime`. Risks include user/group lookup failures being silently omitted, platform-specific stat field drift, and no escaping for names containing separators. Tests in this subset only validate parsing, not Darwin stat output.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_freebsd.go -->
## sources/object-store/minio-mc/pkg/disk/stat_freebsd.go

Purpose: FreeBSD implementation of `GetFileSystemAttrs`, emitting mode, owner, group, access time, and modification time as a slash-separated metadata string.

Control flow performs `syscall.Stat`, formats `Atimespec` and `Mtimespec` seconds/nanoseconds with explicit `int64` casts, appends numeric IDs, and conditionally appends resolved user/group names. State is read-only filesystem metadata. Dependencies are `syscall`, `os/user`, `strconv`, and `strings`. Integration is cross-platform attribute preservation. Risks include silent omission of names, separator collisions in names, and platform-specific build coverage. The comment references an issue requiring int64 casts, making regression tests or build checks on FreeBSD valuable.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_linux.go -->
## sources/object-store/minio-mc/pkg/disk/stat_linux.go

Purpose: Linux implementation of `GetFileSystemAttrs` for preserved filesystem metadata. It uses `os.Stat` and casts `FileInfo.Sys()` to `*syscall.Stat_t`.

Control flow reads stat data, formats `Atim` and `Mtim` seconds/nanoseconds, appends GID, optional group name, mode, UID, and optional user name. State is read-only local file metadata; output is later stored as object metadata. Dependencies are `os`, `syscall`, `os/user`, `strconv`, and `strings.Builder`. Risks include the unchecked type assertion on `Sys()`, omitted lookup names in minimal containers, and no ctime/md5 despite the comment mentioning them. Functional tests include `test_copy_object_preserve_filesystem_attr`, which compares local and remote metadata on the runtime platform.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_netbsd.go -->
## sources/object-store/minio-mc/pkg/disk/stat_netbsd.go

Purpose: NetBSD implementation of `GetFileSystemAttrs`, mirroring the BSD attribute serialization for mc preserved attributes.

Control flow calls `syscall.Stat`, formats `Atimespec` and `Mtimespec`, appends numeric UID/GID and optional resolved user/group names. State is read-only filesystem metadata. Dependencies are syscall and user lookup APIs. Integration is the same metadata path used by copy/archive commands that preserve filesystem attributes. Risks are platform-specific compile/runtime coverage, silent name omissions, and delimiter collisions in user/group names. No direct NetBSD test is present in the subset, so build-matrix coverage is the main signal.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_other.go -->
## sources/object-store/minio-mc/pkg/disk/stat_other.go

Purpose: OpenBSD/Solaris implementation of `GetFileSystemAttrs` selected by `//go:build openbsd || solaris`. It serializes stat metadata using `Atim` and `Mtim` fields.

Control flow is equivalent to the Linux/BSD variants: stat file, append times, numeric IDs, optional names, and mode into the slash-separated attribute string. State is read-only filesystem metadata. Dependencies are `syscall`, `os/user`, and formatting packages. Integration is cross-platform preserved attribute support. Risks include platform struct differences, silent lookup failure, and no direct tests on these less-common targets. The build tag itself is a key integration point because unsupported platforms must either use this file or provide another implementation.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_windows.go -->
## sources/object-store/minio-mc/pkg/disk/stat_windows.go

Purpose: Windows implementation stub for `GetFileSystemAttrs`. It returns an empty string and nil error.

Control flow and state are intentionally absent; Windows does not preserve the Unix-style metadata represented by the other platform files. Dependencies are none beyond package compilation. Integration is with cross-platform copy commands that call the function unconditionally. Risks include users expecting `mc cp -a` to preserve Windows attributes, and tests comparing metadata need platform-aware expectations. The empty success return avoids failing operations but can hide unsupported behavior. No direct Windows test is present in the subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/disk/stat_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/hookreader/hookreader.go -->
## sources/object-store/minio-mc/pkg/hookreader/hookreader.go

Purpose: wraps a source `io.Reader` and a hook reader so each successful source read is mirrored to the hook, commonly for progress accounting. Important APIs are `hookReader`, `Read`, `Seek`, and `NewHook`.

Control flow reads from the source, returns non-EOF source errors immediately, then calls `hook.Read` with the exact bytes read and returns non-EOF hook errors. `Seek` delegates to the source if it implements `io.Seeker`, otherwise to the hook if it does. State is the two readers. Dependencies are only `io`. Risks include the hook being modeled as a reader rather than writer, partial hook reads not being validated, EOF treatment that may hide hook completion, and `Seek` not coordinating both readers. `hookreader_test.go` covers basic progress byte counting.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/hookreader/hookreader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/hookreader/hookreader_test.go -->
## sources/object-store/minio-mc/pkg/hookreader/hookreader_test.go

Purpose: gocheck-based unit test for the hookreader progress behavior.

Control flow creates a buffer containing `Hello`, a `customReader` that counts the length of every buffer it receives, wraps both with `NewHook`, reads three bytes, and asserts the source returned three bytes while progress counted three. State is local buffers and a counter. Dependencies are `testing`, `bytes`, and `gopkg.in/check.v1`. Test signal is basic but narrow: it does not test nil hook passthrough, source or hook errors, EOF behavior, partial reads, or `Seek`. It confirms the intended integration contract for progress bars.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/hookreader/hookreader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/httptracer/httptracer.go -->
## sources/object-store/minio-mc/pkg/httptracer/httptracer.go

Purpose: provides an `http.RoundTripper` wrapper that invokes request/response trace hooks and logs response time in debug output. Important surfaces are `HTTPTracer`, `RoundTripTrace`, `RoundTrip`, and `GetNewTraceTransport`.

Control flow records start time, rejects nil underlying transports, delegates `RoundTrip`, then calls `Trace.Request(req)` and `Trace.Response(res)` if a tracer is configured. State is only wrapper configuration. Dependencies are `net/http`, `time`, `errors`, and MinIO console debug logging. Integration is with HTTP clients that need request/response tracing without changing transport users. Risks include hooks being called after the response returns rather than before the request is sent, returning nil response on hook error, and response body lifetime concerns. The test file is effectively empty.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/httptracer/httptracer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/httptracer/httptracer_test.go -->
## sources/object-store/minio-mc/pkg/httptracer/httptracer_test.go

Purpose: placeholder gocheck test harness for `pkg/httptracer`.

Control flow registers a gocheck suite and defines `TestHTTPTracer`, but the test body is empty. State and persistence are absent. Dependencies are `testing` and `gopkg.in/check.v1`. Test signal is therefore only that the package compiles and the gocheck harness can run; it does not validate nil transport errors, hook invocation order, propagation of hook errors, response-time debug logging, or behavior with failed underlying transports. The main risk is a false sense of coverage for a transport wrapper that can affect all HTTP traffic where installed.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/httptracer/httptracer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/limiter/limiter.go -->
## sources/object-store/minio-mc/pkg/limiter/limiter.go

Purpose: wraps an `http.RoundTripper` to apply upload and download throughput limits using token buckets. Important APIs are `New`, `RoundTrip`, and `limitReader`.

Control flow returns the original transport when both limits are zero; otherwise it creates upload/download buckets for positive limits. During `RoundTrip`, request bodies are replaced with a read-closer whose reader is rate-limited, the underlying transport is called, and response bodies are similarly wrapped. State is the bucket pair and underlying transport. Dependencies are `net/http`, `io`, and `juju/ratelimit`. Risks include nil transport errors, shared bucket behavior across concurrent requests, wrapping response bodies even when the underlying transport returns both response and error, and no tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/limiter/limiter.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/probe/probe.go -->
## sources/object-store/minio-mc/pkg/probe/probe.go

Purpose: tracing error wrapper used across mc to preserve cause, call trace, system info, and app metadata. Important APIs are `Init`, `SetAppInfo`, `GetSysInfo`, `NewError`, `(*Error).Trace`, `Untrace`, `ToGoError`, and `String`.

Control flow captures root path from the caller of `Init`, initializes app metadata, captures host/runtime/memory details for each new error, and appends trace points from callers. `String` prints the cause, reverse call trace, app info, and system details. State includes global `rootPath` and `appInfo`, plus per-error locked trace slices. Dependencies are runtime, filesystem paths, hostname, humanized memory, and sync locks. Risks include global map writes without locking, missing `Init` causing untrimmed paths, and verbose error strings leaking host/app data. Tests cover trace creation and wrapping.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/probe/probe.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/probe/probe_test.go -->
## sources/object-store/minio-mc/pkg/probe/probe_test.go

Purpose: gocheck tests for probe tracing and error wrapping.

Control flow defines three helper functions that stat a non-existent file and add trace tags, calls `probe.Init`, sets `Commit-ID`, verifies traced errors are non-nil, adds another trace, then verifies `WrapError`/`UnwrapError` round-trips a `*probe.Error`. State is global probe root/app info and local error values. Dependencies are `os`, `testing`, probe, and gocheck. Test signal confirms happy-path construction but does not assert trace contents, string formatting, system info, `Untrace`, nil behavior, or concurrent access. It is a smoke test rather than a full specification.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/probe/probe_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/pkg/probe/wrapper.go -->
## sources/object-store/minio-mc/pkg/probe/wrapper.go

Purpose: adapts `*probe.Error` to the standard `error` interface and back. Important APIs are `WrapError`, `UnwrapError`, and `(*wrappedError).Error`.

Control flow stores the probe error in a private `wrappedError` struct; `UnwrapError` type-switches on `*wrappedError` and returns the inner value plus a boolean; `Error` delegates to the probe error's `String`. State is a single pointer. Dependencies are only the local `Error` type. Integration points are APIs that must return `error` while preserving rich probe traces for callers that know how to unwrap. Risks include wrapping nil probe errors, no support for Go's conventional `Unwrap() error`, and type identity being private. Tests cover basic unwrap success.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/pkg/probe/wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/staticcheck.conf -->
## sources/object-store/minio-mc/staticcheck.conf

Purpose: Staticcheck configuration for the mc repository. It enables all checks and disables `S1016`.

Control flow and runtime state are absent; this is tooling configuration consumed by Staticcheck. The integration point is CI or local lint invocation. Disabling `S1016` means Staticcheck will not suggest converting struct literals between identical types, likely preserving explicit conversions or public API clarity used in the codebase. Risks are limited to lint coverage: disabling a style check can hide simplification opportunities but avoids noisy or undesirable rewrites. Test signal is external through lint jobs, not code tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/staticcheck.conf -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/acl-handlers.go -->
## sources/object-store/minio/cmd/acl-handlers.go

Purpose: implements S3 ACL compatibility handlers for buckets and objects while effectively supporting only private/full-control semantics. Key types are `grantee`, `grant`, and `accessControlPolicy`; handlers are `PutBucketACLHandler`, `GetBucketACLHandler`, `PutObjectACLHandler`, and `GetObjectACLHandler`.

Control flow creates request context, audits, extracts bucket/object, checks object layer readiness, authorizes with bucket policy actions, validates bucket/object existence, and parses ACL XML or `x-amz-acl`. PUT accepts empty/header private or XML whose first grant is `FULL_CONTROL`; other ACLs return NotImplemented. GET returns dummy XML with a canonical user full-control grant. State is not persisted beyond existence checks; ACLs are not stored. Dependencies include mux vars, policy auth, XML decoding, object API, and logger. Risks are compatibility surprises for clients expecting real ACL storage or multiple grants. Tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/acl-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-bucket-handlers.go -->
## sources/object-store/minio/cmd/admin-bucket-handlers.go

Purpose: admin APIs for bucket quota, remote replication targets, bucket metadata export/import, replication diff, and MRF backlog streaming. Important handlers include `PutBucketQuotaConfigHandler`, `GetBucketQuotaConfigHandler`, `SetRemoteTargetHandler`, `ListRemoteTargetsHandler`, `RemoveRemoteTargetHandler`, `ExportBucketMetadataHandler`, `ImportBucketMetadataHandler`, `ReplicationDiffHandler`, and `ReplicationMRFHandler`.

Control flow consistently validates admin auth and bucket existence, then mutates or reads global metadata systems. Quotas are parsed and stored as `quota.json` with site-replication hooks. Remote targets are decrypted from admin-client payloads, validated against self-targets/site-replication constraints, stored in `globalBucketTargetSys`, and persisted to `bucket-targets.json`. Export zips selected bucket metadata configs; import reads zip entries, creates buckets as needed, validates object-lock/versioning/lifecycle/SSE/tags/quota, saves metadata, and fires replication hooks. Streaming endpoints encode entries with keepalive flushes. State is persistent cluster/bucket metadata. Risks include partial import reports, encrypted payload handling, zip format assumptions, KMS validation, and replication policy constraints. Test signal is likely elsewhere; this subset has no direct tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-bucket-handlers.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handler-utils.go -->
## sources/object-store/minio/cmd/admin-handler-utils.go

Purpose: shared admin-handler helpers for authorization and error mapping. Important APIs are `validateAdminReq`, `AdminError`, `toAdminAPIErr`, `toAdminAPIErrCode`, `exportError`, `importError`, and `importErrorWithAPIErr`.

Control flow in `validateAdminReq` checks object-layer and notification readiness, then tries each requested admin action until one authorizes; access-denied tries the next action while other auth errors are returned immediately as JSON. `toAdminAPIErr` maps policy, config, IAM, KMS, decommission, tier, site-replication, and generic errors into MinIO API error structures and status codes. State is not persisted. Dependencies include auth, policy, config, madmin, KES, object layer globals, and API error tables. Risks include incomplete error classification, action-list authorization ambiguity, and exposing wrapped error details. Tests referenced by function inventory likely exist outside this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handler-utils.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-config-kv.go -->
## sources/object-store/minio/cmd/admin-handlers-config-kv.go

Purpose: admin APIs for encrypted server config get/set/delete, config history, help, full config import/export, and dynamic subsystem reload. Important surfaces include `DelConfigKVHandler`, `SetConfigKVHandler`, `setConfigKV`, `GetConfigKVHandler`, history handlers, `HelpConfigKVHandler`, `SetConfigHandler`, `GetConfigHandler`, `applyDynamic`, and `setLoggerWebhookSubnetProxy`.

Control flow validates config-update auth, rejects missing/oversized encrypted bodies, decrypts with the caller secret, parses subsystem/target KVs, validates config, saves config/history, and applies dynamic changes when allowed. Get/list APIs clone global config, redact or include secrets according to endpoint, encrypt responses, and write JSON. State is persistent server config and config history stored through the object layer; some subsystems are reloaded cluster-wide through notification signals. Dependencies include config packages, madmin encryption, logger/subnet proxy coupling, IAM config checks, and storageclass/plugin helpers. Risks include secret handling, dynamic reload partial failures, history restore semantics, env-overridden values, and proxy coupling side effects. Tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-config-kv.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-idp-config.go -->
## sources/object-store/minio/cmd/admin-handlers-idp-config.go

Purpose: admin APIs for adding, updating, listing, getting, and deleting identity provider configs for OpenID and LDAP. Important functions are `addOrUpdateIDPHandler`, `handleCreateUpdateValidation`, `AddIdentityProviderCfg`, `UpdateIdentityProviderCfg`, `ListIdentityProviderCfg`, `GetIdentityProviderCfg`, and `DeleteIdentityProviderCfg`.

Control flow validates config-update auth, content length, octet-stream body type, encrypted payload, valid IDP type, and create-vs-update rules. It converts requests into config subsystem KV strings, validates full config, saves config/history, and returns encrypted list/get responses. Delete checks provider existence and rejects deletion of env-overridden configs before removing KVS and applying dynamic reload if the subsystem supports it. State is persistent server config and config history; responses are encrypted with the requester secret. Dependencies include madmin IDP constants, OpenID/LDAP config managers, global IAM system, config parsing, and LDAP validation formatting. Risks include LDAP single-default constraints, env override detection, non-dynamic IDP sanity checks, and inconsistent not-found handling. No direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-idp-config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-idp-ldap.go -->
## sources/object-store/minio/cmd/admin-handlers-idp-ldap.go

Purpose: LDAP-specific admin APIs for policy mapping, policy attach/detach, LDAP service account creation, and access-key listing. Important handlers are `ListLDAPPolicyMappingEntities`, `AttachDetachPolicyLDAP`, `AddServiceAccountLDAP`, `ListAccessKeysLDAP`, and `ListAccessKeysLDAPBulk`.

Control flow validates admin auth, LDAP enabled state, encrypted octet-stream bodies where required, operation names, request schemas, and policy permissions. Policy mapping queries call IAM LDAP policy APIs and return encrypted JSON. Service account creation resolves requester/target LDAP identities, rejects derived-credential edge cases, populates LDAP claims/attributes, enforces target policies, creates IAM service accounts, encrypts credentials, and triggers site-replication hooks for non-root parents. Access-key listing supports self, explicit user, bulk, and all-users modes with deny-only self checks and list-type filtering. State is IAM policy DB, service account credentials, STS/service-account listings, and replication hooks. Risks include DN vs login-name handling, authorization subtleties for self vs admin listing, encrypted response secrecy, and LDAP availability. Tests are elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/admin-handlers-idp-ldap.go -->
