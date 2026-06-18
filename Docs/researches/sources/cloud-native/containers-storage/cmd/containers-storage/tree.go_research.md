<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/tree.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/tree.go

- Purpose: Utility for printing layer/image parent relationships as a tree.
- Important types/functions: `treeNode`, `selectRoot`, `printSubTree`, and `printTree`.
- Control flow: Select roots from nodes, recursively print children with branch/continuation prefixes, and remove printed nodes until complete.
- State and persistence: Pure formatting helper; no storage mutation.
- Dependencies and integration: Used by layer/image list commands for tree output.
- Risks: Cycles or inconsistent parent data can cause missing or repeated output if not prefiltered.
- Test signals: `tree_test.go` exercises basic tree printing without assertions beyond no panic.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/tree.go -->
