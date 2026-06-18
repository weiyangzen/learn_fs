# sources/cloud-native/cri-o/internal/resourcestore/resourcecleaner.go

Purpose: stores cleanup callbacks for a resource and runs them with bounded retry/backoff.

Important APIs/types/functions: `ResourceCleaner`, `cleanupFunc`, `NewResourceCleaner`, `Add`, `Cleanup`, and private `retry`.

Control flow: `Add` wraps a cleanup function in retry logging and prepends it, so cleanup runs in reverse add order. `Cleanup` executes functions sequentially and stops at the first final error. `retry` logs each attempt and uses Kubernetes `wait.ExponentialBackoff`.

State and persistence behavior: in-memory slice of callbacks only. No callback result is persisted, and callbacks decide their own external effects.

Dependencies and integration points: uses CRI-O contextual logging and `k8s.io/apimachinery/pkg/util/wait`. Used by `ResourceStore` to clean stale resources.

Risks: no synchronization around `funcs`, so callers should build a cleaner before concurrent cleanup. Retry treats all callback errors as retryable until the step budget is exhausted. Cleanup order is important for dependent resources.

Test signals: tests verify callbacks are called, transient failures are retried, and test build retry count stops after three failures.
