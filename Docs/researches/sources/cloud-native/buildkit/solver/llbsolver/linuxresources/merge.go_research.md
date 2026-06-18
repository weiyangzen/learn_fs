<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge.go -->
## sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge.go

Purpose: merges Linux resource metadata from shared vertices so a vertex reused by multiple jobs is not constrained by the strictest sibling.

Important APIs and types: `Metadata` implementing `solver.VertexMetadata.Merge`, `mergeRelaxed`, `relaxedMemory`, `relaxedMemorySwap`, `relaxedCPUShares`, `relaxedCPUBandwidth`, and `relaxedCpuset`.

Control flow: metadata merge returns self for nil/unknown metadata and otherwise returns a new `Metadata` with relaxed `pb.LinuxResources`. Memory treats `0` as unlimited; memory swap treats `0` as unset and `-1` as unlimited; CPU shares treats `0` as unset; CPU bandwidth chooses the quota/period pair with higher effective cap and shorter period on ties; cpuset empty string is most relaxed, otherwise parsed sets are unioned and formatted.

State and dependencies: no persistence; clones nil-side resources to avoid pointer aliasing. Depends on solver metadata, BuildKit protobuf Linux resources, and `util/cpuset`.

Integration points: `WithLinuxResourcesMetadata` in LLB loading attaches this metadata, and `solver/jobs.go` merges metadata when shared active states are reused.

Risks and test signals: CPU quota cross multiplication can overflow for extreme values, though typical cgroup values are bounded. Parse errors fall back to the side that parsed cleanly or the first invalid value. `merge_test.go` covers many relaxation cases.
<!-- END_FILE_RESEARCH: sources/cloud-native/buildkit/solver/llbsolver/linuxresources/merge.go -->
