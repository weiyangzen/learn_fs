# sources/cloud-native/buildkit/client/llb/merge_test.go

Purpose: verifies public `Merge` shortcut behavior for scratch and single-input cases.

Important APIs/types/functions: `TestScratchMerge` checks nil/empty/scratch-only merges, single non-empty input, scratch mixed with one input, and scratch mixed with two non-empty inputs.

Control flow: calls `Merge` with different slices and asserts output nil, equality with original input output, or distinct merge output.

State and persistence: none beyond in-memory states.

Dependencies/integration points: `Scratch`, `Image`, and `Merge`.

Risks/test signals: protects API behavior that avoids unnecessary merge ops. It does not validate actual `pb.MergeOp` marshaling for multi-input non-scratch merges.
