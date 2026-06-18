# sources/cloud-native/nydus/smoke/dragonfly/proxy_error_test.go

Purpose: tests nydusd proxy error-handling semantics with a controllable local proxy that injects HTTP status errors and timeouts.

Important APIs/types: `proxyErrorEnv`, `injectError`, `injectTimeout`, `clearInjection`, `setupProxyErrorEnv`, `startNydusdForTest`, `runReadTest`, and `TestProxyErrorSimulation`.

Control flow: setup requires `REPO_ROOT` and `BOOTSTRAP_PATH`, builds `smoke/proxy`, starts it on port 4001, prepares fallback and no-fallback nydusd config paths, and creates cache/mount/log dirs. Each subtest clears caches, starts a fresh nydusd, injects proxy errors, reads `etc/os-release`, and asserts success or failure. Recovery exhausts/clears injected errors and checks that later cold reads succeed without fallback logging.

State and persistence: uses per-run nydusd log files, cache dirs parsed from config, a persistent proxy process with mutable injection rule, and restart counts to avoid log collision.

Dependencies and integration: integrates the test proxy control API, nydusd Dragonfly proxy request/retry code, config files under `misc/dragonfly`, and `testutil.go` process/mount/cache helpers.

Risks: expected outcomes depend on detailed retry semantics (`429` disables proxy, `403` does not retry, `500` and timeout handling differ by fallback mode); config paths must match repo layout; timeout tests are slow; port 4001 conflicts break setup.

Test signals: fallback config succeeds for 429/500/timeout and fails for 403; no-fallback config still succeeds on 429/500/timeout through disable-proxy retry but fails on 403; recovery succeeds through proxy with no fallback log.
