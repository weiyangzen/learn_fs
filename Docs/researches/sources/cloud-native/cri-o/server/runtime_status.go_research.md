# sources/cloud-native/cri-o/server/runtime_status.go

Purpose: implements CRI `Status` and verbose runtime info reporting.

Important APIs and functions: `Status` builds runtime and network readiness conditions, runtime feature flags, runtime handler feature entries, and optional verbose info. `createRuntimeInfo` serializes pause image and CRI-O runtime config.

Control flow: runtime readiness is always true in this file; network readiness is false with reason `NetworkPluginNotReady` if CNI plugin readiness reports an error. The runtime handler list includes every configured runtime plus an empty-name alias for the default runtime.

State and persistence: read-only over CNI readiness, configured runtimes, pause image, and runtime config.

Dependencies and integration: Kubernetes CRI runtime status API, CNI plugin readiness, runtime handler feature discovery for recursive read-only mounts and ID-mapped user namespaces.

Risks: network condition is only as accurate as `CNIPluginReadyOrError`. Runtime handler ordering follows map iteration over configured runtimes.

Test signals: `runtime_status_test.go` covers successful status, condition count/status in the default test setup, and verbose info presence.
