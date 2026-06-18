# sources/cloud-native/ostree/src/libostree/ostree-repo-pull.c lines 1-6429

## Scope And Purpose

This chunk contains the main implementation of libostree remote pulling when built with libcurl or libsoup, plus the beginning of the summary-fetch API near the chunk boundary. It covers object fetch scheduling, metadata scanning, local repository imports, static delta discovery and execution, summary and signature loading/caching, the public `ostree_repo_pull_with_options()` entry point, collection-aware remote discovery, and multi-remote pull orchestration.

The chunk is centered on turning refs or explicit commit checksums into durable OSTree repository state. It resolves refs from a remote summary, `refs/heads`, `refs/mirrors`, or a local repo; verifies summary and commit signatures; chooses static deltas or loose object fetches; imports or writes objects; updates refs in a transaction; and reports progress and journal telemetry. Lines 6300-6429 start `ostree_repo_remote_fetch_summary_with_options()` but stop mid-call while fetching `summary.sig`, so that function's completion and later compatibility wrappers are outside this chunk.

## Important Types And State

`OtPullData`, defined in `ostree-repo-pull-private.h`, is the central mutable state object passed through this file. This chunk initializes and mutates its repo pointers, remote names, mirror lists, fetcher, progress object, cancellable, signature verifier arrays, summary bytes/variants, delta checksum table, requested/scanned object sets, pending fetch queues, outstanding request counters, imported/fetched statistics, timestamp-check state, subdir filters, async error storage, and GLib idle source.

Local request structs model specific asynchronous units:

- `FetchObjectData` carries a serialized object name, object path, detached-metadata mode, already-stored flag, requested collection ref, and retry count for metadata or content fetches.
- `FetchStaticDeltaData` carries static delta part state: object list, expected part checksum, from/to revisions, part index, size, and retry count.
- `ScanObjectQueueData` stores a metadata checksum, object type, current path, recursion depth, and optional requested ref for deferred commit/dirtree scanning.
- `FetchDeltaSuperData` and `FetchDeltaIndexData` describe async fetches for static delta superblocks and delta indexes.
- `CommitMetadata`, `PointerTable`, and `FindRemotesData` support `ostree_repo_find_remotes_async()` by tracking summary-derived commit metadata, a ref-by-remote checksum grid, and async resolver inputs.

The important hash tables are behavioral state, not caches only. `requested_metadata` and `requested_content` deduplicate network/import requests; `scanned_metadata` prevents repeated recursion over shared trees; `fetched_detached_metadata` records whether commit metadata was attempted and stores detached signature metadata when present; `commit_to_depth` enforces history traversal depth; `static_delta_targets` suppresses redundant dirtree scanning for commits supplied by deltas; `pending_fetch_*` tables are backpressure queues drained by `check_outstanding_requests_handle_error()`.

## Pull Control Flow

`ostree_repo_pull_with_options()` is the main synchronous public entry point in this chunk. It parses a large `a{sv}` option set, validates incompatible combinations, initializes `OtPullData`, builds local-cache repo handles and subdir filters, loads remote GPG/signapi settings, creates an `OstreeFetcher`, computes metadata and content mirror lists, detects local `file://` remotes, sets trusted/untrusted import behavior, resolves requested refs or explicit commits, loads and verifies summaries when needed, initializes delta metadata, starts a repository transaction, queues work, iterates the GLib main context until idle, updates refs, optionally mirrors summary files, commits the transaction, clears `.commitpartial` markers, and tears down all owned state.

The fetch loop is event driven:

1. `initiate_request()` decides whether to queue a loose commit metadata scan or static delta request, based on `disable-static-deltas`, `require-static-deltas`, indexed deltas, summary deltas, and local from-revision availability.
2. `queue_scan_one_metadata_object*()` pushes commits and dirtrees into `scan_object_queue`; `ensure_idle_queued()` attaches `idle_worker()` when fetch/write capacity allows more scanning.
3. `idle_worker()` pops scan tasks and calls `scan_one_metadata_object()`, then funnels errors and queue draining through `check_outstanding_requests_handle_error()`.
4. `scan_one_metadata_object()` checks local storage, imports from local remote or local cache when possible, queues missing objects, fetches detached commit metadata before scanning stored commits, and delegates stored commits and dirtrees to `scan_commit_object()` or `scan_dirtree_object()`.
5. `enqueue_one_object_request()` creates `FetchObjectData`, increments requested counters, and either starts `_ostree_fetcher_request_to_tmpfile()` or stores the request in a pending table when `fetcher_queue_is_full()`.
6. Completion callbacks parse/verify/write objects, decrement outstanding counters, retry transient network errors through `_ostree_fetcher_should_retry_request()`, and call `check_outstanding_requests_handle_error()` to launch the next queued work.

`pull_termination_condition()` returns true once no fetches, writes, or scan tasks remain; in dry-run mode it exits after progress has been emitted. Errors are latched in `pull_data->cached_async_error` and `caught_error`; once caught, queued scan and pending fetch tables are cleared while in-flight operations drain.

## Object Fetching And Metadata Scanning

`scan_dirtree_object()` loads a stored `OSTREE_OBJECT_TYPE_DIR_TREE`, validates file and directory names, applies `subdir`/`subdirs` filtering through `pull_matches_subdir()` and `matches_pull_dir()`, checks whether each file object already exists, imports content from local repositories when available, or queues content fetches. It queues child dirtree and dirmeta metadata for directories. It intentionally still validates older on-disk metadata even though newer write paths validate structure earlier.

`scan_commit_object()` verifies GPG or signapi commit signatures if not already verified, loads and validates the commit object, verifies collection/ref binding unless disabled, enforces timestamp checks, records parent traversal depth, and queues root tree metadata when the commit is partial, not commit-only, and not already a static-delta target. Commit partiality is broadened by `legacy_transaction_resuming`, so resumed legacy transactions force scanning.

`meta_fetch_on_complete()` handles fetched metadata tmpfiles. It special-cases missing detached commit metadata as non-fatal, records the attempt, and proceeds to fetch or scan the commit. Missing parent commits during bounded history traversal can be tolerated and optionally followed by tombstone commit fetch/import. Non-detached metadata is parsed as the expected variant type, verified structurally and by checksum before staging, commit signatures are verified before writing, and commits are marked partial before async metadata write. `on_metadata_written()` verifies the final checksum and queues the object for scanning.

`content_fetch_on_complete()` handles file objects. In trusted HTTP mirror-to-archive mode it can link the tmpfile directly into the archive repo. Otherwise it parses the content stream, optionally verifies bareuseronly mode, rebuilds an OSTree content stream, and writes it asynchronously. `content_fetch_on_write_complete()` checks the written checksum against the expected checksum and accounts for normal content versus static-delta fallback content.

Local import uses `async_import_one_local_content_object()` and `_ostree_repo_import_object()` in a `GTask` thread for content, while metadata import in `scan_one_metadata_object()` is synchronous. The import path honors `pull_data->importflags`, including trusted local import and bareuseronly verification.

## Static Delta Flow

Static delta selection starts in `initiate_request()` and `initiate_delta_request()`. `get_best_static_delta_start_for()` first treats a complete local target commit as unchanged, then scans summary/index delta names for deltas targeting the desired revision, prefers the newest complete local `from` commit, and falls back to a scratch delta when available. If deltas are required and no usable delta exists, `set_required_deltas_error()` produces a hard failure.

Delta indexes are fetched by `start_fetch_delta_index()` and parsed in `on_delta_index_fetched()`. Delta superblocks are fetched by `start_fetch_delta_superblock()` and processed in `on_superblock_fetched()`, which optionally verifies the superblock digest against the summary's static delta checksum table and requires summary signatures if GPG summary verification is enabled. Missing optional superblocks fall back to commit object scanning unless static deltas are required.

`process_one_static_delta()` parses the superblock, accounts fallback objects first, writes the target commit metadata when missing after verifying it and marking it partial, then iterates part headers. Already satisfied parts only update progress counters. Inline parts are opened from metadata bytes and executed directly; external parts queue `FetchStaticDeltaData` for `start_fetch_deltapart()`. `static_deltapart_fetch_on_complete()` opens and checksum-verifies fetched delta parts, then runs `_ostree_static_delta_part_execute_async()`. After parsing all parts, the function compares required uncompressed delta space with filesystem free blocks and fails early if insufficient.

Fallback objects in `process_one_static_delta_fallback()` are deliberately limited to content objects. Metadata fallbacks are rejected because the delta compiler should not generate them. Missing fallback content is queued as a normal content fetch while also recorded in `requested_fallback_content` for delta progress accounting.

## Summary, Remote Configuration, And Caching

Remote metadata is loaded from summaries where possible. `lookup_commit_checksum_and_collection_from_summary()` resolves a requested `OstreeCollectionRef` from the primary summary refs or collection map, validates collection IDs and checksum variants, and records expected commit size for later maximum-size fetch enforcement.

`fetch_ref_contents()` is the fallback ref resolver. Local remotes use `ostree_repo_resolve_collection_ref()` or `ostree_repo_resolve_rev_ext()`. HTTP remotes fetch `refs/heads/<ref>` or `refs/mirrors/<collection>/<ref>` from `meta_mirrorlist`, validate UTF-8, chomp, and validate the checksum string.

Summary support includes:

- `_ostree_repo_verify_summary()` for GPG and signapi summary verification.
- `_ostree_repo_load_cache_summary_properties()` to read cached ETag and last-modified data from `cache/summaries`, using `user.etag` xattrs and stat mtime.
- `_ostree_repo_load_cache_summary_file()` and `_ostree_repo_load_cache_summary_if_same_sig()` to reuse cached summaries when signatures match.
- `_ostree_repo_save_cache_summary_file()` and `_ostree_repo_cache_summary()` to persist summary and signature bytes with cache properties.
- `_ostree_preload_metadata_file()` to fetch summary-like metadata either via metalink or mirrored fetcher requests.

`ostree_repo_pull_with_options()` can also accept `summary-bytes` and `summary-sig-bytes` to avoid repeated summary downloads in transaction batching. It retries cached summaries on signature verification failure by forcing a fresh summary download unless test error flags deliberately force invalid-cache failure.

Fetcher setup is centralized in `_ostree_repo_remote_new_fetcher()`. It reads remote options for TLS permissiveness, HTTP/2, client certificates, low-speed timeouts, retry-all behavior, max outstanding requests, CA pinning, proxy, cookie jar, extra headers, and user-agent extension. It returns an `OstreeFetcherSecurityState` used later for systemd journal messages.

Mirror handling flows through `compute_effective_mirrorlist()`, `fetch_mirrorlist()`, and metalink setup. Mirrorlists are text files of HTTP(S) URLs; the code ignores blank/comment/unparseable/non-HTTP entries and probes the first usable mirror by fetching `config`.

## Public APIs In This Chunk

`ostree_repo_pull_with_options()` exposes the main pull operation with options for refs, collection refs, pull flags, subdir filtering, remote override, GPG/signapi verification controls, history depth, fsync behavior, static delta policy, override commit IDs, timestamp checks, metadata limits, dry-run, URL override, transaction inheritance, HTTP headers, progress update frequency, local cache repos, user agent, network retries, low-speed behavior, ref-keyring mapping, preloaded summary bytes, and binding verification.

`ostree_repo_resolve_keyring_for_collection()` searches configured remotes for a matching `collection-id` and returns the first remote with a usable keyring. It is compiled to an unsupported error when GPGME is disabled.

`ostree_repo_find_remotes_async()` starts asynchronous discovery for collection refs using configured finders, mount finders, and optionally Avahi LAN finders. It validates inputs, constructs default finders from `self->repo_finders`, starts Avahi when available, then calls `ostree_repo_finder_resolve_all_async()`.

`ostree_repo_find_remotes_finish()` returns the zero-terminated result array produced by the async discovery task.

`ostree_repo_pull_from_remotes_async()` consumes finder results, builds per-remote `collection-refs` pull options, forces untrusted pull plus commit GPG verification, disables summary verification for those pulls, copies selected caller options, and synchronously calls `ostree_repo_pull_with_options()` for each result inside one transaction. It marks refs as pulled only when a remote succeeds and reports a failure listing refs still unpulled.

`ostree_repo_pull_from_remotes_finish()` propagates the boolean result for the async wrapper.

`ostree_repo_remote_fetch_summary_with_options()` begins in this chunk and sets up option parsing, summary verification policy, signapi summary verifiers, a temporary main context, a gzip-enabled fetcher, metalink or mirrorlist resolution, and cached ETag/mtime headers before starting to preload `summary.sig`. The rest of this function is outside the assigned range.

## Remote Finder Control Flow

`find_remotes_cb()` validates discovered remotes beyond the initial finder claims. It temporarily adds dynamic remotes to the repo so existing remote APIs can fetch their summaries, downloads each summary, filters invalid or summary-less results, processes primary summary refs and collection-map refs, and rejects refs from dynamic remotes whose inherited keyring remote does not match the summary collection ID.

`find_remotes_process_refs()` validates ref names, checksum variants, commit sizes, and timestamps. It builds `CommitMetadata` keyed by checksum, stores the mapping from requested ref index and result index to checksum in `PointerTable`, and rejects inconsistent size/timestamp data across remotes.

If a commit timestamp is unknown from summary metadata or local storage, `find_remotes_cb()` downloads the commit metadata from candidate remotes in priority order and verifies the commit for that remote. It then picks the latest commit per requested ref by timestamp, rebuilds each result's `ref_to_checksum` and `ref_to_timestamp` so remotes only advertise refs for which they have the latest commit, drops remotes with no latest refs, sorts final results, removes temporary remotes, and completes the `GTask`.

## Persistence And Transactions

Pulls persist multiple classes of state:

- Object data and metadata are written through `ostree_repo_write_content_async()`, `ostree_repo_write_metadata_async()`, `_ostree_repo_commit_tmpf_final()`, `_ostree_repo_import_object()`, and static delta execution.
- Commits are marked partial before metadata/body completion and unmarked at the end for full non-subdir, non-commit-only pulls. Parent commits reached by depth traversal are also unmarked.
- Ref updates are staged with `ostree_repo_transaction_set_ref()` or `ostree_repo_transaction_set_collection_ref()` and committed in a repository transaction unless `inherit-transaction` is true.
- Mirror pulls can persist remote `summary` and `summary.sig` into the destination repo, preserving cache properties.
- Summary cache files under the repo cache directory are replaced atomically and annotated with ETag and last-modified metadata.
- Local-cache and local-remote imports can write objects without network transfer while preserving pull accounting.

Failure cleanup is transactional at the repo level: unless transaction inheritance is used, `ostree_repo_abort_transaction()` runs on exit regardless of `ret`; after a successful commit there should be no active transaction to abort. Async errors are propagated from `cached_async_error` only if the synchronous error slot is still empty.

## Dependencies And Integration Points

This chunk integrates tightly with GLib/GIO (`GVariant`, `GHashTable`, `GPtrArray`, `GTask`, `GMainContext`, `GSource`, `GCancellable`, `GError`, `GInputStream`), libglnx file helpers, OSTree core validation and object serialization, repo transaction APIs, repo import APIs, static delta private APIs, fetcher URI and request APIs, GPGME verification when enabled, signapi verification, metalink support, optional Avahi repo discovery, and optional systemd journal logging.

External contracts include OSTree summary variant formats, static delta superblock and index formats, loose object paths, `refs/heads` and `refs/mirrors` layout, remote config keys (`metalink`, `contenturl`, `branches`, TLS/proxy/fetcher settings, `collection-id`, `indexed-deltas`, `mode`, `tombstone-commits`), HTTP cache validators, and filesystem free-space reporting via `fstatvfs()`.

The source is compiled only when `HAVE_LIBCURL_OR_LIBSOUP` is true for most pull functionality. Some collection keyring helpers are available outside that block, with GPG-disabled fallbacks gated by `OSTREE_DISABLE_GPGME`.

## Risks And Edge Cases

- The option lookup for `max-outstanding-fetcher-requests` uses variant type `"b"` while documentation describes `"u"` in both the pull and summary-fetch paths in this chunk. That can reject callers passing the documented unsigned integer option or collapse the value to boolean-sized semantics depending on GLib behavior.
- `fetcher_queue_is_full()` compares outstanding fetches to `max_outstanding_fetcher_requests` using equality, not greater-than-or-equal. Unexpectedly low or malformed limits could interact poorly with already outstanding requests.
- The summary remote-mode fallback branch is compatibility-sensitive: around lines 4489-4511 the code loads remote `config` under a condition named `remote_mode_loaded`, although the comment describes a fallback load. Verify intended behavior when summaries omit mode/tombstone metadata.
- Async error handling intentionally preserves only the first error. Later failures are cleared, which is correct for avoiding overwrite but can hide secondary corruption signals during debugging.
- Detached commit metadata absence is treated as optional, but the fetch attempt is still recorded. Changes to commit signature policy must preserve the distinction between "no detached metadata" and "not attempted".
- Parent commit ENOENT is tolerated only during depth traversal and optionally tombstone-aware paths. Incorrect `commit_to_depth` entries can change whether missing commits are fatal.
- `trusted_http_direct` bypasses content stream parsing/checksumming for archive mirror imports under trusted settings. This is a performance path with a larger trust boundary.
- Static delta free-space checking uses total uncompressed delta size accumulated for the pull data, not just one remaining part at a time. It is conservative but may be imprecise when several deltas or already-present objects are involved.
- The static delta fallback path forbids metadata fallback objects; a producer emitting such deltas will fail pulls rather than silently accept them.
- `find_remotes_cb()` fetches summaries and missing commit metadata serially and has FIXME notes about parallelism and missing support for `contenturl` and mirrorlist when downloading commit metadata for finder validation.
- `ostree_repo_pull_from_remotes_async()` is an async-looking API backed by synchronous pulls inside the callback path. Cancellation is checked through underlying calls, but the API can still occupy the caller's context longer than a fully async implementation would.
- Subdir pulls intentionally leave commits partial and do not clear `.commitpartial` markers at the end, because not all content was fetched.

## Test Signals

Useful focused tests for this chunk include:

- Pull a ref over HTTP with a signed summary and commit signatures enabled; verify summary cache reuse, detached metadata fetch, commit verification, object writes, ref update, and `.commitpartial` cleanup.
- Repeat with an invalid cached summary and valid remote summary to confirm forced re-download and cache replacement behavior; cover the test-error invalid-cache branch.
- Pull from a `file://` repo and a `localcache-repos` source to exercise local import accounting and trusted/untrusted import flags without network fetches.
- Exercise `subdir` and `subdirs` pulls over dirtrees containing prefix collisions such as `/foo` and `/fooo` to validate `matches_pull_dir()`.
- Test static delta paths for indexed deltas, summary deltas, scratch deltas, from-revision deltas, missing optional deltas with loose-object fallback, and `require-static-deltas` failure.
- Corrupt static delta superblock checksums, delta part checksums, fallback object types, and low free-space conditions to validate hard failures.
- Verify timestamp-check and timestamp-check-from-rev reject older commits and only run under supported depth/ref conditions.
- Validate `ref-keyring-map` and `ostree_repo_resolve_keyring_for_collection()` with duplicate matching remotes, missing keyrings, `/dev/null` keyrings, and dynamic remotes whose inherited collection ID does not match.
- Run repo-finder tests with config, mount, and Avahi-disabled/default finders; include remotes with stale refs so `find_remotes_cb()` drops non-latest refs after timestamp comparison.
- Test `ostree_repo_pull_from_remotes_async()` with multiple results where the first remote fails some refs and a later remote succeeds, then verify final transaction behavior and the unpulled refs error path.
- Add API tests for the documented `max-outstanding-fetcher-requests` unsigned option to catch the `"b"`/`"u"` type mismatch.
- Build with `OSTREE_DISABLE_GPGME` and without Avahi to cover compile-time fallback paths and unsupported GPG errors.
