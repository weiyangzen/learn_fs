# sources/cloud-native/buildkit/solver/llbsolver/network.go

Purpose: carries the llbsolver proxy-network switch and proxy policy plumbing between jobs, bridges, source policy evaluation, and worker op resolution.

Important APIs/types/functions: `keyProxyNetwork`, `proxyNetworkForOp`, `provenanceBridge.ProxyPolicy`, `provenanceBridge.ProxyNetwork`, `llbBridge.ProxyNetwork`, `loadProxyNetwork`, and `llbBridge.ProxyPolicy`. `proxyNetworkForOp` is the key guard: only exec ops are affected, `UNSET` and `HOST` inherit the proxy setting, `NONE` disables it, and other modes error when proxy networking is enabled.

Control flow: `Solver.Solve` stores a job value under `keyProxyNetwork`. `llbBridge.ProxyNetwork` ORs bridge config with values on the solver builder. `vertex.loadWithProxyNetwork` uses `proxyNetworkForOp` to mark individual ops before digest recomputation. Worker resolution receives `worker.ProxyOpt` with both network boolean and policy callback.

State/persistence: no persistence; job/solver builder values are transient during solve. Proxy policy is loaded from source policy job values and optional policy session.

Dependencies/integration: ties to `sourcepolicy.Engine`, source policy sessions, `util/network.ProxyPolicy`, `llbBridge.policy`, and `provenanceBridge` for recording proxy metadata.

Risks: proxy-network state participates in vertex digest recomputation, so missed propagation can create incorrect cache hits. Allowing host/unset to inherit proxy while rejecting other modes preserves explicit no-network behavior but requires callers to understand mode interactions.

Test signals: `network_test.go` only asserts interface conformance for `policyEvaluator`; functional coverage is mostly indirect through vertex/provenance/network integration tests elsewhere.
