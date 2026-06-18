# sources/control-plane/rook/pkg/operator/k8sutil/labels.go

## Purpose
`labels.go` centralizes small label helpers used by Rook operator resources. It parses user label strings, applies Kubernetes recommended application labels, and determines which node label should be treated as the node hostname.

## Important APIs, Types, and Functions
`ParseStringToLabels()` converts comma-separated `key=value` input into a `map[string]string`, accepting key-only and empty-value forms. `AddRecommendedLabels()` mutates an existing label map with `app.kubernetes.io/*` keys and `rook.io/operator-namespace`. `LabelHostname()` returns `ROOK_CUSTOM_HOSTNAME_LABEL` when set, otherwise `corev1.LabelHostname`.

## Control Flow, State, and Persistence
The file has no persistence. State is read from environment variables: `PodNamespaceEnvVar` for operator namespace labels and `ROOK_CUSTOM_HOSTNAME_LABEL` for hostname matching. `ParseStringToLabels()` uses simple split logic and logs when a label contains more than one `=`.

## Dependencies and Integration Points
Node selection in `node.go` depends on `LabelHostname()`. Resource builders throughout the operator can call `AddRecommendedLabels()` before creating Kubernetes objects. The label parser is a utility for CLI/config strings.

## Risks
`ParseStringToLabels()` does not trim whitespace and only keeps text before the second `=`, so values containing `=` are truncated. `AddRecommendedLabels()` assumes the input map is non-nil and will panic for nil maps. Operator namespace labeling depends on the environment being populated by the downward API.

## Test Signals
`labels_test.go` covers key/value, key-only, empty value, multi-label, and empty input parsing. It does not cover whitespace, duplicate keys, multiple `=`, custom hostname labels, or nil label maps.
