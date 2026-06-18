# subset-b-000275 Research

Grouped code research for the exact source files assigned to `subset-b-000275`. Each section title preserves the original source path and is bounded for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/namedmutex/namedmutex.go -->
# sources/cloud-native/soci-snapshotter/util/namedmutex/namedmutex.go

## Purpose
`namedmutex.go` defines a tiny package-level primitive, `NamedMutex`, that gives callers independent `sync.Mutex` instances keyed by string names. It is intended for coordinating work on per-resource keys without serializing all callers through one global mutex.

## Important APIs, Types, and Functions
`type NamedMutex` owns `muMap map[string]*sync.Mutex`, `refMap map[string]int`, and a guard mutex `mu`. `Lock(name string)` lazily initializes maps, creates a per-name mutex, increments the reference count, releases the guard mutex, and then locks the per-name mutex. `Unlock(name string)` retrieves the per-name mutex, decrements and possibly deletes the maps entries, releases the guard mutex, and finally unlocks the per-name mutex.

## Control Flow, State, and Persistence
All state is in memory. The guard mutex serializes map creation and reference-count updates. Reference counts include waiters as soon as they call `Lock`, so a per-name mutex is not deleted while other goroutines are waiting on it. No persistence or external IO is involved.

## Dependencies and Integration Points
The only dependency is Go `sync`. The type is reusable anywhere in the snapshotter that needs keyed exclusion.

## Risks and Test Signals
`Unlock` assumes the name was previously locked; unlocking an unknown name will dereference a nil mutex or mutate a nil map. The code also has no direct test in this subset. The reference-count approach is the key safety signal: deleting occurs before the actual unlock, but waiting goroutines already hold a reference count, so they retain the pointer they will lock.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/namedmutex/namedmutex.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ociutil/ociutil.go -->
# sources/cloud-native/soci-snapshotter/util/ociutil/ociutil.go

## Purpose
`ociutil.go` contains OCI image document validation and platform de-duplication helpers copied or adapted from containerd behavior.

## Important APIs, Types, and Functions
`UnknownDocument` models unvalidated image JSON with raw fields for `mediaType`, `config`, `layers`, `manifests`, and schema-1 `fsLayers`. `ValidateMediaType(b, mt)` unmarshals JSON, rejects schema 1, and checks that the declared media type is consistent with manifest-vs-index fields and embedded `mediaType`. `DedupePlatforms(ps)` returns platforms with strict normalized duplicates removed while preserving first occurrence order.

## Control Flow, State, and Persistence
Validation is stateless and operates entirely on the input byte slice. `DedupePlatforms` builds a list of `platforms.Matcher` values as it scans; each new platform is normalized and compared against already accepted matchers.

## Dependencies and Integration Points
The package depends on `containerd/v2/core/images` for media-type classification, `containerd/platforms` for normalization and strict matching, and OCI image-spec platform structs. It integrates with code that consumes OCI manifests or indexes and wants containerd-compatible semantics.

## Risks and Test Signals
`ValidateMediaType` only checks high-level shape, not full manifest schema validity. It returns nil for unknown media types unless they classify as manifest or index. `DedupePlatforms` treats normalized aliases such as `x86_64` and `amd64` as duplicates; callers needing to preserve original spelling should use the returned first occurrence.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ociutil/ociutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ociutil/ociutil_test.go -->
# sources/cloud-native/soci-snapshotter/util/ociutil/ociutil_test.go

## Purpose
This test file validates the behavior of `DedupePlatforms`.

## Important APIs, Types, and Functions
`assertPlatformEqual` compares every field of `ocispec.Platform`, including OS features via `slices.Equal`. `TestDedupePlatforms` covers no duplicates, exact duplicate removal, and normalized duplicate removal where `x86_64` matches `amd64`.

## Control Flow, State, and Persistence
The test is table-driven. For each case, it runs `DedupePlatforms`, asserts result length, and compares platforms positionally. It has no filesystem, network, or persistent state.

## Dependencies and Integration Points
The test uses Go `testing`, `slices`, and OCI platform structs. It indirectly validates integration with `containerd/platforms.Normalize` and `OnlyStrict`.

## Risks and Test Signals
The test does not cover `ValidateMediaType`. It also does not cover variants, OS version, or OS features in the de-duplication path. The strongest signal is that first-match order is expected and normalized architecture aliases collapse.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/ociutil/ociutil_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/ensurehello.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/ensurehello.go

## Purpose
`ensurehello.go` provides an integration-test helper that downloads a known `hello-world` OCI archive, verifies its digest, imports it into a temporary containerd content store, and returns the image descriptor and store.

## Important APIs, Types, and Functions
Constants `HelloArchiveURL` and `HelloArchiveDigest` identify the fixture archive. `EnsureHello(ctx)` performs the download, gzip decompression, digest calculation, temporary directory creation, local content store creation, and `archive.ImportIndex`.

## Control Flow, State, and Persistence
The function streams the HTTP response through an SHA256 tee reader and gzip reader. It creates a temporary content store on disk with `os.MkdirTemp` and `local.NewStore`. The store persists after return; the helper does not return the temp path or register cleanup, so callers must manage lifecycle through the returned content store and process temp cleanup policies.

## Dependencies and Integration Points
It depends on net/http, gzip, containerd content/archive/local store packages, OCI descriptors, and `go-digest`. It integrates with tests needing a real image without a daemon pull.

## Risks and Test Signals
The helper is network-dependent and uses `http.Get` without context binding or response status checks. It closes `resp.Body` twice, which is harmless but redundant. Digest verification protects against fixture corruption after import, but if import reads before full digest consumption, digest calculation depends on the tee reader being fully consumed by the gzip importer.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/ensurehello.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/random.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/random.go

## Purpose
`random.go` supplies deterministic pseudo-random data generation for tests.

## Important APIs, Types, and Functions
`TestRandomSeed` is the fixed global seed. `TestRand` wraps `*rand.Rand`. `NewTestRand(t)` combines the fixed seed with an FNV-1a hash of the test name and creates a PCG-backed `rand/v2.Rand`. Methods `Read`, `RandomByteData`, `RandomByteDataRange`, and `RandomDigest` generate deterministic bytes, bounded printable-ish data, and random digests.

## Control Flow, State, and Persistence
All state is in the `rand.Rand` instance. The helper is intentionally not thread-safe. Generated sequences vary by test name but are repeatable across runs.

## Dependencies and Integration Points
Dependencies are `hash/fnv`, `math/rand/v2`, Go testing, and `go-digest`. The ztoc tests use this package to generate repeatable tar file contents and gzip header data.

## Risks and Test Signals
`Read` converts `Int64()` to byte, which is deterministic but not byte-distribution focused. `RandomByteDataRange` treats `maxBytes` as exclusive and panics if `maxBytes <= minBytes` because of `IntN`. The deterministic seed is a strong reproducibility signal for large ztoc tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/random.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/shell.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/shell.go

## Purpose
`shell.go` provides integration-test utilities for dockershell execution, buffered test logging, snapshotter log monitoring, content-store injection/removal, remote file copying, and process cleanup.

## Important APIs, Types, and Functions
`TestingReporter` adapts `testing.T` to the dockershell reporter interface while buffering logs until failure. `LogMonitor` scans stdout/stderr through tee readers and invokes registered line callbacks. `RemoteSnapshotMonitor` counts structured log lines indicating remote, local, or deferred snapshot preparation. `IndexDigestMonitor` extracts the SOCI index digest from structured logs. `MonitorStartup` and `LogConfirmStartup` detect fatal or successful snapshotter startup logs. File/content helpers include `TempDir`, `InjectContentStoreContentFromReader`, `InjectContentStoreContentFromBytes`, `WriteFileContents`, and `CopyInDir`. Cleanup helpers include `KillMatchingProcess`, `RemoveContentStoreContent`, and store-specific removal functions.

## Control Flow, State, and Persistence
`LogMonitor.Start` launches one goroutine per stream and calls registered monitors until `Cleanup` closes a `finished` channel. Snapshot counters are updated atomically. Content injection either writes directly into the SOCI content store under `blobs/<algo>/<encoded>` or uses `ctr content ingest` and labels the parent content with an incrementing SOCI integration-test label. `CopyInDir` creates a local tar stream through a pipe, writes it to the remote shell, extracts it, and removes the temporary tar.

## Dependencies and Integration Points
The file depends on `dockershell`, SOCI store path/type helpers, OCI descriptors, `go-digest`, `xid`, and `errgroup`. It integrates tightly with containerd CLI (`ctr`), shell execution environments, SOCI content store layout, and integration-test logs.

## Risks and Test Signals
Several shell commands use string interpolation into `/bin/sh -c` with paths supplied by tests; callers need controlled paths. `InjectContentStoreContentFromReader` ignores returned errors from the two concrete injection helpers because it does not return after the switch call, so failures can be lost. `LogMonitor.Cleanup` does not block on scanner shutdown; it launches a goroutine to wait, which avoids hanging tests but can leave late log processing. Process killing uses SIGINT to preserve coverage output and ignores disappeared processes, which is useful but pattern matching must be precise.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/shell.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/store.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/store.go

## Purpose
`store.go` provides a small helper for resolving the blob directory for a configured content store type.

## Important APIs, Types, and Functions
`GetContentStoreBlobPath(contentStoreType)` calls `store.GetContentStorePath(contentStoreType, "")` and appends `blobs/sha256`.

## Control Flow, State, and Persistence
The helper performs path calculation only. It does not verify directory existence or create directories.

## Dependencies and Integration Points
It depends on `path/filepath` and `github.com/awslabs/soci-snapshotter/soci/store`. It is used by shell test helpers for direct SOCI content deletion.

## Risks and Test Signals
Only SHA256 blob layout is supported. Errors from content-store path canonicalization are propagated, but missing directories are not detected here.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/store.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/tar.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/tar.go

## Purpose
`tar.go` is a test fixture factory for tar, tar.gz, and zstd-compressed tar archives with configurable entries, metadata, ownership, modes, timestamps, xattrs, and gzip headers.

## Important APIs, Types, and Functions
`TarEntry` abstracts an entry that can append itself to a `tar.Writer`. `BuildTarOptions` carries name prefix and gzip header fields. `BuildTar`, `BuildTarGz`, and `BuildTarZstd` stream archives through `io.Pipe` from goroutines. `WriteTarToTempFile` persists a generated archive and also returns its bytes. `GetFilesAndContentsWithinTarGz`, `GetFilesAndContentsWithinTar`, and `getFilesAndContentsFromTarReader` inspect regular-file contents. Entry constructors include `Dir`, `File`, `Symlink`, `Link`, `Chardev`, `Blockdev`, and `Fifo`, with option types for directory and file metadata. `permAndExtraMode2TarMode` maps Go mode bits to tar mode bits, including suid, sgid, and sticky.

## Control Flow, State, and Persistence
Archive builders return readers immediately while goroutines write entries and close the pipe or close with errors. Temp-file output uses `os.CreateTemp`, `io.MultiWriter`, and leaves deletion to the caller. Metadata is embedded in tar headers; no other state is retained.

## Dependencies and Integration Points
The file depends on `archive/tar`, gzip, zstd, os/io primitives, and time. It is heavily used by ztoc tests to validate metadata construction, compression header edge cases, decompression, serialization, and benchmarks.

## Risks and Test Signals
Errors in builder goroutines surface when the consumer reads from the returned pipe. `Dir` panics if the directory name lacks a trailing slash; `File` returns an error if the file name has one. Hard link and device constructors use current time, which can affect deterministic archive bytes if compared directly. Tests use these helpers to exercise file types, large payloads, and gzip header variations.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/template.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/template.go

## Purpose
`template.go` provides helpers for applying Go text templates in tests.

## Important APIs, Types, and Functions
`ApplyTextTemplate(temp, config)` wraps `ApplyTextTemplateErr` and returns a string. `ApplyTextTemplateErr(temp, conf)` creates a template named by the digest of the template source, parses it with `template.Must`, executes it into a bytes buffer, and returns the bytes.

## Control Flow, State, and Persistence
The functions are stateless. Parse failures panic due to `template.Must`; execution failures are returned by `ApplyTextTemplateErr` and wrapped without preserving the original error in `ApplyTextTemplate`.

## Dependencies and Integration Points
Dependencies are `bytes`, `fmt`, `text/template`, and `go-digest`. The digest-derived name avoids conflicts and gives deterministic template names.

## Risks and Test Signals
`ApplyTextTemplate` discards the underlying execution error when wrapping, reducing diagnostics. Parse errors panic rather than returning an error, so callers must only pass trusted test templates.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/template.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/util.go -->
# sources/cloud-native/soci-snapshotter/util/testutil/util.go

## Purpose
`util.go` contains general test utilities for logging, project-root discovery, and buffered output.

## Important APIs, Types, and Functions
Constants define the default GOPATH-relative project root, the `SOCI_SNAPSHOTTER_PROJECT_ROOT` environment variable, and `BuildKitVersion`. `TestingL` is a package-level logger. `TestingLogDest` and `BufferedTestingLogDest` return log writers. `GetProjectRoot` resolves the repo path from the env var, GOPATH, or `go env GOPATH`, and validates a `Dockerfile` exists. `TestWriter` adapts `testing.TB` to `io.Writer`. `BufferedWriter` buffers bytes until `Flush`.

## Control Flow, State, and Persistence
Project-root lookup reads environment variables, may execute `go env GOPATH`, and stats candidate paths. Buffered writer state is an in-memory byte slice that is reset on flush.

## Dependencies and Integration Points
The file uses os/exec/env/path utilities and testing/log/io packages. It integrates with the shell test reporter and test harnesses that need repository-relative assets.

## Risks and Test Signals
`GetProjectRoot` assumes a legacy GOPATH layout when the env var is absent, which may fail in module-only checkouts. `TestWriter.Write` logs whole byte chunks as strings, which can add extra test log formatting. Buffered logging is useful for only emitting command logs on failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/util/testutil/util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/version/version.go -->
# sources/cloud-native/soci-snapshotter/version/version.go

## Purpose
`version.go` defines package-level version metadata filled at link time.

## Important APIs, Types, and Functions
`const Unset = "<unknown>"`. Variables `Version` and `Revision` default to `Unset` and are intended to be overwritten via linker flags from the Makefile.

## Control Flow, State, and Persistence
There is no control flow or persistence. State is process-global package variables initialized at startup.

## Dependencies and Integration Points
The file has no imports. The Makefile injects values with `-X <pkg>/version.Version=...` and `-X <pkg>/version.Revision=...`.

## Risks and Test Signals
Tests or binaries built without the expected linker flags may retain `<unknown>`. The paired test only checks `Version`, not `Revision`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/version/version.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/version/version_test.go -->
# sources/cloud-native/soci-snapshotter/version/version_test.go

## Purpose
`version_test.go` enforces that the `Version` variable is populated during test/build execution.

## Important APIs, Types, and Functions
`TestVersion` fails if `Version == Unset`.

## Control Flow, State, and Persistence
The test reads package global state only. It has no IO or persistence.

## Dependencies and Integration Points
It depends on Go `testing` and on build tooling injecting version metadata. It is therefore a signal for Makefile or CI linker flag wiring.

## Risks and Test Signals
The test can fail in plain `go test` invocations that do not set `-ldflags`. It does not validate `Revision`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/version/version_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/fbs/zinfo/TarZinfo.go -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/fbs/zinfo/TarZinfo.go

## Purpose
Generated FlatBuffers accessors for the tar zinfo schema used by `compression.TarZinfo`.

## Important APIs, Types, and Functions
`TarZinfo` wraps `flatbuffers.Table`. Root helpers read size-prefixed or normal roots. Accessors expose `Version()`, `SpanSize()`, and `Size()`, with mutators for each. Builder functions include `TarZinfoStart`, `TarZinfoAddVersion`, `TarZinfoAddSpanSize`, `TarZinfoAddSize`, and `TarZinfoEnd`.

## Control Flow, State, and Persistence
The file reads and writes fields within FlatBuffers byte buffers. Persistent representation is the flatbuffer byte layout consumed by `tar_zinfo.go`.

## Dependencies and Integration Points
It depends on `github.com/google/flatbuffers/go` and is generated code. `compression.TarZinfo.Bytes` writes through these builder functions; `newTarZinfo` reads through these accessors.

## Risks and Test Signals
Generated code assumes valid flatbuffer layout and may panic on malformed input; callers recover in `tar_zinfo.go`. Any schema change must regenerate this file and keep serializer/deserializer compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/fbs/zinfo/TarZinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.c -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.c

## Purpose
`gzip_zinfo.c` implements gzip random-access checkpoint generation, extraction, and binary serialization. It is based on zlib `zran.c` but modified for SOCI zTOC span metadata, little-endian storage, gzip header handling, and concatenated gzip streams such as pigz output.

## Important APIs, Types, and Functions
Metadata functions include `pt_index_from_ucmp_offset`, `get_ucomp_off`, `get_comp_off`, `get_blob_size`, `get_max_span_id`, and `has_bits`. Generation functions include `generate_zinfo_from_fp` and `generate_zinfo_from_file`. Extraction functions include `extract_data_from_fp`, `extract_data_from_file`, and `extract_data_from_buffer`. Serialization functions include `zinfo_to_blob` and `blob_to_zinfo`. Internal helpers encode/decode little-endian integers, initialize zlib streams, add checkpoints, and free zinfo memory.

## Control Flow, State, and Persistence
Checkpoint generation inflates the gzip/zlib stream with `inflate(..., Z_BLOCK)`, records access points at block boundaries when uncompressed output has advanced beyond the requested span, captures the 32 KiB sliding dictionary, and stores compressed and uncompressed offsets. It supports concatenated gzip members by resetting inflate state after `Z_STREAM_END` when more input remains. Extraction seeks or slices to the checkpoint, primes partial bits if needed, installs the saved dictionary, skips to the requested uncompressed offset, and inflates into the destination. Blob persistence stores checkpoint count and span size header followed by packed checkpoint records; version 1 compatibility omits the first checkpoint while version 2 includes it.

## Dependencies and Integration Points
The implementation depends on zlib, C stdio/stdlib/string, endian conversion functions, and the public declarations in `gzip_zinfo.h`. Go cgo wrappers in `gzip_zinfo.go` call these functions for zTOC construction and extraction.

## Risks and Test Signals
Memory ownership is manual; Go calls `C.free` on the top-level pointer but this C file also provides `free_zinfo` because the checkpoint list is separately allocated. Incorrect freeing can leak `index->list`. `blob_to_zinfo` returns NULL for mismatched claimed sizes but leaks the allocated `index` on one invalid-size branch. Buffer extraction must avoid reading past the supplied compressed span; it tracks `remaining`, but malformed inputs can return zlib errors. Tests cover malformed blobs, empty data, zero-size reads, gzip header options, pigz concatenated streams, serialization round trips, and extraction across span sizes.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.c -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.go -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.go

## Purpose
`gzip_zinfo.go` is the Go cgo wrapper implementing the `Zinfo` interface for gzip streams using the C checkpoint engine.

## Important APIs, Types, and Functions
`GzipZinfo` wraps `*C.struct_gzip_zinfo`. Constructors `newGzipZinfo` and `newGzipZinfoFromFile` deserialize checkpoint bytes or generate checkpoints from a gzip file. Methods implement `Close`, `Bytes`, `MaxSpanID`, `SpanSize`, offset-to-span mapping, buffer/file extraction, compressed/uncompressed span boundaries, and gzip header verification. Private methods wrap C offset and bit accessors.

## Control Flow, State, and Persistence
The wrapper converts Go byte slices and strings to C pointers, delegates all checkpoint operations to C, and converts return codes into Go errors. `Bytes` allocates a Go byte slice of `get_blob_size` and asks C to serialize into it. Span start subtracts one compressed byte when a checkpoint has pending bits because raw inflate needs the byte before the checkpoint.

## Dependencies and Integration Points
It depends on cgo, `gzip_zinfo.h`, `libz.a`, Go `compress/gzip`, and `unsafe`. It is instantiated through `compression.NewZinfo` and `NewZinfoFromFile`, and consumed by ztoc builders and extraction paths.

## Risks and Test Signals
`Close` frees only `cZinfo` via `C.free`; because C allocates `list` separately, this may leak unless allocation/free behavior is adjusted elsewhere. `ExtractDataFromBuffer` returns a partially filled byte slice alongside an error when C extraction fails. `VerifyHeader` only checks that `gzip.NewReader` accepts the reader. Unit tests cover malformed zinfo bytes and guard clauses for empty buffers and negative/zero sizes; ztoc integration tests cover real extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.h -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.h

## Purpose
`gzip_zinfo.h` declares the C ABI for gzip checkpoint metadata generation, extraction, and serialization used by Go cgo.

## Important APIs, Types, and Functions
It defines `offset_t`, version constants, `WINSIZE`, `PACKED_CHECKPOINT_SIZE`, `BLOB_HEADER_SIZE`, error codes, `struct gzip_checkpoint`, and `struct gzip_zinfo`. Public functions expose metadata lookup, zinfo generation from file, extraction from file or buffer, and zinfo-to-blob/blob-to-zinfo conversion.

## Control Flow, State, and Persistence
The header describes persisted blob layout sizes and in-memory state: a gzip zinfo has encoded version, count, allocated size, checkpoint list, and span size.

## Dependencies and Integration Points
It includes stdbool/stdint/stdio/string and zlib headers. Go cgo includes this header from `gzip_zinfo.go`.

## Risks and Test Signals
The ABI couples Go wrappers to C struct layout and return-code semantics. Any change to blob constants or struct fields affects persisted zTOC compatibility. Tests in Go validate invalid blob size handling and extraction behavior through this ABI.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo.h -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo_test.go -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo_test.go

## Purpose
This test file exercises guard and deserialization behavior for the gzip zinfo wrapper.

## Important APIs, Types, and Functions
`TestNewGzipZinfo` covers nil/empty blobs, undersized headers, inconsistent checkpoint counts, zero-checkpoint v2-like blobs, and v1 compatibility. `TestExtractDataFromBuffer` validates nil/empty buffer errors, negative-size errors, and zero-size success. `TestExtractDataFromFile` validates negative-size and zero-size behavior.

## Control Flow, State, and Persistence
The tests are table-driven and run in parallel. They instantiate `GzipZinfo` directly for guard checks without building real gzip checkpoint state, relying on early returns before C extraction for most cases.

## Dependencies and Integration Points
They depend on the compression package and Go testing. Broader integration with real gzip data is covered in ztoc tests rather than here.

## Risks and Test Signals
The tests do not validate successful extraction from non-empty real gzip buffers or files. They do signal that malformed serialized checkpoint data must return errors rather than over-read, and that zero-byte extraction is a safe fast path.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/gzip_zinfo_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/tar_zinfo.go -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/tar_zinfo.go

## Purpose
`tar_zinfo.go` implements `Zinfo` for uncompressed tar streams. For tar, compressed and uncompressed offsets are identical, so checkpoint metadata only needs version, span size, and archive size.

## Important APIs, Types, and Functions
`TarZinfo` stores `version`, `spanSize`, and `size`. Constructors deserialize from FlatBuffers bytes or stat a tar file. Methods implement the full `Zinfo` interface: serialization, max span calculation, span size, offset-to-span mapping, buffer/file extraction, span boundary calculations, and no-op header verification.

## Control Flow, State, and Persistence
`Bytes` serializes fields with generated FlatBuffers builders. `newTarZinfo` recovers panics from malformed FlatBuffers access. Extraction from buffers slices relative to the requested span start; extraction from files uses `ReadAt`. Span boundaries are simple multiples of `spanSize`, with the final span ending at the supplied file size.

## Dependencies and Integration Points
The file depends on generated zinfo FlatBuffers, `flatbuffers/go`, os/io, and the shared compression types. It is selected by `NewZinfo` for `Uncompressed` and `Unknown` and by `NewZinfoFromFile` for `Uncompressed`.

## Risks and Test Signals
`MaxSpanID` can underflow when `size == 0` or `spanSize == 0`. `ExtractDataFromBuffer` does not bounds-check the computed slice and can panic on invalid offsets or sizes. `VerifyHeader` intentionally accepts all input because unknown/uncompressed is a catch-all. ztoc tests exercise uncompressed tar ztoc generation and extraction.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/tar_zinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/types.go -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/types.go

## Purpose
`types.go` defines shared primitive types and compression algorithm string constants for zTOC compression support.

## Important APIs, Types, and Functions
`Offset` is `int64` and represents file sizes and offsets. `SpanID` is `int32`. Constants are `Gzip`, `Zstd`, `Uncompressed`, and `Unknown`, intentionally matching containerd `DiffCompression` names.

## Control Flow, State, and Persistence
No runtime behavior exists here. These types are persisted indirectly in zTOC structs and FlatBuffers.

## Dependencies and Integration Points
There are no imports. The constants are used by ztoc builders, zinfo factory functions, marshal/unmarshal conversion, tests, and CI-visible behavior for supported compression algorithms.

## Risks and Test Signals
Using plain strings makes unsupported values possible until factory checks run. Zstd is declared but zinfo creation is not implemented in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/types.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/zinfo.go -->
# sources/cloud-native/soci-snapshotter/ztoc/compression/zinfo.go

## Purpose
`zinfo.go` defines the `Zinfo` abstraction for random access into compressed or uncompressed archive data and provides factory functions by compression algorithm.

## Important APIs, Types, and Functions
`Zinfo` includes extraction from buffer/file, close, byte serialization, max span and span size, uncompressed-offset to span mapping, compressed and uncompressed span boundary methods, and header verification. `NewZinfo` deserializes bytes into gzip or tar zinfo. `NewZinfoFromFile` builds zinfo from a file for gzip or uncompressed tar.

## Control Flow, State, and Persistence
The factories switch on algorithm strings. Gzip maps to C-backed checkpoint data. Uncompressed and unknown deserialization map to tar zinfo, while file-based unknown is rejected. Zstd returns a not-implemented error.

## Dependencies and Integration Points
It depends on `fmt` and `io`. ztoc builders and `Ztoc.Zinfo` use these factories as the central compression dispatch point.

## Risks and Test Signals
Unknown is allowed during deserialization but not file construction, which reflects catch-all reading but stricter building. Zstd has a constant and tar provider support for TOC, but no zinfo implementation, so a full zstd zTOC build is unsupported unless a builder is registered externally.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/compression/zinfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionAlgorithm.go -->
# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionAlgorithm.go

## Purpose
Generated FlatBuffers enum support for zTOC compression algorithms.

## Important APIs, Types, and Functions
`CompressionAlgorithm` is an `int8` enum with values for `Gzip`, `Zstd`, and `Uncompressed`. Maps translate enum values to names and names to enum values. `String()` returns the generated name.

## Control Flow, State, and Persistence
The enum value is persisted inside `CompressionInfo` FlatBuffers. Runtime conversion in `ztoc_marshaler.go` lowers the string when reading and performs case-insensitive lookup when writing.

## Dependencies and Integration Points
No external dependencies beyond generated Go code. It integrates with `CompressionInfo.go` and `ztoc_marshaler.go`.

## Risks and Test Signals
Generated names are capitalized, while SOCI compression constants are lowercase, so conversion helpers are required. Unknown algorithms fail during marshaling.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionAlgorithm.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionInfo.go -->
# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionInfo.go

## Purpose
Generated FlatBuffers accessors and builders for the zTOC compression information table.

## Important APIs, Types, and Functions
`CompressionInfo` exposes `CompressionAlgorithm`, `MaxSpanId`, vector access for `SpanDigests`, byte-vector access for `Checkpoints`, mutators for scalar/vector bytes, and builder helpers for each field and vector.

## Control Flow, State, and Persistence
This file reads and writes compressed-span metadata in the zTOC FlatBuffer. Checkpoints persist the algorithm-specific zinfo bytes, and span digests persist per-compressed-span content digests.

## Dependencies and Integration Points
It depends on `flatbuffers/go`. `ztoc_marshaler.go` uses these functions to serialize and deserialize `ztoc.CompressionInfo`.

## Risks and Test Signals
Generated accessors assume valid FlatBuffer layout. The marshaler copies checkpoint bytes out because the generated byte slice aliases the backing FlatBuffer buffer.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/CompressionInfo.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/FileMetadata.go -->
# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/FileMetadata.go

## Purpose
Generated FlatBuffers code for a single file metadata entry in a zTOC.

## Important APIs, Types, and Functions
Accessors expose name, type, uncompressed offset and size, link name, mode, uid/gid, uname/gname, mod time text, device major/minor, and xattr vector entries. Builder helpers add each field and start/end the xattr vector.

## Control Flow, State, and Persistence
This table persists tar-derived metadata. It does not include `TarHeaderOffset`; the deserializer reconstructs that offset by sorting entries and aligning data boundaries.

## Dependencies and Integration Points
It depends on `flatbuffers/go` and `Xattr.go`. `ztoc_marshaler.go` is the primary consumer.

## Risks and Test Signals
Because tar header offsets are reconstructed, malformed or overlapping entries can be detected only after sort/alignment in `flatbufferToTOC`. Generated mutators are available but not used by main code.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/FileMetadata.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/TOC.go -->
# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/TOC.go

## Purpose
Generated FlatBuffers code for the TOC table that contains a vector of file metadata entries.

## Important APIs, Types, and Functions
`TOC.Metadata(obj, j)` initializes a `FileMetadata` at index `j`; `MetadataLength()` returns the vector length. Builder helpers start the TOC, add the metadata vector, start the vector, and end the table.

## Control Flow, State, and Persistence
The table is a container for ordered metadata offsets in a zTOC FlatBuffer. Serialization in `ztoc_marshaler.go` builds the vector in reverse as required by FlatBuffers.

## Dependencies and Integration Points
It depends on `flatbuffers/go` and `FileMetadata.go`. The zTOC root table references this table.

## Risks and Test Signals
Generated accessors rely on valid vector offsets. Marshaler tests check round-trip ordering and invalid overlap detection after deserialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/TOC.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Xattr.go -->
# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Xattr.go

## Purpose
Generated FlatBuffers code for a key/value xattr entry inside file metadata.

## Important APIs, Types, and Functions
`Xattr` exposes `Key()` and `Value()` byte slices plus builder functions to start, add key/value string offsets, and end the table.

## Control Flow, State, and Persistence
Xattrs are persisted as a vector of key/value tables. The marshaler sorts keys before serialization for deterministic output.

## Dependencies and Integration Points
It depends on `flatbuffers/go` and is used by `FileMetadata.go` and `ztoc_marshaler.go`.

## Risks and Test Signals
Only string-like byte values are represented. Deterministic ordering is enforced outside this generated file.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Xattr.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Ztoc.go -->
# sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Ztoc.go

## Purpose
Generated FlatBuffers root table for serialized zTOC documents.

## Important APIs, Types, and Functions
`Ztoc` exposes version, build tool identifier, compressed and uncompressed archive sizes, nested `TOC`, and nested `CompressionInfo`. Builder helpers add all root fields and finish the table.

## Control Flow, State, and Persistence
This root table is the durable zTOC representation returned by `ztoc.Marshal` and consumed by `ztoc.Unmarshal`.

## Dependencies and Integration Points
It depends on `flatbuffers/go`, `TOC.go`, and `CompressionInfo.go`. It is central to zTOC storage in OCI/content-store descriptors.

## Risks and Test Signals
The generated API does not validate semantic consistency between root sizes, TOC entries, and compression info. Higher-level tests validate deterministic digest/size and successful extraction after round trip.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/fbs/ztoc/Ztoc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/tar.go -->
# sources/cloud-native/soci-snapshotter/ztoc/tar.go

## Purpose
`tar.go` contains tar-format helpers used by zTOC metadata calculations.

## Important APIs, Types, and Functions
`TarBlockSize` is 512. `AlignToTarBlock(o)` rounds offsets up to the next tar block boundary. `Xattrs(paxHeaders)` extracts PAX records with prefix `SCHILY.xattr.` and strips the prefix.

## Control Flow, State, and Persistence
No persistent state exists. Offset alignment is arithmetic. Xattr conversion allocates a new map only when PAX headers exist.

## Dependencies and Integration Points
The file depends on `strings` and compression offset types. `toc_builder.go`, `ztoc_marshaler.go`, and `FileMetadata.Xattrs` use these helpers.

## Risks and Test Signals
`Xattrs` returns an empty map if headers exist but no xattr-prefixed key matches; callers may need to distinguish nil from empty. Alignment is critical for reconstructing tar header offsets after FlatBuffer deserialization.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/tar.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/testutil.go -->
# sources/cloud-native/soci-snapshotter/ztoc/testutil.go

## Purpose
`ztoc/testutil.go` supplies a helper that builds a temporary gzip tar, builds a zTOC for it, and returns both the zTOC and an in-memory section reader over the compressed bytes.

## Important APIs, Types, and Functions
`BuildZtocReader(t, ents, compressionLevel, spanSize, opts...)` uses testutil tar builders, writes to a temp file, builds a zTOC with `NewBuilder("test")`, removes the temp file, and returns the section reader.

## Control Flow, State, and Persistence
The function writes a temp archive to disk because the builder needs a filename, then removes it before returning. The returned section reader is backed by the in-memory tar data, so extraction tests do not depend on the temp file after construction.

## Dependencies and Integration Points
It depends on bytes/io/os/testing and `util/testutil`. It is used by ztoc tests for gzip header edge cases.

## Risks and Test Signals
The `testing.T` parameter is unused except for signature consistency. Errors during temp creation or zTOC build are propagated.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/testutil.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/toc_builder.go -->
# sources/cloud-native/soci-snapshotter/ztoc/toc_builder.go

## Purpose
`toc_builder.go` builds the tar table-of-contents portion of a zTOC for gzip, zstd, or uncompressed tar input by walking tar headers and recording file metadata and uncompressed offsets.

## Important APIs, Types, and Functions
`TarProvider` converts a compressed `*os.File` to an `io.Reader`. Providers exist for gzip, zstd, and tar. `TocBuilder` stores algorithm-to-provider registrations. Public methods include `NewTocBuilder`, `RegisterTarProvider`, `CheckCompressionAlgorithm`, and `TocFromFile`. Internal functions `getFileMetadata`, `metadataFromTarReader`, and `getType` do the actual tar traversal and file-type mapping.

## Control Flow, State, and Persistence
`TocFromFile` verifies provider support, opens the file, wraps it through the chosen provider, tracks uncompressed stream position with `ioutils.NewPositionTrackerReader`, and iterates `tar.Reader.Next`. For each header it stores file metadata, current payload offset, size, header offset, link/device/owner/time/PAX data, and updates the next tar header offset by aligning payload end to 512 bytes.

## Dependencies and Integration Points
Dependencies include `archive/tar`, gzip, zstd, `ioutils`, os/io, and compression offset types. `Builder.BuildZtoc` uses this TOC alongside compression info.

## Risks and Test Signals
Unsupported tar entry types fail the build. Provider/algorithm mismatch surfaces as reader errors. The TOC builder supports zstd metadata traversal, but default zTOC builder does not include a zstd zinfo builder. Tests cover gzip, zstd, uncompressed tar, unsupported algorithms, and mismatch failures.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/toc_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/toc_builder_test.go -->
# sources/cloud-native/soci-snapshotter/ztoc/toc_builder_test.go

## Purpose
This test validates TOC building across supported tar providers and failure modes.

## Important APIs, Types, and Functions
`TestTocBuilder` creates deterministic large file entries, defines generators for tar, gzip tar, and zstd tar, registers providers, and runs a table of algorithm cases.

## Control Flow, State, and Persistence
Each case writes a temp archive, calls `builder.TocFromFile`, removes the file, and verifies either expected error or metadata count matching tar entry count.

## Dependencies and Integration Points
The test uses gzip, zstd, os/io, compression constants, and testutil archive generation. It validates `TocBuilder` independently from zinfo construction.

## Risks and Test Signals
The test checks metadata count but not every metadata field, offset, mode, xattr, or file type. It is useful as a provider registration and decompressor compatibility signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/toc_builder_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/zinfo_builder.go -->
# sources/cloud-native/soci-snapshotter/ztoc/zinfo_builder.go

## Purpose
`zinfo_builder.go` builds the compression-info portion of a zTOC, including algorithm-specific checkpoints, compressed archive size, per-span digests, and max span ID.

## Important APIs, Types, and Functions
`ZinfoBuilder` defines `ZinfoFromFile(filename, spanSize)`. `gzipZinfoBuilder` and `tarZinfoBuilder` implement it via `compression.NewZinfoFromFile`. `getPerSpanDigests` computes a digest for each compressed span using `io.NewSectionReader`. `getFileSize` wraps `os.Stat`.

## Control Flow, State, and Persistence
The builder creates a zinfo object, stats file size, iterates span IDs from 0 through max span ID, digests each compressed span boundary reported by the zinfo, serializes checkpoints, and returns a `CompressionInfo`. Checkpoints and span digests become persisted zTOC fields.

## Dependencies and Integration Points
It depends on os/io, `go-digest`, and the compression package. `Builder.BuildZtoc` dispatches to these builders by algorithm.

## Risks and Test Signals
Digest generation trusts zinfo span boundaries. Error messages for digest failures omit the underlying `digest.FromReader` error. Tar and gzip are implemented; zstd requires external registration. ztoc tests validate consistency, extraction, and serialization using these builders.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/zinfo_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc.go -->
# sources/cloud-native/soci-snapshotter/ztoc/ztoc.go

## Purpose
`ztoc.go` defines the core zTOC data model and extraction APIs for retrieving files from compressed or uncompressed layer archives using TOC metadata and zinfo span checkpoints.

## Important APIs, Types, and Functions
Types include `Version`, `Ztoc`, `CompressionInfo`, `TOC`, `FileMetadata`, and `MetadataEntry`. `FileMetadata.FileMode`, `Equal`, and `Xattrs` provide metadata helpers. `TOC.GetMetadataEntry` resolves file entries and follows links. `Ztoc.ExtractFile` fetches relevant compressed spans through an `io.SectionReader`, decompresses the requested range, and returns bytes. `ExtractFromTarGz` extracts directly from a file path through zinfo. `Zinfo` deserializes algorithm-specific checkpoint state.

## Control Flow, State, and Persistence
`ExtractFile` looks up metadata, handles zero-size files, creates zinfo from stored checkpoints, computes span range for the file, reads all compressed spans into one buffer using an errgroup, and asks zinfo to extract the requested uncompressed byte range. `ExtractFromTarGz` performs similar lookup but lets zinfo read from the file. Stored fields include version, build tool identifier, archive sizes, TOC, span digests, checkpoints, max span ID, and compression algorithm.

## Dependencies and Integration Points
Dependencies include tar/os/time/io, `go-digest`, errgroup, and the compression package. This is the central type consumed by builders, marshaling, OCI artifact handling, and tests.

## Risks and Test Signals
`ExtractFile` has a closure capture risk around loop variable `i` in the errgroup; in modern Go range semantics differ from older loop semantics, but this code uses a `for` loop with a reused variable and should be reviewed for concurrent capture correctness. On `zt.Zinfo()` error, `ExtractFile` returns `nil, nil`, which can hide failures. Link resolution recurses without cycle detection. Tests cover gzip and uncompressed extraction across span sizes, gzip header fields, pigz streams, generation consistency, serialization, and invalid unmarshal handling.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_builder.go -->
# sources/cloud-native/soci-snapshotter/ztoc/ztoc_builder.go

## Purpose
`ztoc_builder.go` composes TOC building and zinfo building into a complete zTOC builder with default support for gzip and uncompressed tar.

## Important APIs, Types, and Functions
`Builder` stores a `TocBuilder`, per-algorithm `ZinfoBuilder` map, and build tool identifier. `NewBuilder` registers gzip, uncompressed, and unknown/tar handling. `WithCompression` configures build algorithm, `defaultBuildConfig` defaults to gzip, `BuildZtoc` creates a full zTOC, `RegisterCompressionAlgorithm` adds extensibility, and `CheckCompressionAlgorithm` verifies both TOC and zinfo support.

## Control Flow, State, and Persistence
`BuildZtoc` validates filename, applies options, checks algorithm support, builds compression info first, builds TOC second, and returns a populated `Ztoc` with version `0.9`. Builder state is in-memory registration maps; output state is the zTOC struct that can later be marshaled.

## Dependencies and Integration Points
It depends on the compression package and the local TOC/zinfo builder types. It is used in tests and any SOCI zTOC creation path.

## Risks and Test Signals
The unsupported compression error message says supported gzip even though uncompressed is also registered. Unknown is registered with tar providers/builders, so callers can build unknown as uncompressed-like data. Tests exercise default and explicit compression through ztoc generation suites.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_builder.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler.go -->
# sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler.go

## Purpose
`ztoc_marshaler.go` serializes and deserializes zTOC structs to/from FlatBuffers and returns OCI descriptors for serialized zTOC blobs.

## Important APIs, Types, and Functions
Public APIs are `Marshal(ztoc)` and `Unmarshal(serializedZtoc)`. Internal conversion functions include `flatbufToZtoc`, `flatbufferToTOC`, `ztocToFlatbuffer`, `tocToFlatbuffer`, `prepareMetadataOffset`, `prepareXattrsOffset`, and `compressionAlgorithmToFlatbuf`. `ErrInvalidTOCEntry` signals overlapping/reordered invalid TOC entries during reconstruction.

## Control Flow, State, and Persistence
`Marshal` builds FlatBuffer bytes, creates a digest from those bytes, and returns an `io.Reader` plus descriptor size and digest. `Unmarshal` reads all bytes, recovers panics, parses root metadata, TOC, compression info, span digests, checkpoint bytes, and compression algorithm. TOC deserialization sorts entries by uncompressed offset and reconstructs tar header offsets by 512-byte alignment, rejecting overlap. Serialization sorts xattr keys for deterministic output.

## Dependencies and Integration Points
Dependencies include FlatBuffers generated ztoc code, compression types, `go-digest`, OCI descriptors, bytes/io, sort, strings, and time. It is the persistence boundary between in-memory zTOC and stored OCI/content blobs.

## Risks and Test Signals
`ModTime.UnmarshalText` errors are ignored, which can silently produce zero times for malformed data. `digest.Parse` errors for span digests are ignored. The panic recovery in `ztocToFlatbuffer` returns a generic error without cause. Tests validate positive round trips, invalid overlapping TOCs, deterministic digest/size, invalid format handling, xattr serialization, and extraction after round trip.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler_test.go -->
# sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler_test.go

## Purpose
This test file focuses on TOC FlatBuffer round-trip behavior and validation.

## Important APIs, Types, and Functions
`roundtrip(toc)` serializes a `TOC` to FlatBuffers and immediately deserializes it with `flatbufferToTOC`. `TestPositiveTOCRoundtrip` checks preservation and sorting by uncompressed offset. `TestNegativeTOCRoundtrip` checks overlapping entries return `ErrInvalidTOCEntry`.

## Control Flow, State, and Persistence
The tests build in-memory FlatBuffers only. They model tar header/data placement and use `FileMetadata.Equal` for comparison.

## Dependencies and Integration Points
Dependencies are Go testing/errors, generated FlatBuffers code, and `flatbuffers/go`. The test isolates TOC conversion rather than full zTOC marshal.

## Risks and Test Signals
The negative test has an unused `anyError` variable but still checks `errors.Is(err, expected)`. The tests do not cover xattrs, mod time parse failure, span digests, or compression info; those are covered more broadly in `ztoc_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_marshaler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_test.go -->
# sources/cloud-native/soci-snapshotter/ztoc/ztoc_test.go

## Purpose
`ztoc_test.go` is the main behavior suite for zTOC generation, extraction, serialization, consistency, and benchmarking across gzip and uncompressed tar.

## Important APIs, Types, and Functions
Helpers `buildTarGZ`, `buildTar`, and `tarGenerator` create archives and expected contents. `testZtocs` enumerates gzip and uncompressed variants. Tests include `TestDecompress`, `TestDecompressWithGzipHeaders`, `TestDecompressWithPigz`, `TestZtocGenerationConsistency`, `TestZtocGeneration`, `TestZtocSerialization`, `TestWriteZtoc`, and `TestReadZtocInWrongFormat`. Benchmarks use `BenchmarkZtocGeneration`, `ztocGenBenchmarkFiles`, and `benchmarkZtocGeneration`. `getPositionOfFirstDiffInByteSlice` aids diagnostics.

## Control Flow, State, and Persistence
Tests generate deterministic random tar entries, write temp archives, build zTOCs with varied span sizes, extract every file, compare against original content maps, marshal/unmarshal zTOCs, compare checkpoint bytes and metadata, and validate deterministic descriptor digest/size for a simple fixture. Pigz tests shell out to a real `pigz` binary when installed and skip otherwise.

## Dependencies and Integration Points
Dependencies include gzip, os/exec, io/bytes, reflect, `go-digest`, compression constants, and testutil archive/random helpers. The tests exercise the full path across builders, C gzip zinfo, tar zinfo, marshaler, and extraction APIs.

## Risks and Test Signals
These tests are strong behavioral signals but can be resource-heavy due to multi-megabyte random files and benchmarks. Pigz coverage is optional. `ExtractFromTarGz` is used for uncompressed variants too, despite the name. The suite would catch many regressions in span offsets, gzip header handling, concatenated gzip streams, deterministic checkpoint generation, and FlatBuffer persistence.
<!-- END_FILE_RESEARCH: sources/cloud-native/soci-snapshotter/ztoc/ztoc_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/dependabot.yml -->
# sources/cloud-native/stargz-snapshotter/.github/dependabot.yml

## Purpose
This Dependabot configuration automates dependency update pull requests for Go modules, Docker base images, and GitHub Actions in stargz-snapshotter.

## Important APIs, Types, and Functions
It uses Dependabot config version 2. Go module updates cover `/estargz`, `/ipfs`, `/`, and `/cmd`, run daily, ignore the internal estargz dependency that is manually upgraded on release, and group dependencies into golang-x, google-golang, containerd, opencontainers, k8s, and a catch-all gomod group. Docker and GitHub Actions updates also run daily.

## Control Flow, State, and Persistence
Dependabot reads this YAML in GitHub infrastructure and opens update PRs. There is no runtime code state.

## Dependencies and Integration Points
It integrates with GitHub Dependabot and repository module layout. Grouping reduces PR noise and keeps ecosystem updates coherent.

## Risks and Test Signals
Daily grouped updates can still create broad PRs that require CI capacity. The explicit ignore for estargz protects release-controlled coupling. The catch-all group uses exclude patterns, so missed ecosystem prefixes may group unrelated modules.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/dependabot.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/benchmark.yml -->
# sources/cloud-native/stargz-snapshotter/.github/workflows/benchmark.yml

## Purpose
The benchmark workflow runs hello benchmark scenarios for stargz-snapshotter on pushes to main and pull requests.

## Important APIs, Types, and Functions
The single `hello-bench` job runs on Ubuntu 24.04 with a matrix over `podman` and `containerd`, installs gnuplot and numpy, checks out code, records Azure instance metadata, runs `make benchmark`, and uploads benchmark results as artifacts.

## Control Flow, State, and Persistence
Workflow state is environment variables for result/log directories, registry, benchmark target images, sample count, percentile, and runtime mode. Artifacts persist benchmark output after each run.

## Dependencies and Integration Points
It depends on GitHub Actions, apt packages, `make benchmark`, benchmark scripts, GHCR target images, and Azure metadata availability.

## Risks and Test Signals
Metadata collection assumes Azure IMDS availability on GitHub-hosted runners, which may fail or return unexpected data. `max-parallel: 1` serializes runtime variants for stability. Uploaded artifacts are the main inspection signal.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/benchmark.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/kind-image.yml -->
# sources/cloud-native/stargz-snapshotter/.github/workflows/kind-image.yml

## Purpose
The kind-image workflow builds and optionally pushes multi-arch KinD node images tagged for releases.

## Important APIs, Types, and Functions
It triggers on version tags and pull requests. Steps checkout, compute Docker metadata, login to GHCR except on PRs, set up QEMU and Buildx, and run `docker/build-push-action` for linux/amd64 and linux/arm64.

## Control Flow, State, and Persistence
For PRs, the image is built but not pushed. For tag pushes, credentials from `GITHUB_TOKEN` push images to `ghcr.io/<repository>` with semver `{{version}}-kind` tags.

## Dependencies and Integration Points
It depends on Docker metadata/login/setup-qemu/setup-buildx/build-push GitHub Actions and the repository Dockerfile kind target.

## Risks and Test Signals
Tag patterns only match `v*`; nonstandard release tags will not run. Multi-arch builds rely on QEMU/binfmt. The workflow does not upload local artifacts for PR inspection.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/kind-image.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/nightly.yml -->
# sources/cloud-native/stargz-snapshotter/.github/workflows/nightly.yml

## Purpose
The nightly workflow runs compatibility and integration tests against containerd main and selected runtime environments on a daily schedule and on changes to the workflow.

## Important APIs, Types, and Functions
Global env sets BuildKit and `DOCKER_BUILD_ARGS=--build-arg=CONTAINERD_VERSION=main`. Jobs include integration, optimize, kind, CRI auth, CRI validation with containerd and CRI-O, and k3s. Several jobs install `apache2-utils`; CRI-O installs Docker and disables swap; k3s installs Go, k3d, yq, and htpasswd.

## Control Flow, State, and Persistence
Each job checks out the repo and invokes a Makefile target such as `make integration`, `make test-optimize`, `make test-kind`, `make test-criauth`, `make test-cri-containerd`, `make test-cri-o`, or `make test-k3s`.

## Dependencies and Integration Points
The workflow integrates GitHub Actions with Docker-based integration scripts, containerd main builds, private registry setup, CRI-O, k3s, and related test scripts.

## Risks and Test Signals
Because it tracks containerd main, failures may indicate upstream breakage rather than local changes. Several installation steps fetch scripts/binaries from the network. Job names include a typo in "Varidate" but behavior is unaffected. The nightly signal is broad runtime compatibility.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/nightly.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/release.yml -->
# sources/cloud-native/stargz-snapshotter/.github/workflows/release.yml

## Purpose
The release workflow builds static release tarballs for multiple Linux architectures and creates a draft GitHub release.

## Important APIs, Types, and Functions
It triggers on `v*` tag pushes. The build job matrix covers amd64, arm-v7, arm64, ppc64le, and s390x. It uses Docker target `release-binaries`, gzip-compresses the output tar stream, writes sha256sum files, and uploads artifacts. The release job downloads artifacts and calls `gh release create` with a draft note.

## Control Flow, State, and Persistence
Build artifacts are persisted via upload/download artifact actions. The final draft release is persisted in GitHub releases using `GITHUB_TOKEN`.

## Dependencies and Integration Points
It depends on Docker BuildKit, repository Dockerfile release target, `sha256sum`, GitHub CLI, and artifact actions.

## Risks and Test Signals
Release notes are placeholder `(TBD)`. Asset glob expansion depends on shell behavior and downloaded artifact directory names. `CGO_ENABLED=0` is forced for static binaries.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/release.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/tests.yml -->
# sources/cloud-native/stargz-snapshotter/.github/workflows/tests.yml

## Purpose
The main test workflow runs build, unit tests, linting, integration matrices, runtime validation, IPFS/k3s/podman scenarios, benchmark-adjacent workflow tests, and CNCF/containerd project checks on pushes to main and pull requests.

## Important APIs, Types, and Functions
Jobs include `build`, `test`, `linter`, `integration`, `test-optimize`, `test-kind`, `test-criauth`, `test-cri-containerd`, `test-cri-cri-o`, `test-podman`, `test-k3s`, `test-ipfs`, `test-k3s-argo-workflow`, and `project`. Matrix axes cover containerd release vs main, builtin snapshotter, metadata store, fuse passthrough, fuse manager, transfer service, and CRI-O metadata store. Project checks run `containerd/project-checks`, generated-code validation, patent check, and vendor validation.

## Control Flow, State, and Persistence
Most jobs checkout and invoke Makefile targets. Some jobs install external tools, remove runner disk-heavy directories, collect Azure metadata, or upload artifacts. Matrix exclusions bound incompatible combinations.

## Dependencies and Integration Points
The workflow depends on GitHub Actions, Go setup, golangci-lint action, Docker/apt/network installers, containerd project checks, Makefile targets, and scripts under `script/`.

## Risks and Test Signals
This is a high-signal but expensive workflow. Several steps fetch network scripts or binaries. Disk cleanup in the Argo job is a runner-specific workaround. Matrix exclusions encode important compatibility constraints and should be maintained alongside feature flags.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.github/workflows/tests.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.golangci.yml -->
# sources/cloud-native/stargz-snapshotter/.golangci.yml

## Purpose
This file configures golangci-lint and formatters for stargz-snapshotter.

## Important APIs, Types, and Functions
Config version is 2. Enabled linters include depguard, misspell, revive, and unconvert; errcheck is disabled. Depguard denies migrated containerd packages and points to replacement modules. Exclusions use generated-code lax mode, common presets, specific revive text exclusions, and path exclusions for docs/images/out/script/third_party/builtin/examples. Formatters enable gofmt and goimports with similar exclusions.

## Control Flow, State, and Persistence
golangci-lint consumes the YAML during CI and local lint runs. There is no runtime state.

## Dependencies and Integration Points
It integrates with `.github/workflows/tests.yml` linter job and Makefile `check`.

## Risks and Test Signals
Disabling errcheck and excluding std-error-handling lowers coverage for ignored errors. Depguard helps enforce containerd v2 migration import hygiene.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/.golangci.yml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/Dockerfile -->
# sources/cloud-native/stargz-snapshotter/Dockerfile

## Purpose
The Dockerfile defines a multi-stage build and test image matrix for stargz-snapshotter, including release binaries, containerd variants, podman/CRI-O/stargz-store environments, demo images, and KinD node images.

## Important APIs, Types, and Functions
Top-level build args pin versions for containerd, runc, CNI plugins, nerdctl, Podman, CRI-O, conmon, containers/common, pause images, rootless helpers, and cri-tools. Stages build containerd, builtin containerd with stargz plugin, runc, snapshotter binaries, stargz-store, Podman, CRI-O, conmon, seccomp config, release binaries, containerd bases, podman rootless environment, demo, kind builtin snapshotter, CRI-O stargz-store, and the final KinD image.

## Control Flow, State, and Persistence
Build stages clone upstream repos at pinned versions, compile binaries, copy outputs into later runtime/test stages, install packages and downloaded tools, configure services, and set entrypoints. `release-binaries` is a scratch target containing built binaries for release packaging.

## Dependencies and Integration Points
The Dockerfile is consumed by Makefile targets, CI workflows, release workflow, and runtime integration scripts. It depends heavily on network access to GitHub, package mirrors, container images, and versioned upstream repositories.

## Risks and Test Signals
Many stages build from live upstream source tags and downloaded scripts, so build reproducibility depends on network and tag integrity. Some stages use `apt-get install -y` without cleanup. Architecture args must be correctly supplied for multi-arch builds. The Dockerfile is central to CI signals for containerd, CRI-O, Podman, k3s, KinD, and release artifacts.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/Dockerfile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/Makefile -->
# sources/cloud-native/stargz-snapshotter/Makefile

## Purpose
The Makefile provides build, install, lint, test, integration, generation, vendor validation, and benchmark entry points for stargz-snapshotter.

## Important APIs, Types, and Functions
Variables compute `PREFIX`, package path, `VERSION`, `REVISION`, linker flags, command names, and command output paths. Binary targets build `containerd-stargz-grpc`, `ctr-remote`, `stargz-store`, `stargz-store-helper`, and `stargz-fuse-manager`. Other targets include `check`, `install`, `uninstall`, `clean`, `generate`, `validate-generated`, `vendor`, `test`, `test-root`, `test-all`, integration/runtime test targets, `validate-vendor`, and benchmark-related targets.

## Control Flow, State, and Persistence
Build targets run `go build` in module subdirectories with link-time version injection. Test targets run `go test -race` across root, estargz, cmd, and ipfs modules. Integration targets delegate to scripts. Install/uninstall mutate `CMD_DESTDIR`; clean removes built binaries; vendor validation copies the repo to a temp dir, runs `make vendor`, diffs, and deletes the temp dir.

## Dependencies and Integration Points
The Makefile integrates with Dockerfile stages and GitHub workflows. It depends on git metadata, Go toolchain, golangci-lint, shell scripts, and module layout.

## Risks and Test Signals
`VERSION` and `REVISION` depend on git commands and dirty state, affecting reproducibility. `GO111MODULE=auto` is legacy. `validate-vendor` copies the full repo and can be expensive. CI uses these targets as authoritative behavior gates.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/analyzer.go -->
# sources/cloud-native/stargz-snapshotter/analyzer/analyzer.go

## Purpose
`analyzer.go` analyzes an image by running it under a monitored root filesystem and recording accessed paths into containerd content store as prioritized file records. The resulting digest can be used by optimization tooling.

## Important APIs, Types, and Functions
`Analyze(ctx, client, ref, opts...)` is the primary API. Helpers include `mountImage`, `waitOnSignal`, `waitOnTimeout`, `killTask`, `lazyReadCloser` with `newLazyReadCloser`, and line waiting via `newLineWaiter`, `lineWaiter`, and `registerWriter`. The file also uses analyzer options defined elsewhere, fanotify spawning, pre-container monitor service, and recorder creation.

## Control Flow, State, and Persistence
`Analyze` resolves the image, ensures it is unpacked, mounts its rootfs snapshot into a temp target, optionally records pre-container accessed paths, spawns a fanotify process in a mount namespace, builds an OCI spec with rootfs pointing at the target and mount namespace bound to fanotify, creates a container and task, starts an image recorder, starts fanotify monitoring, runs the task, waits by signal, timeout, or output line, kills the task when needed, closes fanotify, and commits the record to the content store. Persistent outputs are recorder content blobs in containerd content store and temporary snapshots cleaned by deferred functions.

## Dependencies and Integration Points
The file depends on containerd client/image/snapshot/task APIs, containerd ctr signal helpers, mount package, OCI spec helpers, errdefs/log/platforms, fanotify analyzer packages, recorder package, OCI identity, console handling, and runtime-spec. It integrates with snapshotters, content store, Linux mount namespaces, fanotify, and container lifecycle.

## Risks and Test Signals
This is privileged Linux-specific logic with many cleanup paths. Mount preparation deliberately avoids containerd preparing rootfs inside the wrong namespace. Container creation retries ID collisions three times. Terminal mode requires stdin and conflicts with wait-on-signal. `lazyReadCloser` waits for task registration before allowing stdin reads and closes task IO on EOF. Fanotify shutdown uses a mutex-protected flag to distinguish expected EOF. Risks include leaked mounts/snapshots on partial failures, races around fanotify closure, external process namespace behavior, and unbounded wait if signal/timeout configuration is wrong. Test signals likely come from integration tests and analyzer package tests outside this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/stargz-snapshotter/analyzer/analyzer.go -->
