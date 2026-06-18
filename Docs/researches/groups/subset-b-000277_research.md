# Research: subset-b-000277

Work item `subset-b-000277` covers eStargz compression helpers, external TOC and zstd-chunked variants, filesystem/layer mount behavior, FUSE node behavior, and related metrics/tests in `sources/cloud-native/stargz-snapshotter`.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/estargz_test.go -->
## sources/cloud-native/stargz-snapshotter/estargz/estargz_test.go

Purpose: this focused unit test validates `Reader.ChunkEntryForOffset` offset-to-chunk selection for regular files represented by a first `reg` TOC entry and optional later `chunk` entries. It is a narrow guard around the reader's chunk lookup math.

Important APIs and helpers: `TestChunkEntryForOffset` drives table cases over `fileSize`, requested offset, expected hit/miss, expected `ChunkOffset`, and expected `ChunkSize`. `regularFileReader` builds a minimal in-memory `Reader` with `m` and `chunks` maps rather than constructing a tar/eStargz blob. The helper emits a single regular entry when the file fits in one chunk and additional `chunk` entries when it spans chunks.

Control flow: each case builds a fake reader, calls `ChunkEntryForOffset(name, reqOffset)`, checks the boolean result, and compares chunk metadata only for hits. Boundary cases cover offsets at chunk starts and exactly at EOF for one- and two-chunk files.

State and persistence: no persistent state is used. The test constructs transient `TOCEntry` pointers and reader maps; pointer reuse intentionally models the first `reg` entry becoming the first chunk.

Dependencies and integration points: this test depends on package-internal `Reader`, `TOCEntry`, and `ChunkEntryForOffset` behavior from `estargz.go`. It complements the larger compression suite in `testutil.go`, which validates chunk lookup against real archives.

Risks: coverage is limited to simple same-sized chunk boundaries and does not cover negative offsets, non-zero `InnerOffset`, sparse/multi-payload chunks, missing `chunks` map entries, or offsets inside last partial chunks. It also assumes `ChunkEntryForOffset` interprets EOF as no hit.

Test signals: strong regression signal for basic offset arithmetic; weak signal for full archive parsing because it bypasses footer, TOC parse, and decompression paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/estargz_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc.go -->
## sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc.go

Purpose: implements an `estargz.Compression` variant where the compressed layer footer declares that the TOC is external, while the compressor stores the compressed TOC separately for callers to publish or provide out of band. This keeps the TOC out of the layer data and therefore out of DiffID calculation.

Important APIs/types/functions: `GzipCompression` embeds `GzipCompressor` and `GzipDecompressor`. `NewGzipCompressionWithLevel` wires a compressor and decompressor around a caller-provided `provideTOC` function. `GzipCompressor.Writer` returns a gzip writer for layer chunks; `WriteTOCAndFooter` marshals `estargz.JTOC`, gzip-compresses a tar entry named `estargz.TOCTarName` into an internal buffer, writes only the external-TOC footer to the layer, and returns the digest of raw TOC JSON. `WriteTOCTo` later writes the stored compressed TOC. `GzipDecompressor.ParseFooter` recognizes a 46-byte footer with `SG` extra subfield `STARGZEXTERNALTOC` and returns negative payload/toc offsets to signal external TOC. `ParseTOC` and `DecompressTOC` reject non-nil readers and call `provideTOCFunc` once through `sync.Once`.

Control flow: compression writes normal gzip streams for payload chunks, then finalizes TOC into `gc.buf`, appends a marker footer, and leaves external storage to `WriteTOCTo`. Decompression parses the footer first; the negative TOC offset causes callers to pass nil into `ParseTOC`, which retrieves, validates, decompresses, and JSON-decodes the external TOC.

State and persistence: `GzipCompressor.buf` persists the most recently generated compressed TOC in memory. `GzipDecompressor.rawTOC` caches the provided TOC bytes, and `sync.Once` prevents repeated provider calls after a successful population. No disk persistence is implemented here.

Dependencies and integration points: relies on `archive/tar`, `compress/gzip`, `encoding/json`, `digest`, and the `estargz` compression/decompression interfaces. `estargz.Open`/metadata readers interpret negative TOC offsets according to the `Decompressor` contract. The layer test utilities include this compressor as one source compression mode.

Risks: `ParseFooter` indexes `extra[0:4]` without checking `len(extra)`, unlike the safer gzip parser in `estargz/gzip.go`; malformed short extra fields can panic. `getTOC` uses `sync.Once` but only stores successful bytes; if the provider returns an error, later calls will not retry and may surface "no TOC is provided" instead of the original error. `WriteTOCTo` errors before `WriteTOCAndFooter` has registered a buffer. The error message for invalid subfield length mentions the internal-TOC wanted length, which is misleading for external TOC.

Test signals: `externaltoc_test.go` runs the shared compression suite across gzip levels and checks footer size/negative TOC offset, but does not directly exercise provider retry, short-extra malformed footer handling, or concurrent decompressor access.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc_test.go -->
## sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc_test.go

Purpose: validates the external-TOC gzip compression implementation against the same behavioral contract as regular gzip eStargz, plus a footer-specific check for the external TOC marker.

Important APIs and helpers: `TestGzipEStargz` constructs an `estargz.TestRunner` and passes multiple `gzipControllerWithLevel` factories into `estargz.CompressionTestSuite`. Each controller pairs a compressor with a decompressor whose provider calls `compressor.WriteTOCTo`, proving the compressor's out-of-band TOC buffer can feed parser paths. `TestGzipFooter` checks `gzipFooterBytes`, `FooterSize`, and `GzipDecompressor.ParseFooter`.

Control flow: the shared suite builds archives, opens them with the external decompressor, verifies DiffID/TOC/chunk contents, and checks stream locations. The footer test builds one footer, parses it, and requires `tocOffset == -1`.

State and persistence: test state is in-memory only. The provider closure intentionally captures the same compressor instance so `WriteTOCAndFooter` populates `buf` before `ParseTOC` asks for it.

Dependencies and integration points: integrates external TOC implementation with package-wide `CompressionTestSuite`, `CheckGzipHasStreams`, and `GzipDiffIDOf` from `estargz/testutil.go`. It indirectly exercises `Build`, `Open`, TOC verification, chunk digest checks, and lossless/lossy writer paths.

Risks: the tests do not cover malformed short gzip extra fields, nil provider behavior, provider errors, repeated provider calls after failure, missing `WriteTOCAndFooter`, or a non-nil reader being passed to `ParseTOC`. Because the suite uses a cooperative provider, real registry/annotation wiring for external TOC is outside this file's coverage.

Test signals: strong compatibility signal for normal external TOC archives across gzip levels; narrow direct signal that the footer advertises external TOC by returning negative offsets.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/externaltoc/externaltoc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/gzip.go -->
## sources/cloud-native/stargz-snapshotter/estargz/gzip.go

Purpose: provides the default gzip-based `Compression` implementation for creating and parsing eStargz layers, including modern and legacy footer formats and TOC decompression.

Important APIs/types/functions: `gzipCompression` embeds `GzipCompressor` and `GzipDecompressor`. `NewGzipCompressor` and `NewGzipCompressorWithLevel` expose compressor construction. `GzipCompressor.Writer` returns `gzip.NewWriterLevel` as a `WriteFlushCloser`. `WriteTOCAndFooter` marshals `JTOC`, writes it as a tar entry named `stargz.index.json` into a gzip stream, optionally tees uncompressed TOC tar bytes into `diffHash`, writes the 51-byte eStargz footer, and returns the raw TOC JSON digest. `gzipFooterBytes` and `CreateGzipFooter` encode the footer extra field. `GzipDecompressor.ParseFooter` validates `SG` subfield metadata and extracts the hex TOC offset. `LegacyGzipDecompressor` supports the older 47-byte footer layout. `parseTOCEStargz` and `decompressTOCEStargz` decompress the TOC gzip stream, read the first tar entry, verify its name, and JSON-decode the TOC while computing its digest.

Control flow: writers emit chunk gzip members elsewhere, call `WriteTOCAndFooter` at close, and append a final zero-length gzip stream with a footer extra field pointing to TOC. Readers read the fixed-size footer, parse the TOC offset, range-read the TOC gzip member, decode the tar-contained JSON, and return both `JTOC` and digest for verification.

State and persistence: compressor instances only store compression level. Generated footers and TOC bytes are written to the supplied `io.Writer`; no internal durable state is retained. The parsed TOC is returned to caller-owned metadata/readers.

Dependencies and integration points: depends on Go gzip/tar/binary/json packages and `opencontainers/go-digest`. Implements the interfaces declared in `types.go`, used by `estargz.Build`, `Open`, metadata readers, and layer resolver defaults. `CreateGzipFooter` is reused by the external-TOC implementation.

Risks: `gzip.NewWriterLevel` errors are ignored in `Writer` callers and in `WriteTOCAndFooter` for the TOC writer; invalid compression levels could panic later through a nil writer if allowed. `ParseFooter` now guards `len(extra) < 4`, but after validating subfield length it assumes `subfield` is long enough; gzip extra consistency normally enforces this, but hostile footers are a risk area. Legacy parsing is maintained for compatibility and expands the accepted surface.

Test signals: `gzip_test.go` runs the shared compression suite across no-compression, best-speed, best-compression, default, and Huffman-only levels; it also round-trips modern and legacy footer offsets and verifies invalid short extra fields return errors rather than panics.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/gzip.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/gzip_test.go -->
## sources/cloud-native/stargz-snapshotter/estargz/gzip_test.go

Purpose: exercises regular gzip eStargz creation/parsing through the shared compression suite and directly validates footer encoding/parsing for modern and legacy footer layouts.

Important APIs and helpers: `TestGzipEStargz` runs `CompressionTestSuite` with controllers for `gzip.NoCompression`, `BestSpeed`, `BestCompression`, `DefaultCompression`, and `HuffmanOnly`. `gzipController` implements `TestingController` by combining `GzipCompressor` and `GzipDecompressor`, using `CheckGzipHasStreams` and `GzipDiffIDOf` for stream and DiffID checks. `TestGzipFooter` iterates offsets from 0 to 200000 and calls both `checkFooter` and `checkLegacyFooter`. `TestGzipParseFooterInvalidExtra` synthesizes malformed gzip blocks whose extra fields are nil, empty, or too short.

Control flow: suite cases build tar inputs, convert them to eStargz, compare TOC/tar equivalence, verify TOC digests, and test reads. Footer checks create bytes with `gzipFooterBytes` or `legacyFooterBytes`, parse them, and assert exact offsets. Invalid-extra tests pad a gzip block to `FooterSize` so the parser reaches extra validation.

State and persistence: in-memory byte buffers only; no file or network state.

Dependencies and integration points: depends on `compress/gzip` for test construction and on `testutil.go` for comprehensive archive behavior. Legacy footer helper mirrors the old footer format using `CreateGzipFooter`.

Risks: footer offset iteration is broad but not exhaustive for 64-bit values or corrupt magic strings. Invalid-extra coverage targets the modern parser only, not legacy parser or external TOC parser. Shared suite covers normal operation but not invalid compression-level constructor behavior.

Test signals: strong signal for gzip compatibility across compression levels, footer stability, legacy support, and safe handling of a previously panic-prone malformed extra-field class.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/gzip_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/testutil.go -->
## sources/cloud-native/stargz-snapshotter/estargz/testutil.go

Purpose: defines the shared compression conformance suite used by gzip, external-TOC gzip, and zstd-chunked tests. It verifies that a `Compression` implementation can build valid eStargz blobs, preserve/transform tar input correctly, expose chunked random access, compute DiffID, and enforce TOC/chunk digest verification.

Important APIs/types/functions: `TestingController` extends `Compression` with `TestStreams`, `DiffIDOf`, and `String`. `TestRunner` adapts `testing.T`-style subtests. `CompressionTestSuite` runs `testBuild`, `testDigestAndVerify`, and `testWriteAndOpen`. Helpers include `compressBlob`, `parseStargz`, `rewriteTOCJSON`, `listDigests`, `checkStargzTOC`, `checkVerifyTOC`, invalid verification checks, many `stargzCheck` implementations, tar entry builders (`file`, `dir`, `symlink`, hardlink/device/fifo helpers), landmark builders, random data, gzip stream detection, and DiffID calculation.

Control flow: `testBuild` compares archives built through the writer path against archives built through `Build`, for uncompressed/gzip/zstd input tars, multiple tar formats, path prefixes, chunk sizes, and min chunk sizes. `testDigestAndVerify` builds digest maps for expected chunks, checks raw TOC digests, verifies all chunk digests, rewrites TOCs or data to confirm failures, and validates invalid stargz inputs. `testWriteAndOpen` writes tar entries through lossy and lossless append paths, opens the result, validates telemetry callbacks, stream offsets, chunk counts, file reads at many offsets, xattrs, owners, modes, links, devices, landmarks, hardlink coalescing, and multi-file-in-one-chunk behavior.

State and persistence: all source tars, compressed blobs, rewritten TOCs, and caches are in memory. Digest maps persist expected chunk identifiers across checks. Random 64 KiB data is generated for chunk grouping tests, so failures may include randomized content but deterministic structure.

Dependencies and integration points: this file is tightly coupled to internal `estargz` writer/reader APIs such as `Build`, `Open`, `OpenFile`, `OpenFileWithPreReader`, `VerifyTOC`, `ChunkEntryForOffset`, TOC marshaling, stream offsets, and lossless append. Compression implementations in sibling packages implement `TestingController` to inherit this suite.

Risks: because it is test-only, helper behavior may encode assumptions that make implementation changes hard, especially exact stream counts and offsets. Some random-content tests are probabilistic around compression size assumptions. Invalid-path tests cover digest mismatches and malformed TOC entries but not every malformed tar/gzip/zstd condition. The helper reads and reconstructs whole blobs, so it is not a performance benchmark.

Test signals: very high value cross-implementation regression suite. It catches incompatible compression implementations, wrong TOC shape, broken DiffID, broken chunk digests, lost metadata, incorrect stream boundaries, and cache/preread regressions.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/types.go -->
## sources/cloud-native/stargz-snapshotter/estargz/types.go

Purpose: declares the core eStargz data model, public constants/annotations, TOC entry structure, file info adapter, verification interface, and pluggable compression contracts.

Important APIs/types/functions: constants define `TOCTarName`, modern and legacy footer sizes, OCI/container annotations for TOC digest and uncompressed size, and prefetch/no-prefetch landmark names. `JTOC` is the JSON table of contents. `TOCEntry` models filesystem entries and chunks, including tar metadata, offsets, chunk metadata, digest fields, xattrs, children, and runtime-only fields like `NumLink`, `nextOffset`, and `chunkTopIndex`. Methods include `ModTime`, `NextOffset`, `Stat`, `ForeachChild`, `LookupChild`, `addChild`, and `isDataType`. `fileInfo` converts TOC metadata to `os.FileInfo`, including tar mode conversion and special file type bits. `TOCEntryVerifier`, `Compression`, `Compressor`, `Decompressor`, and `WriteFlushCloser` define verification and codec contracts.

Control flow: this file mostly supplies structures and small methods. Writers/readers populate `TOCEntry` fields during tar conversion and TOC parse, build parent-child maps with `addChild`, expose children through lookup/iteration, and convert to stat data for callers. Compression implementations are called by writer and parser code through the interfaces here.

State and persistence: JSON tags define the durable TOC representation; runtime-only fields are intentionally omitted from JSON. Child maps and link counts are built after parse. `modTime` caches parsed `ModTime3339`, and `nextOffset` is computed to support chunk range reads.

Dependencies and integration points: used by all estargz packages, metadata readers, fs/layer logic, and image manifest label handling. Depends on `archive/tar` for mode interpretation, `os.FileInfo` conventions, `opencontainers/go-digest`, and `io/hash` contracts.

Risks: `ForeachChild` iterates Go maps, so order is nondeterministic unless callers sort. The `Compression` interface requires compatible footer/TOC semantics across codecs; mistakes in `ParseFooter` negative offsets or `tocSize` handling can break metadata loading. `fileInfo.Mode` relies on tar mode conversion and manual type mapping, so new TOC types need explicit handling. Runtime-only fields make it important that parsers rebuild indices consistently.

Test signals: covered indirectly by shared compression tests for metadata, modes, xattrs, chunks, owners, children, links, and digest verification; `estargz_test.go` directly covers chunk lookup boundaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked.go -->
## sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked.go

Purpose: implements zstd:chunked compression/decompression support under the `estargz.Compression` contract, including zstd skippable frames for TOC and footer plus annotations compatible with containers/storage zstd-chunked metadata.

Important APIs/types/functions: exported annotation constants are `ManifestChecksumAnnotation` and `ManifestPositionAnnotation`. `Decompressor.Reader` creates a zstd decoder for file payloads. `ParseTOC` zstd-decompresses the TOC JSON and computes its raw digest. `ParseFooter` decodes a 40-byte footer containing TOC offset, compressed length, raw size, manifest type, and magic. `DecompressTOC` returns a read closer for raw TOC JSON. `Compressor` holds `CompressionLevel`, optional `Metadata`, and a `sync.Pool` of zstd encoders. `Writer` reuses pooled encoders. `WriteTOCAndFooter` marshals TOC JSON, zstd-compresses it, writes a skippable-frame-wrapped TOC, writes a skippable-frame-wrapped footer, populates annotations when `Metadata` is non-nil, and returns raw TOC digest. `zstdFooterBytes` and `appendSkippableFrameMagic` encode the zstd-chunked frames.

Control flow: payload chunks are encoded as normal zstd frames. At close, compressed TOC is appended inside an 8-byte skippable-frame header; footer stores TOC position adjusted past that header and is itself appended as a skippable frame. Readers parse the trailing footer bytes from inside the final skippable frame, then range-read and decompress exactly the compressed TOC length.

State and persistence: compressor state includes reusable zstd encoders in a pool and optional metadata annotations written by side effect. The compressed blob persists TOC and footer frames; no separate state store is used.

Dependencies and integration points: uses `github.com/klauspost/compress/zstd`, `estargz` interfaces, and OCI digests. `fs/layer.Resolve` registers a `zstdchunked.Decompressor` as an additional metadata decompressor by default, making zstd-chunked layers mountable through the same reader path.

Risks: `ParseFooter` assumes the supplied byte slice is at least 40 bytes and indexes fixed ranges without a length check; callers are expected to provide `FooterSize` bytes. It validates magic but not manifest type or raw-size consistency. `WriteTOCAndFooter` stores `err` from `io.Copy` but continues to write the footer before returning it; if TOC copy failed, side effects may already have occurred. Encoder pooling requires `Close` to be called to return encoders.

Test signals: `zstdchunked_test.go` runs the shared compression suite across fastest/default/better compression levels, validates zstd frame offsets, computes DiffID through zstd decompression, and round-trips footer parse values.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked_test.go -->
## sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked_test.go

Purpose: validates the zstd:chunked compression implementation through the shared eStargz compression suite and direct footer round-trip tests.

Important APIs and helpers: `TestZstdChunked` runs `estargz.CompressionTestSuite` with zstd levels `SpeedFastest`, `SpeedDefault`, and `SpeedBetterCompression`. `zstdController` combines `Compressor` and `Decompressor`, implements stream validation with `TestStreams`, and computes DiffID by zstd-decompressing the blob into sha256. `TestZstdChunkedFooter` iterates offsets and compressed/raw sizes through `zstdFooterBytes` and `Decompressor.ParseFooter`. `nextIndex` is a local frame scanning helper.

Control flow: shared suite builds and opens archives, checks TOC/chunk/digest behavior, and expects stream offsets. `TestStreams` sorts expected offsets, adjusts the final footer offset by the 8-byte skippable frame header, scans the blob for zstd or skippable frame magic, and fails if expected frame starts are absent. Footer tests assert payload size equals `off - 8`, TOC offset equals `off`, and parsed TOC size equals compressed size.

State and persistence: all test data is in memory. No metadata annotation assertions are present even though the compressor can populate annotations.

Dependencies and integration points: uses `klauspost/compress/zstd`, shared `estargz` test utilities, and package-local frame magic constants. It indirectly verifies compatibility with `estargz.Build`, `Open`, and verification logic for zstd-chunked codecs.

Risks: `SpeedBestCompression` is intentionally skipped for CI memory reasons, leaving highest compression level less covered. Frame scanning is heuristic and looks for magic sequences rather than parsing complete zstd frame headers. Tests do not cover malformed short footers, invalid footer magic beyond direct parser error path, metadata annotation values, or TOC copy failure behavior.

Test signals: strong normal-operation signal for zstd-chunked archives and footer encoding; moderate signal for stream layout because magic scanning can be fooled by magic-like bytes in payloads, though suite fixtures make that unlikely.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/estargz/zstdchunked/zstdchunked_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/config/config.go -->
## sources/cloud-native/stargz-snapshotter/fs/config/config.go

Purpose: defines configuration and snapshot label keys for the stargz snapshotter filesystem, including cache modes, resolve TTLs, prefetch/background fetch behavior, verification policy, metrics, blob fetching, directory cache, and FUSE options.

Important APIs/types/functions: label constants are `TargetSkipVerifyLabel` and `TargetPrefetchSizeLabel`. `Config` aggregates high-level filesystem settings and embeds `BlobConfig`, `DirectoryCacheConfig`, and `FuseConfig`. `BlobConfig` controls remote blob validity, chunk size, prefetch chunking, retry counts, wait bounds, and single-range mode. `DirectoryCacheConfig` controls LRU sizes, sync adds, direct mode, and fadvise. `FuseConfig` controls attr/entry timeouts, passthrough mode, merge buffer size, and merge worker count.

Control flow: this file is declarative; consumers such as `fs.NewFilesystem`, `layer.NewResolver`, and `remote.NewResolver` interpret zero values as defaults and booleans as feature toggles.

State and persistence: fields are tagged for TOML and JSON serialization, making them persisted through config files or API structs outside this file. No runtime state is stored here.

Dependencies and integration points: imported by `fs/fs.go`, `fs/layer/layer.go`, remote blob resolution, and snapshot label handling. The labels control mount-time prefetch override and optional verification skip when policy permits.

Risks: typo in `BlobConfig.FetchTimeoutSec` JSON tag (`fetching_tieout_sec`) may affect JSON config compatibility. Some comments say seconds for millisecond fields (`MinWaitMSec`, `MaxWaitMSec`). Zero-value defaults are implemented elsewhere, so adding new fields requires coordinated defaulting in consumers.

Test signals: no direct tests in this subset. Behavior is indirectly covered where filesystem/layer code reads config values for default concurrency, timeouts, cache types, prefetch, passthrough, and verification.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/config/config.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/fs.go -->
## sources/cloud-native/stargz-snapshotter/fs/fs.go

Purpose: implements the snapshotter `FileSystem` that resolves remote layer sources, verifies or skips layer verification according to labels/config, starts prefetch/background fetch, exposes the layer through go-fuse, tracks mounted layers, and manages per-layer metrics.

Important APIs/types/functions: option functions customize source extraction, remote handlers, metadata store, metrics log level, overlay opaque mode, and extra decompressors. `NewFilesystem` applies defaults, creates a background task manager, layer resolver, metrics namespace/controller, and returns a `snapshot.FileSystem`. `filesystem.Mount` resolves sources and layers, pre-resolves neighboring layers, verifies TOC digest or skip policy, creates a root node, registers metrics, and starts a FUSE server. `Check` verifies layer connectivity and waits for prefetch. `check` refreshes broken blob connections from current labels. `Unmount` closes/evicts layer state and unmounts with force fallback. `prefetch` starts asynchronous prefetch/background fetch. `neighboringLayers` filters target layer out of manifest layers.

Control flow: mount begins with prioritized-task gating to avoid background network contention. It obtains sources from labels, applies prefetch label override, resolves the target in a goroutine, pre-resolves neighboring layers in parallel, waits up to 30 seconds, enforces verification policy, builds FUSE node FS/server, then waits for mount. Prefetch and background fetch are launched when resolution succeeds. Check locates the registered layer, optionally refreshes connectivity if not fully fetched, and blocks on prefetch unless disabled.

State and persistence: `filesystem.layer` maps mountpoints to active `layer.Layer` references under `layerMu`. Package-level `ns` and `metricsCtr` are singleton metric registration state guarded by `nsLock`. The resolver/cache state lives under the configured root and layer resolver.

Dependencies and integration points: integrates containerd remote/source labels, OCI descriptors, `fs/layer`, `metadata`, `task`, go-fuse, Prometheus/docker metrics, and Linux unmount syscall. Verification uses `estargz.TOCJSONDigestAnnotation` and `config.TargetSkipVerifyLabel`.

Risks: `Mount` starts `fs.prefetch` inside the resolver goroutine before the layer is registered and before verification completes; prefetch can run on unverified content unless the layer reader itself enforces verification state. The 30-second resolve timeout is hard-coded. `Check` treats prefetch wait errors as warnings and returns nil, which may allow container startup despite prefetch failure. `Unmount` holds `layerMu` while closing the layer, potentially blocking other mountpoint operations during cleanup. Metrics singletons mean configuration changes after first filesystem may not re-register common metrics.

Test signals: `fs_test.go` covers `Check` success/failure with a breakable layer and refresh path. Mount/unmount/FUSE server behavior is not directly tested here and relies on integration tests elsewhere.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/fs.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/fs_test.go -->
## sources/cloud-native/stargz-snapshotter/fs/fs_test.go

Purpose: unit-tests `filesystem.Check` behavior with a controllable fake layer.

Important APIs and helpers: `TestCheck` creates a `filesystem` with one mountpoint mapped to `breakableLayer`, a small background task manager, and default-label source resolver. `breakableLayer` implements the full `layer.Layer` interface with success/failure switches for `Check` and `Refresh`; other methods are stubs returning failures or nil as needed.

Control flow: first the fake layer succeeds, and `fs.Check` must return nil. Then the fake layer fails, and `fs.Check` must return an error. Because `Info` reports `Size: 1` and default `FetchedSize: 0`, `Check` exercises connectivity/refresh logic before prefetch waiting.

State and persistence: in-memory fake layer state only (`success bool`). No mounts, FUSE server, disk cache, or remote registry are used.

Dependencies and integration points: depends on `fs/layer.Layer`, `fs/source`, `task.BackgroundTaskManager`, and containerd reference/registry host types to satisfy the check path. The fake ensures interface compatibility with the production layer contract.

Risks: coverage is narrow. It does not test a missing mountpoint, successful refresh after initial failure, prefetch wait warning semantics, noprefetch behavior, or actual label-driven source refresh. Stubs can hide interactions with real layer state and metrics.

Test signals: basic regression signal that `Check` consults layer connectivity and propagates hard refresh failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/fs_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/layer.go -->
## sources/cloud-native/stargz-snapshotter/fs/layer/layer.go

Purpose: implements remote layer resolution, layer/blob caching, per-layer data caches, verification lifecycle, prefetch/background fetch, FUSE root node creation, and resource cleanup for the stargz snapshotter.

Important APIs/types/functions: `Layer` is the interface consumed by `fs`. `Info` reports digest, size, fetched/prefetched sizes, read time, and TOC digest. `Resolver` holds remote resolver, TTL caches, config, metadata store, background task manager, named resolve lock, and decompressor hooks. `NewResolver` initializes TTL layer/blob caches with eviction cleanup. `newCache` creates memory or directory blob caches. `Resolver.Resolve` deduplicates/caches layer resolution, resolves blobs, creates fs cache, builds metadata reader with telemetry and zstd decompressor, creates `reader.VerifiableReader`, and caches a new `layer`. `resolveBlob` caches remote blobs. `layer` implements verification, prefetch, background fetch, root node creation, `ReadAt`, `Done`, and `Close`. `waiter` coordinates prefetch completion.

Control flow: `Resolve` serializes by ref/digest name, returns valid cached layers when possible, resolves a blob otherwise, wraps blob reads as prioritized tasks for metadata parsing, builds telemetry hooks, installs default and additional decompressors, constructs a verifiable reader, and adds the layer to a TTL cache. `Verify` or `SkipVerify` must initialize `l.r` before `RootNode`. `Prefetch` runs once, checks landmarks, computes prefetch size, optionally releases waiters early for async prefetch threshold, caches compressed and uncompressed prefetched data, and records metrics. `BackgroundFetch` runs once and invokes cancellable background reads through the task manager.

State and persistence: resolver state includes root directories, TTL caches, and disk cache subdirectories. Layer state includes blob reference, verifiable reader, verified reader, prefetch size, one-shot guards, closed flag, passthrough settings, and waiter channel. Cache eviction calls close on layers/blobs; `Done(false)` decrements references for reuse and `Close` evicts immediately.

Dependencies and integration points: depends on `remote`, `reader`, `metadata`, `cache`, zstdchunked decompressor, task manager, named mutexes, OCI descriptors, and fs metrics. It is the bridge between registry blobs and FUSE nodes in `node.go`.

Risks: `Verify` and `SkipVerify` are not mutex-protected; concurrent calls could race on `l.r`. `Prefetch` calls `prefetchWaiter.done()` via defer and also early for async threshold, relying on `sync.Once` for correctness. If async prefetch later fails, `WaitForPrefetchCompletion` may already have returned nil. `newCache` creates temp directories; cleanup depends on cache close/eviction paths. `Resolve` closes a discarded duplicate layer without checking the returned error. Background fetch timeouts and cancellation may leave partially cached data.

Test signals: `layer_test.go` plus `testutil.go` cover prefetch sizing/caching across compression modes, node reads, passthrough configurations, whiteouts, xattrs, state file, and waiter behavior. Resolver remote-cache error paths are less directly covered.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/layer_test.go -->
## sources/cloud-native/stargz-snapshotter/fs/layer/layer_test.go

Purpose: entry point for the shared layer test suite and a direct test of the prefetch waiter primitive.

Important APIs and helpers: `TestLayer` wraps `testing.T` in the local `TestRunner` and runs `TestSuiteLayer` with `memorymetadata.NewReader`. `TestWaiter` constructs `newWaiter`, launches a goroutine waiting with a long timeout, sleeps one second, calls `done`, and verifies wait did not return too early.

Control flow: the layer suite itself is implemented in `testutil.go` and runs prefetch, node read, and node behavior tests across default and passthrough configurations. `TestWaiter` directly exercises channel closure and `sync.Once` behavior.

State and persistence: no persistent state. Test suite creates in-memory metadata/cache and temporary synthetic blobs through helper code.

Dependencies and integration points: depends on `metadata/memory` as the metadata store under test and package-local layer helpers. It indirectly integrates estargz test tar builders and compression variants through `testutil.go`.

Risks: `TestWaiter` only tests the success path where `done` fires before timeout; it does not test timeout behavior or idempotent repeated `done`. `TestLayer` coverage depends entirely on shared helper breadth.

Test signals: good smoke signal that the memory metadata backend satisfies layer expectations; direct waiter test catches premature wakeups but not timeout edge cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/layer_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/node.go -->
## sources/cloud-native/stargz-snapshotter/fs/layer/node.go

Purpose: maps verified layer metadata into a go-fuse node tree, implements directory lookup/read, file open/read, overlay whiteout/opaque semantics, xattrs, symlinks, statfs, passthrough fd support, and a hidden state directory for observability.

Important APIs/types/functions: `OverlayOpaqueType` selects which overlay opaque xattrs are exposed. `newNode` builds the root node around a `reader.Reader`, remote blob, base inode, overlay xattr policy, passthrough config, and access logging flag. `fs` holds shared node state and inode calculators. `node` implements `Readdir`, `Lookup`, `Open`, `Getattr`, `Getxattr`, `Listxattr`, `Readlink`, and `Statfs`. `file` implements read/getattr/passthrough/release. `whiteout` exposes overlayfs char-device whiteouts. `state`, `statFile`, and `statJSON` expose `.stargz-snapshotter/<digest>.json` with error/fetch state. Attribute conversion helpers map metadata to FUSE attrs and system modes.

Control flow: directory reads fetch children from metadata, hide root-level prefetch landmarks and `.wh.*` marker files, synthesize `.`/`..`, synthesize whiteout char entries where no normal sibling replaces them, sort entries, and cache the result. Lookup hides landmarks/whiteout markers, exposes the hidden state directory only by direct lookup, reuses child inodes when cached, resolves metadata children, or synthesizes whiteout nodes. File open creates a reader, logs first access once, and optionally enables passthrough fd using reader support. Reads call the reader and translate non-EOF errors to `EIO`. State file reads update fetched size and percent before marshaling JSON.

State and persistence: nodes cache directory entries under `entsMu`. Each node has an atomic first-access flag. The state file stores last reported error in memory and queries blob fetched size on read. Inode numbers combine `baseInode` with reserved IDs for state/stat files and metadata IDs for source entries; no disk persistence is performed here.

Dependencies and integration points: depends on go-fuse v2 interfaces, `reader.Reader`, metadata attributes, remote blob state, fs common metrics, OCI digest, Linux syscall/unix device helpers, and estargz landmark constants. It is constructed by `layer.RootNode` after verification.

Risks: cached directory entries may go stale if metadata were mutable, though layer metadata is expected immutable. `Getxattr`/`Listxattr` return `ERANGE` based on buffer sizes and include opaque xattrs dynamically. `statJSON.FetchedPercent` divides by size; zero-size blobs would produce NaN/Inf risk. `Open` mutates shared `fs.passThrough.enable` to false on one passthrough failure, affecting later opens. The hidden state directory is not listed but is accessible by name, so callers must treat it as intentional observability surface.

Test signals: layer test utilities cover root landmark hiding, whiteout and opaque xattr synthesis, state file read/report, mode bits, symlink size, directory dot entries, cached prereads, and file read offsets across compression modes and passthrough configurations.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/node.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/testutil.go -->
## sources/cloud-native/stargz-snapshotter/fs/layer/testutil.go

Purpose: provides the comprehensive shared test suite for `fs/layer`, exercising prefetch, file reads, FUSE node behavior, overlay semantics, state files, passthrough settings, compression variants, and cache behavior.

Important APIs/types/functions: `TestSuiteLayer` runs tests for default and three passthrough configurations. `testPrefetch` builds sample eStargz blobs and validates blob cache calls, landmark-selected prefetch sizes, and cached uncompressed reads. `sampleBlob` tracks read/cache calls and duplicate regions. `testNodeRead` validates file `Read` across offsets, request sizes, chunk positions, and file sizes. `makeNodeReader` constructs a root node and opens a test file. `testNodes` and `testNodesWithOpaque` validate whiteouts, opaque dirs, landmarks, state files, special modes, symlink sizes, multi-file chunks, directory dots, xattrs, and cache hits. Numerous check helpers traverse go-fuse nodes and assert attrs/content.

Control flow: tests build eStargz blobs through `util/testutil.BuildEStargz` with gzip, zstd, and external-TOC gzip compression. Metadata readers are created from the supplied `metadata.Store`, readers are verified by TOC digest, root nodes are initialized with `fusefs.NewNodeFS`, and checks interact through FUSE-like methods (`Lookup`, `Readdir`, `Open`, `Read`, `Getattr`, xattr calls). Prefetch tests call `layer.Prefetch`, inspect remote cache arguments, then read expected files to prove no remote blob reads occur.

State and persistence: all data is in memory: sample blobs, memory caches, called offsets, test state file JSON, and synthetic node trees. The test creates no actual mountpoints. `calledReaderAt` records lower-level reads to distinguish cache hits from misses.

Dependencies and integration points: imports `estargz`, `fs/reader`, `remote`, `metadata`, go-fuse, util test tar builders, gzip/zstd compression helpers, and Linux mode/device packages. It is invoked by `layer_test.go` with the memory metadata backend.

Risks: the suite is broad but synthetic: it bypasses real registry/network behavior, real FUSE kernel mounts, disk directory cache behavior, and resolver TTL eviction. Random data supports compression-size assumptions that are likely but not mathematically guaranteed. Some passthrough scenarios only verify functional reads, not OS-level passthrough performance.

Test signals: very high signal for layer-to-node correctness, cache/preread behavior, overlay translation, and prefetch policy. Lower signal for remote resolver lifecycle and production mount/unmount interactions.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/layer/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/metrics/common/metrics.go -->
## sources/cloud-native/stargz-snapshotter/fs/metrics/common/metrics.go

Purpose: defines shared Prometheus metrics and log helpers for filesystem operations, including mount latency, registry reads, metadata reads, FUSE node operations, prefetch/background fetch phases, on-demand reads, and byte counters.

Important APIs/types/functions: constants name metric keys and operation labels. Histograms `operationLatencyMilliseconds` and `operationLatencyMicroseconds`, counter `operationCount`, and gauge `bytesCount` are registered once by `Register`. Public helpers are `MeasureLatencyInMilliseconds`, `MeasureLatencyInMicroseconds`, `IncOperationCount`, `AddBytesCount`, `WriteLatencyLogValue`, `WriteLatencyWithBytesLogValue`, and `LogLatencyForLastOnDemandFetch`.

Control flow: callers record a start time, then call measure/log helpers after operations complete. `Register` uses `sync.Once` to set log level and register collectors. Log helpers add fields `metrics`, `operation`, and `layer_sha` to the containerd logger. `LogLatencyForLastOnDemandFetch` only logs positive duration from mount start to last on-demand read.

State and persistence: package-level Prometheus collectors and `logLevel` persist for process lifetime. Metrics are exported through the Prometheus registry; latency logs go to configured logging sinks.

Dependencies and integration points: used by `fs.Mount`, `fs.Check`, `layer.Prefetch`, `layer.BackgroundFetch`, `node.Readdir`, and `file.Read`. `fs.NewFilesystem` calls `Register` unless Prometheus is disabled.

Risks: `Register` only honors the first log level due to `sync.Once`. `bytesCount` is a gauge but helpers only add, so semantics are cumulative unless externally reset. High-cardinality layer digest labels may expand metric series. `LogLatencyForLastOnDemandFetch` silently drops zero/negative durations, which is intentional but can hide missing read-time updates.

Test signals: no direct tests in this subset. Indirect coverage exists where layer/fs paths invoke metrics, but assertions generally do not inspect Prometheus collectors or logs.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/metrics/common/metrics.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/metrics/layer/layer.go -->
## sources/cloud-native/stargz-snapshotter/fs/metrics/layer/layer.go

Purpose: declares per-mounted-layer metric definitions for fetched size, prefetched size, and total layer size.

Important APIs/types/functions: package variable `layerMetrics` is a slice of `metric` definitions consumed by the layer metrics controller. Each metric defines name, help text, unit `metrics.Bytes`, Prometheus value type `CounterValue`, and a `getValues` function that reads `layer.Layer.Info()`.

Control flow: no active control flow in this file; `Controller.Collect` in `metrics.go` iterates these definitions and emits values for each registered mountpoint/layer.

State and persistence: metric definitions are immutable package-level state. Actual layer references live in the controller.

Dependencies and integration points: depends on `fs/layer.Layer`, docker/go-metrics units, and Prometheus value types. Integrated by `NewLayerMetrics`, which appends this slice to a controller.

Risks: values like fetched size and prefetched size can change over time but are emitted as `CounterValue`; if they ever decrease due to cache eviction/reconnect semantics, Prometheus counter semantics would be wrong. Calling `Info()` once per metric can repeat work and potentially observe slightly different snapshots across metrics.

Test signals: no direct tests. Metrics are operational observability only in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/metrics/layer/layer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/metrics/layer/metrics.go -->
## sources/cloud-native/stargz-snapshotter/fs/metrics/layer/metrics.go

Purpose: implements a docker/go-metrics collector/controller that tracks active mounted layers by mountpoint and exports the metric definitions from `layer.go`.

Important APIs/types/functions: `NewLayerMetrics` creates a `Controller`, attaches layer metric definitions, adds it to a metrics namespace, and returns a no-op controller when namespace is nil. `Controller` implements `Describe` and `Collect`. `Add` and `Remove` register/unregister mountpoint-to-layer mappings. `metric.desc` creates descriptors with labels `digest`, `mountpoint`, and optional metric-specific labels. `metric.collect` emits `prometheus.MustNewConstMetric`.

Control flow: filesystem mount calls `Add`; unmount calls `Remove`. During collection, the controller R-locks the layer map, starts a goroutine per mounted layer using `sync.WaitGroup.Go`, collects each metric for that layer, unlocks, and waits. Each metric reads layer info and sends a Prometheus metric to the channel.

State and persistence: `Controller.layer` stores active layers keyed by mountpoint under `layerMu`. Namespace and metric definitions persist for controller lifetime. No disk persistence.

Dependencies and integration points: used from `fs.NewFilesystem`, `fs.Mount`, and `fs.Unmount`. Depends on docker/go-metrics namespace descriptors, Prometheus collector interfaces, and the `layer.Layer` info contract.

Risks: `sync.WaitGroup.Go` requires a Go version that provides that method; older Go toolchains would fail to build. `Collect` holds the read lock while spawning and waiting for all goroutines, so `Add`/`Remove` block until collection finishes. Concurrent metric collection calls `l.Info()` from multiple goroutines, so layer implementations must remain concurrency-safe. A nil namespace intentionally disables all operations.

Test signals: no direct tests. Indirect runtime coverage comes from filesystem mounting registering/removing layers, but metric output correctness is not asserted here.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/fs/metrics/layer/metrics.go -->
