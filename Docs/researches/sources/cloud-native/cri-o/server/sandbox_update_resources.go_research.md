# sources/cloud-native/cri-o/server/sandbox_update_resources.go

Purpose: implements CRI `UpdatePodSandboxResources` by forwarding pod overhead/resource updates to NRI.

Important APIs and functions: `UpdatePodSandboxResources`.

Control flow: resolves sandbox by request ID, returns gRPC NotFound on lookup failure, calls `s.nri.updatePodSandbox` with overhead and resources, then returns an empty success response.

State and persistence: does not directly mutate CRI-O cgroups; any effect depends on NRI plugins and NRI integration.

Dependencies and integration: CRI update sandbox resources API, gRPC status codes, NRI pod update hook.

Risks: with NRI disabled this becomes a successful no-op. Direct CRI-O cgroup resource updates are not performed in this file.

Test signals: `sandbox_update_resources_test.go` covers success for an available sandbox and error for an invalid sandbox.
