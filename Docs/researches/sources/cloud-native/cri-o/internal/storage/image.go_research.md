# sources/cloud-native/cri-o/internal/storage/image.go

Purpose: implements CRI-O image service operations over containers/storage and containers/image: list/status, pull, delete/untag, short-name resolution, signature checks, image IDs, caching, and pinned-image matching.

Important APIs/types/functions: `ImageResult`, `ImageCopyOptions`, `CgroupPullConfiguration`, `ImageServer`, `GetImageService`, `ListImages`, `ImageStatusByName`, `ImageStatusByID`, `PullImage`, `UntagImage`, `DeleteImage`, `IsRunningImageAllowed`, `CandidatesForPotentiallyShortImageName`, `HeuristicallyTryResolvingStringAsIDPrefix`, `CompileRegexpsForPinnedImages`, `FilterPinnedImage`, and `WrapSignatureCRIErrorIfNeeded`.

Control flow: list/status resolve storage references, build or reuse image cache items, parse names, supplement repo digests, inspect labels/config/annotations, and verify mountpoints. Pull either runs in-process or reexecs `crio-pull-image` in a configured cgroup, streams JSON progress/result records, copies with signature policy, and falls back to OCI artifact pull for non-transient image-copy failures. Delete/untag resolves stable image IDs before mutation.

State and persistence behavior: persists images in containers/storage, caches immutable image metadata in memory, tracks in-progress names in `ImageBeingPulled`, may unmount stale image mountpoints, and can pull OCI artifacts into libartifact stores. Reexec passes store options over stdin.

Dependencies and integration points: depends heavily on containers/image, containers/storage, libimage/ociartifact, CRI errors, shortnames, signature policy, mountinfo, reexec, CRI-O references/config/logging, and platform `moveSelfToCgroup`.

Risks: image reference resolution is race-prone because tags can move; code switches to resolved refs where possible. Pull fallback must avoid masking cancellations/network errors. Pinned patterns use regexps and can panic on invalid `"*"`. Signature checks around multi-image manifests must select the correct instance.

Test signals: tests cover service construction, store getter, ID-prefix heuristics, short-name resolution including aliases and tag+digest normalization, untag paths, status/list failures, pull error paths, cancellation/deadline handling, and pinned regexp compilation.
