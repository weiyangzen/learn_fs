<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/retryhandler/retry.go -->
# sources/cloud-native/buildkit/util/resolver/retryhandler/retry.go

Purpose: wraps image descriptor handlers with exponential retry for transient registry/network failures.

Important APIs and types: package variable `MaxRetryBackoff`, `New`, and `retryError`.

Control flow: the wrapper calls the underlying handler, returns immediately on success or non-retryable error, logs errors/retry delays when logger is supplied, sleeps with exponential backoff starting at one second, and stops once backoff reaches `MaxRetryBackoff`. Context cancellation short-circuits with the current error.

State and persistence: no persistence; `MaxRetryBackoff` is mutable global configuration for embedders.

Dependencies and integration: used by pull and push handlers around limited fetch/push operations. Recognizes containerd unexpected 5xx statuses, `io.EOF`, connection reset/pipe/closed errors, and temporary net errors.

Risks: uses `time.Sleep` rather than a context-aware timer, so cancellation during sleep is not observed until after sleep returns. Retry budget is time/backoff based, not attempt-count based.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/util/resolver/retryhandler/retry.go -->
