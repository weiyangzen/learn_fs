# sources/cloud-native/buildkit/solver/llbsolver/ops/opsutils/validate.go

Purpose: central lightweight protobuf operation validation before constructing solver ops or loading vertices.

Important APIs/types/functions: `Validate(op *pb.Op) error`. It checks nil ops, required inner op structs, exec meta/args/mounts/rootfs, file actions, build/merge/diff presence, and passthrough ID/output indexes.

Control flow: computes `inputCount := len(op.Inputs)`, switches on the concrete `op.Op` oneof, and returns descriptive errors for invalid cases. Exec validation additionally requires at least one mount and a root mount. Passthrough validation ensures outputs exist and point to valid inputs when inputs are known.

State/persistence: none.

Dependencies/integration: called from op constructors and `vertex.loadLLB` before vertex materialization. It protects downstream code from nil pointer panics and missing rootfs assumptions.

Risks: validation is intentionally incomplete; many index checks remain in op-specific execution paths. Passthrough input validation is conditional when `inputCount` is zero, so callers must still handle runtime invalid indexes.

Test signals: direct tests are not in this subset. Invalid file-action graph cases are tested in `file_test.go`; exec constructor validity is mostly exercised indirectly.
