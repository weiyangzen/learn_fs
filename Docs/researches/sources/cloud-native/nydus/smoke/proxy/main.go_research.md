# sources/cloud-native/nydus/smoke/proxy/main.go

Purpose: standalone HTTP/CONNECT proxy for smoke tests with dynamic and per-request failure simulation.

Important APIs/types: `InjectionRule`, `ProxyStats`, global injection state/counters, `handleControlAPI`, `maybeInjectError`, `handleFailureSimulation`, `httpsProxy`, `httpProxy`, `copyHeader`, and `transfer`.

Control flow: server listens on `:4001`; `/_test/inject` POST installs a rule, DELETE clears it, and `/_test/stats` returns counters/rule. Non-control traffic can be failed by query/header simulation or by the active injection rule. Dynamic injection only applies when `X-Dragonfly-Use-P2P` is present so disable-proxy/direct requests can pass through. CONNECT requests tunnel TCP after hijacking; HTTP requests are forwarded with a plain `http.Client`.

State and persistence: in-memory injection rule protected by mutex, atomic total/injected counters, and process logs. Counted rules decrement and clear when positive count reaches zero; negative count means persistent.

Dependencies and integration: used by `proxy_error_test.go`, exposes Dragonfly-style `X-Dragonfly-Error-Type: proxy`, and supports timeout/status scenarios that exercise nydusd retry/fallback paths.

Risks: listens on a fixed port, lacks graceful shutdown/auth, mutates and reuses the incoming request for forwarding, has no custom transport timeout for HTTP forwarding, and only increments injected counter for status responses, not timeout-only delays.

Test signals: control API status 200, stats JSON, injected HTTP statuses with Dragonfly error header, successful direct forwarding after disable-proxy headers disappear, and CONNECT/HTTP proxying behavior.
