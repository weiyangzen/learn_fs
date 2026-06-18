# Research: subset-b-007891

Grouped code research for Tahoe-LAFS immutable/grid-manager files. Each section preserves the original source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/grid_manager.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/grid_manager.py

## Purpose
Implements Tahoe-LAFS Grid Manager internal state, storage-server authorization certificates, JSON persistence, and runtime certificate verification predicates. A Grid Manager signs short JSON certificates binding a storage server public key to an expiry time; clients can then decide whether a server announcement is authorized by any configured Grid Manager key.

## Important APIs, Types, And Functions
`SignedCertificate` is an attrs-frozen container for JSON-encoded certificate bytes plus raw Ed25519 signature bytes. `load()` reads a JSON container with base32 signature text, while `marshal()` emits JSON-compatible bytes/signature fields.

`_GridManagerStorageServer` stores a user-facing server name, Ed25519 verifying key, and in-memory list of issued `SignedCertificate` objects. `public_key_string()` serializes the key in Tahoe's Ed25519 format.

`_GridManagerCertificate` is a parsed certificate record loaded from `name.cert.N` files, with filename, numeric index, expiry, and storage-server public key.

`create_grid_manager()` generates a new Ed25519 signing keypair and returns `_GridManager`. `load_grid_manager(config_path)` loads `config.json` from a directory or stdin, validates config version `0`, parses the private key, loads configured storage servers, and optionally validates stored certificate files. `save_grid_manager()` writes the marshaled config to stdout or `config.json`, creating a 0700 directory for file-backed configs.

`_GridManager.sign(name, expiry)` signs a canonical JSON certificate containing `expires`, `public_key`, and `version`. It immediately verifies its own signature before appending the certificate to the server's in-memory certificate list.

`parse_grid_manager_certificate()` validates the outer JSON certificate container shape. `validate_grid_manager_certificate()` verifies a signature and returns decoded certificate data, deliberately not checking expiry. `create_grid_manager_verifier(keys, certs, public_key, now_fn=None, bad_cert=None)` pre-validates signatures against configured Grid Manager keys and returns a zero-argument predicate that checks certificate public-key match and expiry at call time.

## Control Flow
Creation starts with Ed25519 key generation and an empty storage-server dict. Loading reads `config.json`, rejects unknown versions or missing/invalid private keys, then constructs each `_GridManagerStorageServer` from persisted public keys. For file-backed configs, `_load_certificates_for()` scans sequential `name.cert.0`, `name.cert.1`, ... files until a missing index stops the loop, validating signatures when the Grid Manager public key is known.

Signing requires an existing storage server name. It computes `expiration = current_datetime_with_zone() + expiry`, serializes certificate metadata with deterministic separators and sorted keys, signs those bytes, self-verifies, records the certificate on the server object, and returns it.

Verifier creation has two phases. If no Grid Manager keys are configured, it returns a predicate that always succeeds. Otherwise it verifies each alleged certificate against each key, calls `bad_cert` for failures, keeps only successfully decoded cert bodies, and returns a predicate that compares encoded `public_key` bytes and `expires > now`.

## State And Persistence
Persistent state lives under a Grid Manager config directory: `config.json` contains config version, private signing key, and storage-server public keys; certificate files are separate sequential files per server. `_GridManager` keeps mutable state in a `UnicodeKeyDict` and per-server certificate lists. The verifier caches signature-valid certificate bodies, but expiry is evaluated fresh through `now_fn()` on each predicate call.

## Dependencies And Integration Points
Depends on `allmydata.crypto.ed25519`, Tahoe `base32` and `jsonbytes`, Twisted `FilePath`, `attrs`, and `datetime`. CLI code and admin/client config paths call these helpers; tests reference `allmydata.test.test_grid_manager`, `allmydata.test.cli.test_grid_manager`, `allmydata.test.cli.test_admin`, client announcement tests, and `integration/test_grid_manager.py`.

## Risks And Edge Cases
The annotation on `_load_certificates_for(gm_key=Optional[...])` uses a typing object as the default instead of `None`; runtime behavior still treats it as not-None unless callers pass explicitly, but actual calls pass the public key. Certificate scanning stops at the first missing numeric file, so gaps hide later certificates. `bad_cert` may be called repeatedly for multi-key setups even if another key validates the same certificate. `validate_grid_manager_certificate()` does not enforce version, expiry, or public key binding; callers must layer those checks. `save_grid_manager()` writes private key material and relies on directory permissions, not atomic replace.

## Test Signals
Primary coverage is `src/allmydata/test/test_grid_manager.py` for load/save/sign/parse/verifier behavior, `src/allmydata/test/cli/test_grid_manager.py` for CLI operations, `src/allmydata/test/cli/test_admin.py` for certificate installation, client announcement tests for config integration, and `integration/test_grid_manager.py` for end-to-end Grid Manager workflows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/grid_manager.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/hashtree.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/hashtree.py

## Purpose
Provides Tahoe's Merkle hash tree primitives for immutable uploads/downloads: complete trees for producing roots/proofs, and incomplete trees for incrementally validating hashes and leaves from untrusted storage servers.

## Important APIs, Types, And Functions
`roundup_pow2(x)` expands leaf counts to the next power of two. `CompleteBinaryTreeMixin` supplies array-indexed complete-tree navigation: `parent`, `lchild`, `rchild`, `sibling`, `needed_for`, `depth_first`, `dump`, `get_leaf_index`, and `get_leaf`.

`depth_of(i)`, `empty_leaf_hash(i)`, and `pair_hash(a, b)` encapsulate tree-level math and tagged hashing. `HashTree(L)` builds a full list-backed Merkle tree from leaf hashes, padding to a power of two with deterministic empty-leaf hashes. `HashTree.needed_hashes(leafnum, include_leaf=False)` returns proof nodes excluding root by default.

`IncompleteHashTree(num_leaves)` starts as a same-shaped list of `None`. `needed_hashes()` asks only for missing proof nodes. `set_hashes(hashes=None, leaves=None)` atomically adds internal hashes and/or leaf-indexed hashes, verifies them up to a known or computed root, and rolls back all newly inserted hashes on `BadHashError` or `NotEnoughHashesError`.

## Control Flow
Complete tree construction pads leaves, computes parent rows bottom-up with `pair_hash`, reverses rows, and flattens them into the heap-style tree list. Proof calculation walks from a leaf node toward root collecting siblings.

Incomplete validation first normalizes `leaves` into tree indices and checks for conflicting caller-supplied hashes. It provisionally inserts new hashes, tracks inserted nodes by depth, then validates from deepest level to root. For each pending node it requires a sibling, computes the parent from sorted left/right children, verifies or inserts the parent, and marks sibling coverage as validated. On failure it clears every hash inserted during the call before re-raising.

## State And Persistence
No disk persistence. Both tree classes are mutable `list` subclasses. `HashTree` stores complete bytes for every node. `IncompleteHashTree` progressively stores validated bytes or `None`, with `first_leaf_num` defining the leaf offset. Atomic rollback in `set_hashes()` is the key state invariant.

## Dependencies And Integration Points
Uses Tahoe `mathutil`, `base32`, and `hashutil.tagged_hash/tagged_pair_hash`. It is used by immutable encoding to build block, share, and ciphertext hash trees; immutable checker/downloader paths use `IncompleteHashTree` to validate UEB-derived roots, share hash chains, block hash chains, and ciphertext segment hashes.

## Risks And Edge Cases
Tree construction assumes at least one leaf; zero leaves would make `roundup_pow2(0)` return 1 but indexing semantics are not meaningful. The list subclass exposes mutation operations that can violate invariants if external callers modify entries directly. `set_hashes()` insists on enough data to validate every new hash, so callers must include a trusted root or already have one. Performance is covered by tests because earlier implementations had quadratic behavior.

## Test Signals
`src/allmydata/test/test_hashtree.py` covers complete tree proofs, incomplete-tree validation, failure rollback, bad/conflicting hashes, insufficient hashes, odd leaf counts, and performance behavior. Downloader corruption tests in `test_download.py` also exercise hash-tree failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/hashtree.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/history.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/history.py

## Purpose
Keeps lightweight in-memory status history for recent Tahoe operations, mainly for status displays and counters. It tracks downloads, uploads, mutable map updates/publishes/retrieves, and helper uploads.

## Important APIs, Types, And Functions
`History` exposes `add_download`, `add_upload`, `notify_mapupdate`, `notify_publish`, `notify_retrieve`, and `notify_helper_upload` to register operation status objects. `list_all_*` methods iterate weak-key dictionaries for all still-live status objects. `recent_*` lists retain bounded recent items using module constants such as `MAX_DOWNLOAD_STATUSES` and `MAX_RETRIEVE_STATUSES`.

## Control Flow
Each add/notify method inserts the status object into a `WeakKeyDictionary`, appends it to the matching recent list, and pops oldest entries until the list fits its limit. Publish/retrieve notifications additionally update `stats_provider` counters when present.

## State And Persistence
All state is process-local and non-persistent. Weak dictionaries avoid keeping old status objects alive solely through history, while recent lists intentionally hold strong references to a bounded number of recent operations. Stats are delegated to the injected provider.

## Dependencies And Integration Points
Depends only on `weakref`. Downloader filenodes add `DownloadStatus` through `History.add_download`; upload and mutable subsystems use the corresponding notify methods; web/status views can enumerate these collections.

## Risks And Edge Cases
`stats_provider` is optional but `DownloadNode.read()` assumes `history.stats_provider` is usable when history exists, so callers should pass a fully initialized history or `None`. Recent-list strong references can keep the last N status objects alive even after weak dictionaries would otherwise drop them. Iteration order over weak dictionaries is not a stable status ordering.

## Test Signals
Coverage is mostly indirect through status, upload/download, and system tests rather than a dedicated history test. Useful probes are downloader status tests and mutable publish/retrieve tests that assert counters and visible status lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/history.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/__init__.py

## Purpose
Empty package marker for `allmydata.immutable`. It defines no public API and exists to group immutable-file upload, download, check, repair, and placement modules.

## Important APIs, Types, And Functions
No symbols are defined.

## Control Flow
No runtime control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Imported implicitly by Python package resolution for modules such as `allmydata.immutable.checker`, `allmydata.immutable.encode`, `allmydata.immutable.filenode`, `allmydata.immutable.downloader`, and `allmydata.immutable.happiness_upload`.

## Risks And Edge Cases
Because the package initializer is empty, callers should not rely on package-level re-exports. Adding side effects here would affect many immutable subsystem imports.

## Test Signals
No direct tests are expected; import coverage is exercised by all immutable subsystem tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/checker.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/checker.py

## Purpose
Implements immutable CHK file checking and optional full verification. It can either ask servers which shares they claim to hold or download and cryptographically validate UEB metadata, hash trees, and every block in each share.

## Important APIs, Types, And Functions
Integrity exceptions classify UEB and hash failures: `IntegrityCheckReject`, `BadURIExtension`, `BadURIExtensionHashValue`, `BadOrMissingHash`, and `UnsupportedErasureCodec`.

`ValidatedExtendedURIProxy` wraps a `ReadBucketProxy` and `CHKFileVerifierURI`, fetches the URI extension block, verifies its hash against the verifycap, parses fields with `uri.unpack_extension`, computes segment/block/tail sizes, validates optional/redundant fields, and records mandatory `segment_size`, `crypttext_root_hash`, and `share_root_hash`.

`ValidatedReadBucketProxy` validates server bucket data. `get_all_sharehashes`, `get_all_blockhashes`, and `get_all_crypttext_hashes` fetch and validate complete hash-tree material for verifier mode. `get_block(blocknum)` fetches share hashes, block hashes, and block bytes needed for one block, then `_got_data()` validates share tree, block tree, and block hash.

`Checker` orchestrates server queries. `_get_buckets()` optionally renews leases and gets share buckets. `_download_and_verify()` fully verifies one share. `_verify_server_shares()` verifies all shares from one server. `_check_server_shares()` only trusts reported buckets. `_format_results()` builds `CheckResults`.

## Control Flow
`Checker.start()` maps connected servers through either `_verify_server_shares()` or `_check_server_shares()` and gathers all results before formatting. Lightweight check calls `get_buckets`, wraps claimed sharenums, and records server response status.

Full verification opens each bucket through immutable layout, validates the UEB, seeds a share hash tree with the UEB root, validates all share hashes, all block hashes, and all ciphertext hashes, then sequentially downloads every block and discards its bytes after validation. Remote/storage failures are converted to `(False, sharenum, reason)` tuples for diagnostics; unexpected local failures propagate.

`_format_results()` aggregates verified shares by share number and server, corrupt and incompatible locators, responding servers, health (`all total_shares present`), recoverability (`needed_shares present`), good hosts, and servers-of-happiness.

## State And Persistence
No durable state is written. The checker holds verifycap, server list, monitor, add-lease flag, derived file renewal/cancel secrets, and per-check temporary hash trees. Lease renewal may update remote storage-server lease state through `add_lease`.

## Dependencies And Integration Points
Depends on Twisted Deferreds, Foolscap remote errors, CHK URI types, immutable layout bucket proxies, Tahoe codec parsing, hash utilities, `hashtree.IncompleteHashTree`, `CheckResults`, and `servers_of_happiness`. `filenode.CiphertextFileNode.check()` and `check_and_repair()` instantiate `Checker`; repair consumes its `CheckResults`.

## Risks And Edge Cases
The checker waits for all server Deferreds, so a server that neither fails nor completes can stall checks. Full verify can be expensive because it downloads every block and all hash trees. UEB validation rejects unsupported erasure codec names and inconsistent redundant fields, while normal download ignores those redundant fields. Lease-renewal failures are deliberately tolerated for known old-server errors. A malformed but signature-valid UEB can still trigger assertions in downstream size calculations.

## Test Signals
`src/allmydata/test/test_encode.py` covers `ValidatedExtendedURIProxy`. Download corruption tests in `test_download.py` exercise hash and layout failures. `test_deepcheck.py`, `test_repairer.py`, and immutable filenode tests exercise checker/recoverability integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/checker.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/__init__.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/__init__.py

## Purpose
Package marker for immutable downloader implementation modules.

## Important APIs, Types, And Functions
No public symbols are defined or re-exported. The docstring only notes Python 3 porting.

## Control Flow
No runtime control flow.

## State And Persistence
No state or persistence.

## Dependencies And Integration Points
Supports package imports for `common`, `fetcher`, `finder`, `node`, `segmentation`, `share`, and `status`.

## Risks And Edge Cases
Adding imports here would change import-time behavior for the downloader package and may introduce dependency cycles because downloader modules already have mutual local imports.

## Test Signals
No direct tests; package import is covered by downloader and filenode tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/__init__.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/common.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/common.py

## Purpose
Defines shared downloader state labels and exception types used across segment fetching, share fetching, node orchestration, and segmentation.

## Important APIs, Types, And Functions
State constants are `AVAILABLE`, `PENDING`, `OVERDUE`, `COMPLETE`, `CORRUPT`, `DEAD`, and `BADSEGNUM`. Exceptions are `BadSegmentNumberError`, `WrongSegmentError`, and `BadCiphertextHashError`.

## Control Flow
No active control flow. Constants are compared by identity or equality by caller modules to route share/block events.

## State And Persistence
No mutable state or persistence.

## Dependencies And Integration Points
Imported by `fetcher.py`, `segmentation.py`, and `node.py`. `Share.get_block()` emits terminal/nonterminal states consumed by `SegmentFetcher._block_request_activity`; segmentation uses the segment-number and wrong-segment exceptions for retry behavior; `DownloadNode._check_ciphertext_hash()` raises `BadCiphertextHashError`.

## Risks And Edge Cases
The states are plain strings, not an enum, so typo safety is limited. Some code imports only subsets, making additions require careful search across downloader modules and tests.

## Test Signals
`src/allmydata/test/test_download.py` imports these exceptions directly and exercises bad segment, wrong segment retry, corrupt block, and ciphertext hash failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/common.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/fetcher.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/fetcher.py

## Purpose
`SegmentFetcher` obtains enough validated share blocks to reconstruct one ciphertext segment. It chooses shares, balances server diversity, handles overdue/failed/corrupt shares, and reports either `process_blocks()` or `fetch_failed()` to its parent `DownloadNode`.

## Important APIs, Types, And Functions
`SegmentFetcher(node, segnum, k, logparent)` tracks unused shares sorted by DYHB RTT and shnum, outstanding shares per server, active share per shnum, overdue shares, observers, completed blocks, and no-more-shares state.

Public callbacks from the parent are `add_shares(shares)`, `no_more_shares()`, and `stop()`. Internal scheduling is `loop()`/`_do_loop()`, `_find_and_use_share()`, `_start_share()`, `_ask_for_more_shares()`, `_cancel_all_requests()`, and `_block_request_activity()`.

## Control Flow
When shares arrive, they are sorted and the loop is eventually scheduled. The loop first checks whether the requested segment is valid if the node has authoritative segment count. It then sends block requests until the union of completed and active share numbers reaches `k`. It prefers one share per server, increases `_max_shares_per_server` if diversity is blocking progress, and asks `DownloadNode.want_more_shares()` when more candidates are needed.

Share observers emit `COMPLETE`, `OVERDUE`, `CORRUPT`, `DEAD`, or `BADSEGNUM`. Complete blocks are retained by share number. Overdue requests are removed from active accounting but can still complete. Terminal states retire the share from observer/server maps. When at least `k` blocks are complete, the fetcher stops and calls `node.process_blocks(segnum, blocks)`. If no possible set can reach `k`, `_no_shares_error()` raises `NoSharesError` or `NotEnoughSharesError` through `node.fetch_failed()`.

## State And Persistence
All state is in-memory per segment fetch. `stop()` cancels outstanding `EventStreamObserver`s and deletes large tracking structures to help garbage collection. Completed block data lives only long enough for `DownloadNode` to decode the segment.

## Dependencies And Integration Points
Depends on Foolscap `eventually`, Twisted `Failure`, Tahoe `NotEnoughSharesError`/`NoSharesError`, `DictOfSets`, logging, and states from `common.py`. It consumes `Share.get_block()` observers and calls `DownloadNode` methods.

## Risks And Edge Cases
The diversity algorithm can increase requests per server when necessary, trading reliability/latency against server concentration. Overdue requests are not canceled and can still affect completion. A bad segment number is handled on the next loop after authoritative segment metadata is known. Exceptions in the loop are converted to parent fetch failure and then re-raised, so tests need eventual-error handling.

## Test Signals
`src/allmydata/test/test_download.py` has a dedicated `SegmentFetcher` test cluster around share selection, overdue behavior, diversity growth, failures, and no-shares/not-enough-shares handling. Hung-server behavior is also covered in `test_hung_server.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/fetcher.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/finder.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/finder.py

## Purpose
Finds immutable shares by asking storage servers for buckets for a storage index. It feeds discovered `Share` objects to the download node on demand and manages pending/overdue DYHB requests.

## Important APIs, Types, And Functions
`incidentally(res, f, *args, **kwargs)` is a Deferred-chain helper that performs side effects while preserving the original result. `RequestToken` wraps a server for pending request tracking.

`ShareFinder(storage_broker, verifycap, node, download_status, logparent=None, max_outstanding_requests=10)` tracks server iterator, pending/overdue requests, timers, and per-shnum `CommonShare` objects.

Important methods are `start_finding_servers()`, `hungry()`, `loop()`, `send_request(server)`, `_got_response()`, `_create_share()`, `_deliver_shares()`, `_got_error()`, `overdue()`, `_request_retired()`, `update_num_segments()`, and `stop()`.

## Control Flow
The finder is lazy: it does not fetch the server iterator until `hungry()` is called. The loop sends parallel `get_buckets(storage_index)` requests while hungry and below the non-overdue outstanding limit. Each request records a `DownloadStatus` DYHB event and installs an overdue timer. Responses create `Share` instances for returned buckets, reusing or creating one `CommonShare` per share number, then deliver shares to the node and clear hunger. If all servers and pending requests are exhausted, it eventually calls `share_consumer.no_more_shares()`.

## State And Persistence
All state is transient. `CommonShare` instances preserve per-share block hash tree knowledge across multiple `Share` instances and servers for the same shnum. `stop()` cancels overdue timers and disables further looping.

## Dependencies And Integration Points
Depends on the storage broker server ordering (`get_servers_for_psi`), server storage APIs (`get_storage_server().get_buckets`), downloader `Share` and `CommonShare`, Twisted reactor timers, Foolscap eventual scheduling, and `DownloadStatus` event APIs. `DownloadNode.want_more_shares()` drives `hungry()`.

## Risks And Edge Cases
Overdue requests remain pending but stop counting toward the outstanding limit, allowing more server probes under latency. `stop()` cancels timers but does not cancel remote Deferreds. `update_num_segments()` asserts authoritative segment count, so it must be called only after UEB validation. Server iterator exhaustion plus hanging requests can delay `no_more_shares()`.

## Test Signals
`src/allmydata/test/test_immutable.py` includes `TestShareFinder`. Downloader and hung-server tests exercise overdue handling, max outstanding requests, and no-more-shares integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/finder.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/node.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/node.py

## Purpose
Central immutable ciphertext download coordinator. `DownloadNode` owns shared per-file download state, discovers shares, validates UEB/hash trees, fetches segments, decodes erasure-coded blocks, checks ciphertext hashes, and feeds `Segmentation` readers.

## Important APIs, Types, And Functions
`IDownloadStatusHandlingConsumer` is an interface for consumers that can receive `DownloadStatus` read-event/status handles. `Cancel` is a small active flag plus callback used for cancelable segment requests.

`DownloadNode(verifycap, storage_broker, secret_holder, terminator, history, download_status)` initializes guessed segment tables, shared `share_hash_tree`, `ciphertext_hash_tree`, `ShareFinder`, known shares, request queues, and logging.

External methods are `read(consumer, offset, size)`, `get_segment(segnum, logparent=None)`, `get_segsize()`, and `stop()`. Share/fetcher callbacks include `got_shares`, `no_more_shares`, `validate_and_store_UEB`, `process_share_hashes`, `process_ciphertext_hashes`, `want_more_shares`, `fetch_failed`, and `process_blocks`.

## Control Flow
Construction guesses segment size from `DEFAULT_IMMUTABLE_MAX_SEGMENT_SIZE` and verifycap parameters so initial reads can speculatively fetch data before UEB metadata is known. `read()` clips ranges, records status, creates a `Segmentation` producer, and delegates range-to-segment sequencing.

`get_segment()` appends a cancelable segment request and starts a `SegmentFetcher` if none is active. Only one active segment fetch runs per node. Existing live shares are offered to each new fetcher, and the fetcher asks `ShareFinder` for more when needed.

When any share provides a valid UEB, `validate_and_store_UEB()` checks the UEB hash against the verifycap, parses actual segment/block/tail sizes, configures CRS decoder and authoritative hash trees, seeds ciphertext/share roots, fires segment-size observers, and updates `ShareFinder` common-share sizes.

`process_blocks()` decodes `k` validated blocks using `CRSDecoder`, trims tail padding, validates the ciphertext segment hash against the ciphertext Merkle tree, records status events, and delivers `(offset, segment, decodetime)` to all queued requests for that segment. Failures are delivered to all matching request Deferreds.

## State And Persistence
State is in-memory and shared across reads of the same `CiphertextFileNode`: UEB knowledge, segment size, hash trees, known `Share` objects, current active segment, queued segment requests, and status events. It registers with an optional terminator so shutdown can stop active fetches and share finding. No durable state is written.

## Dependencies And Integration Points
Depends on CHK verifycaps, `CRSDecoder`, `IncompleteHashTree`, `hashutil`, `mathutil`, `observer.OneShotObserverList`, downloader `ShareFinder`, `SegmentFetcher`, `Segmentation`, and status/history objects. It is created lazily by `CiphertextFileNode` in `filenode.py`.

## Risks And Edge Cases
The guessed segment-size path can fetch a wrong segment for nonzero offsets and relies on `Segmentation` retry after UEB discovery. Only one active segment fetch can serialize concurrent reads for different segments. `validate_and_store_UEB()` notes malformed authentic UEBs can still throw assertions. `no_more_shares()` sets `_no_more_shares` without initialization in `__init__`, relying on dynamic attribute creation. Hash-tree failures after successful share validation are considered severe and become `BadCiphertextHashError`.

## Test Signals
`src/allmydata/test/test_download.py` exercises range reads, wrong-segment retry, bad segment numbers, corrupt hash trees, decode failures, status accounting, and segment fetch orchestration. `test_system.py` and filenode tests cover integration through immutable nodes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/node.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/segmentation.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/segmentation.py

## Purpose
Adapts arbitrary `read(offset, size)` requests into sequential segment downloads and implements Twisted `IPushProducer` flow control for the consumer.

## Important APIs, Types, And Functions
`Segmentation(node, offset, size, consumer, read_ev, logparent=None)` tracks remaining requested byte range, active segment number, cancel handle, consumer hunger/paused state, read status event, and completion Deferred.

Methods implementing behavior are `start()`, `_maybe_fetch_next()`, `_fetch_next()`, `_got_segment()`, `_retry_bad_segment()`, `_error()`, `stopProducing()`, `pauseProducing()`, and `resumeProducing()`.

## Control Flow
`start()` registers itself as a streaming producer and begins fetching. `_fetch_next()` chooses segment 0 for offset 0 or divides the current offset by actual or guessed segment size. It calls `DownloadNode.get_segment()`, tracks the cancel handle, and attaches callbacks.

`_got_segment()` verifies the returned `(segment_start, segment)` overlaps the next desired byte. If it does not include the current offset, it raises `WrongSegmentError`. Otherwise it slices the desired bytes, updates remaining offset/size, writes to the consumer, updates status, and maybe fetches the next segment.

If the initial segment size was guessed, `_retry_bad_segment()` traps `WrongSegmentError` and `BadSegmentNumberError`, asserts actual segment size is now known, and retries once. Producer flow control toggles `_hungry`; `stopProducing()` cancels outstanding segment requests and errbacks with `DownloadStopped`.

## State And Persistence
State is per read call and non-persistent. It mutates the remaining offset/size as bytes are delivered, and records pause time/decrypted-byte progress through `read_ev`.

## Dependencies And Integration Points
Depends on Twisted Deferreds and `IPushProducer`, Foolscap `eventually`, `allmydata.util.spans.overlap`, `DownloadStopped`, and exceptions from `common.py`. It is created by `DownloadNode.read()` and calls back into `DownloadNode.get_segment()`.

## Risks And Edge Cases
Wrong guessed segment size costs an extra round trip, especially for offset reads. Consumer `write()` can pause the producer reentrantly, so `_maybe_fetch_next()` must respect `_hungry`. `stopProducing()` errbacks the read Deferred; callers must handle cancellation. Returned segment data must cover exactly the next requested byte or the read cannot progress.

## Test Signals
`src/allmydata/test/test_download.py` contains coverage for `_retry_bad_segment`, range slicing, stopped downloads, and consumer flow-control behavior through higher-level download tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/segmentation.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/share.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/share.py

## Purpose
Represents a concrete immutable share on one server and performs lazy byte-range fetching, layout parsing, UEB validation, hash-tree validation, corruption reporting, and block delivery. `CommonShare` shares per-shnum block hash state across replicas.

## Important APIs, Types, And Functions
Exceptions are `LayoutInvalid` for malformed share layout and `DataUnavailable` for known-unavailable required bytes.

`Share(rref, server, verifycap, commonshare, node, download_status, shnum, dyhb_rtt, logparent)` stores remote bucket reference, server, verifycap-derived guessed offsets, actual offsets after parsing, pending/received/unavailable spans, requested block observers, and liveness.

`get_block(segnum)` returns an `EventStreamObserver` that will emit `COMPLETE`, `CORRUPT`, `DEAD`, or `BADSEGNUM`. Internal methods are organized into satisfaction (`_satisfy_offsets`, `_satisfy_UEB`, `_satisfy_share_hash_tree`, `_satisfy_block_hash_tree`, `_satisfy_ciphertext_hash_tree`, `_satisfy_data_block`), desire (`_desire_*`), and I/O (`_send_requests`, `_got_data`, `_got_error`, `_fail`).

`CommonShare` owns an authoritative or guessed block `IncompleteHashTree` for a share number. It exposes `set_authoritative_num_segments`, `need_block_hash_root`, `set_block_hash_root`, `get_desired_block_hashes`, `get_needed_block_hashes`, `process_block_hashes`, and `check_block`.

## Control Flow
`get_block()` queues observers for a segment and schedules the loop. The loop repeatedly consumes received data while it can satisfy prerequisites: parse version/offset table; fetch and validate UEB through `DownloadNode`; validate share hash chain; install block hash root; validate required block/ciphertext hash nodes; finally validate and deliver the data block.

If current data cannot satisfy progress, `_desire()` computes wanted and needed byte spans. Before actual offsets are known it may use guessed offsets when the server version tolerates immutable read overrun; otherwise it conservatively fetches version and offset table first. `_send_requests()` subtracts pending and already received spans, records block-request status events, and calls remote `read(start, length)`.

Received bytes move from `_pending` to `_received`; short reads mark remaining bytes as `_unavailable`. Required unavailable spans raise `DataUnavailable`. Corruption in layout, UEB, share hashes, or hash trees abandons the whole share and advises the server. Corrupt data blocks notify observers as `CORRUPT` but do not necessarily kill the share.

## State And Persistence
All state is in-memory. `DataSpans` stores received byte fragments until consumed; hash-tree state is retained in `DownloadNode` and `CommonShare` across block requests. The only persistence-like side effect is remote `advise_corrupt_share` notification to the storage server.

## Dependencies And Integration Points
Depends on remote bucket `read`, server version metadata, immutable layout offset conventions from `make_write_bucket_proxy`, `Spans`/`DataSpans`, `IncompleteHashTree`, hash utilities, `EventStreamObserver`, `DownloadStatus`, `DownloadNode` validation APIs, and states from `common.py`. `SegmentFetcher` consumes its observer events.

## Risks And Edge Cases
Guessed offsets plus overrun reads optimize round trips but require careful fallback when guesses are wrong. The file contains TODOs about empty share-hash sets, offset-section overlaps causing lost progress, over-requesting hash leaves, and leftover ciphertext hash data. Fatal share liveness after a single network/layout/hash failure may be conservative. `_satisfy_block_hash_tree()` computes corruption span size with `max(needed_hashes) * HASH_SIZE`, which is a diagnostic range rather than exact length.

## Test Signals
`src/allmydata/test/test_download.py` has extensive corruption and layout tests, including bad offset tables, block hashes, ciphertext hashes, share hashes, short reads, overrun behavior, and observer state transitions. `test_immutable.py` contains supporting mock hash-tree tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/share.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/status.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/status.py

## Purpose
Records append-only, mutable-in-place telemetry for immutable downloads: read requests, segment requests, DYHB server probes, block reads, known shares, problems, and miscellaneous timing events.

## Important APIs, Types, And Functions
`ReadEvent`, `SegmentEvent`, `DYHBEvent`, and `BlockRequestEvent` are thin mutator wrappers around event dictionaries. They update finish/success fields and propagate latest timestamps to `DownloadStatus`.

`DownloadStatus` implements `IDownloadStatus`. It allocates a monotonic `counter`, stores storage index/size, and exposes event creation methods (`add_read_event`, `add_segment_request`, `add_dyhb_request`, `add_block_request`, `add_misc_event`) plus interface methods (`get_counter`, `get_storage_index`, `get_size`, `get_status`, `get_progress`, `using_helper`, `get_active`, `get_started`, `get_results`).

## Control Flow
Download components append event dictionaries when work starts and mutate them through event wrapper methods on completion or failure. `get_status()` derives a text status from unfinished and failed segment events. `get_progress()` computes aggregate progress over unfinished reads only. `get_active()` returns true while any read event lacks `finish_time`.

## State And Persistence
All state is in-memory per `CiphertextFileNode`/`DownloadNode`. Event lists are append-only in ordering, but contained dicts are mutated as work progresses. No persistence or pruning is performed here; `History` bounds visible recent status objects.

## Dependencies And Integration Points
Depends on `itertools.count`, `zope.interface`, and `IDownloadStatus`. Used by `DownloadNode`, `ShareFinder`, `Share`, `Segmentation`, `DecryptingConsumer`, web status elements, and CLI/web status tests.

## Risks And Edge Cases
Event dict schemas are implicit and shared with web/status rendering. Progress ignores completed reads, so it returns `1.0` when no reads are currently outstanding even if prior reads failed. `using_helper()` and `get_results()` are placeholders. Lists can grow for long-lived file nodes with many reads.

## Test Signals
`src/allmydata/test/test_download.py` covers status behavior around reads and requests. `src/allmydata/test/web/test_status.py`, `src/allmydata/test/cli/test_status.py`, and web tests render or instantiate `DownloadStatus`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/downloader/status.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/encode.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/encode.py

## Purpose
Encodes encrypted immutable file data into erasure-coded shares, uploads blocks and hash trees to storage bucket writers, constructs URI extension metadata, enforces upload happiness after shareholder failures, and returns a CHK verifier capability.

## Important APIs, Types, And Functions
`UploadAborted` marks user-requested aborts. `Encoder` implements `IEncoder`.

Setup APIs: `set_encrypted_uploadable(uploadable)` reads size, encoding parameters, and storage index from an `IEncryptedUploadable`; `_got_all_encoding_parameters()` configures required/min-happiness/total shares, segment size, CRS encoder/tail encoder, share size, and URI extension base fields. `set_shareholders(landlords, servermap)` installs `IStorageBucketWriter`s and share placement map.

Upload APIs: `start()` builds a Deferred chain: put headers, encode/send each segment, finish hashes, send ciphertext hash tree, block hash trees, share hash trees, URI extension, close shareholders, then return verifier cap. `_encode_segment()`, `_gather_data()`, `_send_segment()`, `send_block()`, and `_remove_shareholder()` perform segment work and failure handling.

Finalization APIs: `finish_hashing()`, `send_crypttext_hash_tree_to_all_shareholders()`, `send_all_block_hash_trees()`, `send_all_share_hash_trees()`, `send_uri_extension_to_all_shareholders()`, `close_all_shareholders()`, `done()`, `err()`, and getters for shares/times/UEB/hash/size.

## Control Flow
After setup, `start()` ensures a reactor turn before work, starts all bucket writers, loops over all non-tail segments and the tail segment, and inserts turn barriers between segments to reduce Deferred retention. Each segment reads exact encrypted data pieces, updates segment and whole-file ciphertext hashers, encodes through CRS, sends each produced block to its landlord if assigned, and records block hashes per share.

After all segments, the encoder finalizes crypttext hash, uploads complete ciphertext hash tree to each live shareholder, builds and uploads one block hash tree per share, builds a share hash tree from block tree roots and uploads only each share's needed proof nodes, packs URI extension metadata, uploads it, and closes bucket writers. `done()` returns `CHKFileVerifierURI(storage_index, uri_extension_hash, k, N, file_size)`.

On shareholder errors, `_remove_shareholder()` aborts that bucket writer, removes it from landlord/servermap state, recomputes servers-of-happiness, and raises `UploadUnhappinessError` if remaining placement no longer satisfies `min_happiness`. `err()` aborts all remaining shareholders and unwraps `DeferredList` first errors.

## State And Persistence
Encoder state is process-local until bucket writers persist data remotely. It tracks `uri_extension_data`, codec instances, upload status, abort flag, encoding parameters, landlords, servermap, block hash lists, share root hashes, crypttext hashes, timing metrics, and placed shares. Remote side effects are append-ordered writes to storage bucket writers: header, blocks, crypttext hashes, block hashes, share hashes, UEB, close/abort.

## Dependencies And Integration Points
Depends on Twisted Deferreds, Foolscap `fireEventually`, `CRSEncoder`, Tahoe URI and hash utilities, `HashTree`, storage bucket writer interfaces, upload status, `happinessutil.servers_of_happiness`, and `UploadUnhappinessError`. Server selection/upload code creates the encoder and passes landlords/servermap; downloader/checker validate the UEB/hash-tree layout it writes.

## Risks And Edge Cases
`segment_size` must be divisible by required shares. Tail encoding pads encrypted data to a multiple of `k` and must match downloader tail calculations. The code intentionally generates all shares to compute roots even if not all shares have landlords. Upload abort only takes effect before/during next data gather and TODO notes it is too late after final segment shares are sent. `_gather_responses()` avoids swallowing non-happiness errors but consumes `UploadUnhappinessError` to let DeferredList semantics work. Long uploads rely on bucket writers preserving append order.

## Test Signals
`src/allmydata/test/test_encode.py` targets UEB/encoding details. `src/allmydata/test/test_upload.py` covers encoder bucket aborts, shareholder failure, happiness enforcement, placement interactions, and upload result behavior. Codec tests cover CRS primitives.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/encode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/filenode.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/filenode.py

## Purpose
Provides user-facing immutable file node wrappers. `CiphertextFileNode` reads/checks encrypted CHK content by verifycap; `ImmutableFileNode` wraps it with the read key to expose plaintext reads and immutable filesystem node APIs.

## Important APIs, Types, And Functions
`CiphertextFileNode` lazily creates a `DownloadStatus` and `DownloadNode` on first read/segment access. It exposes `read`, `get_segment`, `get_segment_size`, verifycap/size/storage-index accessors, `check`, and `check_and_repair`.

`DecryptingConsumer` implements `IConsumer` and `IDownloadStatusHandlingConsumer`. It wraps a downstream consumer, constructs an AES CTR decryptor positioned to the requested offset, passes producer registration through, decrypts each ciphertext chunk in `write()`, and records decrypt timing.

`ImmutableFileNode` implements `IImmutableFileNode`. It stores the CHK read cap and read key, delegates reads through `DecryptingConsumer`, exposes URI/cap/readcap/verifycap/repair-cap/size methods, immutable/read-only predicates, check/repair delegation, and `download_best_version`/`download_to_data`.

## Control Flow
Reading plaintext creates a `DecryptingConsumer`, calls ciphertext node `read()`, and maps the callback back to the original consumer. The ciphertext node creates shared download status/node if needed, adds download status to history, and delegates range reads or segment fetches.

Checking constructs a `Checker` over connected servers and starts it. `check_and_repair()` runs the checker, returns unchanged results if healthy, or starts `Repairer` and merges original check results with upload repair results in `_gather_repair_results()`.

Repair result gathering builds a new sharemap by unioning pre-existing good shares and newly uploaded shares, recomputes good hosts, health, recoverability, servers-of-happiness, corrupt/incompatible counts, and fills `CheckAndRepairResults`.

## State And Persistence
`CiphertextFileNode` keeps one lazily initialized `DownloadNode` and `DownloadStatus`, so multiple reads share learned UEB/hash/share state. `ImmutableFileNode` stores immutable cap and read key only. Repair can cause remote writes through `Repairer`; check can renew leases when requested through `Checker`.

## Dependencies And Integration Points
Depends on CHK URI classes, AES crypto, Twisted Deferreds, consumer utilities, `Checker`, `Repairer`, `DownloadNode`, `DownloadStatus`, `CheckResults`, `CheckAndRepairResults`, `DictOfSets`, and `servers_of_happiness`. Client, directory, web, and system layers use `IImmutableFileNode`.

## Risks And Edge Cases
`DecryptingConsumer` manually advances AES CTR for unaligned offsets; offset arithmetic must match encryption. `__ne__` appears to return `self.u.__eq__(other.u)` for another immutable node, which is logically inverted relative to `__eq__`. Repair health uses `len(sm) >= total_shares` for healthy, mirroring checker semantics, and may not indicate ideal distribution beyond happiness count. Download status/history are only created on demand.

## Test Signals
`src/allmydata/test/test_filenode.py` covers immutable equality/interfaces. `test_download.py`, `test_system.py`, `test_client.py`, and directory/web tests exercise reads, downloads, and node integration. Repair behavior is covered in `test_repairer.py`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/filenode.py -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/happiness_upload.py -->
# sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/happiness_upload.py

## Purpose
Computes share placement for immutable uploads with "servers of happiness" goals. It uses max-flow matching to maximize unique server coverage, preserve read-only/existing allocations when useful, and distribute unmatched shares.

## Important APIs, Types, And Functions
Graph helpers: `bfs(graph, s)`, `augmenting_path_for(graph)`, and `residual_network(graph, f)` implement Edmonds-Karp max-flow machinery over adjacency-list graphs with unit capacities.

Placement helpers: `_reindex()`, `_flow_network()`, `_servermap_flow_graph()`, `_compute_maximum_graph()`, `_convert_mappings()`, `_calculate_mappings()`, `_extract_ids()`, and `_distribute_homeless_shares()`.

Public functions: `calculate_happiness(mappings)` returns the count of unique non-None peers in a share-to-peer map. `share_placement(peers, readonly_peers, shares, peers_to_shares)` returns `{share_num: peer_id}` for upload/renewal placement.

## Control Flow
`share_placement()` returns empty placement when no peers are writable/readable. It first computes mappings for read-only servers and their existing shares, preserving renewals where possible. It removes used peers/shares, builds a servermap for remaining existing allocations, computes a second max-flow mapping to preserve useful existing read-write placements, then maps remaining shares to remaining peers with a complete bipartite flow graph.

The three mapping sets are merged. Shares mapped to `None` are "homeless": `_distribute_homeless_shares()` first renews existing placements if the share already exists, then uses a priority queue to balance remaining homeless shares across read-write peers with the fewest assigned shares. Any still-None mappings are assigned by round-robin over writable peers.

`_compute_maximum_graph()` repeatedly finds augmenting paths in the residual network, updates the flow matrix, rebuilds residual graph/capacity, then derives share-to-peer assignments from residual edges.

## State And Persistence
All data structures are local and non-persistent. Inputs are sets and maps of peer/share IDs; outputs are placement decisions consumed by upload/server-selection code. Existing allocations in `peers_to_shares` are treated as renewals, not modified directly here.

## Dependencies And Integration Points
Uses `queue.PriorityQueue`. Upload/server-selection code calls `share_placement`; `encode.Encoder` later enforces happiness after remote failures with `happinessutil.servers_of_happiness`. The algorithm references `docs/specifications/servers-of-happiness.rst`.

## Risks And Edge Cases
The graph code assumes adjacency-list indices are dense and derived from `_reindex()`. `_servermap_flow_graph()` uses an `indexedShares` list built across peers without resetting inside the peer loop, which may intentionally or accidentally accumulate edges; tests should guard behavior. The final round-robin uses `peers - readonly_peers`; if that set is empty while None mappings remain, iteration would not yield. Placement uses sets, so deterministic order relies on sorted loops only in some phases.

## Test Signals
`src/allmydata/test/test_happiness.py` directly covers graph helpers, residual networks, servermap flow graphs, placement with read-only peers, existing allocations, homeless shares, and happiness calculation. Upload tests in `test_upload.py` and repair tests exercise integration with server selection and happiness failure messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/tahoe-lafs/src/allmydata/immutable/happiness_upload.py -->
