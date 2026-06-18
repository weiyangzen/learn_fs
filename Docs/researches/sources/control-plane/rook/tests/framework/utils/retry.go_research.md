# sources/control-plane/rook/tests/framework/utils/retry.go

Purpose: this file provides a small generic retry helper for test predicates.

Important APIs/types/functions: `Retry(count uint16, wait time.Duration, description string, f func() bool) bool`.

Control flow: the helper calls `f` up to `count` times. It returns true immediately on the first true result, logging the attempt number. On false, it logs and sleeps for `wait`. If all attempts fail, it logs final failure and returns false.

State and persistence behavior: no persistence. The callback can have arbitrary side effects; `Retry` itself only logs and sleeps.

Dependencies and integration points: depends on package logger from `exec_utils.go`. Used wherever tests need a concise polling loop outside the richer Kubernetes wait helpers.

Risks: only boolean success is supported, so error details must be logged inside the callback or are lost. Sleeps occur after every failed attempt including the last failed callback before final return. `uint16` count is unusual and can truncate larger configured retry values if cast by callers.

Test signals: retry count, early success behavior, wait interval usage, and log messages are straightforward to validate with a stub callback.
