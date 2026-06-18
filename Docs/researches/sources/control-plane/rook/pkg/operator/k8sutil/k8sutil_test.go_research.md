# sources/control-plane/rook/pkg/operator/k8sutil/k8sutil_test.go

Purpose: unit tests for stable node-name truncation and Kubernetes label value sanitization.

Important APIs/types/functions: `TestTruncateNodeName`, `TestTruncateJobName`, and `TestValidateLabelValue`.

Control flow: truncation tests use maps keyed by expected output to validate short names, max-length names, long names hashed to a stable 32-character value, job-specific stricter length behavior, and formats whose fixed text is too long for the final DNS limit. Label tests validate empty strings, valid versions, replacement of `+` with `-`, 63-character truncation, and trimming leading/trailing punctuation.

State and persistence behavior: no persistence.

Dependencies/integration: uses testify and the exact stable hash produced by `Hash`.

Risks: map iteration order is nondeterministic but tests are independent. Expected hashes form a compatibility guard, so intentional hash changes would require careful migration.

Test signals: strong signal for backwards-compatible object naming, which other controllers rely on for stable Kubernetes resources.
