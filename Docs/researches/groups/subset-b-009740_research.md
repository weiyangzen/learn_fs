# subset-b-009740 research

Grouped source research for rclone backend files in `sources/user-network-fs/rclone/backend/...`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file documents.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cloudinary/cloudinary.go -->
# sources/user-network-fs/rclone/backend/cloudinary/cloudinary.go

## Purpose
This file implements the `cloudinary` rclone backend, exposing Cloudinary Digital Asset Management as an `fs.Fs` with object listing, lookup, upload, update, download, directory creation/removal, hashing, and eventual-consistency handling. It registers configuration for Cloudinary credentials, upload prefix/preset, path encoding, consistency delay, and Cloudinary media extension adjustment.

## Important APIs, types, and functions
`Options` stores Cloudinary credentials and behavior flags. `Fs` holds rclone identity, root, options, feature set, pacer, CDN REST client, Cloudinary SDK client, and `lastCRUD`. `Object` stores rclone-visible metadata plus Cloudinary `publicID`, resource type, delivery type, URL, MD5/etag, and timestamps. `NewFs` builds SDK clients with rclone HTTP clients, applies upload prefix, initializes the pacer and features, and detects whether the configured root points at a file. Encoding helpers bridge rclone names and Cloudinary's path/display conventions: `FromStandardPath`, `FromStandardName`, `ToStandardPath`, `ToStandardName`, `FromStandardFullPath`, `ToAssetFolderAPI`, and `ToDisplayNameElastic`.

Core filesystem methods are `List`, `NewObject`, `Put`, `Mkdir`, `Rmdir`, `Hashes`, `Precision`, and feature accessors. Object methods implement hash, metadata accessors, `Open`, `Update`, and `Remove`. `shouldRetry` centralizes retry handling for context cancellation, HTTP retry codes, general retryable errors, and Cloudinary rate-limit messages containing retry timestamps.

## Control flow
`List` first lists subfolders with `Admin.SubFolders`, then assets with `Admin.AssetsByAssetFolder`, converting Cloudinary folder/display names back to rclone paths and appending directories and objects. `NewObject` uses Cloudinary Admin Search against `asset_folder` and escaped `display_name`, sorts newest first, retries partial responses through the pacer, and materializes the first result. `Put` builds `uploader.UploadParams`; update mode is activated by backend-specific `api.UpdateOptions`, otherwise it derives asset folder and display name from the source remote and suggests a deterministic BLAKE3 public ID. `Open` performs a CDN GET through `rest.Client`, translates range/seek options into headers, and retries until returned content length matches the expected range count.

## State and persistence behavior
Persistent state lives in Cloudinary assets and folders. The backend maintains only local connection/client state plus `lastCRUD`, used by `WaitEventuallyConsistent` to sleep after CRUD operations when configured. Object identity is stored as Cloudinary `publicID` plus resource/delivery type, while rclone-visible paths are reconstructed from Cloudinary asset folders and display names. Empty files cannot be uploaded. Modtime precision is unsupported; update paths set local object modtime to `time.Now()` because Cloudinary returns creation time for overwritten assets.

## Dependencies and integration points
The file integrates rclone `fs`, config, HTTP, hashing, pacer, REST, encoder, and Cloudinary-specific API helpers. Cloudinary operations go through `github.com/cloudinary/cloudinary-go/v2` Admin and Upload SDKs; CDN downloads use rclone's `rest.Client`. Name handling depends on `backend/cloudinary/api.CloudinaryEncoder`. The backend declares empty-directory support and MD5 hashes.

## Risks and edge cases
Cloudinary media extension adjustment strips or reattaches extensions based on URL and configured media extensions, which can affect names with query strings or uncommon extensions. Search selects the first of up to two newest matching assets, so duplicate display names depend on Cloudinary ordering. `List` reuses `nextCursor` between the folder and asset phases without resetting it, which deserves scrutiny if folder listing returns a cursor before completion. `shouldRetry` slices retry-after text assuming the full timestamp length is present; malformed messages could panic. CDN range validation depends on `content-length` matching `count`, but `count` may be zero when no range option is supplied, causing normal whole-file downloads to rely on retry semantics.

## Test signals
Coverage is mainly integration-driven by `cloudinary_test.go`, which runs rclone `fstests` against a configured Cloudinary remote with a 7-second eventual-consistency delay and invalid UTF-8 skipped. There are no local unit tests for encoding helpers, retry parsing, or the folder/assets pagination flow.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cloudinary/cloudinary.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cloudinary/cloudinary_test.go -->
# sources/user-network-fs/rclone/backend/cloudinary/cloudinary_test.go

## Purpose
This file provides the Cloudinary backend integration test harness. It validates the backend through rclone's generic filesystem test suite rather than through direct unit tests of Cloudinary-specific helpers.

## Important APIs, types, and functions
`TestIntegration` calls `fstests.Run` with `RemoteName` set to `TestCloudinary:`, `NilObject` set to `(*cloudinary.Object)(nil)`, and `SkipInvalidUTF8` enabled. The test injects one extra config item: `eventually_consistent_delay=7`, matching Cloudinary's eventual-consistency characteristics.

## Control flow
When the test runs in an environment with a configured `TestCloudinary` remote, the shared rclone test suite creates, updates, lists, reads, removes, and checks objects/directories through the registered backend. All behavior is exercised through public `fs.Fs` and `fs.Object` interfaces, not direct package internals.

## State and persistence behavior
The test writes to a real Cloudinary remote and therefore depends on external credentials, network availability, Cloudinary account state, and cleanup behavior from `fstests`. The configured delay is intended to reduce false negatives caused by delayed Cloudinary search/list consistency.

## Dependencies and integration points
It depends on the `cloudinary` backend package for the nil object type and on `github.com/rclone/rclone/fstest/fstests` for the behavioral contract. The test is a signal that the backend is expected to satisfy broad rclone semantics despite Cloudinary-specific limitations such as unsupported modtime precision and empty-file uploads.

## Risks and edge cases
Because this is only an integration harness, CI without a configured Cloudinary remote may skip or fail depending on rclone test setup. It does not isolate Cloudinary API error handling, name encoding, media extension adjustment, public ID determinism, or retry-after parsing. Failures may be slow due to the 7-second consistency delay.

## Test signals
The presence of a generic `fstests.Run` means common rclone operations are covered at high level. Local deterministic unit coverage for backend helper functions is absent in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/cloudinary/cloudinary_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/combine/combine.go -->
# sources/user-network-fs/rclone/backend/combine/combine.go

## Purpose
This file implements the `combine` backend, which overlays multiple configured upstream remotes under top-level directory mountpoints. It presents them as one directory tree while delegating most operations to the appropriate upstream backend after translating paths.

## Important APIs, types, and functions
`Options` contains the space-separated `upstreams` config. `Fs` stores backend identity, root, common hash set, synthetic directory timestamp, feature set, and a map of mountpoint names to `upstream` values. `adjustment` maps paths between upstream-relative and combined-root-relative namespaces through `do` and `undo`. `upstream` wraps an `fs.Fs`, its mountpoint directory, and path adjustment. `NewFs` parses and validates upstream definitions, creates upstream filesystems concurrently through `cache.Get`, pins them until finalized, constructs a feature mask over all upstreams, and detects file roots.

Core APIs include `findUpstream`, `multithread`, `ListP`, `ListR`, `NewObject`, `Put`, `PutStream`, `Copy`, `Move`, `DirMove`, `Purge`, `About`, `ChangeNotify`, metadata and tier delegation, `PublicLink`, `MergeDirs`, and object wrappers.

## Control flow
Operations first resolve the combined path to an upstream with `findUpstream`. Root listing with empty root emits synthetic top-level directories for each upstream. Non-root listing delegates to upstream `ListP` or `List`, then wraps returned objects/directories so their `Remote()` values appear under the combined namespace. Recursive root listing lists synthetic upstream directories first, then recursively lists each upstream in parallel with a mutex-protected callback. Writes either update existing combined objects or delegate puts to the resolved upstream using `fs.NewOverrideRemote`.

Server-side operations are intentionally limited to same-combine objects. `Copy` and `Move` unwrap `*combine.Object`, locate destination upstreams, use destination `Copy`/`Move` if available, and wrap the returned object. `Move` falls back to copy plus source removal when move is unavailable but copy exists. Directory moves require both source and destination paths to resolve and delegate to destination upstream `DirMove`.

## State and persistence behavior
The combine backend stores no file data itself. Persistent data remains in upstream remotes. Local state includes upstream mappings, feature decisions, common hash intersection, and a synthetic `when` timestamp for top-level mounted directories. Root directories are virtual: `Mkdir` and `Rmdir` at empty root succeed without touching upstreams. `Purge` at empty root purges all upstream roots in parallel.

## Dependencies and integration points
The file is deeply integrated with rclone `fs`, `cache`, `operations`, `list`, `walk`, and `hash` packages. Feature masking controls the surface exposed by the wrapper, while selected optional features are re-enabled if any or all upstreams can support them. It marks `features.Overlay = true` and advertises metadata support inherited from upstreams.

## Risks and edge cases
Upstream mountpoint dirs cannot contain `/`, so this backend only supports one-level mount roots. Map iteration order means upstream resolution order is nondeterministic; overlapping path adjustments are mostly prevented by mountpoint restrictions, but root and file-root behavior still deserves care. `PutUnchecked` returns the underlying object without wrapping it, unlike `Put`, which may leak the upstream namespace to callers. Feature selection is conservative in most places, but `ListR` enables fallbacks based on ListR/local combinations and should be tested across mixed remotes. Cross-upstream `Move` may use destination copy on an object from another upstream; whether that succeeds depends on the destination backend's server-side copy constraints.

## Test signals
`combine_internal_test.go` unit-tests path adjustment. `combine_test.go` runs generic `fstests` against local, memory, mixed local/memory, or an externally configured remote. These tests provide broad filesystem behavior coverage but limited direct assertions for feature masking, change notifications, quota aggregation, and cross-upstream server-side operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/combine/combine.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/combine/combine_internal_test.go -->
# sources/user-network-fs/rclone/backend/combine/combine_internal_test.go

## Purpose
This file unit-tests `adjustment`, the path translation primitive that maps upstream-relative paths into combined paths and combined paths back into upstream-relative paths. Correctness here is central because most combine backend operations delegate based on these transformations.

## Important APIs, types, and functions
`TestAdjustmentDo` covers `newAdjustment(...).do`, which maps an upstream path into the combine view. `TestAdjustmentUndo` covers `newAdjustment(...).undo`, which maps a combine path into the upstream namespace. The tests use `assert.Equal` from `stretchr/testify`.

## Control flow
Each test iterates table-driven cases with `root`, `mountpoint`, `in`, expected `want`, and expected error. `do` cases validate empty root prefixing, root equal to mountpoint, nested roots that strip a shared prefix, and `errNotUnderRoot` for inputs outside the combined root. `undo` cases validate the reverse mapping from combine-visible paths back to upstream paths and error behavior when the effective absolute path does not fall under the mountpoint.

## State and persistence behavior
There is no persistent state. Each case creates a fresh `adjustment` value and checks pure string transformations.

## Dependencies and integration points
The tests are in package `combine`, not `combine_test`, so they can access unexported `newAdjustment` and `errNotUnderRoot`. They directly protect the internal routing logic used by `findUpstream`, listing wrappers, `Object.Remote`, and operations that delegate to upstream paths.

## Risks and edge cases
The tests cover representative root/mountpoint relationships but not empty mountpoint rejection, leading slashes, path cleaning behavior from `join`, root equal to input path returning empty string, or mountpoints with characters that might interact with `path.Join`. They also do not cover nondeterministic map iteration in `findUpstream`.

## Test signals
These are fast deterministic unit tests that isolate the highest-risk string mapping logic. They complement the broader `fstests` integration coverage in `combine_test.go`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/combine/combine_internal_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/combine/combine_test.go -->
# sources/user-network-fs/rclone/backend/combine/combine_test.go

## Purpose
This file provides generic filesystem test coverage for the combine backend using rclone's shared `fstests` framework. It exercises combine over configured external remotes, temporary local directories, in-memory remotes, and a mixed setup.

## Important APIs, types, and functions
`unimplementableFsMethods` records optional rclone features not expected from combine in these tests: `UnWrap`, `WrapFs`, `SetWrapper`, `UserInfo`, `Disconnect`, and `OpenChunkWriter`. `TestIntegration` uses a user-provided `fstest.RemoteName`. `TestLocal`, `TestMemory`, and `TestMixed` create combine configurations and call `fstests.Run`. `MakeTestDirs` creates temporary directories for local upstreams.

## Control flow
The external integration test is skipped unless `-remote` is configured. Local and memory tests are skipped when `-remote` is set. Each local-memory test builds an `upstreams` string such as `dir1=<path> dir2=<path> dir3=:memory:dir3`, registers a temporary config named `TestCombine...`, and tests a sub-root such as `TestCombineLocal:dir1`.

## State and persistence behavior
Local tests write to temp directories owned by the test process. Memory tests use rclone's memory backend. Mixed tests combine both. Cleanup is handled by Go temp directory cleanup and `fstests`. The combine backend itself persists nothing.

## Dependencies and integration points
The test imports local and memory backends for registration side effects, plus rclone `fstest` and `fstests`. It validates that combine can satisfy the shared rclone contract when backed by common upstreams.

## Risks and edge cases
The tests focus on a mounted subdirectory (`:dir1`) rather than exhaustive root-level multi-upstream behavior. They do not explicitly verify cross-upstream copy/move restrictions, quota aggregation, feature masking, change notification fan-out, purge across all upstreams, or metadata propagation. The external integration test depends on caller-supplied remote configuration.

## Test signals
The generic test suite provides broad operation coverage for object lifecycle, listings, hashes where available, and directory behavior. Combined with the internal adjustment tests, it gives useful confidence in common paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/combine/combine_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/compress.go -->
# sources/user-network-fs/rclone/backend/compress/compress.go

## Purpose
This file implements the `compress` wrapper backend, which stores each logical object on an underlying remote as a data object plus JSON metadata. It can compress data with gzip or zstd when heuristics show sufficient benefit, fall back to uncompressed storage, and expose original names, sizes, MIME type, and MD5 through rclone interfaces.

## Important APIs, types, and functions
`Options` configures wrapped remote, compression mode, level, and RAM cache limit. `Fs` wraps an underlying `fs.Fs`, selected mode id, mode handler, and feature set. `compressionModeHandler` defines the algorithm-specific operations used by this file. `ObjectMetadata` records `Mode`, original `Size`, original `MD5`, MIME type, and per-algorithm metadata. `Object` wraps the data object and metadata object; metadata may be lazy-loaded. `ObjectInfo` overrides remote and size for underlying writes.

Important helpers include `compressionModeFromName`, `makeMetadataName`, `makeDataName`, `processFileName`, `checkCompressAndType`, `verifyObjectHash`, `rcat`, `putCompress`, `putUncompress`, `putMetadata`, and `putWithCustomFunctions`.

## Control flow
`NewFs` parses the wrapped remote, checks whether the requested path is a metadata-backed file or a directory, selects a handler, masks features with the wrapped fs, and disables `PutStream` unless server-side move/copy is possible. Listing delegates to the wrapped remote and filters out metadata files; data file names are parsed into logical object names and sizes. `NewObject` reads `<remote>.json`, extracts metadata, computes the expected data object name, and wraps both objects.

`Put` checks for an existing logical object, samples up to `heuristicBytes` for MIME/compressibility, uploads either compressed or uncompressed data, then writes metadata. `PutStream` performs the same but uploads compressed streams under a temporary unknown-size name and moves them to the final size-encoded name once compression metadata is known. Updates preserve server-side versioning when possible, but may delete the old data object when the encoded data filename changes. `Open` lazy-loads metadata, passes uncompressed files straight through, and uses `chunkedreader` plus algorithm-specific random-access readers for compressed files.

## State and persistence behavior
For each logical file, the backend persists `<name>.json` metadata and either `<name>.<base64-original-size>.gz`, `<name>.<base64-original-size>.zst`, or `<name>.bin`. Metadata is authoritative for logical size, MD5, MIME type, mode, and compression seek metadata. Partial upload failure paths attempt to remove data or metadata to avoid orphaned objects, but data/metadata two-phase writes can still leave orphaned files if cleanup fails. Uncompressed files store logical size as the underlying object size rather than in the filename.

## Dependencies and integration points
The backend uses rclone wrapping, accounting, chunkedreader, list, object, operations, hash, and metadata interfaces. Compression-specific behavior is delegated to handler files. MIME detection uses `gabriel-vasile/mimetype`. Gzip metadata uses `buengese/sgzip`; zstd uses local helper code and `klauspost/compress/zstd`.

## Risks and edge cases
`compressionModeFromName` treats unknown modes as uncompressed, so the `unknownModeHandler` is not normally selected through config. `processEntries` ignores parse failures except for logging, so malformed stored data objects disappear from listings. `ListR` assumes the wrapped fs exposes `Features().ListR`; if not, it can panic unless feature masking prevents calls. `rcat` defers close/remove on `tempFile` before checking `os.CreateTemp` error; if temp creation fails, dereferencing `tempFile` in the defer would panic. Metadata upload failure cleanup returns removal errors ahead of metadata errors, which can hide the original cause. `SetMetadata` writes metadata to the data object, while `Metadata` reads from the metadata object, creating possible inconsistency.

## Test signals
`compress_test.go` runs generic `fstests` for configured remotes and local gzip/zstd wrappers. It marks several optional methods unimplementable, including `PutStream`, even though the backend conditionally supports it. There is no targeted unit coverage for filename parsing, metadata consistency, `rcat` spooling, update/delete sequencing, MIME detection, or malformed metadata handling.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/compress.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/compress_test.go -->
# sources/user-network-fs/rclone/backend/compress/compress_test.go

## Purpose
This file provides integration-style validation for the compress backend through rclone's shared filesystem test suite. It exercises the wrapper against configured remotes and against local temporary directories in gzip and zstd modes.

## Important APIs, types, and functions
`defaultOpt` defines the shared `fstests.Opt`, including `RemoteName`, nil object type, unimplementable fs methods, tiers to test, and object method expectations. `TestIntegration` runs against `TestCompress:`. `TestRemoteGzip` and `TestRemoteZstd` build temporary local-backed compress remotes with mode-specific level config and enable quick tests.

## Control flow
The integration test always calls `fstests.Run` with `defaultOpt`, expecting external configuration. The local gzip and zstd tests are skipped if `fstest.RemoteName` is set, then configure a compress remote over a temp path under `os.TempDir()` using extra config entries. Each test delegates actual behavior validation to `fstests`.

## State and persistence behavior
Local tests persist temporary data under fixed tempdir names such as `rclone-compress-test-gzip` and `rclone-compress-test-zstd`; cleanup depends on the shared test suite and filesystem state. The tests exercise creation of metadata/data object pairs indirectly.

## Dependencies and integration points
The file imports several backends for registration side effects (`drive`, `local`, `s3`, `swift`) and depends on rclone `fstest`/`fstests`. Tier tests imply the wrapper should propagate tier operations when the underlying remote supports them.

## Risks and edge cases
The fixed tempdir names under `os.TempDir()` can retain state across failed runs. The test marks `PutStream` unimplementable in `defaultOpt`, so conditional streaming behavior and compressed final-name renaming are not strongly covered. There are no focused tests for metadata file contents, zstd seek metadata, gzip partial reads, corrupt metadata, orphan cleanup, or MIME detection.

## Test signals
The generic suite provides broad object lifecycle coverage for both gzip and zstd local configurations. It is useful for API compatibility but not sufficient for the backend's two-object persistence invariants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/compress_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/gzip_handler.go -->
# sources/user-network-fs/rclone/backend/compress/gzip_handler.go

## Purpose
This file implements the gzip-specific `compressionModeHandler`. It decides compressibility, compresses upload streams into seekable gzip, constructs gzip metadata, and opens compressed objects for normal or offset reads.

## Important APIs, types, and functions
`gzipModeHandler` implements all handler methods. `isCompressible` compresses a sample with `sgzip.DefaultCompression` and compares original/compressed ratio to `minCompressionRatio`. `newObjectGetOriginalSize` reads `CompressionMetadataGzip.Size`. `openGetReadCloser` uses `sgzip.NewReaderAt` when offset is nonzero and `sgzip.NewReader` otherwise, then wraps with optional `io.LimitReader`. `putCompress` builds a compression goroutine around `io.Pipe`, records original MD5, optionally hashes compressed bytes using an underlying-supported hash, uploads via `f.rcat`, reads gzip metadata from the goroutine, validates the compressed hash, and returns data object plus metadata. `newMetadata` builds `ObjectMetadata`.

## Control flow
Upload flow unwraps accounting, tees plaintext into an MD5 hasher, compresses in a goroutine, wraps the pipe reader, optionally tees compressed bytes into a destination hash verifier, and streams/spools via `rcat`. Once upload completes, it waits for the compression result channel, removes partial output on compression errors, then records original MD5 and seek metadata.

## State and persistence behavior
Gzip metadata is stored in `ObjectMetadata.CompressionMetadataGzip` and includes original size plus seek data from `sgzip`. The persisted data object name includes original size and `.gz`. MD5 stored in metadata is over original uncompressed content, while optional transfer hash verification covers compressed bytes as stored on the underlying remote.

## Dependencies and integration points
The handler depends on `github.com/buengese/sgzip`, rclone accounting, chunkedreader, hash utilities, and the shared `compress.Fs` persistence helpers. It is selected by `compress.go` when mode is `gzip`.

## Risks and edge cases
The goroutine writes an error to an unbuffered channel after closing the pipe; if upload fails before the goroutine can send, ordering must avoid leaks. `newMetadata` panics on wrong metadata type, so all caller paths must preserve the handler contract. Compressibility is estimated on only the sampled bytes and at default compression, not necessarily the configured level. Offset reads rely on correct sgzip metadata and chunkedreader behavior.

## Test signals
Coverage is indirect through gzip-mode `fstests` in `compress_test.go`; no unit test directly validates gzip metadata, random-access reads, error cleanup, or ratio thresholds.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/gzip_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/szstd_helper.go -->
# sources/user-network-fs/rclone/backend/compress/szstd_helper.go

## Purpose
This file provides seekable zstd support for the compress backend. It defines metadata, writer, and reader abstractions over the seekable zstd format so compressed zstd objects can support ranged logical reads.

## Important APIs, types, and functions
`SzstdMetadata` stores block size, uncompressed size, and cumulative compressed block offsets. `SzstdWriter` wraps a `klauspost/compress/zstd.Encoder` and `a1ex3/zstd-seekable-format-go` concurrent writer. `NewWriterSzstd` initializes both. `Write` chunks input into `szstdChunkSize` blocks, updates uncompressed size, and records cumulative compressed offsets through a write callback. `Close` closes the seekable writer and encoder. `GetMetadata` returns the recorded metadata.

`SzstdReaderAt` wraps a seekable zstd reader, zstd decoder, metadata, current position, and mutex. `NewReaderAtSzstd` creates the reader and seeks to an initial logical offset. `Seek`, `Read`, `ReadAt`, and `Close` expose random-access reads and cleanup.

## Control flow
`Write` initializes `BlockData` lazily with a zero offset, then passes a frame source callback to `WriteMany`. The callback returns sequential chunks from the caller's `p` buffer and updates original size; the write callback appends cumulative compressed offsets. `ReadAt` translates an uncompressed byte range into block indexes, launches bounded parallel goroutines to read and decode compressed blocks, collects results by block index, copies requested subranges into the caller buffer, and returns the total bytes read.

## State and persistence behavior
`SzstdMetadata` is persisted inside the compress metadata JSON and is required for offset reads. `BlockData` is cumulative, where each pair of adjacent entries identifies one compressed block. Runtime state includes decoder/reader handles and current read position protected by a mutex.

## Dependencies and integration points
This helper is used by `zstd_handler.go`. It depends on `github.com/a1ex3/zstd-seekable-format-go/pkg`, `github.com/klauspost/compress/zstd`, Go `runtime` for concurrency bounds, and synchronization primitives.

## Risks and edge cases
`Write` only chunks within each `Write(p)` call; if the compressor receives many small writes, block boundaries and metadata depend on upstream copy behavior. `ReadAt` shares a single `zstd.Decoder` across parallel goroutines calling `DecodeAll`, which may not be concurrency-safe. It also returns `nil` error even if fewer bytes than requested are read near EOF, so callers must interpret byte counts carefully. Metadata corruption can cause invalid block offsets, large allocations, or decode failures. `Seek` and `Read` use the underlying seekable reader while `ReadAt` also uses it concurrently, so mixed access patterns should be treated cautiously.

## Test signals
There are no direct unit tests for this helper in the listed files. Zstd behavior is indirectly exercised by generic compress zstd integration tests, but parallel `ReadAt`, metadata corruption, and small-write block layout are not explicitly covered.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/szstd_helper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/uncompressed_handler.go -->
# sources/user-network-fs/rclone/backend/compress/uncompressed_handler.go

## Purpose
This file defines the handler used for the nominal uncompressed compression mode. It mainly disables compression-specific behavior and passes object opens through to the underlying object.

## Important APIs, types, and functions
`uncompressedModeHandler` implements `compressionModeHandler`. `isCompressible` always returns false. `newObjectGetOriginalSize` returns zero. `openGetReadCloser` delegates directly to `o.Object.Open`. `processFileNameGetFileExtension` returns an empty extension. `putCompress`, `putUncompressGetNewMetadata`, and `newMetadata` return unsupported-mode errors or nil.

## Control flow
The handler prevents compression by returning `compressible=false`. If an object metadata mode is uncompressed, `compress.go` already opens the wrapped object directly before invoking handler-specific compressed open logic. The unsupported methods are defensive stubs for paths that should not be used in normal uncompressed operation.

## State and persistence behavior
No algorithm metadata is produced by this handler. In the main compress backend, uncompressed persisted data is expected to use the `.bin` suffix plus a JSON metadata file produced by the active gzip or zstd handler's `putUncompressGetNewMetadata` when a file is not worth compressing. This handler itself does not produce metadata for that path.

## Dependencies and integration points
It depends only on shared rclone `fs` and `chunkedreader` types and the `compress` package's `Object` type. It is selected when `compressionModeFromName` returns `Uncompressed`, which currently includes any mode string other than `gzip` or `zstd`.

## Risks and edge cases
Because unknown config names map to `Uncompressed`, this handler may be selected for typoed modes and then fail on upload with `unsupported compression mode` rather than falling back to a full uncompressed wrapper. `newObjectGetOriginalSize` returning zero can make `NewObject` look for `<remote>.bin` based on size zero if metadata mode is uncompressed and this handler is active. The intended uncompressed fallback for incompressible files is actually implemented by gzip/zstd handlers, not this one.

## Test signals
No direct tests cover this handler. The generic compress tests configure only gzip and zstd modes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/uncompressed_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/unknown_handler.go -->
# sources/user-network-fs/rclone/backend/compress/unknown_handler.go

## Purpose
This file defines a defensive handler for unknown compression modes. It returns explicit errors for operations that require a known algorithm.

## Important APIs, types, and functions
`unknownModeHandler` implements the full `compressionModeHandler` interface. `isCompressible`, `openGetReadCloser`, `putCompress`, and `putUncompressGetNewMetadata` all return errors that include the unknown mode where possible. `newObjectGetOriginalSize` returns zero, `processFileNameGetFileExtension` returns empty, and `newMetadata` returns nil.

## Control flow
If selected, any attempt to check compressibility, open compressed data, upload compressed data, or produce metadata should fail quickly. The handler does not attempt compatibility behavior or migration.

## State and persistence behavior
It does not create or interpret persistent compression metadata beyond returning zero size from `newObjectGetOriginalSize`. No data should be written successfully through this handler.

## Dependencies and integration points
It depends on rclone `fs`, `chunkedreader`, and the package's `Object`/`Fs` types. However, `compress.go` currently maps all unknown mode strings to `Uncompressed`, and the switch's default branch is therefore not reachable through `compressionModeFromName` as written.

## Risks and edge cases
The apparent unreachable state means typoed config values do not get this clearer unknown-mode behavior. If future code passes a truly unknown integer mode, `newObjectGetOriginalSize` returning zero could cause misleading object-name lookups before errors occur elsewhere. The handler methods are mostly stubs and should not be treated as a migration path for unknown stored metadata modes.

## Test signals
There are no tests for this handler or for invalid compression mode config behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/unknown_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/zstd_handler.go -->
# sources/user-network-fs/rclone/backend/compress/zstd_handler.go

## Purpose
This file implements the zstd-specific `compressionModeHandler`. It mirrors gzip handler responsibilities using the package's seekable zstd helper for compression metadata and offset reads.

## Important APIs, types, and functions
`zstdModeHandler` implements all handler methods. `isCompressible` compresses a sample with `NewWriterSzstd` at default speed and compares original/compressed ratio. `newObjectGetOriginalSize` requires `CompressionMetadataZstd`. `openGetReadCloser` uses `NewReaderAtSzstd` for nonzero offsets and `zstd.NewReader` for full reads from offset zero. `putCompress` streams plaintext through a zstd writer goroutine, computes original MD5, optionally hashes compressed bytes for transfer verification, uploads with `f.rcat`, waits for `SzstdMetadata`, and builds `ObjectMetadata`.

## Control flow
Upload uses `io.Pipe` and a goroutine that creates `NewWriterSzstd` with configured encoder level, copies plaintext, closes the writer and pipe, then publishes metadata/errors on a channel. The main goroutine uploads the compressed pipe reader, receives the compression result, removes partial output on compression failure, and verifies underlying hash if available. Reads use metadata-backed seeking for ranged opens and plain streaming decoder for offset-zero reads.

## State and persistence behavior
Zstd metadata is stored in `ObjectMetadata.CompressionMetadataZstd`, including uncompressed size and block offsets. The stored data filename uses original size and `.zst`. Metadata MD5 is over the original plaintext. Optional hash verification validates the compressed object as stored by the underlying backend.

## Dependencies and integration points
This handler depends on `klauspost/compress/zstd`, the local seekable zstd helper, rclone accounting, chunkedreader, and hash utilities. It is selected from `compress.go` when mode is `zstd`.

## Risks and edge cases
Compression level is cast directly to `zstd.EncoderLevel`, so config validation must ensure values are meaningful. Partial upload cleanup is less detailed than the gzip handler in some error paths. Offset reads inherit concurrency and metadata risks from `szstd_helper.go`. Compressibility is sampled using default speed rather than the configured level. As with gzip, `newMetadata` panics if called with the wrong metadata type.

## Test signals
Zstd mode is covered by generic local `fstests` in `compress_test.go`, but there are no focused unit tests for seek metadata, range reads, zstd-level mapping, or corruption behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/compress/zstd_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/cipher.go -->
# sources/user-network-fs/rclone/backend/crypt/cipher.go

## Purpose
This file implements the core cryptographic primitives for rclone's `crypt` backend: filename encryption/obfuscation, stream encryption/decryption, nonce arithmetic, size translation, and ranged decrypt reads. It is security-critical because it defines on-disk/on-remote ciphertext formats and authentication behavior.

## Important APIs, types, and functions
`Cipher` holds data and name keys, EME tweak, AES block, name encryption mode, filename encoding, buffer pool, random source, directory-name behavior, bad-block passthrough flag, and encrypted suffix. `NameEncryptionMode` and `NewNameEncryptionMode` parse name modes. `NewNameEncoding` selects base32, base64, or base32768 filename encodings. `newCipher`, `Key`, `setEncryptedSuffix`, and `setPassBadBlocks` configure cipher state.

Name APIs include `encryptSegment`, `decryptSegment`, `obfuscateSegment`, `deobfuscateSegment`, `EncryptFileName`, `DecryptFileName`, `EncryptDirName`, and `DecryptDirName`. Data APIs include `EncryptData`, `DecryptData`, `DecryptDataSeek`, `EncryptedSize`, and `DecryptedSize`. Internal stream types `encrypter` and `decrypter` implement on-the-fly block processing. `calculateUnderlying` maps plaintext range requests to ciphertext byte ranges.

## Control flow
`Key` derives data key, name key, and name tweak with scrypt unless the password is empty, which deliberately yields zero keys for tests. Standard filename encryption pads each segment with PKCS#7, encrypts with AES-EME using a deterministic tweak, and encodes the ciphertext. Obfuscation performs reversible rune rotations keyed by the name key and quotes special cases. File and directory name methods optionally preserve version suffixes and may skip directory segments.

Data encryption emits a fixed magic header plus a random 24-byte nonce, then reads plaintext in 64 KiB chunks and seals each with NaCl `secretbox`, incrementing the nonce per block. Decryption validates magic, extracts nonce, opens each authenticated block, and returns plaintext. Ranged decryption either seeks an existing underlying `RangeSeeker` or reopens through an `OpenRangeSeek` callback, computes the correct nonce increment, decrypts the first needed block, discards intra-block offset, and enforces limits.

## State and persistence behavior
The encrypted file format is `RCLONE\x00\x00` magic, file nonce, then repeated secretbox blocks with 16-byte authentication overhead and up to 64 KiB data. Encrypted size and decrypted size are deterministic functions of block size and header overhead. Filenames in standard mode are deterministic for a given key and segment; name encryption off appends a configurable suffix, default `.bin`, unless set to `none`. Runtime buffers are recycled through `sync.Pool`.

## Dependencies and integration points
The file depends on Go crypto AES/rand/cipher packages, `x/crypto/nacl/secretbox`, `x/crypto/scrypt`, `rfjakob/eme`, local `pkcs7`, rclone accounting/range interfaces, readers helpers, version suffix helpers, and base32768. It exposes interfaces expected by higher-level crypt backend object operations.

## Risks and edge cases
This code is security-sensitive. Deterministic filename encryption leaks equality of names. Empty password intentionally creates zero keys for tests and must not be confused with secure configuration. `passBadBlocks` converts authentication failures into zero-filled plaintext, which is useful for recovery but dangerous for integrity. Ranged reads depend on exact `calculateUnderlying` math and nonce addition; off-by-one errors corrupt data or authentication. `deobfuscateSegment` leaves dangling quote state unchecked. `setEncryptedSuffix` silently prefixes a missing dot after logging, which may mask config mistakes. Buffer pool misuse after `finish` would be hazardous, though methods guard with `fh.err`.

## Test signals
`cipher_test.go` is extensive: it covers mode parsing, filename encodings, encryption/decryption vectors for base32/base64/base32768, obfuscation, suffix behavior, encrypted/decrypted size math, nonce arithmetic, stream encryption/decryption across buffer sizes and large data, truncated/corrupt input errors, ranged seek/limit behavior, close semantics, bad-block passthrough, and scrypt key vectors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/cipher.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/cipher_test.go -->
# sources/user-network-fs/rclone/backend/crypt/cipher_test.go

## Purpose
This file is the primary unit-test suite for `backend/crypt/cipher.go`. It validates public and internal cipher behavior with deterministic vectors, table-driven error checks, stream round trips, and range-seek coverage.

## Important APIs, types, and functions
Tests cover `NewNameEncryptionMode`, `NameEncryptionMode.String`, `NewNameEncoding`, segment encryption/decryption, file and directory name encryption/decryption, `EncryptedSize`, `DecryptedSize`, nonce helpers, `EncryptData`, `DecryptData`, `DecryptDataSeek`, `calculateUnderlying`, stream close behavior, `getBlock`/`putBlock`, and `Key`. Helpers include `EncodingTestCase`, `testEncodeFileName`, `testEncryptSegment`, `testStandardEncryptFileName`, `testStandardDecryptFileName`, `randomSource`, `zeroes`, and `closeDetector`.

## Control flow
The first half focuses on name behavior. It verifies base32/base64/base32768 encoding vectors, invalid decode errors, standard encrypted segment vectors, encrypted file/directory paths with and without directory-name encryption, version suffix preservation, off-mode suffix behavior, and obfuscation/deobfuscation. The middle tests size formulas and nonce arithmetic, including carry propagation and adding large offsets. The later tests exercise streaming encryption/decryption with deterministic nonces and large pseudo-random data, known ciphertext vectors, error propagation from readers, truncated headers/blocks, bad magic, block authentication failure, `passBadBlocks`, close semantics, and seek/limit behavior across many offsets and limits. `TestKey` locks in scrypt-derived keys for several password/salt combinations.

## State and persistence behavior
The tests use deterministic sources to avoid external state. `randomSource` produces predictable bytes and can also validate writes. `zeroes` forces nonce generation to known values. Hard-coded `file0`, `file1`, and `file16` represent encrypted file fixtures for empty, one-byte, and sixteen-byte plaintext inputs.

## Dependencies and integration points
The suite uses `stretchr/testify` assert/require helpers, local `pkcs7` error values, base encoders, and rclone reader helpers. It directly tests unexported internals because it is in package `crypt`, which is appropriate for this low-level component.

## Risks and edge cases
The tests are thorough but computationally heavy: several stream tests copy up to `1e8` bytes. They do not fuzz arbitrary Unicode obfuscation cases or all malformed ciphertext structures, but they cover many boundary conditions. The deterministic empty-password vectors are test conveniences, not secure usage patterns.

## Test signals
This file provides strong regression signals for ciphertext format compatibility, filename compatibility, ranged decryption correctness, error behavior, and key derivation stability. It is much more focused than the generic backend `fstests` harnesses in the other researched packages.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/backend/crypt/cipher_test.go -->
