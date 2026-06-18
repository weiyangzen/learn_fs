# sources/cloud-native/cri-o/internal/config/seccomp/seccompociartifact/seccompociartifact.go

Purpose: resolves seccomp profiles stored as OCI artifacts based on pod and image annotations.

Important APIs/types/functions: `SeccompOCIArtifact`, `New`, constants `SeccompProfilePodAnnotation` and `requiredConfigMediaType`, and `(*SeccompOCIArtifact).TryPull`.

Control flow: `New` creates a datastore-backed implementation rooted at the supplied graph root and system context. `TryPull` searches annotations in priority order: pod container-specific, pod-wide, image generic, image container-specific, then image pod-wide. If no annotation matches, it returns nil. With a profile reference, it calls `PullData` while enforcing the seccomp config media type, rejects empty artifact data, and returns the first artifact’s bytes.

State and persistence behavior: holds only the datastore implementation. Pulled profiles come from OCI artifact storage/network via the implementation; this file does not persist bytes itself.

Dependencies/integration points: integrates CRI-O annotations v2, OCI artifact datastore, image system context, and CRI-O logging. `seccomp.Config.Setup` uses it before normal security-profile handling when profile field is nil or unconfined.

Risks: only the first artifact data item is used. Annotation priority is security-sensitive. Pod annotation logging trims `/POD` or container suffixes for readability but uses exact values for lookup. Empty pulls are errors, not no-ops.

Test signals: tests mock `Impl.PullData` and cover no annotation, pod/image annotation variants, pull errors, and empty artifact data.
