# sources/cloud-native/buildkit/client/llb/fileop_test.go

Purpose: comprehensive unit tests for LLB file action marshaling.

Important APIs/types/functions: tests cover mkdir, chained mkdir/mkfile/rm/symlink, copy from states and action outputs, multi-stage file pipelines, owner parsing by name/root/UID/GID, created timestamps, deterministic marshal, and parallel marshal. Helpers `parseDef` and `last` decode protobuf definitions and final pointer ops.

Control flow: each test builds a state, marshals it, decodes ops into digest maps and ordered arrays, then asserts input indexes, secondary inputs, action outputs, normalized paths, mode/timestamp/owner fields, source identifiers, and graph length.

State and persistence: no external persistence. Parallel marshal test exercises shared marshal cache locking.

Dependencies/integration points: `pb.FileOp`, image/source ops, digest calculation, `errgroup`, and fileop public APIs.

Risks/test signals: strong signal for wire-format stability and deterministic graph generation. Tests would catch many path/index regressions but currently may not catch missing cap metadata for advanced copy/symlink features.
