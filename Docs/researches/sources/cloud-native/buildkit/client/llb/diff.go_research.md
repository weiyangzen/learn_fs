# sources/cloud-native/buildkit/client/llb/diff.go

Purpose: implements LLB diff operations, producing a state that represents changes from a lower state to an upper state.

Important APIs/types/functions: `DiffOp` implements `Vertex` with lower/upper outputs, constraints, output, and marshal cache. `NewDiff` creates the op and requires `pb.CapDiffOp`. `Diff` is the public helper that optimizes scratch cases.

Control flow: `Marshal` returns cached data when possible, marshals constraints without platform because diff is not platform-specific, assigns lower and upper input indexes or `pb.Empty`, serializes a `pb.DiffOp`, and stores it in cache. Public `Diff` returns scratch for scratch/scratch, upper for scratch/upper, otherwise creates a diff output attached to lower.

State and persistence: in-memory marshal cache only.

Dependencies/integration points: solver protobuf `DiffOp`, capability metadata, `Merge` workflows, and state/output conversion.

Risks/test signals: `Validate` is currently no-op, so invalid combinations depend on marshal/input errors or solver-side validation. Scratch shortcut semantics are important for callers. No direct test in this subset, but merge examples and compatibility use diff/merge behavior indirectly.
