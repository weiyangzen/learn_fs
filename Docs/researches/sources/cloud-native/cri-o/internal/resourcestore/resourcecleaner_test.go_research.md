# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner_test.go

Purpose: validates `ResourceCleaner` callback invocation and retry behavior.

Important APIs/types/functions: tests `NewResourceCleaner`, `Add`, and `Cleanup`.

Control flow: specs add callbacks that set booleans, callbacks that fail twice before success, and a callback that always fails. Assertions check final error state and call counts.

State and persistence behavior: in-memory counters and booleans only.

Dependencies and integration points: uses context.Background, Ginkgo/Gomega, and the test-build retry budget.

Risks: tests do not assert reverse cleanup order or context cancellation behavior. Backoff timing can still slow tests if retry defaults leak in.

Test signals: demonstrates retry-until-success and failure after exactly three attempts under the test build tag.
