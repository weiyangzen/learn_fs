# sources/cloud-native/containerd/pkg/namespaces/context_test.go

Purpose: tests namespace context propagation and environment fallback.

Important APIs/types/functions: `TestContext` verifies missing namespace, `NamespaceRequired` errors, `WithNamespace` storage, valid required lookup, and invalid namespace failure. `TestNamespaceFromEnv` uses `t.Setenv` to test default namespace and explicit `CONTAINERD_NAMESPACE`.

Control flow: each test creates a background context, applies namespace helpers, and asserts lookup results.

State/persistence: mutates process environment only through test-scoped `t.Setenv`.

Dependencies/integration: same-package tests with `context`, `testing`, and errdefs/identifier behavior through production functions.

Risks: does not directly test gRPC/ttrpc metadata fallback; those are covered by separate metadata tests. Validation expectations depend on `identifiers.Validate`.

Test signals: protects the missing namespace precondition contract, default namespace name, environment variable name, and invalid-namespace rejection path.
