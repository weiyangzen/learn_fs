# sources/control-plane/external-snapshotter/pkg/utils/conversion.go

Purpose: provides small conversion helpers from CSI protobuf-style values to Kubernetes snapshot API status fields.

Important APIs/functions: `CSITimestampToKubernetes` converts a `timestamppb.Timestamp` to a Unix nanoseconds pointer; `CSISizeToKubernetes` converts a byte size to an `*int64` but treats zero as unset.

Control flow: both helpers are straight-line nil/zero guards followed by pointer return.

State and persistence: stateless; callers decide whether to persist returned pointers into CRD status.

Dependencies and integration: depends on protobuf timestamp types and is intended for controller status population.

Risks and test signals: risks are semantic: zero-size snapshots cannot be distinguished from absent size, and timestamp validity is delegated to protobuf conversion. Tests cover nil timestamp, non-nil timestamp, zero size, and non-zero size.
