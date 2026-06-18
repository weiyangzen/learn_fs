# sources/control-plane/rook/pkg/apis/ceph.rook.io/v1/labels_test.go

Purpose: unit-tests label helper behavior and DNS label normalization.

Important APIs/types/functions: `TestCephLabelsMerge`, `TestLabelsSpec`, `TestLabelsApply`, `TestLabelsOverwriteApply`, `TestLabelsMerge`, `TestToValidDNSLabel`, and `Test_cutMiddle`.

Control flow: table-driven tests exercise metadata application, overwrite behavior, merge conflicts, YAML-to-JSON unmarshalling, symbol/digit/case conversion, maximum length handling, and `cutMiddle`.

State and persistence: test-only in-memory maps and ObjectMeta.

Dependencies/integration: uses `testify/assert`, Kubernetes YAML converter, JSON unmarshal, and DNS-1035 expectations from implementation.

Risks: test expectations lock in byte-wise DNS conversion and non-overriding merge semantics.

Test signals: `go test ./pkg/apis/ceph.rook.io/v1 -run Labels`.
