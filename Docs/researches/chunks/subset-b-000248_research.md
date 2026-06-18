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
