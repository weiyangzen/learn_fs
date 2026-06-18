## sources/distributed-fs/seaweedfs/weed/s3api/sts_packed_policy_test.go

Purpose: validates STS packed policy size percentage calculation for inline session policies.

Important test: `TestComputePackedPolicySize` plus the shared `repeat` helper from the session-name test file.

Control flow: table cases pass empty, tiny, half-budget, full-budget, and oversized strings to `computePackedPolicySize`, checking nil for empty policy, integer percentages for non-empty policy, and a 100 percent cap for oversized input.

State and dependencies: no persistence; depends on `sessionPolicyBudgetBytes` and `computePackedPolicySize` production code.

Signals and risks: protects AWS-compatible response metadata for packed policy size. It tests length-based behavior only, not actual compression or policy validation semantics.
