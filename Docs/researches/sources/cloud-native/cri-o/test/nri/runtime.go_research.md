<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/runtime.go -->
# sources/cloud-native/cri-o/test/nri/runtime.go

Purpose: test-only CRI runtime helper for NRI integration tests. It connects to CRI-O over the `-crio-socket` gRPC endpoint, exposes typed helpers for image pulling, pod/container lifecycle, resource updates, listing, and synchronous exec, and tracks created pod/container IDs so tests can address objects by either UID or runtime ID.

Important APIs and flow: `ConnectRuntime` builds runtime and image service clients with insecure local gRPC credentials and blocking dial timeout. `PullImages`/`PullImage` cache and pull the Fedora CRI-O CI image. `CreatePod` builds a `PodSandboxConfig` with DNS, cgroup parent selection from `-cgroup-manager`, SELinux fields, labels, annotations, and pod option hooks. `CreateContainer` builds a default long-running shell container, applies container option hooks, and calls `CreateContainer`; `StartContainer`, `StopContainer`, `RemoveContainer`, `UpdatePod`, and `ExecSync` wrap corresponding CRI calls.

State and persistence: in-memory maps store pod configs, UID-to-ID aliases, container aliases, and pulled image refs; the actual persistent state is in CRI-O/container storage. A mutex protects map mutation, but reads before RPCs are mostly unsynchronized, which is acceptable for serial test usage but not a general concurrent client.

Dependencies and integration points: depends on Kubernetes CRI API, gRPC, local CRI-O socket flags, CRI-O image availability, and NRI test flags. Risks include stale aliases after failed cleanup, missing `PullImages` before `CreateContainer`, long image-pull timeout behavior, and use of deprecated gRPC dial options retained for blocking semantics. Test signal is indirect: NRI tests exercise this helper against a live CRI-O daemon rather than unit tests in this file.
<!-- END_FILE_RESEARCH: sources/cloud-native/cri-o/test/nri/runtime.go -->
