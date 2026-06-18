# sources/control-plane/rook/pkg/operator/k8sutil/k8sutil.go

Purpose: core Kubernetes utility constants and helpers for stable hashing, safe resource names, foreground deletion waiting, and Rook version label sanitization.

Important APIs/types/functions: constants for namespaces, data dirs, env vars, labels, and default service account; `Hash`, `TruncateNodeNameForJob`, `TruncateNodeName`, `truncateNodeName`, `deleteResourceAndWait`, `addRookVersionLabel`, and `validateLabelValue`.

Control flow: `Hash` returns the first 16 bytes of SHA-256 as hex and is documented as stable across versions. Name truncation hashes the node name when format plus node name exceed DNS label length, with a stricter max for Jobs due to Kubernetes pod-name generation behavior. `deleteResourceAndWait` foreground-deletes a resource and polls for NotFound up to 45 times. Version label sanitization replaces invalid label characters, trims invalid leading/trailing characters, and truncates to 63 characters.

State and persistence behavior: no direct persistent storage except deletion via injected closures. Hash outputs are a compatibility contract.

Dependencies/integration: capnslog, Rook version string, Kubernetes API errors, meta delete options, and Kubernetes label validation constants.

Risks: changing `Hash` or truncation behavior would break stable object-name mappings. `deleteResourceAndWait` has fixed sleeps and no context. `validateLabelValue` truncates after trimming but does not re-trim after truncation, so a truncated value could theoretically end with an invalid separator depending on input.

Test signals: `k8sutil_test.go` guards truncation outputs for node/job names and label value sanitization.
