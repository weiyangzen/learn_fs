# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/annotations_test.go

Purpose: unit-tests the annotation helper behavior.

Important APIs/types/functions: `TestCephAnnotationsMerge`, `TestAnnotationsSpec`, `TestAnnotationsApply`, and `TestAnnotationsMerge`.

Control flow: tests construct annotation specs with and without `all`, unmarshal YAML to typed maps, apply annotations to `ObjectMeta`, and verify merge conflict behavior.

State and persistence: test-only in-memory state.

Dependencies/integration: uses `stretchr/testify/assert`, Kubernetes YAML converter, JSON unmarshal, and `metav1.ObjectMeta`.

Risks: tests encode the current non-overwrite merge behavior, so changing comments to match code or code to match comments needs test updates.

Test signals: run with `go test ./pkg/apis/ceph.rook.io/v1 -run Annotations`.
