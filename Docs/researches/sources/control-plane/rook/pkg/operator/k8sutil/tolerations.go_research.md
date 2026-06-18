# sources/control-plane/rook/pkg/operator/k8sutil/tolerations.go

## Purpose
`tolerations.go` parses raw YAML configuration into Kubernetes toleration arrays.

## Important APIs, Types, and Functions
`YamlToTolerations(raw string) ([]v1.Toleration, error)` returns an empty slice for empty input, converts YAML to JSON, and unmarshals into `[]v1.Toleration`.

## Control Flow, State, and Persistence
The function is pure and has no persistence. Errors from YAML conversion or JSON unmarshal are returned directly.

## Dependencies and Integration Points
It depends on Kubernetes core/v1 toleration types and `k8s.io/apimachinery/pkg/util/yaml`. It integrates with CRD/operator configuration paths that accept tolerations as YAML text.

## Risks
No semantic validation beyond Kubernetes JSON unmarshal occurs. Unknown YAML fields may be ignored depending on Kubernetes type behavior, so malformed but structurally valid input can pass.

## Test Signals
No direct mapped test file covers this helper. Useful signals would include empty input, valid key/effect/operator/tolerationSeconds YAML, invalid YAML, and unexpected field behavior.
