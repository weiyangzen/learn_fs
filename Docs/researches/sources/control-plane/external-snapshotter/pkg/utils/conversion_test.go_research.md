# sources/control-plane/external-snapshotter/pkg/utils/conversion_test.go

Purpose: verifies the CSI-to-Kubernetes scalar conversion helpers.

Important APIs/functions: `TestCsiSizeToKubernetes` and `TestCsiTimestampToKubernetes`.

Control flow: tests assert zero size and nil timestamp return nil, while non-zero size and current timestamp return expected int64 values.

State and persistence: no external state.

Dependencies and integration: depends on `timestamppb.Now` and the local conversion helpers.

Risks and test signals: useful regression signal for nil-vs-zero status behavior; it does not test negative sizes or invalid timestamp values.
