# Research: sources/cloud-native/ostree/src/libostree/ostree-repo-pull.c

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000247`: lines 1-6429, `Docs/researches/chunks/subset-b-000247_research.md`
- `subset-b-000248`: lines 6430-6594, `Docs/researches/chunks/subset-b-000248_research.md`

## Chunk Research

### subset-b-000247: lines 1-6429

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

### subset-b-000248: lines 6430-6594

# sources/cloud-native/ostree/src/libostree/ostree-repo-pull.c lines 6430-6594

## Scope And Purpose

This chunk covers the end of `ostree_repo_remote_fetch_summary_with_options()` when HTTP fetching support is compiled in, followed by the fallback implementations compiled when `HAVE_LIBCURL_OR_LIBSOUP` is not defined. The boundary matters: lines 6430-6508 are still in the network-capable implementation and finish summary/signature cache handling, verification, optional cache persistence, and output transfer. Lines 6510-6594 are the no-fetcher build path, where public pull and remote discovery APIs remain exported but fail deterministically with `G_IO_ERROR_NOT_SUPPORTED`.

The purpose of the fallback branch is ABI/API continuity. Consumers can link against `ostree_repo_pull_with_options()`, `ostree_repo_remote_fetch_summary_with_options()`, `ostree_repo_find_remotes_async()`, `ostree_repo_find_remotes_finish()`, `ostree_repo_pull_from_remotes_async()`, and `ostree_repo_pull_from_remotes_finish()` even in builds that omit libsoup/libcurl. Instead of partially implementing remote I/O, each entry point reports that the build cannot fetch over HTTP.

The preceding summary-fetch tail is important context for what the fallback replaces. In fetcher-enabled builds, `ostree_repo_remote_fetch_summary_with_options()` downloads `summary.sig` and `summary`, supports conditional requests using cached ETag/Last-Modified values, verifies the summary with GPG and signapi policy, caches new summary data when possible, and returns `GBytes` for the raw summary and signature to callers.

## Important APIs, Types, And Functions

`ostree_repo_remote_fetch_summary_with_options()` returns raw `summary` and `summary.sig` bytes for a configured remote. In the normal implementation, the visible tail uses `GBytes` ownership transfer through `g_steal_pointer()`, `GCancellable`, `GError`, and helper APIs such as `_ostree_preload_metadata_file()`, `_ostree_repo_load_cache_summary_file()`, `_ostree_repo_load_cache_summary_if_same_sig()`, `_ostree_repo_verify_summary()`, and `_ostree_repo_cache_summary()`. In the fallback implementation, the same public signature is preserved but no validation or output assignment occurs; it sets a not-supported error and returns `FALSE`.

`ostree_repo_pull_with_options()` is the main synchronous pull API. The full implementation earlier in the file consumes a `GVariant` `a{sv}` options dictionary, configures `OtPullData`, fetches refs, commits, metadata, content, and deltas, and manages transactions/progress. The fallback body ignores all operational parameters except the `GError **` output, sets `G_IO_ERROR_NOT_SUPPORTED`, and returns `FALSE`.

`ostree_repo_find_remotes_async()` and `ostree_repo_find_remotes_finish()` are the async discovery pair for `OstreeRepoFinderResult` arrays. In network-capable builds, discovery can use configured remotes, mounts, and Avahi when enabled. In this fallback, the async starter validates only `OSTREE_IS_REPO(self)` and immediately completes via `g_task_report_new_error()`. The finish method validates the task source tag, propagates a pointer result, asserts that the result is `NULL`, and returns `NULL`.

`ostree_repo_pull_from_remotes_async()` and `ostree_repo_pull_from_remotes_finish()` are the async multi-remote pull pair used after remote discovery. In network-capable builds, the async starter wraps synchronous `ostree_repo_pull_with_options()` calls in an overall transaction, pulls each still-unpulled collection ref from priority-ordered finder results, and reports success only when all refs are pulled. In this fallback, the async starter immediately reports `G_IO_ERROR_NOT_SUPPORTED`; the finish method propagates a boolean, asserts it is false, and returns `FALSE`.

The principal GLib types in this range are `GTask`/`GAsyncResult` for async result tagging and completion, `GError` for structured failure, `GVariant` for option dictionaries, `GBytes` for immutable summary payloads, and `GPtrArray` for the normal find-remotes result container. OSTree-specific types include `OstreeRepo`, `OstreeAsyncProgress`, `OstreeCollectionRef`, `OstreeRepoFinder`, and `OstreeRepoFinderResult`.

## Control Flow

The summary-fetch tail first handles the result of preloading `summary.sig`. If the server returned a not-modified response for the signature, the code clears any downloaded `signatures` and `summary` bytes, then reloads `summary.sig` and `summary` from the local cache. If signatures are available but summary bytes are not, `_ostree_repo_load_cache_summary_if_same_sig()` attempts to reuse the cached summary only if it corresponds to the fetched signature.

If a summary is already available after the signature/cache checks, `summary_is_from_cache` is set. Otherwise, the code preloads the `summary` metadata file, passes conditional request validators, and reloads summary bytes from cache on a not-modified response. It then verifies the summary using the remote's GPG summary policy and signapi summary verifiers. New non-cache summary/signature pairs are cached with ETag and Last-Modified metadata; permission-denied while saving the cache is downgraded to a debug message, while other cache errors fail the API call.

Successful normal summary fetch exits by transferring ownership to `out_summary` and `out_signatures` when those locations are non-`NULL`, then returning `TRUE`. The use of `g_autoptr` plus `g_steal_pointer()` ensures unreturned temporary bytes are unreffed while returned bytes remain owned by the caller.

The no-fetcher branch has intentionally shallow control flow. Both synchronous APIs call `g_set_error_literal(error, G_IO_ERROR, G_IO_ERROR_NOT_SUPPORTED, "...cannot fetch over HTTP")` and return `FALSE`. `ostree_repo_find_remotes_async()` validates `self`, then calls `g_task_report_new_error()` with `ostree_repo_find_remotes_async` as the source tag and the same not-supported message. Its finish function propagates the task pointer result, expects it to be absent, and returns `NULL`.

`ostree_repo_pull_from_remotes_async()` follows the same immediate-error pattern but should be read carefully: it validates `self`, then reports a new error. Its finish function expects a task tagged with `ostree_repo_pull_from_remotes_async`, propagates a boolean, asserts the propagated value is not successful, and returns `FALSE`.

## State And Persistence Behavior

The normal summary-fetch tail is the only part of this chunk that mutates persistent state. `_ostree_repo_cache_summary()` writes cached `summary` and `summary.sig` data, along with HTTP cache validators, into the repository's summary cache for the remote. This cache is an optimization and resilience layer for future summary fetches. Permission errors while saving it are explicitly non-fatal, which allows read-only or unprivileged callers to fetch and verify summaries without being able to update cache state.

The cache state is only updated when the summary was not loaded from cache and both `summary` and `signatures` are present. That condition prevents rewriting the cache with data already sourced from it and avoids caching incomplete summary data. The not-modified paths rely on existing cache contents; if the cache lookup fails when the server claims not-modified, the API fails rather than returning an unverifiable or missing payload.

The fallback branch does not start transactions, create temporary files, alter refs, update remote configuration, emit progress values, or cache summary data. Its state behavior is limited to allocating/completing `GTask` error results for async calls and setting `GError` for sync calls. This is important for builds without fetcher support: callers should see a clean capability failure, not a partially initialized pull.

## Dependencies And Integration Points

The conditional compilation boundary is controlled by `HAVE_LIBCURL_OR_LIBSOUP`, defined by the build configuration when either HTTP backend is available. Above the `#else`, this file depends on fetcher internals, metalink support, repository summary cache helpers, GPG/signapi verification helpers, and the large `OtPullData` pull engine. Below the `#else`, the code only needs the public OSTree/GLib types already visible through the file's base includes.

The exported symbols integrate with the public declarations in `src/libostree/ostree-repo.h` and with language bindings such as the Rust sys bindings. Command-line integration includes callers such as `src/ostree/ot-builtin-find-remotes.c`, which can call the async find/pull APIs. In a no-fetcher build, those callers must handle `G_IO_ERROR_NOT_SUPPORTED`.

`g_task_report_new_error()` is the key async integration point. It schedules or reports an already-failed `GTask` to the supplied callback while preserving the source object, callback, user data, source tag, domain, code, and message. Finish functions then use `g_task_is_valid()`, `g_async_result_is_tagged()`, and `g_task_propagate_pointer()` or `g_task_propagate_boolean()` to enforce that callers finish the matching async operation.

The summary-fetch path integrates with remote metadata caching and verification policy. `_ostree_repo_verify_summary()` ties the fetched bytes to configured GPG and signapi trust settings. `_ostree_repo_cache_summary()` ties HTTP cache metadata to future conditional summary fetches.

## Risks And Edge Cases

The most visible risk in this chunk is the source tag passed by fallback `ostree_repo_pull_from_remotes_async()`. It calls `g_task_report_new_error()` with `ostree_repo_find_remotes_async` as the source tag, while `ostree_repo_pull_from_remotes_finish()` validates that the result is tagged with `ostree_repo_pull_from_remotes_async`. In builds without libsoup/libcurl, a caller using the documented async/finish pair can therefore hit the finish-time tag precondition before the propagated `G_IO_ERROR_NOT_SUPPORTED` is delivered. The normal implementation sets the pull source tag correctly.

The synchronous fallback functions do not validate `self`, options, progress, cancellable, or output pointers before returning not-supported. This is consistent with a hard capability failure, but it means invalid-argument diagnostics differ from network-capable builds where many `g_return_*` checks and option validations run before work starts.

The fallback `ostree_repo_find_remotes_async()` validates only `self`, not `refs`, `options`, `finders`, `progress`, or `cancellable`. Again, this changes failure precedence: a no-fetcher build reports not-supported for many inputs that a full build might reject as programmer errors.

The normal summary-cache tail must preserve the distinction between `summary_sig_not_modified`, `summary_not_modified`, and `summary_is_from_cache`. Marking fetched-but-not-cached data as cached would skip cache persistence. Treating not-modified responses as usable without a valid local cache would produce missing data or trust decisions over absent bytes.

Cache writes are intentionally best-effort only for permission-denied. Other `_ostree_repo_cache_summary()` failures are propagated. Tests and callers should not assume summary fetch success always means cache persistence occurred, especially in read-only repositories or sandboxed environments.

## Test Signals

No-fetcher build tests should compile with `HAVE_LIBCURL_OR_LIBSOUP` undefined and call `ostree_repo_pull_with_options()` and `ostree_repo_remote_fetch_summary_with_options()`. Both should return `FALSE` and set `G_IO_ERROR_NOT_SUPPORTED` with the message that the build lacks libsoup or libcurl and cannot fetch over HTTP. They should not write refs, cache files, or transaction state.

Async fallback tests should call `ostree_repo_find_remotes_async()` and finish with `ostree_repo_find_remotes_finish()`, expecting a `NULL` result and `G_IO_ERROR_NOT_SUPPORTED`. A focused regression test should also cover `ostree_repo_pull_from_remotes_async()` followed by `ostree_repo_pull_from_remotes_finish()` in a no-fetcher build, because the source-tag mismatch in this chunk is exactly the kind of issue such a test would catch.

Summary-cache tests in fetcher-enabled builds should cover HTTP 304 handling for `summary.sig` and `summary`: when the remote reports not-modified, the function must load the corresponding cached bytes and still verify the summary. Tests should also cover the `signatures && !summary` path where the cached summary is reused only if it matches the signature.

Verification tests should ensure `_ostree_repo_verify_summary()` is still called before returning summary bytes, including cache-hit paths. Cache-persistence tests should distinguish permission-denied cache saves, which should not fail the fetch, from other cache write failures, which should propagate through `error`.

Ownership tests should verify that non-`NULL` `out_summary` and `out_signatures` receive live `GBytes` references on success, and that omitted output pointers do not leak. In the fallback implementation, output pointers should remain untouched because the function returns before assigning them.
