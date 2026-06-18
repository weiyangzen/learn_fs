# sources/cloud-native/buildkit/solver/llbsolver/network_test.go

Purpose: compile-time assertion that `policyEvaluator` implements `network.ProxyPolicy`.

Important APIs/types/functions: the single declaration `var _ network.ProxyPolicy = (*policyEvaluator)(nil)` protects the interface contract between llbsolver source policy evaluation and the network proxy layer.

Control flow: none at runtime; the Go compiler fails if `policyEvaluator` stops satisfying the interface.

State/persistence: none.

Dependencies/integration: imports `github.com/moby/buildkit/util/network` and binds `policyEvaluator` from `policy.go` to the proxy policy interface used by workers.

Risks: this is intentionally minimal. It cannot catch semantic regressions in policy decisions, proxy-network mode validation, or session policy request behavior.

Test signals: only interface conformance. Behavioral tests for proxy policy should be in policy/network integration coverage.
