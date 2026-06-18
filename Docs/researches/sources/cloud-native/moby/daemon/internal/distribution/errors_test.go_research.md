# sources/cloud-native/moby/daemon/internal/distribution/errors_test.go

## Purpose
Tests endpoint fallback decisions for distribution errors.

## APIs, Control Flow, and Integration
The tests define errors that should always continue, only continue from mirror endpoints, and never continue. They run `continueOnError` with mirror and non-mirror settings to verify unauthorized/name-unknown behavior, unexpected HTTP response fallback, image config pull fallback, unsupported media type blocking, cancellation/deadline blocking, and unexpected error fallback.

## State, Dependencies, and Risks
No external state. Coverage is intentionally narrow to fallback control. It does not verify `translatePullError`, `retryOnError`, or daemon error interface markers beyond their effect on fallback decisions.
