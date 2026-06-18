# sources/cloud-native/ostree/src/libostree/ostree-fetcher-util.c

## Purpose
This file provides synchronous and retrying helpers around the asynchronous fetcher API, plus HTTP failure journald logging and status-to-`GIOErrorEnum` mapping.

## Important APIs, Types, And Functions
`FetchUriSyncData` captures async completion state for a private main context. `fetch_uri_sync_on_complete()` calls the async finish function and wakes the context. `_ostree_fetcher_mirrored_request_to_membuf_once()` runs one async memory request synchronously, handles optional-content 404 as success with `NULL`, and transfers ETag/Last-Modified/not-modified outputs. `_ostree_fetcher_mirrored_request_to_membuf()` loops with retry classification. `_ostree_fetcher_request_uri_to_membuf()` wraps a single URI into a mirror list. `_ostree_fetcher_journal_failure()` emits structured systemd journal messages. `_ostree_fetcher_should_retry_request()` identifies transient errors. `_ostree_fetcher_http_status_code_to_io_error()` maps HTTP statuses.

## Control Flow, State, And Persistence
The sync helper pushes a new thread-default `GMainContext`, starts the fetch, iterates until completion, then pops and cleans state. Retry count is decremented by the caller loop. Journald output persists operational failure records when systemd support is enabled through otutil.

## Dependencies And Integration Points
It depends on GIO Unix output streams, optional systemd journal APIs, fetcher util header, and otutil. Repository pull/summary code uses these helpers for metadata fetches where synchronous control flow is simpler.

## Risks And Test Signals
The retry loop uses unsigned decrement in the condition, so tests should verify zero and nonzero retry counts. Optional content only suppresses not-found errors. Tests should cover transient classifications, HTTP mappings with retry-all, cancellation before request, out-argument cleanup on failure, journald skip for local/no-remote cases, and not-modified metadata propagation.
