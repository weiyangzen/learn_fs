# sources/cloud-native/containerd/internal/cri/util/util.go

## Purpose
Collects core CRI utility functions for namespaced containerd contexts, cleanup timeout handling, annotation filtering, label construction, OCI user-string generation, and shim ttrpc closed-error detection.

## Important APIs, Types, And Functions
`DeferContext`, `NamespacedContext`, and `WithNamespace` apply the Kubernetes containerd namespace and cleanup timeout. `GetPassthroughAnnotations` filters pod annotations by glob patterns. `BuildLabels` merges validated image labels with request labels and injects the CRI container kind label. `GenerateUserString` converts CRI username/uid/gid combinations into OCI user strings. `IsShimTTRPCClosed` recognizes closed shim ttrpc errors.

## Control Flow
Package init registers the defer cleanup timeout. Annotation matching uses `path.Match` so Windows backslashes are not treated as separators. Label building logs and skips invalid image labels, then lets config labels override. User generation follows CRI's allowed username/uid/gid matrix and rejects gid-only input.

## State And Persistence
State is limited to the global timeout key. Returned contexts, label maps, and strings are transient, but labels may be persisted in container metadata.

## Dependencies And Integration Points
Integrates Kubernetes CRI runtime API, containerd namespaces/timeouts/labels, CRI constants and labels, containerd logging, errdefs, and ttrpc.

## Risks
Invalid config labels are not revalidated after override. Annotation glob errors are ignored as non-matches. `IsShimTTRPCClosed` relies on string suffix matching inside an unknown error wrapper.

## Test Signals
`util_test.go` covers user-string combinations, annotation glob filtering, and shim closed-error detection.
