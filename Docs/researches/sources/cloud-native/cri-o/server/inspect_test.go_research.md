# sources/cloud-native/cri-o/server/inspect_test.go

Purpose: unit tests for inspect helper functions without the HTTP mux.

Important APIs and functions: tests `getInfo` for storage/cgroup fields and `getContainerInfo` with injected lookup functions. It also validates the sentinel errors `errCtrNotFound`, `errCtrStateNil`, and `errSandboxNotFound`.

Control flow: builds synthetic `oci.Container` objects with image references, labels, annotations, mount/log paths, state timestamps, and sandbox IDs; then calls `getContainerInfo` and compares projected fields.

State and persistence: test state is entirely in memory. The tests avoid the real container server by injecting `getContainerFunc`, `getInfraContainerFunc`, and `getSandboxFunc`.

Dependencies and integration: uses CRI-O `oci`, `sandbox`, storage image reference parsing, Kubernetes CRI types, runtime-spec state, and default config setup.

Risks: tests verify regular container projection but do not cover infra-container PID fallback, nil image name handling, host-network pointer semantics, or HTTP serialization.

Test signals: strong coverage for normal field mapping and the three main failure branches in `getContainerInfo`; basic coverage for `getInfo` cgroup/storage projection.
