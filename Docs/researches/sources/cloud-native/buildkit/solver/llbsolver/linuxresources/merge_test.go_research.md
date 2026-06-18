<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge_test.go -->
## sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge_test.go

Purpose: validates relaxed merging semantics for Linux resource metadata.

Important APIs and types: `TestMergeRelaxed` table of subtests over `mergeRelaxed`.

Control flow: tests cover nil handling and clone/no-alias behavior, memory unlimited and max behavior, memory-swap unset/unlimited/max semantics, CPU shares unset/max semantics, CPU quota unlimited and pairwise cap comparison, equal quota shorter period, cpuset unset/union/canonical range formatting, and all-fields merge together.

State and dependencies: test-only protobuf resources. Depends on testify.

Integration points: protects shared-vertex resource metadata merging in solver state.

Risks and test signals: coverage is broad for documented semantics. It does not cover invalid cpuset parse fallback or extremely large quota/period values.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge_test.go -->
