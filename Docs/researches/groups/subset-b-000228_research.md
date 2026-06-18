# subset-b-000228 Research

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/prefetch.rs -->
## sources/cloud-native/nydus/rafs/src/prefetch.rs

### Purpose
`prefetch.rs` implements a streaming blob prefetcher for RAFS images. Instead of issuing per-chunk range requests, it groups chunks by blob and performs rangeless/streaming reads from each blob, then extracts chunk byte ranges by compressed offset and persists them through the configured `BlobCache`. The module is explicitly aimed at Dragonfly proxy efficiency: one streaming connection per blob replaces many small range requests.

### Important APIs, Types, And Functions
`BlobPrefetcher::new()` builds an `Arc<BlobPrefetcher>` from a `RafsSuper`, a cache vector indexed by blob index, thread count, and optional bandwidth limit. `start()` spawns the controller thread, `stop()` sets a stop flag and waits up to five seconds, and `progress()` exposes atomic counters. Internal `BlobWork` holds one `BlobInfo` and compressed-offset-sorted `BlobChunkInfo` entries. `PrefetchProgress` tracks total and completed blobs/chunks/bytes. `RateLimiter` is a token bucket with two seconds of capacity. Core internals are `build_blobs()`, `prefetch_all()`, `prefetch_one_blob()`, and `stream_and_cache()`.

### Control Flow
The controller traverses the RAFS tree from `root_ino`, collecting regular-file chunks and descending directories with `get_child_by_index()`. Chunks are grouped by `blob_index` and keyed by `compressed_offset`, which both deduplicates same-offset chunks and naturally sorts streaming order. `prefetch_all()` creates a bounded worker pool, sends each `BlobWork` with its matching cache, and workers retry each blob up to `DEFAULT_MAX_RETRY`. `prefetch_one_blob()` checks cache readiness, finds the first missing chunk, calls `BlobReader::stream_read(start_offset, RequestSource::Prefetch)`, and delegates stream matching. `stream_and_cache()` accumulates 1 MiB reads, matches complete chunk ranges inside the buffer, calls `cache_chunk_data()`, updates counters, trims old bytes while keeping the largest chunk window, and exits when all chunks are done or the stream passes the last chunk end.

### State, Persistence, And Dependencies
State is process-local and concurrency-oriented: `State` owns the stop flag, counters, thread handle, condvar, worker count, rate limiter, and retry limit. Persistence happens only via the external `BlobCache`; the prefetcher itself does not write metadata. It depends on `nydus_storage` cache/backend/device traits and RAFS inode/superblock metadata.

### Integration Points
The cache vector must align with RAFS blob indexes. Backend implementations must support `stream_read`; cache implementations must expose `ChunkMap` and `cache_chunk_data()`. Logs use standard `info!`, `warn!`, and `error!` macros.

### Risks
Deduplication by compressed offset can collapse distinct chunk IDs if different chunks share an offset. The retry loop treats per-chunk cache errors inside `stream_and_cache()` as warnings, so a blob may be counted as prefetched even if some chunks failed to cache. `total_bytes` is never populated. `stop()` may detach the controller thread after timeout.

### Test Signals
The in-file tests cover rate limiter behavior, progress defaults, stream accumulation across read boundaries, pre-marked chunks, cache errors, stop behavior, fully cached blobs, empty blobs, and constructor defaults. These tests are strong for local buffer/control logic but do not exercise real backend streaming, RAFS traversal, or Dragonfly behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/src/prefetch.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rafs/tests/io_amplify.rs -->
## sources/cloud-native/nydus/rafs/tests/io_amplify.rs

### Purpose
`io_amplify.rs` is a disabled integration-style test file for RAFS read amplification behavior. The entire body is inside a block comment under `// Temporarily disable`, so it contributes no active tests. Its intended target is `RafsSuper::carry_more_until()`, which appears to append adjacent or following compressed chunks to reduce user I/O amplification when requested reads do not fully cover nearby useful chunks.

### Important APIs, Types, And Functions
The commented tests use `RafsConfig`, `RafsSuper`, `MockSuperBlock`, `MockInode`, `MockChunkInfo`, and `CHUNK_SIZE`. Every test constructs mock inodes with explicit file offsets, compressed offsets/sizes, decompressed offsets, and decompressed sizes, then calls `carry_more_until(inode, user_io_size_or_limit, tail_chunk, threshold)` and checks whether a `BlobIoDesc` is returned and how many `bi_vec` entries it contains.

### Control Flow
Each scenario builds a cached-mode `RafsSuper`, installs mock inodes into `MockSuperBlock`, and selects a chunk as the current/tail chunk. Calls to `carry_more_until()` vary thresholds and requested sizes to check when no amplification happens, when a single following chunk is appended, and when multiple compressed-contiguous chunks across inodes are appended. Cases cover small expected reads, normal expected reads, large boundary transitions, sparse compressed offsets, two inodes with four chunks, and a single-file tail case.

### State, Persistence, And Dependencies
All state is ephemeral test setup. There is no disk persistence or runtime cache interaction. The tests depend on RAFS mock metadata types and the `assert_matches` crate, which is also commented out.

### Integration Points
The file documents expected integration between RAFS inode metadata and blob I/O descriptor generation. The checked `bi_vec[*].chunkinfo.compress_offset()` values imply that `carry_more_until()` should reason over compressed blob layout, not only file-local offsets.

### Risks
Because the file is disabled, regressions in read amplification will not be caught by this test target. Some expressions use `(0 - 1) as u64`, which would underflow if compiled in modern Rust without wrapping context; this may be one reason it is commented. The comments also show abandoned expectations, suggesting the intended behavior changed without the tests being updated.

### Test Signals
There are no active test signals from this file. As historical/specification material, it signals desired coverage for boundary thresholds, sparse offsets, cross-inode amplification, and huge expected reads. Re-enabling would require updating syntax, expectations, and dependency wiring.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rafs/tests/io_amplify.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/rust-toolchain.toml -->
## sources/cloud-native/nydus/rust-toolchain.toml

### Purpose
`rust-toolchain.toml` pins the Nydus workspace toolchain. It requests Rust channel `1.94.0` and installs the `rustfmt` and `clippy` components.

### Important APIs, Types, And Functions
This is configuration rather than Rust code. The only top-level table is `[toolchain]`; `channel` selects the compiler release and `components` asks rustup to provision formatting and linting tools with the toolchain.

### Control Flow
There is no runtime control flow. Tooling flow is driven by rustup: entering the repository or invoking cargo/rustc/rustfmt/clippy under rustup should resolve to Rust `1.94.0` with the listed components available.

### State, Persistence, And Dependencies
The file affects developer and CI environment state by causing rustup to install or select the pinned toolchain. It does not persist application state. It depends on the Rust release existing in the active rustup distribution channel; if `1.94.0` is not available to an environment, builds fail before source compilation.

### Integration Points
Cargo, rust-analyzer, CI jobs, formatting checks, and lint workflows all consume this file indirectly through rustup. The requested `clippy` and `rustfmt` components match the service crate's likely quality gates.

### Risks
Pinning a future or unavailable compiler version can block reproducibility. It also means code may rely on language/library behavior newer than many distributions provide. If CI images cache an older toolchain, this file forces a download step. There are no feature flags or profile settings here, so all behavior is delegated to workspace manifests and cargo commands.

### Test Signals
The file itself has no tests. Validation is indirect: `rustup show`, `cargo check`, `cargo fmt --check`, and `cargo clippy` would confirm availability and compatibility of the pinned toolchain and components.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/rust-toolchain.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/Cargo.toml -->
## sources/cloud-native/nydus/service/Cargo.toml

### Purpose
`service/Cargo.toml` defines the `nydus-service` crate, version `0.4.0`, for the Nydus image service manager. It declares core service dependencies and feature gates for FUSE, virtiofs, block device export, NBD, userfaultfd, and confidential-computing related backend registration.

### Important APIs, Types, And Functions
The manifest exports feature names rather than Rust APIs. `default = ["fuse-backend-rs/fusedev"]` enables normal FUSE device support. `virtiofs` enables vhost-user and VM-memory dependencies. `block-device` enables `dbs-allocator` and `tokio/fs`. `block-nbd` extends `block-device` with `bytes`. `block-uffd` extends `block-device`. `coco` enables FUSE device support and `nydus-storage/backend-registry`.

### Control Flow
Build-time control flow is feature-based. `blob_cache.rs`, `block_device.rs`, `block_nbd.rs`, and `block_uffd.rs` rely on optional dependencies listed here. Linux-specific dependency sections add `tokio-uring` for runtime async file/socket I/O and `procfs` for Linux tests.

### State, Persistence, And Dependencies
The crate depends on internal workspace/path crates (`nydus-api`, `nydus-rafs`, `nydus-storage`, `nydus-upgrade`, `nydus-utils`) and external crates for serialization, logging, async channels, finite-state-machine behavior, fd passing, ioctl/syscall interaction, and versioned persistence. There is no runtime state in the manifest, but feature selection changes compiled code and available daemon modes.

### Integration Points
This manifest is the integration point between service modules and workspace dependency resolution. `block_nbd.rs` needs `bytes`; `block_device.rs` needs `dbs-allocator`; UFFD/NBD paths need Linux-only `tokio-uring`; daemon state code uses `rust-fsm`; live-upgrade or persistence code can use `versionize`.

### Risks
Feature coupling is important: enabling `block-nbd` or `block-uffd` without Linux support would fail because the implementation depends on Linux APIs. `block-uffd` currently adds no extra optional dependency beyond `block-device`, relying on always-on `flume`, `sendfd`, `mio`, and `tokio`. Dependency versions are partly pinned and partly workspace-inherited, so compatibility is controlled across the root workspace.

### Test Signals
Manifest validation comes from cargo feature builds, for example `cargo check -p nydus-service --features block-nbd` and `--features block-uffd`. The service modules include unit tests gated by normal Rust test compilation and Linux-only dependencies.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/Cargo.toml -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/blob_cache.rs -->
## sources/cloud-native/nydus/service/src/blob_cache.rs

### Purpose
`blob_cache.rs` manages RAFS metadata and data blob cache configuration for the service block-device paths. It converts API blob cache entries into scoped metadata/data blob objects, validates local paths and cache settings, loads RAFSv6 bootstrap metadata, and exposes async read/fetch wrappers around metadata files and data blob cache objects.

### Important APIs, Types, And Functions
`generate_blob_key(domain_id, blob_id)` scopes blobs as `domain/blob` unless the domain is empty. `MetaBlobConfig` stores bootstrap id/path/config, referenced data blobs, extra RAFS blob info, and TARFS mode. `DataBlobConfig` stores `BlobInfo`, config, scoped id, and reference count. `BlobConfig` wraps either config type. `BlobCacheMgr` provides `add_blob_entry()`, `add_blob_list()`, `remove_blob_entry()`, and `get_config()`. Runtime access wrappers are `MetaBlob::new()/blocks()/async_read()` and `DataBlob::new()/async_fetch()/async_read()`.

### Control Flow
Adding a meta blob validates the API entry, canonicalizes `metadata_path`, validates fscache/filecache work dirs, converts to `ConfigV2`, and marks blobs accessible. `add_meta_object()` loads `RafsSuper`, rejects RAFSv5, creates the meta config, adds it to the locked state, then adds each referenced data blob and associates it with the meta config. Data blobs are reference-counted; duplicate metadata blobs are rejected. Removal can delete an entire domain or one meta/data object, decrementing referenced data blob counts.

### State, Persistence, And Dependencies
`BlobCacheMgr` state is an in-memory `Mutex<HashMap<String, BlobConfig>>`. Persistent data remains in bootstrap/blob files and the cache backend; `DataBlob::async_fetch()` delegates persistence/population to `BlobObject::fetch_range_uncompressed()`. `MetaBlob` and `DataBlob` wrap `tokio_uring::fs::File` for async reads, and `DataBlob::new()` duplicates the underlying blob object fd.

### Integration Points
The manager consumes `nydus_api` cache entries, loads `nydus_rafs` metadata, creates caches through `nydus_storage::factory::BLOB_FACTORY`, and feeds `BlockDevice`. TARFS and mapped block addresses are taken from RAFS superblock extra info.

### Risks
`BlobCacheState::try_add()` increments duplicate data ref counts but does not update config fields, so callers rely on identical scoped blob configuration. `add_meta_object()` partially mutates state and performs rollback only for data-add failure after meta insertion. `DataBlob::async_fetch()` uses `spawn_blocking`, so heavy misses can consume blocking pool capacity. The id splitter `/` is forbidden in domain/blob ids for meta entries.

### Test Signals
Tests cover key generation, entry parsing, invalid ids and metadata paths, add/remove/reference behavior across domains, metadata async reads, fd getters, zero-length fetch, and data fetch/read with fixture blobs. They exercise localfs/filecache/fscache-style config paths but not remote backend failure modes.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/blob_cache.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/block_device.rs -->
## sources/cloud-native/nydus/service/src/block_device.rs

### Purpose
`block_device.rs` presents a RAFSv6 image as a block-addressable device. It maps bootstrap metadata, holes, and data blobs into a single logical block address space so the image can be read as an EROFS-compatible disk or exported to NBD/UFFD.

### Important APIs, Types, And Functions
`BlockRange` represents `Hole`, `MetaBlob`, or `DataBlob`. `BlockDevice::new()` creates a private `BlobCacheMgr` from a `BlobCacheEntry`; `new_with_cache_manager()` builds the interval map from an existing cache manager. Public accessors include `meta_blob_id()`, `cache_mgr()`, `blocks()`, `block_size()`, `size_to_blocks()`, and `blocks_to_size()`. Read paths are `async_read()` and `fetch_ranges()`. `probe_blob_ranges()` identifies already cached data blob chunk ranges. `export()` and `do_export()` write the logical device to a raw disk image and optionally append dm-verity hashes.

### Control Flow
Construction inserts an initial free interval, loads the meta blob config, maps the metadata blob at the beginning, then iterates referenced data blobs. It inserts explicit `Hole` ranges when mapped block addresses leave gaps, validates TARFS mode consistency, computes block counts from blob sizes, creates `DataBlob` wrappers, and updates the interval tree. `async_read()` walks intervals covering the requested block range, zero-fills holes, reads metadata at absolute offsets, and reads data blobs at offsets relative to their mapped range. `fetch_ranges()` returns fd/offset/len/block-offset tuples, either fetching data first or probing readiness only. `export()` partitions the device into batches across up to 32 threads, each with a tokio-uring runtime, and optionally records Merkle leaf digests.

### State, Persistence, And Dependencies
The block layout is in-memory: `blocks`, `blob_id`, `cache_mgr`, `IntervalTree<BlockRange>`, and `is_tarfs_mode`. Reads and exports persist only through the output disk file and through cache population performed by `DataBlob::async_fetch()`. Dependencies include RAFS v6 layout constants, `dbs_allocator::IntervalTree`, `tokio_uring`, Nydus cache wrappers, and dm-verity helpers.

### Integration Points
`BlockDevice` is the common storage engine for `block_nbd.rs` and `block_uffd.rs`. It relies on `BlobCacheMgr` for scoped blob configuration and on RAFS `RafsBlobExtraInfo::mapped_blkaddr` for the logical disk map.

### Risks
`size_to_blocks()` truncates rather than rounds, so callers must pass aligned sizes. `fetch_ranges()` skips holes, which is correct for mmap-style zero-fill users but requires callers to handle missing ranges. Multi-threaded export rebuilds `BlockDevice` in each thread and shares a locked verity generator, so performance depends on metadata/cache construction and lock granularity. Output open uses `truncate(false)`, leaving stale bytes if overwriting a larger previous file.

### Test Signals
Tests cover construction, invalid ids, block-size conversion, async reads across metadata/hole/data/out-of-range regions, export digest stability for one and two threads, `fetch_ranges()` invalid/out-of-range/meta/data/hole/probe cases, and zero-block reads. Coverage is fixture-based and does not include TARFS images.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/block_device.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/block_nbd.rs -->
## sources/cloud-native/nydus/service/src/block_nbd.rs

### Purpose
`block_nbd.rs` exports a RAFSv6 `BlockDevice` through the Linux Network Block Device driver. It configures an `/dev/nbd*` device, handles kernel NBD requests over Unix socket pairs, and implements the `NydusDaemon` lifecycle wrapper for running the service under the daemon state machine.

### Important APIs, Types, And Functions
`nbd_ioctl()` wraps Linux NBD ioctl request generation. `NbdService::new()` configures block size/count/timeout/read-only/multi-conn flags; `create_worker()` establishes a socket pair and attaches one end to the kernel; `run()` invokes `NBD_DO_IT`; `stop()` clears active state and socket. `NbdWorker::run()` processes request headers asynchronously. `handle_request()` parses NBD requests and sends replies. `NbdDaemon` implements `DaemonStateMachineSubscriber` and `NydusDaemon`. `create_nbd_daemon()` constructs, starts, and transitions the daemon.

### Control Flow
Daemon creation builds a `BlobCacheMgr`, adds the bootstrap entry, creates a `BlockDevice`, initializes `NbdService`, starts the daemon state machine, then sends `Mount` and `Start`. Starting the daemon creates `nbd_threads` workers, each with a socket registered through `NBD_SET_SOCK`, and starts a control thread blocked in `NBD_DO_IT`. Workers read fixed 28-byte headers, validate magic/alignment, call `BlockDevice::async_read()` for read commands, return EINVAL/EIO on invalid or failed reads, stop on disconnect, and send a 16-byte reply plus data for successful reads.

### State, Persistence, And Dependencies
State includes an `active` atomic, scoped blob id, shared cache manager, open NBD device file, broadcast sender, daemon state atomics, service/control thread handles, and state-machine channels. There is no save/restore implementation; `save()` and `restore()` are unimplemented in `NbdDaemon`. Persistence is through the kernel NBD device and underlying blob cache population. Dependencies include Linux NBD ioctls, `bytes` parsing/building, `tokio_uring::net::UnixStream`, `mio::Waker`, and daemon FSM types.

### Integration Points
The module is compiled through the `block-nbd` feature and depends on `BlockDevice` for all storage semantics. It integrates with the general `NydusDaemon` trait so supervisors can start, stop, wait, and query state/cache manager.

### Risks
Only read and disconnect commands are handled; unknown command types return success with no data unless validation fails, which may be too permissive. `NbdDaemon::wait_service()` joins worker threads but not the `nbd_control_thread`, so lifecycle cleanup depends on control-loop exit elsewhere. Kernel NBD tests require privileged devices and are ignored. `save()`/`restore()` panic if called.

### Test Signals
The only in-file test, `test_nbd_device`, is ignored and requires `/dev/nbd15`. It exercises creating two workers and stopping after a short delay, but normal CI receives little active coverage for protocol parsing, ioctl setup, or daemon shutdown.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/block_nbd.rs -->

<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/nydus/service/src/block_uffd.rs -->
## sources/cloud-native/nydus/service/src/block_uffd.rs

### Purpose
`block_uffd.rs` exports a RAFSv6 `BlockDevice` through Linux userfaultfd. It supports a daemon socket protocol where clients send a userfaultfd and VMA regions, and an embeddable `UffdCore` that resolves page faults directly. Zerocopy mode returns blob fd/range metadata to clients; copy mode fills faulting pages with `UFFDIO_COPY`.

### Important APIs, Types, And Functions
Kernel-facing types are `UffdMsg`, `UffdPagefault`, `UffdioCopy`, and `UffdioZeropage`; low-level helpers are `read_uffd_msg()`, `uffdio_zeropage()`, `uffdio_copy()`, and `uffdio_wake()`. `UffdCore::handle_page_fault()` is the main resolution entry. It uses `resolve_zerocopy_ranges()`, `resolve_copy()`, and `prefault_ranges()`. `UffdWorker` handles socket connections, handshakes, stat requests, fd passing, UFFD events, response batching, and optional prefault. `UffdService` owns listener/workers/active connections. `UffdDaemon` implements `NydusDaemon`, and `create_uffd_daemon()` wires it to the state machine.

### Control Flow
Service startup creates worker threads with tokio-uring runtimes, binds the Unix socket, accepts clients, and distributes streams round-robin over flume channels. A connection waits for protocol messages and UFFD readiness. Handshake accepts either a `HandshakeRequest` or Firecracker-compatible bare VMA array, takes the first passed uffd fd, closes extras, makes it nonblocking, and optionally spawns prefault. On a page fault, `UffdCore` finds the containing VMA, aligns to the VMA page size, clamps to VMA and device bounds, zero-pages beyond-device or hole regions, then either fetches fd ranges from `BlockDevice::fetch_ranges()` or reads/copies data into the faulting address.

### State, Persistence, And Dependencies
Runtime state is active flags, active socket fd list, scoped blob id, shared `BlobCacheMgr`, socket path, broadcast sender, worker channels/threads, daemon state-machine channels, and per-connection `ConnState` with VMA regions, fault policy, and `AsyncFd<OwnedFd>` for the uffd. The service is explicitly stateless for save/restore. Persistent effects are limited to cache population through `BlockDevice`; page resolution mutates client memory through UFFD ioctls. Dependencies include `sendfd`, `flume`, `tokio::io::unix::AsyncFd`, `tokio_uring`, `mio::Waker`, and `uffd_proto` message types.

### Integration Points
`UffdCore` uses the same `BlockDevice` layout and cache manager as NBD/export. The daemon mode integrates with Nydus daemon lifecycle. The JSON+SCM_RIGHTS protocol is documented as Firecracker compatible and sends `PageFaultResponse` batches with up to `MAX_RANGES_PER_MSG` fds.

### Risks
There are many raw fd ownership transitions; incorrect test or caller ownership can double-close descriptors. `resolve_copy()` reads full block-rounded data but copies only requested `len`, so alignment assumptions matter. `UffdService::run()` computes `worker_num` once; running with zero workers would make round-robin indexing invalid on first connection. `try_recv_from_sock()` assumes one complete JSON message per recv buffer and has no framing for larger/split messages. UFFD tests may require kernel permissions and can be environment-sensitive.

### Test Signals
The file has broad tests for daemon lifecycle, service stop/save/restore, fd closing, socket receive parsing, Firecracker handshake format, prefault, batch responses, stat handling, handshake fd validation, worker creation, async fd sending, graceful shutdown, no-event UFFD handling, core construction, non-pagefault/no-VMA paths, copy and zerocopy page faults, beyond-device zeroing, `resolve_copy`, `resolve_zerocopy_ranges`, `prefault_ranges`, and `uffdio_wake`. Coverage is substantial but relies on Linux userfaultfd support.
<!-- END_FILE_RESEARCH: sources/cloud-native/nydus/service/src/block_uffd.rs -->
