# Research: subset-b-007892

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/layout.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/layout.py

## Purpose

This module defines the on-wire/on-disk layout of Tahoe-LAFS immutable shares and provides bucket proxy implementations for writing and reading those layouts through storage-server remote references. It supports the legacy v1 share format with 32-bit offsets and the v2 format with 64-bit offsets for large shares. It is a low-level compatibility boundary: upload and repair code write through `WriteBucketProxy` instances, while checker/downloader/debug/helper code read through `ReadBucketProxy`.

## Important APIs, Types, and Functions

- `LayoutInvalid`, `RidiculouslyLargeURIExtensionBlock`, and `ShareVersionIncompatible` model parse failures for corrupted or unsupported immutable share bytes.
- `FORCE_V2` is a test hook that forces `make_write_bucket_proxy` to choose the v2 writer even for small files.
- `make_write_bucket_proxy(rref, server, data_size, block_size, num_segments, num_share_hashes, uri_extension_size)` chooses `WriteBucketProxy` first and falls back to `WriteBucketProxy_v2` on `FileTooLargeError`.
- `_WriteBuffer` batches sequential writes. `queue_write` appends data and returns whether the batch threshold has been reached; `flush` returns the current remote offset and byte payload; `get_total_bytes` tracks flushed plus queued bytes.
- `WriteBucketProxy` implements `IStorageBucketWriter` for v1 shares. It computes fixed section offsets, queues header/data/hash/UEB writes, flushes to remote `write`, and finally calls remote `close`.
- `WriteBucketProxy_v2` overrides only offset/header packing, using 8-byte fields and a `0x44` header.
- `ReadBucketProxy` implements `IStorageBucketReader`. It lazily fetches and parses the share header once, then exposes methods for block data, crypttext hashes, optional block hashes, share hashes, and URI extension bytes.

## Control Flow

Write flow starts with offset calculation in `_create_offsets`. For v1, the header starts at `0x24`; for v2, at `0x44`. The uploader then calls `put_header`, `put_block` for every encoded segment/share block, `put_crypttext_hashes`, `put_block_hashes`, `put_share_hashes`, `put_uri_extension`, and `close` in byte order. `_queue_write` asserts that each requested offset equals the buffer's current total, enforcing a no-hole sequential write discipline. When the batch threshold is reached, `_actually_write` flushes queued bytes to `rref.callRemote("write", offset, data)`. `close` verifies the full allocated size has been queued/written, flushes any remaining bytes, and calls remote `close`.

Read flow begins lazily through `_start_if_needed`. The first read method invokes `_fetch_header`, reads up to the largest header size (`0x44`), and `_parse_offsets` detects version 1 or 2 and unpacks section offsets. Subsequent methods calculate section sizes from adjacent offsets and call remote `read`. `get_uri_extension` reads only the length field first, rejects implausibly large lengths (`>= 2000`), and then reads exactly that UEB payload. `get_share_hashes` validates that the share-hash area is a multiple of the encoded `(2 + HASH_SIZE)` tuple size.

## State and Persistence Behavior

The module itself persists nothing locally; persistence is the remote bucket share written by storage-server calls. Writer state is local and transient: calculated offsets, expected data sizes, segment/hash sizes, and the `_WriteBuffer`. Reader state is also transient: parsed offsets, version, field size/struct, started flag, and a `OneShotObserverList` used to share one header-parse result among concurrent consumers. The actual durable format is the immutable share byte layout documented in the module comments.

## Dependencies and Integration Points

The module depends on Twisted `Deferred`s, Foolscap-like remote bucket references exposing `write`, `close`, `abort`, and `read`, Tahoe interfaces `IStorageBucketWriter`/`IStorageBucketReader`, `HASH_SIZE`, `FileTooLargeError`, `mathutil.next_power_of_k`, and logging/assert helpers. `upload.ServerTracker` uses `make_write_bucket_proxy` both to compute `allocated_size` and to wrap allocated remote bucket writers. `immutable.checker`, downloader share code, helper preflight checks, and debug commands instantiate `ReadBucketProxy` to parse existing shares. The storage server's immutable bucket implementation must accept the offsets and exact write ordering this module emits.

## Risks and Edge Cases

- `_queue_write` requires strict write ordering and no holes. Any future caller that tries random-access bucket writes will fail assertions rather than degrade gracefully.
- The `close` assertion error message references `self._written_buffer`, which does not exist; the assertion condition is still meaningful, but a failure path would raise a misleading secondary `AttributeError` while formatting.
- V1 offsets reject `block_size`, `data_size`, or total offset space at `>= 2**32`; v2 rejects at `>= 2**64`. Boundary tests matter because the selected writer affects compatibility with older Tahoe versions.
- `ReadBucketProxy` trusts parsed offsets enough to derive read sizes; corrupted offset ordering can result in invalid sizes or reads unless caught by downstream validation.
- The hard-coded UEB length sanity cap (`>= 2000`) protects against corrupt lengths but is a protocol assumption that must be updated if legitimate UEBs grow.
- `get_block_hashes` returns `[]` when `at_least_these` is empty, so callers relying on complete block hashes must request at least one hash.

## Test Signals

Relevant coverage appears in `src/allmydata/test/test_storage.py`, which imports `WriteBucketProxy`, `WriteBucketProxy_v2`, `ReadBucketProxy`, and `_WriteBuffer` and exercises v1/v2 layout behavior. Debug and downloader integration paths also rely on `ReadBucketProxy`. Additional repair/checker corruption tests in `test_repairer.py` exercise invalid share layouts and UEB/hash-tree corruption through higher-level verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/layout.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/literal.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/literal.py

## Purpose

This module implements in-memory immutable file nodes backed by literal file capabilities. Literal files are small files whose bytes are embedded directly in the URI, so they do not have storage indexes, shares, verify caps, or repair work. The node exposes the same high-level immutable file interface as CHK-backed immutable files so directory and web/download code can treat literal nodes uniformly.

## Important APIs, Types, and Functions

- `_ImmutableFileNodeBase` provides common immutable node identity and capability behavior: no write URI, read-only URI equals `get_uri`, immutable/read-only flags, immutable-directory eligibility, no-op `raise_error`, and URI-based equality/hash.
- `LiteralFileNode` implements `IImmutableFileNode` and `ICheckable`.
- `LiteralFileNode.__init__(filecap)` requires a `LiteralFileURI`.
- `get_size`, `get_current_size`, `get_cap`, `get_readcap`, `get_verify_cap`, `get_repair_cap`, `get_uri`, and `get_storage_index` expose literal metadata. Verify/repair caps and storage index are always `None`.
- `check` and `check_and_repair` immediately succeed with `None`.
- `read(consumer, offset=0, size=None)` slices embedded bytes and streams them into a Twisted consumer through `basic.FileSender`.
- `get_best_readable_version`, `download_best_version`, `download_to_data`, and `get_size_of_best_version` provide the readable-file compatibility surface.

## Control Flow

Construction wraps a `LiteralFileURI`. Reads are purely local: the requested byte range is sliced from `self.u.data`, wrapped in `BytesIO`, and passed to `FileSender.beginFileTransfer`. The returned deferred maps back to the consumer object. Download-to-data bypasses streaming and immediately returns the embedded bytes. Check and repair paths avoid network or storage checks and return already-fired deferreds.

## State and Persistence Behavior

The only state is `self.u`, the literal URI object containing the bytes. There is no local or remote persistence beyond the URI string itself. Equality and hashing derive from the URI object, so two literal nodes with the same embedded cap compare equal.

## Dependencies and Integration Points

The module depends on Twisted `Deferred`s and `FileSender`, the `IImmutableFileNode`/`ICheckable` interfaces, and `allmydata.uri.LiteralFileURI`. `nodemaker.py` constructs `LiteralFileNode` for literal caps. `upload.LiteralUploader` creates literal caps for data at or below `Uploader.URI_LIT_SIZE_THRESHOLD` and returns upload results with no sharemap/servermap. Directory, filenode, web, and system tests use this node wherever immutable file nodes are expected.

## Risks and Edge Cases

- `check` and `check_and_repair` return `None`, not a rich check result; callers must tolerate literal nodes as trivially local.
- `get_storage_index`, verify cap, and repair cap are `None`; code that assumes all immutable nodes are CHK-backed will break.
- `read` slices the embedded data before handing it to `FileSender`. This is fine for literal caps because they are intentionally tiny, but the implementation would not be appropriate for large embedded payloads.
- `raise_error` is a no-op, matching the absence of deferred latent errors; callers should not expect it to validate cap contents.

## Test Signals

`src/allmydata/test/test_immutable.py` contains `LiteralFileNodeTests` for URI-based equality. `test_filenode.py`, `test_dirnode.py`, and `test_system.py` also instantiate literal nodes in broader filesystem flows. Upload behavior that chooses literal caps is covered through `upload.LiteralUploader` and small-file upload paths in `test_upload.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/literal.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/offloaded.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/offloaded.py

## Purpose

This module implements the helper-server side of assisted CHK immutable uploads. A client-side `AssistedUploader` can ask a remote helper whether a CHK file is already fully present in the grid; if not, the helper fetches encrypted ciphertext from the client, stores it in resumable local staging files, and runs the normal CHK upload pipeline from the helper node. This offloads peer selection, erasure encoding, and share pushing from the client while preserving the same immutable cap results.

## Important APIs, Types, and Functions

- `NotEnoughWritersError` reports that all assisted upload readers failed.
- `CHKCheckerAndUEBFetcher` checks storage servers for all shares of a storage index and fetches one URI extension block. It returns `False` or `(sharemap, ueb_data, ueb_hash)`.
- `CHKUploadHelper` implements `RICHKUploadHelper` and subclasses `upload.CHKUploader`. It is a Foolscap `Referenceable` used by clients after `Helper.remote_upload_chk`.
- `AskUntilSuccessMixin` manages a list of remote readers and retries `callRemote` operations against the next reader when one fails.
- `CHKCiphertextFetcher` pulls encrypted bytes from one or more remote `RIEncryptedUploadable` readers into `CHK_incoming/<si>`, then atomically renames to `CHK_encoding/<si>` when complete.
- `LocalCiphertextReader` implements `IEncryptedUploadable` over the helper's local ciphertext file and proxies encoding parameters/close to the original reader.
- `Helper` implements `RIHelper` and `IStatsProducer`; it handles `remote_upload_chk`, tracks active uploads, counters, stats, and on-disk helper staging directories.

## Control Flow

`Helper.remote_upload_chk(storage_index)` increments counters and first deduplicates active uploads. If no upload is active, `_check_chk` uses `CHKCheckerAndUEBFetcher` to ask storage servers for existing buckets and fetch a UEB through `ReadBucketProxy`. If all `total_shares` are found and a UEB is available, the helper returns a `HelperUploadResults` object and no upload helper. Otherwise `_did_chk_check` creates or returns a `CHKUploadHelper` for the storage index.

`CHKUploadHelper` wires together three phases in its constructor: wait for `CHKCiphertextFetcher.when_done`, start `LocalCiphertextReader`, then run inherited `start_encrypted`. `remote_upload(reader)` registers the client reader with both the fetcher and local reader and returns a deferred that fires when `_finished_observers` fires. `_finished` converts normal `UploadResults` into `HelperUploadResults`, translating server objects into server IDs, closes the local reader, deletes the completed encoding file, notifies helper completion, and fires observers. `_failed` logs, fires failure, and removes the active upload.

`CHKCiphertextFetcher` starts once a reader is added. It resumes from an existing incoming file if present, bypasses fetching if the encoded file already exists, otherwise calls remote `get_size`, opens the incoming file in append mode, and repeatedly calls remote `read_encrypted(offset, CHUNK_SIZE)`. It writes returned chunks, updates counters/status, and when complete renames incoming to encoding. `AskUntilSuccessMixin.call` retries failed remote calls with remaining readers and raises `NotEnoughWritersError` if none remain.

## State and Persistence Behavior

`Helper` creates and maintains `CHK_incoming` and `CHK_encoding` under its base directory. Incoming files are partial ciphertext and enable resumable fetch after interrupted helper/client activity. Encoding files represent complete ciphertext ready for local erasure encoding and upload. Active uploads live in `_active_uploads` keyed by storage index, while `_all_uploads` is a weak dictionary for debugging/history. Stats include active upload count, incoming/encoding file counts and bytes, age-over-48h byte totals, and upload/fetch counters.

`CHKUploadHelper` stores transient upload status, storage index, file paths, reader/fetcher objects, timing data, and completion observers. `CHKCiphertextFetcher` tracks the reader list, open output file, expected/have bytes, cumulative fetch time, total time, and fetched byte count. Completed encoding files are deleted after successful upload; failed or interrupted files may remain for later resume or cleanup.

## Dependencies and Integration Points

The module depends on Foolscap `Referenceable`, `DeadReferenceError`, and `eventually`; Twisted deferreds; Tahoe upload classes/results; `ReadBucketProxy` for UEB fetching; storage broker server enumeration; URI extension packing/unpacking; `hashutil.uri_extension_hash`; `fileutil.make_dirs`; and Tahoe stats/history/logging utilities. Client-side integration is `upload.AssistedUploader`, which calls helper `upload_chk` and then invokes the returned `RICHKUploadHelper.upload` with a `RemoteEncryptedUploadable`. The helper reuses `upload.CHKUploader`, so server selection, layout writing, and encoder behavior remain shared with direct uploads and repairs.

## Risks and Edge Cases

- Existing complete encoding files bypass fetching. This supports resume but depends on file naming by storage index and assumes prior file contents are correct for that SI.
- Partial incoming files resume by byte count without local cryptographic validation until later encoding/checking stages. Bad partial files can waste work or fail later.
- `AskUntilSuccessMixin` retries any remote call against the next reader, but non-idempotent interactions need scrutiny; current uses are size, encoding parameters, ciphertext reads, and close.
- `_got_response` records all bucket references from all servers; `_get_uri_extension` pops one arbitrary reader and treats UEB fetch failure as file unavailable rather than trying every reader.
- `_done` in `CHKCheckerAndUEBFetcher` requires all `total_shares`, not merely `needed_shares`, to declare the file already present. This is conservative and may force unnecessary upload work for recoverable but not perfectly healthy files.
- `LocalCiphertextReader.close` forwards `close` to one remote reader; the comment questions whether forwarding makes sense.
- Staging directories can accumulate old incoming/encoding files after failures; `get_stats` reports old bytes, but cleanup behavior is external.

## Test Signals

`src/allmydata/test/test_helper.py` directly exercises assisted uploads, concurrent uploads, failed previous uploads/resume behavior, already-uploaded detection, and fake `CHKUploadHelper`/checker injection. `test_system.py` adjusts `CHKCiphertextFetcher.CHUNK_SIZE` in integration scenarios. Upload result conversion and helper protocol compatibility are also indirectly exercised by `test_upload.py` assisted-upload paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/offloaded.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/repairer.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/repairer.py

## Purpose

This module implements immutable CHK file repair by presenting an existing immutable file node as an `IEncryptedUploadable` and passing it through the normal CHK upload pipeline. Missing shares are regenerated by downloading ciphertext from the file node segment by segment and uploading replacement shares to storage servers selected by `upload.CHKUploader`.

## Important APIs, Types, and Functions

- `Repairer` implements `IEncryptedUploadable` and inherits `log.PrefixingLogMixin`.
- `__init__(filenode, storage_broker, secret_holder, monitor)` captures the damaged file, storage access, secrets, cancellation monitor, and current read offset.
- `start()` obtains the file segment size and verify-cap share parameters, sets encoding parameters `(k, happy, N, segsize)` with `happy = 0`, constructs a `upload.CHKUploader`, and starts it with `self`.
- `set_upload_status`, `get_size`, `get_all_encoding_parameters`, `read_encrypted`, `get_storage_index`, and `close` satisfy `IEncryptedUploadable` for the uploader.

## Control Flow

Repair begins with `start`. After `filenode.get_segment_size()` resolves, the repairer reads the verify cap for `needed_shares` and `total_shares`, sets `happy` to zero per ticket notes, and creates a `CHKUploader`. From the uploader's perspective, the repairer is already encrypted uploadable data: `get_storage_index` returns the original storage index, `get_all_encoding_parameters` returns the original coding parameters, and `read_encrypted(length, hash_only)` reads ciphertext from the file node at the repairer's current offset into a `MemoryConsumer`, advances the offset, and returns the collected chunks. Upload server selection and share writing are handled by the shared upload/encoder machinery.

## State and Persistence Behavior

Repairer state is small and transient: the source file node, storage broker, secret holder, cancellation monitor, upload status, encoding parameters, and monotonic `_offset`. It does not write local files. Persistent effects are remote immutable bucket allocations and writes performed by `upload.CHKUploader`/`encode.Encoder` through the normal storage-server protocol. Because repair reuses the original storage index and encoding parameters, replacement shares are for the same CHK object.

## Dependencies and Integration Points

The module depends on `upload.CHKUploader`, `consumer.MemoryConsumer`, Twisted deferreds, storage broker/secret holder interfaces, and the file node's `get_segment_size`, `get_verify_cap`, `get_size`, `read`, and `get_storage_index` methods. `immutable.filenode` constructs `Repairer` from `check_and_repair`. Upload/encoder code treats it like any other encrypted uploadable. The monitor is documented as a cancellation source, but this file does not itself call `monitor.raise_if_cancelled`; cancellation may be handled in higher layers or is an implementation gap relative to the class docstring.

## Risks and Edge Cases

- The docstring says the repairer checks cancellation before new server requests, but the implementation shown does not call the monitor. The shared upload path may not fully satisfy that promise.
- `happy = 0` makes repair server selection permissive so it can place as many replacement shares as possible, but it also means success criteria differ from normal upload happiness.
- The repairer trusts servers that report existing shares, even if those shares are corrupt, as documented. This can limit corruption repair effectiveness.
- `read_encrypted` advances `_offset` by requested `length` before verifying returned byte count, relying on the file node/read path to provide correct data or fail.
- `close` is a no-op, so any source-node cleanup must be owned elsewhere.

## Test Signals

`src/allmydata/test/test_repairer.py` is the main coverage area: it checks repair from deletion, servers-of-happiness repair behavior, tiny reads, and many verifier corruption cases. The file also documents a disabled corruption-repair test and limitations around replacing corrupted shares. `test_checker.py` exercises higher-level check-and-repair result rendering and flows that invoke immutable repair through file nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/repairer.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/upload.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/upload.py

## Purpose

This module is the main immutable upload orchestration layer for Tahoe-LAFS. It turns user-provided uploadables into literal caps for tiny files or CHK immutable files for larger files. For CHK uploads it handles encryption, storage-index derivation, encoding parameter setup, peer/server selection using servers-of-happiness, remote bucket allocation, encoder wiring, upload status/results, helper-assisted upload client behavior, and uploadable wrappers for file handles, filenames, and in-memory data.

## Important APIs, Types, and Functions

- Eliot fields/actions/messages (`LOCATE_ALL_SHAREHOLDERS`, `GET_SHARE_PLACEMENTS`, `CONVERGED_HAPPINESS`) record peer-selection decisions.
- `TooFullError` marks full-server allocation responses internally.
- `HelperUploadResults` is the Foolscap-compatible result object exchanged with older/newer helpers. Its shape is compatibility-sensitive.
- `UploadResults` implements `IUploadResults` and stores file size, helper ciphertext bytes, preexisting/pushed shares, share/server maps, timings, UEB data/hash, verify cap string, and final read URI.
- `ServerTracker` wraps one storage server for a specific upload. It computes allocated share size with `layout.make_write_bucket_proxy`, asks for existing buckets, allocates buckets, wraps returned bucket writers in layout proxies, and aborts partial buckets.
- `PeerSelector` tracks writeable/read-only/bad peers, preexisting shares, computes share placements via `happiness_upload.share_placement`, and calculates happiness.
- `_QueryStatistics` tracks allocation query totals, good/bad/full/error/contacted counts.
- `Tahoe2ServerSelector` drives the server-selection algorithm and returns `(upload_trackers, already_serverids)`.
- `_Accum` and `EncryptAnUploadable` adapt an `IUploadable` plaintext source into an `IEncryptedUploadable` ciphertext source while computing plaintext hashes and storage index.
- `UploadStatus` implements `IUploadStatus` with storage index, size, helper flag, status string, three progress channels, active flag, results, and a monotonic counter.
- `CHKUploader` runs direct CHK uploads using `encode.Encoder`, `Tahoe2ServerSelector`, and storage bucket writers.
- `read_this_many_bytes` repeatedly reads from an uploadable until a requested byte count is reached.
- `LiteralUploader` builds literal file URIs and upload results for tiny files.
- `RemoteEncryptedUploadable` exposes an encrypted uploadable over Foolscap for helper-assisted uploads and supports forward-only reads with hash-only skipping.
- `AssistedUploader` is the client-side helper upload coordinator.
- `BaseUploadable`, `FileHandle`, `FileName`, and `Data` implement uploadable sources and convergent/random encryption-key generation.
- `Uploader` is the `IUploader` service entry point used by the Tahoe client.

## Control Flow

Top-level upload starts in `Uploader.upload`. It requires a running service with a parent client, gets the source size, applies default encoding parameters from the parent, counts stats, then chooses a path. Files at or below `URI_LIT_SIZE_THRESHOLD` go to `LiteralUploader`, which reads all bytes and returns a `LiteralFileURI` result. Larger files are wrapped in `EncryptAnUploadable`. If a helper connection is available, `AssistedUploader` first computes the storage index and contacts the helper; otherwise `CHKUploader` performs direct upload locally. In both CHK cases, the final callback combines the verify cap from upload results with the encryption key to produce the read cap URI.

Direct CHK upload flow is `CHKUploader.start` -> `start_encrypted`. It creates an `encode.Encoder`, attaches the encrypted uploadable, asks `locate_all_shareholders` to select/allocate buckets, passes bucket writers and preexisting share map into the encoder, starts encoding, and converts the returned verify cap into `UploadResults`. `locate_all_shareholders` extracts encoder parameters, creates `Tahoe2ServerSelector`, and passes storage index, share/block/segment counts, happiness, and UEB size.

Server selection in `Tahoe2ServerSelector.get_shareholders` first creates trackers for up to `2 * total_shares` candidate servers. It filters writeable servers by `maximum-immutable-share-size`; oversized-incompatible servers become read-only candidates. It asks read-only and writeable trackers about existing shares with 15-second timeouts. Then it repeatedly computes share placements, asks trackers to allocate assigned shares, updates homeless/preexisting/use-tracker state, marks failed/full servers read-only, merges preexisting and newly allocated shares, and stops when effective happiness reaches the requested minimum or no progress remains. On failure it aborts allocated buckets and raises `UploadUnhappinessError`; on success it returns trackers holding allocated shares plus preexisting share locations.

Encryption flow in `EncryptAnUploadable` obtains encoding parameters and size, derives an AES key from either convergent hashing or random uploadable key generation, computes the storage index as a hash of the key, and services `read_encrypted(length, hash_only)` by repeatedly reading plaintext chunks up to `CHUNKSIZE`. Every plaintext chunk updates whole-file and per-segment hashers and advances the AES-CTR encryptor. In hash-only mode it still encrypts to advance the counter but discards ciphertext.

Assisted upload flow in `AssistedUploader` gets size/encoding parameters, calls remote helper `upload_chk(storage_index)`, and either accepts already-present helper results or creates `RemoteEncryptedUploadable` and calls the returned helper's `upload`. It validates returned UEB parameters, builds a verify cap, converts helper server IDs to local stub server objects, and returns normal `UploadResults`.

## State and Persistence Behavior

`Uploader` stores helper connection state, stats/history hooks, and weak references to active uploaders. `UploadStatus` is mutable in-memory progress state; status progress indexes are `[0]` convergence/storage-index work, `[1]` ciphertext/encryption/fetching, and `[2]` encode/push. `CHKUploader` stores its encoder, upload status, storage index, timing fields, and per-share server tracker mapping. `Tahoe2ServerSelector` stores peer-selection state during one upload: peer selector, homeless shares, preexisting shares, servers with shares, trackers selected for use, query statistics, and last failure.

Persistent effects for CHK uploads are remote immutable shares allocated and written via storage server `allocate_buckets` and layout bucket writers. `ServerTracker.abort` attempts to remove partial remote buckets after selection failure. `FileHandle` caches file size and encryption key; convergent key generation rewinds and scans the source file. `FileName.close` closes the owned file handle; `FileHandle.close` intentionally leaves externally-owned handles open; `Data` wraps a `BytesIO`.

## Dependencies and Integration Points

The module depends on Twisted `Deferred`s/services, Foolscap remote objects, Tahoe crypto/hash utilities, URI classes, storage server wrappers, `encode.Encoder`, immutable share `layout`, happiness utilities, server broker APIs, and interfaces including `IUploadable`, `IUploader`, `IEncryptedUploadable`, `RIEncryptedUploadable`, `IUploadStatus`, and `IPeerSelector`. `offloaded.py` subclasses `CHKUploader` and consumes/produces `HelperUploadResults`; `repairer.py` reuses `CHKUploader` by presenting a file node as `IEncryptedUploadable`; `literal.py` consumes literal caps created by `LiteralUploader`; storage and checker/downloader layers consume the remote shares and verify caps generated here.

## Risks and Edge Cases

- `Tahoe2ServerSelector.__init__` initializes `_query_stats`, but `get_shareholders` assigns `_query_status`; the existing `_query_stats` remains in use, so the intended reinitialization may be a typo and stale stats would matter if a selector instance were reused.
- Server selection mutates tracker lists inside asynchronous callbacks. The code assumes Twisted callback serialization, but changes to concurrency or data structures could affect placement/retry behavior.
- Read-only servers are still queried to renew existing shares; this is intentional but easy to break if allocation calls are optimized away.
- `PeerSelector.mark_readonly_peer` removes from `peers` without guarding membership; callers currently add peers first, but future paths must preserve that order.
- `EncryptAnUploadable` must encrypt even in `hash_only` mode to advance AES-CTR state. Replacing the crypto backend or adding seek support must preserve counter alignment for helper forward skips.
- `_hash_and_encrypt_plaintext` computes progress as bytes read divided by file size; zero-sized CHK files are avoided by literal upload threshold, but any alternate path should avoid division by zero.
- `read_this_many_bytes` asserts every read returns at least one byte until the requested size is satisfied; uploadables with premature EOF will assert rather than return a structured error.
- `LiteralUploader` reads the entire tiny file into memory, which is acceptable only because `Uploader` gates it by size.
- Helper result compatibility is fragile: `HelperUploadResults` must not change existing field shapes because helpers and clients may be different versions.
- `Uploader.upload` closes the uploadable in an `addBoth` callback, so caller-owned uploadables must implement close semantics carefully; `FileHandle` intentionally does not close external handles.

## Test Signals

`src/allmydata/test/test_upload.py` is the primary suite for uploadable wrappers, encryption behavior, server selection, happiness behavior, assisted/direct upload results, and `EncryptAnUploadable` edge cases including known ciphertext and large requested reads. `test_helper.py` covers helper interaction through `AssistedUploader` and `offloaded.Helper`. `test_encode.py` exercises encoder integration with encrypted uploadables. `test_storage.py` validates layout bucket writer/reader assumptions used by `ServerTracker`. `test_repairer.py` covers the repair path that reuses `CHKUploader`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/upload.py -->
