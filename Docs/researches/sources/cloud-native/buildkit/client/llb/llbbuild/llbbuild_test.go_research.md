# sources/cloud-native/buildkit/client/llb/llbbuild/llbbuild_test.go

Purpose: validates marshaling of `llbbuild` build operations.

Important APIs/types/functions: `TestMarshal` uses `NewBuildOp` with `WithFilename`, decodes a protobuf op, and checks digest, input count, builder kind, build input mapping, and filename attr. `dummyOutput` supplies a fixed `pb.Input`.

Control flow: create build op, marshal with empty constraints, verify digest equals bytes digest, unmarshal bytes into `pb.Op`, then inspect `BuildOp` fields.

State and persistence: no persistence; dummy output avoids a real LLB graph.

Dependencies/integration points: `llb.Constraints`, `pb.BuildOp`, OpenContainers digest, and `testify/require`.

Risks/test signals: confirms basic wire shape. It does not test `Build` as a `StateOption`, constraints merging, nil source errors, or deterministic repeated marshals.
