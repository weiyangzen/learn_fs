# sources/cloud-native/moby/integration/internal/system/goroutines.go

Purpose: polling helpers for daemon goroutine-count stability and leak checks.

Important APIs and helpers: `WaitForStableGoroutineCount`, `StableGoroutineCount`, `CheckGoroutineCount`, and `getGoroutineNumber`.

Control flow: `getGoroutineNumber` calls `SystemInfo` and extracts `NGoroutines`. `StableGoroutineCount` stores the first observed count and succeeds only when subsequent polls match it, otherwise updates the count and continues. `WaitForStableGoroutineCount` wraps that predicate and returns the stabilized count. `CheckGoroutineCount` succeeds when the current count equals the expected value and continues otherwise.

State and persistence: reads daemon system info only. The expected/stable count is kept in caller-provided or local memory between poll attempts.

Dependencies and integration: depends on Moby `SystemAPIClient`, system info response, and gotest poll settings.

Risks: goroutine counts naturally fluctuate in busy daemons, so tests must choose timeouts and quiet conditions carefully. Equality checks are strict and can be flaky if background activity is expected.

Test signals: helper-only; supports integration tests that need to detect goroutine leaks or wait for daemon quiescence.
