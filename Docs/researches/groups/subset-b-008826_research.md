# Research: subset-b-008826

Grouped research for the TiKV codec, collections, and compact-log-backup files in work item `subset-b-008826`. Each source file section is marker-bounded for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/byte.rs -->
# sources/storage-engines/tikv/components/codec/src/byte.rs

## Purpose
Implements byte-slice codecs used by TiKV binary keys and metadata streams. It has two families: memory-comparable bytes, where encoded byte order preserves or reverses lexical order, and compact bytes, where bytes are prefixed by a varint length and are not order preserving.

## APIs and control flow
`MemComparableByteCodec` encodes source bytes into 8-byte groups followed by a marker byte. Full groups use marker `0xff`; the terminal group is padded with zero bytes and marker `!(padding_size)`. Descending order reuses ascending encoding and bit-flips the encoded region. The main public methods are `encoded_len`, `get_first_encoded_len`, `get_first_encoded_len_desc`, `encode_all`, `encode_all_in_place`, descending variants, and `try_decode_first` variants. Decoding copies each data group, interprets the marker through `Ascending` or `Descending`, validates terminal padding with `libc::memcmp`, and returns read and written byte counts. `MemComparableByteEncoder` and `MemComparableByteDecoder` extend `NumberEncoder` and `BufferReader`.

`CompactByteCodec::get_first_encoded_len` inspects the leading varint length. `CompactByteEncoder` writes varint length plus raw bytes for `NumberEncoder` implementors and `std::fs::File`; `CompactByteDecoder` reads from `NumberDecoder` implementors and from `BufReader<T>`.

## State, dependencies, and integration
The production codec is stateless but mutates caller buffers and cursor positions. It depends on crate `buffer`, `number`, `ErrorInner`, `libc`, `std::io::Read`, and nightly `std::intrinsics::unlikely`. Integration is through the codec prelude and downstream key encoders that need bytewise sort compatibility.

## Risks and test signals
Unsafe pointer copies require non-overlap for out-of-place encoding and destination capacity at least `encoded_len`. Decoders can leave partial junk beyond `written_bytes`; callers must truncate. Compact length casts `i64` varints to `usize`, so corrupt negative lengths would be dangerous if produced externally. Tests cover exact encodings, first-encoded-length detection, compact file IO, in-place flips, overlap-safe decode, invalid padding and EOF, panic conditions, ordering preservation, plus benchmark-only comparisons against older implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/byte.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/convert.rs -->
# sources/storage-engines/tikv/components/codec/src/convert.rs

## Purpose
Provides bit-level conversions that turn signed integers and floating-point values into unsigned integers whose big-endian byte representation is memory-comparable.

## APIs and control flow
`encode_i64_to_comparable_u64` and `decode_comparable_u64_to_i64` XOR the sign bit (`1 << 63`), moving signed integer ordering into unsigned ordering. `encode_f64_to_comparable_u64` reads IEEE bits with `to_bits`; positive values set the sign bit, while negative values are bitwise inverted. `decode_comparable_u64_to_f64` reverses that transform before `from_bits`.

## State, dependencies, and integration
The module is pure and has no persistence or allocation. It is private to the codec crate and is consumed by `number.rs` for `i64` and `f64` ascending and descending encodings. The functions assume normal Rust `f64` bit semantics and preserve bit patterns through reversible transforms.

## Risks and test signals
NaN ordering is not defined by ordinary `PartialOrd`; the paired number codec tests intentionally exclude NaN. Signed zero is represented distinctly, and local tests verify `0.0` and `-0.0` encode differently. Tests also check integer sign-bit mapping and representative decode behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/convert.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/error.rs -->
# sources/storage-engines/tikv/components/codec/src/error.rs

## Purpose
Defines the codec crate error model, result alias, compact error boxing, and integration with TiKV error-code reporting.

## APIs and control flow
`ErrorInner` carries concrete failure categories: `Io(io::Error)`, `BadPadding`, and `KeyNotFound`. Helpers `eof` and `bad_padding` construct common errors used by byte and number decoders. Public `Error` wraps `Box<ErrorInner>` and is transparent for formatting. A direct `From<ErrorInner>` and a specialization-based blanket `From<T: Into<ErrorInner>>` convert lower-level errors into boxed `Error`. `Result<T>` aliases `std::result::Result<T, Error>`.

## State, dependencies, and integration
Errors are value objects with no persistent state. The module depends on `thiserror`, `error_code`, `static_assertions`, and `std::io`. `ErrorCodeExt` maps codec failures to `error_code::codec::{IO,BAD_PADDING,KEY_NOT_FOUND}` so upstream TiKV components can classify failures uniformly.

## Risks and test signals
The crate relies on nightly `min_specialization` for the blanket conversion. `const_assert!(8 == size_of::<Result<()>>())` protects the intended small result layout. There are no local unit tests in this file; behavior is exercised indirectly by decode tests that expect EOF, bad padding, and IO propagation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/error.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/lib.rs -->
# sources/storage-engines/tikv/components/codec/src/lib.rs

## Purpose
Crate root for TiKV's low-level codec component. It exposes buffer, byte, and number codecs plus the common error type and prelude.

## APIs and control flow
The root enables nightly features needed by child modules: `test` under cfg(test), `core_intrinsics`, and `min_specialization`. It imports `tikv_alloc`, declares public modules `buffer`, `byte`, and `number`, keeps `convert` and `error` private, and exports `Error`, `ErrorInner`, and `Result`.

The `prelude` re-exports `BufferReader`, `BufferWriter`, byte encoder and decoder traits, compact-byte traits, and number encoder and decoder traits. Downstream code can import the prelude to gain extension methods on buffers and cursors.

## State, dependencies, and integration
This file owns no runtime state. Its integration role is API shaping: it hides conversion internals but exposes codec extension traits. `tikv_alloc` is retained as an extern crate for allocator integration even if not referenced directly here.

## Risks and test signals
The crate is tied to nightly Rust features. Any downstream module expecting the prelude depends on these exact re-export names. There are no direct tests in this file; child module tests validate that the exposed traits work for `Vec`, slices, cursors, and file readers.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/number.rs -->
# sources/storage-engines/tikv/components/codec/src/number.rs

## Purpose
Implements primitive numeric encoding and decoding for fixed-width memory-comparable values, little-endian non-comparable values, and protobuf-style varints. Extension traits connect those routines to TiKV buffer readers and writers.

## APIs and control flow
`NumberCodec` includes direct encode/decode routines for `u8`, `u16`, `u32`, `u64`, descending `u64`, comparable `i64` and `f64`, little-endian `u16/i16/u32/i32/f32/u64/i64/f64`, and varint `u64/i64`. Comparable fixed-width values use big-endian bytes; descending values invert the comparable `u64`; signed and float forms delegate to `convert.rs`. Varint encoding writes 7-bit groups with continuation bits. Varint decoding has a fast path for buffers at least 10 bytes and a bounded slow path for shorter buffers; `get_first_encoded_var_int_len` returns the complete prefix length or the available incomplete length.

`NumberDecoder` extends `BufferReader` with methods that validate remaining bytes before advancing. `NumberEncoder` extends `BufferWriter` with symmetric writers; fixed-width writers require exact remaining capacity, while varint writers require reservation of 10 bytes but advance by actual encoded length.

## State, dependencies, and integration
The module is stateless except for mutating buffer cursors. It depends on `byteorder`, crate `buffer`, crate errors, and conversion helpers. It is a central dependency of byte compact encoding and any TiKV binary format using the codec prelude.

## Risks and test signals
Many routines use unsafe pointer reads/writes and rely on prior capacity checks. Varint decoding accepts the 10th byte with only one payload bit, matching u64 width but without explicit validation of overlong encodings. Tests are extensive: sample generation covers numeric boundaries, ordering checks verify memory-comparable encodings, cursor tests verify no mutation on insufficient space, varint tests compare protobuf output and incomplete-buffer behavior, and benches compare TiKV, byteorder, bytes, protobuf, and older implementations.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/codec/src/number.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/collections/Cargo.toml -->
# sources/storage-engines/tikv/components/collections/Cargo.toml

## Purpose
Cargo manifest for TiKV's lightweight `collections` component, which centralizes hash collection aliases using a faster hasher.

## APIs and control flow
The package is named `collections`, version `0.1.0`, edition 2021, Apache-2.0 licensed, and `publish = false`. There is no build script, binary target, feature definition, or dev dependency here.

## State, dependencies, and integration
Dependencies are `fxhash = "0.2.1"` and workspace `tikv_alloc`. `fxhash` backs the component's type aliases, while `tikv_alloc` keeps allocation behavior aligned with the broader TiKV workspace. The manifest integrates as a private workspace crate.

## Risks and test signals
FxHash is optimized for speed, not adversarial hash resistance; callers should not use this alias for untrusted attacker-controlled key sets without considering collision risks. The manifest itself has no tests. Validation comes from compiling dependents that import `collections::{HashMap,HashSet}`.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/collections/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/collections/src/lib.rs -->
# sources/storage-engines/tikv/components/collections/src/lib.rs

## Purpose
Exports TiKV-standard hash map and hash set aliases backed by `fxhash::FxHasher`, plus a convenience constructor for pre-sized hash sets.

## APIs and control flow
`HashMap<K,V>` aliases `std::collections::HashMap<K,V,BuildHasherDefault<fxhash::FxHasher>>`. `HashSet<T>` aliases the matching standard set. `HashMapEntry` re-exports `std::collections::hash_map::Entry`. `hash_set_with_capacity` creates a `HashSet` with requested capacity and `FxBuildHasher::default()`.

## State, dependencies, and integration
The module has no global state. It imports `tikv_alloc` for workspace allocation integration and depends on `fxhash`. It is designed as an API convenience crate: downstream modules can choose the TiKV fast-hash defaults without repeating verbose hasher types.

## Risks and test signals
Fast non-cryptographic hashing can be a poor fit for untrusted inputs. Type aliases hide the hasher choice, so changing this file would affect performance and determinism across all users. No local tests exist; compile-time usage by dependents is the main signal.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/collections/src/lib.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/Cargo.toml -->
# sources/storage-engines/tikv/components/compact-log-backup/Cargo.toml

## Purpose
Manifest for the `compact-log-backup` workspace crate, which compacts log-backup artifacts into SST outputs and metadata migrations.

## APIs and control flow
The package is private, edition 2021, and exposes a `failpoints` feature forwarding to `fail/failpoints`. The dependency set shows the crate is asynchronous and storage-heavy: it uses external storage, cloud IO, backup-stream types, Rocks engine traits, protobuf metadata, encryption, zstd/async compression, Tokio, futures, tracing, Prometheus, and TiKV utility crates.

## State, dependencies, and integration
Runtime state is not in the manifest, but dependency wiring indicates integration with Rocks SST creation (`engine_rocks`, `engine_traits`), BR protobufs (`kvproto`), external storage, backup stream metadata, and TiKV transaction/key codecs. `zstd` is noted as test-utils-only while still in normal dependencies; `pprof`, `tempfile`, and `test_util` are dev dependencies.

## Risks and test signals
The crate depends on many workspace crates, so feature or version drift can affect compilation broadly. The `tokio` feature set includes runtime, macros, time, sync, and signal support, which implies async execution paths must be tested under runtime context. Manifest validation is compile-time plus crate test suites.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/cache.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/cache.rs

## Purpose
Implements a bounded, sharded in-memory cache for raw physical log files. It lets multiple logical log spans share one downloaded physical object and returns zero-copy `Bytes` slices to compaction workers.

## APIs and control flow
`PhysicalFileCache::new` sets capacity, reservation counter, notify channel, and 256 mutex-protected shards. `register_physical_file` reserves capacity and records reference counts, returning `Registered`, `Full(wait)`, or `Bypass`. `load_part` loops over `cache_decision`: ready returns a slice, wait awaits another downloader, bypass asks caller to read directly, and download loads the full physical file then publishes it. `DownloadGuard` clears `loading` and notifies waiters if a download future is cancelled. `PhysicalFileCacheRefGuard` drops physical-file refs on `Drop`; when refs hit zero, entries are removed and reserved capacity is released.

## State, dependencies, and integration
State is entirely in-memory: per-shard `HashMap<Chars, CacheEntry>`, atomic `reserved_bytes`, notify objects, content bytes, loading flags, and remaining refs. It depends on `external_storage`, `cloud::blob::read_to_end`, `bytes`, `parking_lot`, Tokio notify futures, protobuf `Chars`, and compaction `Input`. It integrates with cached subcompaction collection and `Source` loading.

## Risks and test signals
Reference accounting must match logical input consumption; early drops can release reservations while slices still live, although `Bytes` keeps allocation alive. Full-file downloads can allocate `physical_size` capacity and require valid offset/length ranges. Tests cover cancelled-download loading cleanup and reservation release after both cached parts are consumed.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/collector.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/collector.rs

## Purpose
Transforms streams of backup log metadata into executable `Subcompaction` groups. It supports ordinary grouping by logical files and cache-aware grouping by physical-file cache windows.

## APIs and control flow
`CollectSubcompaction<S>` wraps a `Stream<Item = Result<LogFile>>`. It filters metadata/out-of-range files, groups files by `SubcompactionCollectKey`, emits a group when accumulated size exceeds `subcompaction_size_threshold`, and flushes pending undersized groups at stream end. `CollectCachedSubcompaction<S>` consumes `PhysicalLogFile` streams, registers physical files in `PhysicalFileCache`, defers a file when capacity is full, forces pending groups into a ready queue, waits for capacity, and resumes. Ready groups are sorted by input count, size, region, CF, file type, meta flag, and table id; matching pending groups can be merged before yielding when under threshold.

`CollectSubcompactionConfig` carries `compact_shift_from_ts`, `compact_from_ts`, `compact_to_ts`, and size threshold. `take_statistic` drains collection counters.

## State, dependencies, and integration
Collector state is `HashMap<SubcompactionCollectKey, UnformedSubcompaction>`, delayed final groups, cache wait futures, deferred physical files, ready queues, and statistics. It depends on Tokio streams, `engine_traits::{CF_DEFAULT,CfName}`, `PhysicalFileCache`, log storage types, and error tracing. The output feeds `SubcompactionExec`.

## Risks and test signals
Timestamp filtering uses `compact_shift_from_ts` only for default CF, which is subtle. Meta files are excluded. Cache mode must not deadlock when capacity is full; it relies on ref guards in execution to release capacity. Tests cover normal grouping, cache full waits and forced drains, pending merge thresholds, error propagation, timestamp filtering, group keys, default-CF shift bounds, and region epoch hint aggregation.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/collector.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/exec.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/exec.rs

## Purpose
Executes one `Subcompaction`: loads input log records, sorts and deduplicates them, writes an in-memory SST, uploads the SST artifact, and returns metadata and statistics.

## APIs and control flow
`SubcompactionExecArg` constructs `SubcompactionExec` with output storage, optional Rocks engine, optional output prefix, and optional physical-file cache. `SubcompactExt` controls load concurrency and SST compression. `run` initializes expected checksum/key/size totals from inputs, loads records concurrently, sorts and dedups via `process_input`, adjusts checksum diff for removed duplicates, writes an SST under `out_prefix/outputs`, uploads it with SHA-256, and returns `SubcompactionResult`.

Conflict resolution is intentionally narrow. Identical records dedup. Different records in non-write CF panic. Write-CF conflicts are resolved only for collapsed rollback versus put, or protected rollback precedence; otherwise execution panics. `write_sst` decodes encoded keys to raw start/end metadata, makes end key exclusive by appending `0`, writes data-key-prefixed entries, and records CRC64, versions, sizes, and counts.

## State, dependencies, and integration
Mutable state includes `Source`, external output storage, cooperative yielding, output prefix, optional DB, and load/compact statistics. It depends on Rocks SST traits, external storage, `Sha256Reader`, TiKV key/transaction codecs, retry utilities, metrics, and `PhysicalFileCache`. Its output metadata is consumed by compaction metadata migration writers and checkpoint hooks.

## Risks and test signals
Empty compactions return no SST metadata. Conflict handling can panic on unexpected duplicated values. Output names use UUIDs and timestamp ranges, so uploads are persistent external side effects. Tests compact one or many files, deduplicate duplicates, preserve region hints, verify range elision, fail checksum under failpoints, and exercise write-CF conflict-resolution rules and panic paths.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/exec.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/meta.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/meta.rs

## Purpose
Builds protobuf metadata for subcompactions and derives migration edits that identify obsolete physical or logical log files after compaction.

## APIs and control flow
`SubcompactionResult::verify_checksum` XORs output SST CRCs and totals output bytes and key counts, comparing them with expected values. `Subcompaction::crc64` hashes input spans and subcompaction identity fields. `to_pb_meta` emits `LogFileSubcompactionMeta`, and `inputs_to_pb` groups spans by physical file. `singleton` and `of_many` create subcompactions from log files for tests and utility paths.

`CompactionRunInfoBuilder` accumulates origin subcompaction spans, updates aggregate compaction timestamps and artifact hash, normalizes spans, scans `StreamMetaStorage`, and writes a `Migration` through `MigrationStorageWrapper`. `expiring` compares compacted spans with each meta file's physical files: fully covered files become deletable physical files; partial coverage becomes `DeleteSpansOfFile`; all-covered metadata can set `destruct_self`; data-only coverage controls `all_data_files_compacted`.

## State, dependencies, and integration
State is a span map keyed by physical file bytes plus a protobuf `LogFileCompaction`. Persistence occurs when `write_migration` writes migration edits to external storage. Dependencies include protobuf BR types, external storage, futures streams, shard config, storage metadata loaders, and compaction structs.

## Risks and test signals
Span normalization is required before deletion derivation; duplicate or unsorted spans could otherwise confuse full-cover checks. `full_covers` asserts compacted span length does not exceed physical file size. Metadata and data files have different deletion semantics. Tests cover partial compaction, full physical-file deletion, whole-meta destruction, multi-meta edits, and aggregate timestamp fields.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/meta.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/mod.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/compaction/mod.rs

## Purpose
Defines core compaction data structures and module boundaries for collection, execution, and metadata generation.

## APIs and control flow
`Input` records a logical input span plus physical size, compression, CRC, logical KV size, and entry count. `SubcompactionCollectKey` groups files by CF, region, file type, meta flag, and table id. `Subcompaction` holds inputs, size, timestamp range, compact bounds, min/max keys, and region epoch hints; its private `merge` combines same-key groups. `EpochHint` preserves region range and epoch information. `SubcompactionResult` pairs the origin with protobuf output metadata, expected checksum/key/size totals, and load/compact statistics.

`UnformedSubcompaction` is the collector's mutable accumulator. `by_file`, `add_file`, and `form` aggregate file state into a concrete `Subcompaction`. `to_input` converts storage `LogFile` metadata into executable input.

## State, dependencies, and integration
This module owns no persistence directly. It depends on `kvproto::brpb`, bytes, display derivation, storage log metadata, statistics types, and collector config. It re-exports child modules `collector`, `exec`, and `meta`, and constants `SST_OUT_REL` and `META_OUT_REL` define output subdirectories used by executor and checkpoint logic.

## Risks and test signals
`Subcompaction::merge` uses debug assertions for matching keys and compaction bounds, so release builds rely on callers to merge compatible groups. `of_many` panics on empty input and asserts all files have the same collect key. Tests live in child modules and validate grouping, execution, metadata, and epoch hint behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/compaction/mod.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/errors.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/errors.rs

## Purpose
Defines the compact-log-backup error wrapper, error categories, annotation helpers, and conversion utilities used across async compaction code.

## APIs and control flow
`Error` stores an `ErrorKind`, a notes string, and caller frames captured with `#[track_caller]`. `Display` prints the kind, optional note, and top caller location. `ErrorKind` wraps IO, protobuf, engine, codec, or uncategorized string failures. `From<T: Into<ErrorKind>> for Error` captures the current frame. `TraceResultExt` adds `trace_err` and `annotate` to crate `Result<T>`; these attach frames or replace notes before returning errors. `OtherErrExt::adapt_err` converts arbitrary displayable errors into `Other`. `Error::message` appends notes.

## State, dependencies, and integration
Errors are transient values but carry a stack-like vector of source locations for diagnostics. The module depends on `thiserror`, `tikv_util::codec`, `engine_traits`, protobuf, and `std::panic::Location`. Most compact-log-backup modules import `Result`, `TraceResultExt`, or `OtherErrExt`.

## Risks and test signals
`annotate` overwrites previous notes instead of appending through `message`, which may hide earlier context. Capturing static locations increases error size but improves traces. There are no direct tests here; coverage is indirect through modules that convert IO, protobuf, engine, codec, and generic errors.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/errors.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/checkpoint.rs -->
# sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/checkpoint.rs

## Purpose
Implements an execution hook that skips subcompactions already recorded in checkpoint metadata under the compaction metadata output directory.

## APIs and control flow
`Checkpoint` owns a `HashSet<CheckpointedSubcompaction>`. `load` reads existing checkpointed subcompactions from external storage and extends the set while logging elapsed time. As an `ExecHooks` implementor, `before_execution_started` computes `"{out_prefix}/metas"` using `META_OUT_REL` and loads checkpoints. `before_a_subcompaction_start` converts the pending subcompaction into a checkpoint key; if present, it logs and calls `cx.skip(SkipReason::AlreadyDone)`.

## State, dependencies, and integration
State is in-memory per execution run, sourced from persisted checkpoint metadata in external storage. The hook depends on `ExternalStorage`, checkpoint save/load helpers, compaction `META_OUT_REL`, execution hook contexts, TiKV logging, and timing utilities. It integrates with the executor scheduler through the `ExecHooks` trait.

## Risks and test signals
Correctness depends on `CheckpointedSubcompaction::from_subcompaction` matching the format written by the save-meta path. Loading uses `extend`, so repeated calls accumulate rather than reset. If checkpoint metadata is stale or corrupt, valid work may be skipped or load may fail before execution. No local tests are present in this file; validation is likely covered by broader execution-hook or checkpoint integration tests.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/compact-log-backup/src/exec_hooks/checkpoint.rs -->
