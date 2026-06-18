# sources/cloud-native/moby/integration/container/update_test.go

Purpose: cross-platform integration tests for non-Linux-specific container update behavior, especially restart policy mutation.

Important APIs and helpers: `TestUpdateRestartPolicy` and `TestUpdateRestartWithAutoRemove` use `client.ContainerUpdateOptions`, `containertypes.RestartPolicy`, `container.Run`, `container.WithAutoRemove`, and polling helpers from `integration/internal/container`.

Control flow: the restart policy test starts a container configured to fail after a short sleep with `on-failure` retry count 3, updates the policy to retry 5 times, waits for final exit, and asserts both `RestartCount` and persisted `HostConfig.RestartPolicy.MaximumRetryCount`. The auto-remove test creates an auto-remove container, tries to set an `always` restart policy, and expects a conflict.

State and persistence: restart count is runtime state, while policy settings are daemon container metadata. The conflict test protects the invariant that auto-remove containers cannot later gain restart policies because removal and restart lifecycles are incompatible.

Dependencies and integration: depends on container lifecycle scheduling, restart-manager behavior, container inspect, containerd error classification through `cerrdefs.IsConflict`, and polling.

Risks: retry timing can be slower on Windows, hence the longer timeout. The first test assumes the failing command and restart manager reach a deterministic final stopped state.

Test signals: verifies update-to-restart-policy takes effect for an existing container and that daemon validation rejects auto-remove/restart-policy combinations.
