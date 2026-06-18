# sources/cloud-native/buildkit/solver/llbsolver/policy.go

Purpose: implements source policy evaluation for LLB source ops, including static policy engine decisions and optional interactive policy-session verification.

Important APIs/types/functions: `SourcePolicyEvaluator`, `policyEvaluator`, `Evaluate`, recursive `evaluate`, `mapsEqual`, platform converters, `fromPBHTTPChecksumAlgo`, `validateSourcePolicy`, `loadSourcePolicy`, and `loadSourcePolicySession`.

Control flow: `evaluate` ignores non-source ops, runs the source policy engine, then optionally contacts a `policysession.PolicyVerifier` session. The verifier can request source metadata resolution with strict identifier/attr matching and resolve options for image, OCI layout, git, or HTTP checksum metadata. It loops until a decision is returned, with a max-depth guard. `CONVERT` decisions mutate the source identifier/attrs and recursively re-evaluate; non-ALLOW decisions return wrapped deny errors.

State/persistence: policies and policy session ID are job builder values. Source ops may be mutated by conversion decisions before digest recomputation.

Dependencies/integration: sourcepolicy engine, gateway source metadata protobufs, sourceresolver options, policy sessions, session manager, and network proxy policy conformance.

Risks: policy-request loops are capped but still complex. Session metadata requests are rejected if they change source identity/attrs, which protects against confused-deputy behavior. Source mutation must be followed by digest recomputation or cache keys become stale.

Test signals: only interface conformance in `network_test.go` within this subset. Functional policy coverage should exist in broader source policy tests.
