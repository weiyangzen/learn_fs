# subset-b-008173 grouped research

This grouped report covers the MinIO mc client abstraction, local filesystem backend, S3 backend, URL parsing, tracing, tests, and legacy config compatibility files in `sources/object-store/minio-mc/cmd`. Each source file section is bounded by reconciliation markers for deterministic split into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs.go -->
# sources/object-store/minio-mc/cmd/client-fs.go

## Purpose

`client-fs.go` implements the local filesystem backend for the shared `Client` interface. It lets mc commands treat POSIX/Windows paths like object-storage URLs for copy, list, stat, remove, bucket-like directory creation, watch, and metadata-preservation flows. The file deliberately returns `APINotImplemented` for S3-only features such as select, bucket policies beyond chmod-style access, object lock, tags, lifecycle, versioning, replication, encryption, restore, multipart object-download parts, and CORS.

## Important APIs, Types, And Control Flow

The central type is `fsClient`, which stores a normalized `ClientURL`. `fsNew` validates and absolutizes paths, preserving a trailing separator because listing uses it to distinguish "list this directory" from "treat this path as a prefix". `Put` delegates to `put`; `PutPart` uses `putN` when a nonnegative byte count is supplied. Both write through a UUID-named temp file in the target directory, copy data with `hookreader.NewHook` for progress, close the descriptor before rename for Windows compatibility, validate expected size, and atomically commit with `os.Rename`. Attribute preservation parses mc metadata, applies chmod/chown while writing, then restores atime/mtime after rename.

`Get`, `Stat`, and `List` translate file metadata into `ClientContent`. `List` chooses recursive walking, directory-first/last recursion, or nonrecursive prefix behavior, then filters `.part.minio` incomplete artifacts. `Remove` consumes `ClientContent` values and deletes files, incomplete parts, and empty parent directories within the original base path. `Watch` maps mc event names onto platform notify events and emits S3-style `EventInfo`.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is the host filesystem: created directories, renamed temp files, chmod/chown timestamps, xattrs, and `.part.minio` suffixes. Dependencies include `os`, `filepath`, `syscall`, `rjeczalik/notify`, `pkg/xattr`, `disk.GetFileSystemAttrs`, and shared mc errors. Important risks are path-length differences, recursive deletion escaping the base path, symlink stat behavior, platform event differences, unsupported xattr handling, and chmod/chown failures during preserve mode. `client-fs_test.go` covers put/get/stat/copy/list/mkdir/access basics, range-style reading, recursive listing, and OS-specific ignore behavior.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_darwin.go -->
# sources/object-store/minio-mc/cmd/client-fs_darwin.go

## Purpose

This Darwin-specific companion supplies macOS filesystem event classification and xattr readers used by `client-fs.go`. It is selected by the `darwin` build tag and keeps platform-specific notify/xattr behavior out of the portable filesystem client.

## Important APIs, Control Flow, And State

The file defines `EventTypePut` as create/write/rename, `EventTypeDelete` as remove, and `EventTypeGet` as empty because access/read notifications are not available for this backend. `IsPutEvent` tests bit overlap against the put event list, `IsDeleteEvent` checks `notify.Remove`, and `IsGetEvent` always returns false. `getXAttr` wraps `xattr.Get`, while `getAllXattrs` lists all extended attribute keys, reads each value, and treats filesystem-not-supported errors from `isNotSupported` as a nil metadata result rather than a hard failure.

## Dependencies, Integration, Risks, And Tests

Dependencies are `github.com/rjeczalik/notify` and `github.com/pkg/xattr`. The functions are consumed by preserve-mode `Get`/`Stat` and by `Watch` in `client-fs.go`. The main risk is silent loss of get events on macOS, which is explicit, and xattr read failures after a successful list. Tests are mostly indirect through filesystem preserve/list/watch behavior; `client-fs_test.go` has OS-specific assertions for `.DS_Store` filtering on Darwin.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_darwin.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_freebsd.go -->
# sources/object-store/minio-mc/cmd/client-fs_freebsd.go

## Purpose

This FreeBSD platform file provides notify event constants and extended-attribute enumeration for the filesystem client. It mirrors the non-Linux Unix behavior where get/access notifications are unavailable.

## Important APIs, Control Flow, And State

`EventTypePut` includes create, write, and rename; `EventTypeDelete` includes remove; `EventTypeGet` is empty. `IsPutEvent` scans the configured put events for bit overlap, `IsDeleteEvent` checks remove, and `IsGetEvent` returns false. `getXAttr` converts an xattr byte value to string, and `getAllXattrs` lists all keys and fetches values while treating unsupported xattrs as nonfatal.

## Dependencies, Integration, Risks, And Tests

The file depends on `notify` and `xattr`, and integrates with `fsClient.Watch`, `fsClient.Get`, and `fsClient.Stat`. Persistent state is only whatever xattrs already exist on disk; this file does not mutate them. Risks are the absence of read-event support and brittle behavior if an xattr disappears between `List` and `Get`. Coverage is indirect through shared filesystem tests and any platform-specific build/test lane.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_freebsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_linux.go -->
# sources/object-store/minio-mc/cmd/client-fs_linux.go

## Purpose

`client-fs_linux.go` provides Linux-specific filesystem watch event mapping and xattr extraction for mc's filesystem backend. Linux is the richest platform here because inotify can report access/open events and xattrs can contain non-UTF-8 data.

## Important APIs, Control Flow, And State

`EventTypePut` maps to `InCloseWrite | InMovedTo`, delete maps to `InDelete | InDeleteSelf | InMovedFrom`, and get maps to `InAccess | InOpen`. `IsGetEvent`, `IsPutEvent`, and `IsDeleteEvent` scan the respective event slices for bit overlap. `getXAttr` reads a key and returns a UTF-8 string when valid, otherwise hex-encodes the raw value. `getAllXattrs` lists keys, skips `system.*` attributes, and returns nil rather than an error when xattrs are unsupported.

## Dependencies, Integration, Risks, And Tests

The file integrates with `fsClient.Watch` and preserve-mode metadata in `Get`/`Stat`. Dependencies are `notify`, `xattr`, `encoding/hex`, and UTF-8 validation. Key risks are event coalescing semantics from inotify, read/open events producing noisy watch output, and lossy user expectations for binary xattrs because non-UTF-8 values are exposed as hex strings. Tests are indirect through filesystem listing/get/stat tests and any Linux watch or preserve-mode coverage.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_linux.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_netbsd.go -->
# sources/object-store/minio-mc/cmd/client-fs_netbsd.go

## Purpose

This NetBSD companion supplies the filesystem backend's platform-specific event classification and xattr readers. Its behavior matches the BSD-style pattern used by the Darwin and FreeBSD files.

## Important APIs, Control Flow, And State

Put events are create/write/rename, delete events are remove, and get events are unsupported. `IsGetEvent` returns false, `IsPutEvent` tests the configured event set, and `IsDeleteEvent` checks `notify.Remove`. `getXAttr` and `getAllXattrs` fetch all xattrs into a string map, treating unsupported xattrs as a nil metadata result.

## Dependencies, Integration, Risks, And Tests

Dependencies are `notify` and `xattr`; consumers are the shared filesystem client's watch and preserve paths. The file does not persist state itself. Risks are missing access events and xattr races between list and read. Test signals come from successful NetBSD compilation plus shared filesystem behavior tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_netbsd.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_other.go -->
# sources/object-store/minio-mc/cmd/client-fs_other.go

## Purpose

This build-tagged file covers Solaris and OpenBSD filesystem behavior where mc supports basic notify event classification but does not expose xattr preservation.

## Important APIs, Control Flow, And State

The file defines put events as create/write/rename, delete as remove, and no get events. `IsGetEvent` returns false, `IsPutEvent` scans for bit overlap, and `IsDeleteEvent` checks remove. `getAllXattrs` returns nil metadata and nil error, making preserve-mode callers degrade gracefully on these platforms.

## Dependencies, Integration, Risks, And Tests

Only `notify` is imported. The implementation is consumed by `fsClient.Watch`, `Get`, and `Stat`. There is no persistence in this file. Risks are expected feature gaps: no get notifications and no xattr reporting, which can surprise users relying on preserve mode across platforms. Coverage is mostly by successful platform builds and shared filesystem tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_other.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_test.go -->
# sources/object-store/minio-mc/cmd/client-fs_test.go

## Purpose

This test file validates the local filesystem `Client` implementation against common mc client operations. It focuses on basic file and directory semantics rather than every S3-compatible method stub.

## Important Tests And Control Flow

`TestList` creates temporary files through `fsClient.Put`, verifies nonrecursive and recursive listings, counts regular files/directories, and checks `.DS_Store` filtering differences on Darwin versus other platforms. `TestPutBucket` and `TestStatBucket` exercise `MakeBucket` and `Stat` for directory paths. `TestBucketACLFails` confirms chmod-style access works for directories on non-Windows platforms. `TestPut`, `TestGet`, `TestGetRange`, and `TestStatObject` cover file write, readback, reader-at access, and size metadata. `TestCopy` creates a source file and copies it to a target filesystem client.

## Dependencies, Risks, And Signals

The tests use temporary directories, `gopkg.in/check.v1`, `bytes`, `io`, `filepath`, and runtime OS checks. They signal that basic temp-file commit, list ordering/filtering, stat metadata, and local copy are expected to work. Gaps remain around remove recursion, watch events, preserve/xattr behavior, partial put through `PutPart`, path-length errors, symlink loops, and unsupported S3 API methods.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_windows.go -->
# sources/object-store/minio-mc/cmd/client-fs_windows.go

## Purpose

This Windows-specific file adapts filesystem watch events and metadata behavior to Windows. It enables the shared filesystem client to compile and classify common create/delete/read notifications while disabling xattr preservation.

## Important APIs, Control Flow, And State

`EventTypePut` includes create/write/rename and Windows file-name/directory-name change events. `EventTypeDelete` includes remove, while get uses `FileNotifyChangeLastAccess`. `IsPutEvent` specially excludes `FileActionRenamedOldName` so rename-away is not mistaken for a put. `IsDeleteEvent` treats both remove and renamed-old-name as deletion. `getAllXattrs` returns nil metadata because Windows xattr support is not implemented here.

## Dependencies, Integration, Risks, And Tests

The only dependency is `notify`. The file feeds `fsClient.Watch` and preserve-mode metadata calls. Risks include Windows rename event ambiguity, last-access notifications depending on filesystem settings, lack of chmod policy support in `client-fs.go`, and no xattr preservation. `client-fs_test.go` explicitly skips chmod access validation on Windows and the main filesystem tests indirectly validate build compatibility.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-fs_windows.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3-trace_v2.go -->
# sources/object-store/minio-mc/cmd/client-s3-trace_v2.go

## Purpose

`client-s3-trace_v2.go` implements debug HTTP tracing for S3 signature v2 clients. It lets mc dump request and response headers without exposing v2 access keys or signatures.

## Important APIs, Control Flow, And State

`traceV2` satisfies the `httptracer.HTTPTracer` interface. `newTraceV2` constructs it. `Request` saves the original `Authorization` header, replaces it with a redacted v2 form, dumps outbound headers with `httputil.DumpRequestOut`, writes the trace through `console.Debug`, and restores the original header before the request proceeds. `Response` dumps response headers for success and includes the body for non-OK/non-partial/non-no-content statuses; it also prints TLS certificate information when present.

## Dependencies, Integration, Risks, And Tests

The tracer is installed by `Config.initTransport` when debug is enabled and the configured signature is S3v2. Dependencies are `net/http`, `httputil`, `strings`, `httptracer`, and console debug output. Risks are accidental body logging for error responses and incomplete redaction if future v2 authorization formats change. Test coverage is indirect through debug transport construction and STS/S3 client tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3-trace_v2.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3-trace_v4.go -->
# sources/object-store/minio-mc/cmd/client-s3-trace_v4.go

## Purpose

`client-s3-trace_v4.go` implements debug tracing for S3 signature v4 clients. It redacts authorization credentials and SSE-C key headers before dumping HTTP traffic.

## Important APIs, Control Flow, And State

`traceV4` satisfies `httptracer.HTTPTracer`; `newTraceV4` returns a value instance. `Request` captures the original authorization and SSE-C customer key headers, redacts the SSE-C key, uses regex replacement to hide the access key inside `Credential=.../` and the hex `Signature=...`, dumps headers, then restores the original authorization. `Response` mirrors v2 tracing: successful responses dump headers only, error-like responses dump body too, and TLS certificate details are printed when available.

## Dependencies, Integration, Risks, And Tests

`Config.initTransport` installs this tracer for debug S3v4 clients. Dependencies include `httputil`, `regexp`, `strings`, `httptracer`, and console debug. Risks are regex drift as authorization formats evolve, error-body leakage in debug logs, and the SSE-C header being restored only indirectly by the request object lifecycle rather than explicitly. Test signals are indirect through debug-enabled S3/admin tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3-trace_v4.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3.go -->
# sources/object-store/minio-mc/cmd/client-s3.go

## Purpose

`client-s3.go` is the S3/object-storage implementation of mc's shared `Client` interface. It wraps `minio-go` to support bucket/object I/O, listing, incomplete uploads, versioned listing, notifications, select, presigned sharing, access policy, object lock, tags, lifecycle, versioning, replication, encryption, bucket info, restore, object parts, and CORS.

## Important APIs, Types, And Control Flow

`S3Client` stores a target `ClientURL`, cached `minio.Client`, virtual-host style flag, and a mutex around list/stat operations. `newFactory` creates `S3New`, a closure that hashes endpoint and credentials to cache `minio.Client` instances, builds transports from `Config`, installs chain credentials, handles virtual-host/accelerated endpoints, and sets app info. Custom dialers enforce connection deadlines and optional resolver overrides.

I/O methods translate mc options into SDK options. `Get` uses `minio.Core.GetObject`, handles ranges, versions, zip extraction, SSE, and typed error mapping. `Put` separates headers from user metadata, parses tags and object-lock headers, configures multipart/checksum/SSE/storage-class options, and maps SDK errors to mc errors. `Copy` selects single-copy or compose based on size/multipart settings. `Remove` streams batched deletes per bucket, handles incomplete uploads, forced delete, bucket removal, governance bypass, and async SDK error draining.

Listing paths include bucket listing, regular object listing, zip extraction listing, incomplete upload listing, versioned listing with fallback when unsupported, prefix-as-directory detection, and conversion from `minio.ObjectInfo` to `ClientContent`. Control helpers split bucket/object paths, detect AWS/GCS virtual-host support, and build URL paths.

## State, Dependencies, Integration, Risks, And Tests

Persistent state is remote S3-compatible service state: objects, buckets, bucket configs, policies, object-lock metadata, tags, lifecycle, versioning, replication, encryption, notifications, and incomplete uploads. Dependencies are broad: `minio-go`, notification/policy/tags/SSE/replication/lifecycle packages, mc transports, env config, deadline connections, custom global roots/resolvers, and shared errors. Risks include cached client reuse across mutable configs, virtual-host bucket parsing, provider-specific listing differences, versioning fallback, delete-channel deadlocks, object-lock header parsing, metadata filtering, and feature availability differences. Tests cover bucket/object operations through httptest, select compression inference, and STS credential-chain operation; many advanced bucket configuration APIs depend on integration testing.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3_test.go -->
# sources/object-store/minio-mc/cmd/client-s3_test.go

## Purpose

This test file provides lightweight HTTP-server coverage for the S3 client wrapper and select compression inference. It avoids a real S3 service by implementing minimal handlers for expected SDK calls.

## Important Tests And Control Flow

`bucketHandler` responds to list-buckets, list-objects, bucket location, PUT bucket, and HEAD requests. `objectHandler` validates authorization, accepts PUT bodies, returns object metadata for HEAD, supports basic multipart initiation/completion responses, lists incomplete uploads, and serves object bytes. `TestBucketOperations` builds `S3New` clients for bucket and root URLs, exercises `MakeBucket`, and checks list behavior for root, bucket without slash, and bucket with slash. `TestObjectOperations` uploads and downloads a small object. `TestSelectCompressionType` validates explicit compression override and extension/mime-based defaults for gzip, bzip2, parquet, csv, and json names.

## Dependencies, Risks, And Signals

Tests use `httptest`, `minio-go`, `gopkg.in/check.v1`, and shared test suite state. They confirm signing is present, URL path semantics influence list type, basic put/get work, and compression selection is stable. Gaps include delete, policy, versioning, notification, object lock, lifecycle, replication, encryption, CORS, virtual-host parsing, and error mapping.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-s3_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-sts_test.go -->
# sources/object-store/minio-mc/cmd/client-sts_test.go

## Purpose

`client-sts_test.go` validates that mc can obtain web-identity STS credentials from environment-driven configuration and use them for both S3 object operations and admin operations.

## Important APIs, Control Flow, And State

`TestSTSS3Operation` writes a JWT to a temp file, exposes a fake STS endpoint with `stsHandler`, sets `MC_STS_ENDPOINT_test` and `MC_WEB_IDENTITY_TOKEN_FILE_test`, creates an S3 client with alias `test`, and verifies a PUT succeeds against the object httptest server. `TestAdminSTSOperation` performs the same STS setup, creates an admin client with debug/insecure enabled, and calls `AddCannedPolicy` against a fake admin handler. These tests exercise `Config.getCredsChain`, which sets AWS web identity environment variables and prepends IAM/STS credentials ahead of static credentials.

## Dependencies, Risks, And Signals

Dependencies include `httptest`, temp files, environment mutation through `t.Setenv`, and handlers from nearby S3/admin tests. The tests signal that alias-scoped STS env vars are wired into minio-go credential resolution. Risks are process-wide AWS env mutation in `getCredsChain`, endpoint parsing failures, and interactions between debug transport and STS transport reuse.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-sts_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-url.go -->
# sources/object-store/minio-mc/cmd/client-url.go

## Purpose

`client-url.go` defines mc's internal URL representation and helpers for parsing aliased paths, object-storage URLs, filesystem paths, content-type guessing, stat lookup, and prefix checks. It is the glue between user-facing path syntax and the `Client` abstraction.

## Important APIs, Types, And Control Flow

`ClientURL` records type, scheme, host, path, scheme separator, and path separator. `newClientURL` parses `http://` and `https://` authorities as object storage, otherwise treats input as filesystem. `String` converts object-storage URLs to canonical slash-separated form, with Windows-specific path cleanup, and returns filesystem paths unchanged. `joinURLs` and `urlJoinPath` append paths after normalizing to slash separators.

`url2Stat` builds a client with `newClient`, derives alias-specific SSE keys, and calls `Stat`. `firstURL2Stat` lists recursively and returns the first match. `url2Alias` separates the alias from the path with Windows adjustments. `guessURLContentType` uses `mimedb` extension lookup. `urlParts` and `isURLPrefix` split paths and test whether source/destination should be considered nested, accounting for trailing separators and wildcard path parts.

## State, Dependencies, Integration, Risks, And Tests

This file has no durable state. It depends on `filepath`, `runtime`, `regexp`, `mimedb`, and client factory helpers from other files. Integration points include copy/mirror safety checks, stat calls, content-type defaults, and alias expansion. Risks are scheme parsing that accepts only alphabetic schemes despite the comment, Windows separator edge cases, mutation of `url1` in `joinURLs`, and prefix logic around wildcards. `client-url_test.go` covers URL parsing, URL joining, and symmetric prefix detection.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-url.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-url_test.go -->
# sources/object-store/minio-mc/cmd/client-url_test.go

## Purpose

This test file validates the URL parser/joiner and nested-prefix detector used by mc copy and client-selection paths.

## Important Tests And Control Flow

`TestURL` confirms a local-looking string containing `?` remains a filesystem path and that an HTTPS S3 URL is parsed into scheme, host, and object path without query handling side effects. `TestURLJoinPath` verifies joining object-storage URLs to another URL or plain path, including preserving a trailing slash in the second path. `Test_isURLPrefix` exercises symmetric prefix checks for direct nesting, trailing separators, deeper descendants, wildcard path segments, and false positives such as `test` versus `test.123`.

## Dependencies, Risks, And Signals

Tests use both `gopkg.in/check.v1` and standard `testing`. They signal expected compatibility for copy destination safety checks and URL assembly. Gaps include Windows path behavior, alias expansion, filesystem absolute paths, non-HTTP schemes, and malformed authority strings.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client-url_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client.go -->
# sources/object-store/minio-mc/cmd/client.go

## Purpose

`client.go` defines the shared client contract and common option/content/config types that let mc commands operate uniformly against S3-compatible services and local filesystems.

## Important APIs, Types, And Control Flow

`DirOpt` controls whether directory entries appear before objects, after objects, or not at all. `GetOptions`, `PutOptions`, `StatOptions`, `BucketStatOptions`, `ListOptions`, and `CopyOptions` carry operation-specific flags such as SSE, version IDs, zip extraction, multipart settings, checksums, retention metadata, preserve mode, and listing modes. `Client` is the large interface implemented by `fsClient` and `S3Client`, covering common stat/list, bucket operations, object I/O, object locking, sharing, watch, remove, tags, lifecycle, versioning, replication, encryption, bucket info, restore, object-part, and CORS operations.

`ClientContent` is the normalized metadata carrier for list/stat/get flows, with URL, bucket, size, mode, storage class, HTTP metadata, user metadata, tags, checksum, ETag, retention/legal hold, versioning, replication, restore, and embedded error. `Config` contains S3 alias credentials, endpoint, debug, TLS, lookup, deadlines, limits, and transport. `getCredsChain` builds static and optional STS web-identity credentials. `initTransport` creates deadline-aware transports, TLS config, custom headers, bandwidth limiter, debug tracers or certificate-expiry notifier, and gzip support.

## State, Dependencies, Integration, Risks, And Tests

State includes cached `Config.Transport`, process environment mutation for STS variables, and global certificate-expiry records. Dependencies include minio-go, credentials, encryption/lifecycle/replication/CORS packages, `gzhttp`, limiter, httptracer, env helpers, and global TLS/header settings. Risks are a very broad interface forcing many filesystem stubs, process-wide STS environment changes, transport reuse with mutable configs, and debug tracer leakage. Tests in S3/STS files cover credential-chain and transport paths indirectly.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/client.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/common-methods.go -->
# sources/object-store/minio-mc/cmd/common-methods.go

## Purpose

`common-methods.go` contains cross-command helpers for deciding whether a URL is directory-like, opening source streams, writing/copying targets, preserving metadata, choosing S3 server-side copy versus streaming upload, and constructing clients from aliases.

## Important APIs, Control Flow, And State

`isAliasURLDir` stats a target when possible, then falls back to alias expansion and trailing-separator heuristics. `getSourceStreamMetadataFromURL`, `getSourceStreamFromURL`, and `getSourceStream` expand aliases, apply SSE keys, and call `Client.Get`. `putTargetRetention`, `putTargetStream`, `putTargetStreamWithURL`, and `copySourceToTargetURL` wrap target client operations with retention/legal-hold metadata. `filterMetadata` drops invalid HTTP headers and server-encryption headers. `getAllMetadata` merges source metadata with target user metadata during preserve flows.

`uploadSourceToTargetURL` is the central copy/upload decision tree. It computes source/target aliases and SSE keys, applies retention/legal hold overrides, merges metadata, uses server-side copy when source and target aliases match, zip/checksum constraints allow it, and otherwise streams from source to target. It also parses multipart size/thread settings from options or env, updates progress totals for streaming readers, copies tags, and chooses `io.LimitReader` when the source is not seekable. `newClientFromAlias` selects filesystem or S3 client based on alias config; `newClient` rejects raw HTTP URLs without an alias.

## Dependencies, Integration, Risks, And Tests

Persistent state is remote/local data changed through the selected client plus environment-controlled multipart settings. Dependencies include alias expansion, SSE lookup, URL structs, `minio-go` tags/retention types, `httpguts`, humanize parsing, progress bars, and shared errors. Risks are metadata mutation through maps, retention handling short-circuiting uploads, server-side copy eligibility tied only to alias equality, nonseekable stream length handling, and process env parsing. Coverage is indirect through copy, S3, filesystem, and STS tests.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/common-methods.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-fix.go -->
# sources/object-store/minio-mc/cmd/config-fix.go

## Purpose

`config-fix.go` performs targeted repairs for historically broken mc config files before normal migration runs. These fixes handle malformed v3 host JSON, bad v6 glob host entries, v6 hosts missing schemes, and duplicate Windows config locations.

## Important APIs, Control Flow, And State

`fixConfig` orchestrates `fixConfigLocation`, `fixConfigV3`, `fixConfigV6`, and `fixConfigV6ForHosts`. `ConfigAnyVersion` loads only the config version. `fixConfigV3` detects version `3`, loads a `brokenConfigV3`, rewrites hosts through proper `hostConfigV3` JSON tags, drops unused ACL/access fields, and saves only when mutation is detected. `fixConfigV6` rewrites known glob-style host keys to concrete S3/GCS/local defaults and fatals on unsupported glob patterns. `fixConfigV6ForHosts` adds `https://` to known host keys that lack schemes. `fixConfigLocation` handles Windows `.exe` config directory duplication by renaming legacy/current directories depending on invocation path.

## State, Dependencies, Integration, Risks, And Tests

This file mutates `config.json` and config directories via quick config load/save, `os.Stat`, `os.Rename`, and `os.RemoveAll`. It integrates with startup config repair before migration. Risks are fatal exits on load/save issues, key collisions when rewriting hosts, dropping malformed entries not matching known patterns, and Windows rename failure requiring manual intervention. Test coverage is not in this subset; validation likely relies on config migration/fix integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-fix.go -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-migrate.go -->
# sources/object-store/minio-mc/cmd/config-migrate.go

## Purpose

`config-migrate.go` upgrades mc config files from older schema versions to the current v10 alias format. It preserves user credentials/aliases where possible while applying historical defaults and schema renames.

## Important APIs, Control Flow, And State

`migrateConfig` runs each migration step in order, with every step first loading `ConfigAnyVersion` and returning unless the current version exactly matches its source version. V1 to V1.0.1 adds example localhost, loopback, and AWS entries. V1.0.1 to V2 switches to integer versioning. V2 to V3 changes host config JSON tags. V3 to V4 adds API signature defaults. V4 to V5 renames `Signature` to `API`. V5 to V6 adds GCS defaults and normalizes AWS glob patterns. V6 to V7 drops the separate alias map and converts host entries into named hosts, preserving old alias names when possible and assigning `cloudN` otherwise. V7 to V8 removes deprecated play/dl aliases. V8 to V9 adds virtual lookup defaulting to auto. V9 to V10 renames `hosts` to `aliases` and maps lookup `dns/path/auto` to path `off/on/auto`.

## State, Dependencies, Integration, Risks, And Tests

The file persists changes to `mustGetMcConfigPath()` using `quick.NewConfig(...).Save`, logs successful migrations, and fatals on load/save failures. Dependencies include all historical config structs and host conversion types. Risks are ordered migration coupling, alias collisions during V6 to V7, default entries overriding user expectations, and inability to continue after partially written configs. Tests are not in this subset; high-value signals would be fixture migrations for every version and idempotency checks when current version is not in scope.
<!-- END_FILE_RESEARCH: sources/object-store/minio-mc/cmd/config-migrate.go -->
