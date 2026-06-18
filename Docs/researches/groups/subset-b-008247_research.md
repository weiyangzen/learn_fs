<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/endpoints.rs -->
# sources/object-store/rustfs/crates/ecstore/src/endpoints.rs

## Purpose
Builds, validates, and classifies RustFS storage endpoints from disk layout input. It turns CLI volume expressions into pool/set/disk-indexed `Endpoint` values, marks which endpoints are local to the current server, determines `SetupType`, exposes peer/node views for distributed erasure, and enforces local disk safety checks before erasure pools are accepted.

## Important APIs, types, and functions
`SetupType` distinguishes unknown, filesystem, single-drive erasure, local erasure, and distributed erasure setups. `Node` is the cluster-facing view of a peer URL, pool membership, locality, and grid host. `Endpoints` wraps `Vec<Endpoint>` with conversion helpers, duplicate detection, same-type/same-scheme validation, and accessor methods. `PoolEndpointList::create_pool_endpoints` is the central async constructor that consumes `DisksLayout`, assigns pool/set/disk indexes, resolves hosts, normalizes ports, validates path conflicts, checks local physical disk independence, and computes setup type. `EndpointServerPools` is the public aggregate with `from_volumes`, `create_server_endpoints`, `add`, `get_nodes`, `hosts_sorted`, `peers`, and `find_grid_hosts_from_peer`. `validate_local_physical_disk_independence` and `validate_local_cross_device_mounts` enforce local topology invariants, with diagnostic reporting through `LocalDiskValidationDiagnostic`.

## Control flow
`EndpointServerPools::from_volumes` first asks `DisksLayout::from_volumes` to expand volume arguments, then delegates to `create_server_endpoints`. `create_server_endpoints` rejects empty layouts, calls `PoolEndpointList::create_pool_endpoints`, then wraps each pool with legacy/set/drive/cmd/platform metadata.

`PoolEndpointList::create_pool_endpoints` validates `server_addr` with `check_local_server_addr`. A single-drive layout is handled as `ErasureSD`: the endpoint must be path-style, is marked local, receives pool/set/disk index `0`, and returns immediately. Multi-endpoint layouts are expanded per pool and set with `Endpoints::try_from`, then each endpoint receives its pool, set, and disk indexes. After `update_is_local`, the function performs three URL/path consistency passes per pool: it resolves endpoint hosts with `get_host_ip` and rejects the same path served by the same host address on multiple ports; it rejects duplicate local file paths under different local addresses; and it rejects all-local URL layouts that use multiple local hostnames/IPs for one port. Missing URL ports are filled from the server address, while local endpoints on a different explicit port are reclassified as remote. Finally, local disk topology validation runs and setup type is derived from endpoint type plus unique host-port cardinality.

`Endpoints::try_from` is a low-level parser. It converts each string with `Endpoint::try_from`, requires all endpoints to share `EndpointType` and URL scheme, and rejects duplicates by `Endpoint::to_string`. Cluster views are derived later: `get_nodes` groups endpoints by `host_port`, merges pool indexes, then sorts by `grid_host`; `peers` collects URL endpoint host-ports and chooses the local peer matching `global_rustfs_port`; `hosts_sorted` sorts peers and converts non-local peers into `XHost`.

## State and persistence behavior
This module does not persist state itself, but it defines the in-memory topology passed into the storage layer. It mutates endpoint metadata in place: `is_local`, URL port, pool index, set index, and disk index become part of subsequent pool construction, peer routing, and disk placement behavior. `PoolEndpoints` also stores `cmd_line`, `legacy`, `set_count`, `drives_per_set`, and platform strings, which can become observable in diagnostics or cluster metadata. Environment variables affect validation state: `RUSTFS_UNSAFE_BYPASS_DISK_CHECK` is the canonical bypass for physical disk independence, while `MINIO_CI` is accepted as a legacy alias.

## Dependencies and integration points
Depends on `crate::disk::endpoint::{Endpoint, EndpointType}` for parsing and endpoint methods, `crate::disks_layout::DisksLayout` for expanded pool/set layouts, and `crate::global::global_rustfs_port` for local peer selection. It uses `rustfs_utils` host helpers (`check_local_server_addr`, `get_host_ip`, `is_local_host`, `XHost`), filesystem helpers (`canonicalize`, `os::get_physical_device_ids`, `os::check_cross_device_mounts`), and environment helpers. Non-Windows disk diagnostics use `rustix::fs::stat`; Windows has a fallback path resolution branch for non-standard volumes. The module integrates with tracing for parse/resolve diagnostics and warnings.

## Risks and test signals
Topology validation is safety-critical: bad localness detection or host resolution can misclassify distributed endpoints as local or remote, and disk independence bypass can allow multiple erasure endpoints on one physical disk. The same-path/same-host/different-port rejection uses resolved IP intersections, so DNS instability and cache behavior matter. Nonexistent local paths are excluded from physical disk validation on non-Windows, which is convenient during parsing but can postpone real safety failures. `peers` only sets `local` when the endpoint port equals `global_rustfs_port`, so mismatched global port configuration affects internode routing.

Tests cover endpoint parsing errors, mixed style/scheme rejection, duplicate paths, single-drive path-only enforcement, distributed/local setup classification, automatic port insertion, localhost path conflict cases, ellipsis layout validity, and Linux physical-disk checks with both canonical and legacy bypass environment variables. Useful additional signals would include DNS multi-A-record conflict cases, IPv6/IPv4 mixed local aliases beyond the existing local-hostname case, and Windows fallback validation.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/endpoints.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/bitrot.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/bitrot.rs

## Purpose
Provides the per-shard bitrot framing layer used by erasure-coded reads, writes, heals, and tests. Each shard block is stored as an optional hash prefix followed by shard bytes; readers verify the prefix before returning data, and writers compute and emit the prefix atomically with the data where possible.

## Important APIs, types, and functions
`BitrotReader<R>` wraps an async reader with `HashAlgorithm`, `shard_size`, scratch buffers, `skip_verify`, and an id used in mismatch logging. `BitrotReader::read` reads one framed shard block into caller-provided output and validates the hash unless disabled. `BitrotWriter<W>` wraps an async writer and writes one framed shard block at a time; `write` rejects oversized data and marks the writer finished after a short final shard. `write_all_vectored` is the low-level hash+data vectored write loop. `bitrot_shard_file_size` computes on-disk shard length including hash prefixes for HighwayHash S variants. `bitrot_verify` verifies a full shard stream against expected sizing. `CustomWriter` abstracts in-memory inline buffers and boxed async writers. `BitrotWriterWrapper` is the concrete writer wrapper used by encode/heal APIs, preserving inline-buffer extraction for tests and in-memory paths.

## Control flow
`BitrotWriter::write` returns immediately for empty input, rejects calls after a previous short write, verifies `buf.len() <= shard_size`, and marks `finished` if the block is shorter than a full shard. If the selected hash algorithm has a nonzero digest size, it hashes the data and writes hash plus data through `write_all_vectored`; otherwise it writes only data. `shutdown` flushes and shuts down the inner writer.

`BitrotReader::read` rejects output buffers larger than `shard_size`, reads the hash prefix exactly when the algorithm has a digest, then reads up to the requested output length. On hash mismatch it logs the reader id, read length, and requested length and returns `InvalidData`; otherwise it returns the number of bytes actually read. `bitrot_verify` compares the expected file size to `bitrot_shard_file_size`, then walks hash/data blocks, shrinking the final shard read to the remaining byte count and comparing each computed hash with the stored prefix.

`CustomWriter` implements `AsyncWrite` directly. Inline buffers append bytes to a `Vec<u8>` and report full writes, including vectored writes; `Other` delegates all write, flush, shutdown, and vectored behavior to the boxed writer. `BitrotWriterWrapper` owns a `BitrotWriter<CustomWriter>` and exposes `write`, `shutdown`, and `into_inline_data`.

## State and persistence behavior
The persistent format is a repeated sequence of `hash || shard_data` for algorithms with nonzero digest size, or raw shard data for `HashAlgorithm::None`. `bitrot_shard_file_size` models that format for the HighwayHash256S and HighwayHash256SLegacy variants. `BitrotWriter` enforces an append pattern where a short shard is terminal; this prevents writing more blocks after the last partial shard. `BitrotReader` is stateful over the underlying stream and consumes exactly one framed block per `read` call.

## Dependencies and integration points
Uses `bytes::Bytes`, `rustfs_utils::HashAlgorithm`, `tokio::io::{AsyncRead, AsyncWrite}`, `pin_project_lite`, `uuid::Uuid`, and `tracing`. `BitrotReader` is consumed by `decode::ParallelReader` and `heal`; `BitrotWriterWrapper` is consumed by `encode::MultiWriter` and `heal`. `CustomWriter::InlineBuffer` is an important test/in-memory integration point for heal and encode fast paths.

## Risks and test signals
The reader reads until EOF or the requested output length, so callers must pass the correct shard size for the current block, especially for final partial shards. `bitrot_verify` takes a `_want` parameter marked unused, suggesting an incomplete or legacy API contract. Size accounting differs by hash algorithm, so mismatching `HashAlgorithm` during read/write will desynchronize the stream. Vectored writes must handle partial writes correctly; `write_all_vectored` explicitly tracks hash and data offsets.

Tests cover hash read/write round trips, hash mismatch detection, no-hash operation, shutdown flush/shutdown counts, and vectored hash+data writes. Additional tests could exercise partial vectored writes and `bitrot_verify` with multi-block final-shard boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/bitrot.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/decode.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/decode.rs

## Purpose
Implements erasure-coded reads from bitrot-protected shard streams. It reads shard blocks in parallel, tolerates missing or corrupt shards up to the erasure limit, reconstructs missing data shards, and writes a requested byte range into an async output writer.

## Important APIs, types, and functions
`ParallelReader<R>` owns a vector of optional `BitrotReader<R>` values plus shard offset, shard size, shard-file size, data shard count, and total shard count. `ParallelReader::read` reads one erasure block across readers until it has enough successful shards. `ParallelReader::can_decode` checks read quorum. `get_data_block_len` sums available data-shard bytes. `write_data_blocks` writes a range from decoded data shards to the target writer. `Erasure::decode` is the public async read path for a requested `offset`, `length`, and `total_length`.

## Control flow
`Erasure::decode` first validates that the reader count equals `data_shards + parity_shards`, rejects `offset + length` overflow or ranges past `total_length`, and returns immediately for zero length. It constructs a `ParallelReader` positioned to the start block. The loop spans `start = offset / block_size` through `end = (offset + length - 1) / block_size`; each iteration computes the in-block offset and length for start, middle, and final blocks.

For each block, `ParallelReader::read` computes the current shard block length from `offset`, `shard_size`, and `shard_file_size`, then creates one future per reader. Missing readers immediately return `FileNotFound`; present readers call `BitrotReader::read`. It initially polls only `data_shards` futures and starts additional shard reads only when an earlier one fails, stopping once it has `data_shards` successes. `Erasure::decode` records the first reducible `FileNotFound` or `FileCorrupt`, fails with `ErasureReadQuorum` if fewer than `data_shards` shards are available, reconstructs with `decode_data`, and calls `write_data_blocks` to emit the requested range. If no hard error occurred but fewer bytes than requested were written, it returns `LessData`.

`write_data_blocks` validates that the data-shard slice is long enough, checks `offset + length` for overflow, ensures the available data block length covers the requested range, then skips whole shards until the offset lands and writes the requested slices with `write_all`.

## State and persistence behavior
This module does not write persistent state. It interprets the persistent shard layout established by `BitrotWriter` and `Erasure::shard_file_size`. `ParallelReader` holds stream readers and advances them one framed shard block per `read` call; the production caller must seek/open readers at the correct shard-file offset before constructing it. Error state is returned per block as a vector of optional disk errors and summarized by `reduce_errs`.

## Dependencies and integration points
Depends on `crate::disk::error::Error`, `crate::disk::error_reduce::reduce_errs`, `BitrotReader`, and `Erasure`. It uses `futures::stream::FuturesUnordered` for bounded parallel reads, `tokio::io::AsyncRead/AsyncWrite`, and tracing for error logging. It calls `Erasure::decode_data`, so its parity/backend behavior is controlled by `erasure.rs`.

## Risks and test signals
Because `ParallelReader` stops after enough successful reads, errors on later shards may remain unobserved in healthy reads; this is good for latency but can hide latent corruption until those shards are needed. `ParallelReader::offset` is initialized from the starting block but is not incremented inside `read`, so repeated calls rely on reader stream advancement for data and use the same final-block sizing calculation; this works for normal full-size middle blocks but is a risk area for edge cases near shard-file tails. Range math is guarded against overflow, but callers must ensure readers are pre-positioned consistently with the requested offset.

Tests cover ranged reads across block boundaries, compressed stream preservation behind the `rio-v2` feature, write-range helper errors, normal parallel reads, offline disks, and bitrot-corrupt disks. The ranged-read regression test explicitly documents that `Erasure::decode` does not seek readers itself.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/decode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/encode.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/encode.rs

## Purpose
Implements erasure-coded writes from an async reader into bitrot-protected shard writers. It handles Reed-Solomon encoding, bounded producer/consumer buffering, write quorum enforcement, metrics for in-flight encoded data, and small-object fast paths.

## Important APIs, types, and functions
`MultiWriter<'a>` coordinates a mutable slice of optional `BitrotWriterWrapper` values, tracks per-writer errors, and enforces a write quorum for writes and shutdown. `MultiWriter::write_shard`, `write`, `shutdown_writer`, and `shutdown` are the core write fanout. `Erasure::encode` is the main streaming pipeline. `Erasure::encode_inline_small` and `encode_single_block_non_inline` use `encode_small_direct` to avoid the task/channel pipeline for small data. `encode_channel_capacity`, `queued_block_bytes`, and `drain_queued_inflight_bytes` bound and clean up encode buffering. Formatting helpers turn `WriteQuorumFailureSummary` into stable error and metric labels.

## Control flow
`Erasure::encode` rejects zero `block_size`, computes expanded encoded block bytes as `shard_size * total_shard_count`, reads `RUSTFS_ERASURE_ENCODE_MAX_INFLIGHT_BYTES` with a 32 MiB default, and creates a bounded MPSC channel capped at 32 encoded blocks. A spawned producer task repeatedly reads full blocks with `rustfs_utils::read_full_or_eof`, encodes each block on `tokio::task::spawn_blocking`, adds encoded byte count to `rustfs_io_metrics`, and sends the encoded block vector to the consumer. It maps checksum-mismatch-flavored unexpected EOFs to `InvalidData`.

The consumer wraps writers in `MultiWriter`, receives encoded blocks, removes the corresponding in-flight metric, and calls `writers.write`. On write error it aborts the producer task, awaits it, drains any queued metric bytes, attempts writer shutdown, and returns the write error. If the stream completes cleanly, it awaits the producer result and shuts down writers, returning the original reader and total plaintext bytes read.

`MultiWriter::write` concurrently writes each shard to writers that do not already have an error. A short write marks that writer failed; a missing writer is `DiskNotFound`. It succeeds once non-error writers meet `write_quorum`; otherwise it reduces errors with `reduce_write_quorum_errs`, emits an internode metric labelled by dominant error, logs the full error vector, and returns a summarized `io::Error`. `shutdown` applies the same quorum accounting to flush/shutdown. `encode_small_direct` reads all data or one bounded block, encodes via `encode_data_owned`, writes once through `MultiWriter`, then shuts down.

## State and persistence behavior
This module writes persistent shard streams through `BitrotWriterWrapper`: encoded shard bytes become bitrot-framed blocks on each disk or remote writer. It mutates writer state by setting failed writer slots to `None` after short writes or shutdown failures and by retaining `errs` across blocks, so a writer that fails once is skipped for later blocks. In-flight metrics are incremented when encoded blocks enter the queue and decremented on receive or drain, making abort cleanup part of correctness.

## Dependencies and integration points
Depends on `disk::error` and `disk::error_reduce` for quorum semantics, `BitrotWriterWrapper` and `Erasure` for shard writing and encoding, `futures::FuturesUnordered` for concurrent fanout, `tokio::sync::mpsc`, `rustfs_utils` for env parsing and full-block reads, `rustfs_rio` for checksum mismatch identification, and `rustfs_io_metrics` for memory/quorum telemetry. The functions integrate with object write paths that supply shard writers and quorum values.

## Risks and test signals
The streaming producer owns the reader inside a spawned task, so cancellation paths must correctly abort, await, and drain metrics. A writer error causes shutdown to be attempted but returns the original write error, meaning shutdown failures are logged but secondary. `MultiWriter::write` asserts data/writer length equality instead of returning an error, so callers must maintain exact shard counts. `encode_inline_small` returns without shutting down writers for empty streams, which tests assert; callers must be prepared for no commit on empty input. The single-block fast path deliberately reads `block_size + 1` and rejects oversized input.

Tests cover shutdown after small shards, truncated limited readers, zero block size rejection, inline empty and payload behavior, single-block payload and oversized rejection, channel capacity edge cases, and stable write-quorum summary labels. Additional high-value tests would simulate producer encode failure after queued blocks and verify in-flight metric cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/encode.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/erasure.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/erasure.rs

## Purpose
Provides the core Reed-Solomon erasure coding abstraction used by RustFS object storage. It splits object blocks into data and parity shards, reconstructs missing data/parity shards, calculates shard sizing and shard-file offsets, and supports both the current codec and a legacy MinIO/main-branch compatible format.

## Important APIs, types, and functions
`calc_shard_size` is the current `ceil(block_size / data_shards)` formula; `calc_shard_size_legacy` rounds the ceil value up to an even size for legacy files. `ReedSolomonEncoder` wraps `reed_solomon_erasure::galois_8::ReedSolomon` for current parity encode and reconstruct operations. `LegacyReedSolomonEncoder` wraps cached `reed_solomon_simd` encoder/decoder instances for legacy encode, data reconstruct, full reconstruct, and parity regeneration. `encode_parity_shards` is shared parity-regeneration plumbing that validates shard count and shard lengths. `Erasure` is the central type with `new`, `new_with_options`, `encode_data`, `encode_data_owned`, `decode_data`, `decode_data_and_parity`, `total_shard_count`, `shard_size`, `shard_file_size`, `shard_file_offset`, and `encode_stream_callback_async`.

## Control flow
`Erasure::new_with_options` chooses backend state from `uses_legacy`: current mode creates a `ReedSolomonEncoder` when `parity_shards > 0`; legacy mode creates a `LegacyReedSolomonEncoder`; zero-parity configurations skip backend creation. `encode_data` and `encode_data_owned` calculate the per-shard size from the selected formula and input length, pad a `BytesMut` to `per_shard_size * total_shard_count`, collect mutable shard slices, encode parity when parity exists, freeze the buffer, and split it into zero-copy `Bytes` shards. The owned variant tries to reuse the caller's `Vec<u8>` allocation through `Bytes::try_into_mut`.

`decode_data` reconstructs missing data shards only. `decode_data_and_parity` reconstructs missing data shards and regenerates parity, which is needed for healing missing parity shards. Current mode delegates to `reed-solomon-erasure`; legacy mode delegates to the SIMD wrapper. `LegacyReedSolomonEncoder` caches encoder/decoder objects behind `RwLock<Option<_>>`, takes a cached instance, resets it for the current shard length, and returns it to the cache after use. `encode_parity_shards` fills missing parity shard slots with zeroed buffers, verifies all shard lengths match, then invokes the backend encoder.

`shard_file_size` maps original object length to the number of bytes stored in each shard file, accounting for full blocks plus the final partial block. `shard_file_offset` calculates a shard-file read extent for a logical range. `encode_stream_callback_async` is a callback-oriented async encoder: it reads blocks, offloads encoding to blocking tasks, invokes `on_block` for either encoded blocks or errors, and returns total bytes read.

## State and persistence behavior
`Erasure` itself is mostly stateless apart from codec configuration, backend caches, `uses_legacy`, block size, and a UUID. Its calculations define persistent object layout: shard count, shard size, padding, parity contents, and legacy compatibility. The distinction between `decode_data` and `decode_data_and_parity` is persistence-relevant: read repair should not unnecessarily rebuild parity, while heal must recreate all missing shards. Legacy mode changes both shard sizing and parity backend, so metadata that selects `uses_legacy` must be accurate for old objects.

## Dependencies and integration points
Uses `bytes::{Bytes, BytesMut}` for shard buffers, `reed_solomon_erasure` for current coding, `reed_solomon_simd` for legacy coding, `smallvec` for stack-optimized shard slice vectors, `tokio::task::spawn_blocking` in the async callback path, and tracing warnings. `encode.rs`, `decode.rs`, and `heal.rs` extend `Erasure` with streaming write, read, and repair operations. File metadata code is expected to choose `new_with_options` when old-version or legacy-checksum objects are encountered.

## Risks and test signals
Constructors call `unwrap()` when creating backend encoders, so invalid shard counts can panic instead of returning an error. `calc_shard_size` divides by `data_shards`, so zero data shards are invalid even if not always guarded at construction. `encode_stream_callback_async` treats `UnexpectedEof` as a break rather than an error except in the main `encode.rs` pipeline, so callers should understand the differing stream semantics. Legacy cache locks can fail only on poisoning but return I/O errors if they do. Tests include compatibility hash expectations with comments noting MinIO parity behavior; these are critical because any backend or formula change can alter persistent shard bytes.

Tests cover owned-vs-borrowed encode equivalence, read decode not rebuilding missing parity, full decode-and-parity reconstruction for current and legacy modes, shard-file sizing, current and legacy encode/decode round trips, missing shard recovery, stream callback behavior and zero-block-size reporting, SIMD-oriented large and small data cases, maximum erasures, and compatibility hashes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/erasure.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/heal.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/heal.rs

## Purpose
Implements erasure healing: reconstructs missing or selected shard files from available bitrot-protected shard readers and writes the rebuilt shards through bitrot writers.

## Important APIs, types, and functions
The file adds `Erasure::heal`. It accepts mutable optional `BitrotWriterWrapper` slots for target shards, a vector of optional `BitrotReader<R>` inputs, `total_length`, and an unused `_prefer` slice. It uses `decode::ParallelReader` to read available shard blocks and `encode::MultiWriter` to write reconstructed shard blocks.

## Control flow
`heal` logs the writer/reader counts and total length, then rejects writer slices whose length does not equal `data_shards + parity_shards`. It constructs a `ParallelReader` from the readers and computes the number of erasure blocks from `total_length` and `block_size`. Write quorum is set to the count of available writers, with a minimum of one, so all provided repair targets must be writable.

For each block, `ParallelReader::read` returns optional shard buffers and per-shard errors. `heal` counts successful shards and returns an error if fewer than `data_shards` are available. If parity exists, it calls `decode_data_and_parity`, reconstructing both missing data shards and missing parity shards. It converts every shard option to `Bytes`, using an empty default for any still-missing shard, and writes the full shard vector through `MultiWriter`. After all blocks, it calls `writers.shutdown`.

## State and persistence behavior
Healing writes reconstructed shard data back to the provided writer slots in the same bitrot-framed format used by normal encoding. It does not choose disks or persist metadata itself; caller-provided writer presence controls which shards are repaired. Because write quorum equals available writer count, a single repair writer failure fails the heal. `_prefer` is currently ignored, so no preferred source/target selection state affects reconstruction.

## Dependencies and integration points
Depends on `crate::disk::error::{Error, Result}`, `BitrotReader`, `BitrotWriterWrapper`, `ParallelReader`, `MultiWriter`, `bytes::Bytes`, `tokio::io::AsyncRead`, and tracing. It integrates directly with `erasure.rs` reconstruction logic and the same write quorum machinery used by `encode.rs`.

## Risks and test signals
The function validates writer count but not reader count explicitly; `ParallelReader` can work with the supplied reader vector, but mismatched lengths could lead to unexpected shard vectors. Mapping `None` shards to empty `Bytes` after reconstruction should be safe only if reconstruction filled all needed positions; if a backend leaves parity missing unexpectedly, empty shards may be offered to writers. The ignored `_prefer` parameter suggests incomplete parity/source preference behavior. `end_block` divides by `block_size`, so zero block size would panic.

Tests cover rebuilding a missing parity shard and rebuilding a missing data shard across multiple blocks, using inline writers and no checksum to compare healed bytes with original encoded shards.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/heal.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/mod.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/mod.rs

## Purpose
Defines the public module boundary for RustFS erasure coding. It wires together bitrot framing, stream decode, stream encode, core Reed-Solomon operations, and healing.

## Important APIs, types, and functions
The module declares private `bitrot`, public `decode`, `encode`, `erasure`, and `heal` submodules. It re-exports all public items from `bitrot`, plus `Erasure`, `ReedSolomonEncoder`, `calc_shard_size`, and `calc_shard_size_legacy` from `erasure`.

## Control flow
There is no runtime control flow in this file. Compile-time module declarations make `decode`, `encode`, `erasure`, and `heal` addressable as submodules, while re-exports shorten common imports for callers that need bitrot wrappers or the core erasure type.

## State and persistence behavior
The file holds no state and performs no persistence. Its persistence relevance is API-level: re-exported shard sizing functions and `Erasure` are the entry points that downstream object metadata and storage code use to encode, decode, and interpret persisted shard files.

## Dependencies and integration points
Integrates the sibling files in `erasure_coding`. External callers can import `crate::erasure_coding::BitrotReader`, `BitrotWriterWrapper`, `Erasure`, and sizing helpers without referencing the private `bitrot` module path. The public submodules allow tests or callers to reach `decode`, `encode`, `erasure`, and `heal` APIs directly where visibility permits.

## Risks and test signals
Because `bitrot` is private but re-exported wholesale, any new public item in `bitrot.rs` automatically becomes part of this module's public API. Conversely, only selected symbols from `erasure.rs` are re-exported, so new core helpers require explicit export decisions. Test signal is indirect through all submodule tests; there are no module-only tests needed unless API visibility changes.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/mod.rs -->
