## sources/cloud-native/buildkit/util/network/proxy.go

Purpose: defines exec proxy policy/provider interfaces and captures HTTP material metadata for reproducible/source-policy-aware builds.

Important types/APIs: `ProxyPolicy`, `ProxyConfig`, `ProxyProvider`, `ProxyNamespace`, `ProxyMaterial`, `ProxyRequest`, `ProxyIncomplete`, `ProxyCapture` with `AddMaterial`, `AddRequest`, `AddIncomplete`, `Materials`, `Requests`, and `Incomplete`.

Control flow: capture add methods are nil-safe and mutex-protected. `Materials` clones direct materials, builds redirect URL mapping from requests, then iteratively adds aliases so redirected URLs inherit the final digest. `Requests` and `Incomplete` return copies.

State/persistence: in-memory capture slices protected by mutex; no external persistence here. Dependencies: solver protobuf ops, OCI digest.

Integration points: implemented by `proxyprovider`, used by source policy and build result material capture. Risks: redirect alias expansion can loop until no new digest aliases; maps prevent duplicate URLs but request list can grow unbounded during long executions. Test signals: proxy provider tests exercise material capture, redirects, redaction, incomplete reasons.
