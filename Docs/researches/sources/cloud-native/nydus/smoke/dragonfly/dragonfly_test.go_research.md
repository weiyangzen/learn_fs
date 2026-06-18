# sources/cloud-native/nydus/smoke/dragonfly/dragonfly_test.go

Purpose: end-to-end tests for Nydus Dragonfly proxy integration across SDK proxy, HTTP proxy, strict no-fallback, and fallback-enabled modes.

Important APIs/types: `testEnv`, `setupTestEnv`, mode helpers `isSDKMode`, `isStrictMode`, `hasFallback`, `envOrDefault`, `TestDragonflyE2E`, and `truncateString`.

Control flow: setup reads required env (`TEST_MODE`, `NYDUSD_CONFIG`, `BOOTSTRAP_PATH`, Dragonfly configs through helpers), creates cache/mount dirs, starts a Dragonfly manager/scheduler/dfdaemon cluster, and starts nydusd. Subtests verify mount readability, multi-file and binary reads, directory traversal, blob cache population, reread consistency, SDK-client logs, and proxy/backend log activity. Failure subtests stop dfdaemon/scheduler, stop nydusd, clear caches, restart cold, then assert fallback or strict failure behavior and recovery logs.

State and persistence: uses real mount directory, nydusd log file, blob cache dir, Dragonfly cache dir, and external Dragonfly processes. It deliberately clears caches and drops page cache to force network/proxy behavior.

Dependencies and integration: integrates `testutil.go` process/mount/log helpers, nydusd config JSON, Dragonfly binaries/configs, FUSE mount behavior, and log messages from proxy health/fallback code.

Risks: timing-sensitive health/recovery log checks, fixed port assumptions from helpers, root/mount permissions, reliance on specific files inside the test image, and log-message drift. Some checks warn instead of failing to avoid flaky health-log timing.

Test signals: readable files and populated cache prove data path; strict mode expects read errors with proxy down; fallback modes expect successful cold reads via origin; recovery expects successful reads after Dragonfly restart and optional recovered/fallback log signals.
