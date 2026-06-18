# sources/cloud-native/moby/integration/internal/container/ns.go

Purpose: helper for retrieving a container's Linux namespace identifier/path from `docker inspect` state.

Important APIs and helpers: `GetContainerNS(ctx, t, apiClient, cID, nsName)` calls `ContainerInspect` and returns `inspect.Container.NetworkSettings.SandboxKey`.

Control flow: the function asserts inspect succeeds and then switches on `nsName`. Currently only `net` is supported; any other namespace name fails the test.

State and persistence: reads container inspect state only. It does not mutate daemon state.

Dependencies and integration: depends on Moby API client, testing assertions, and network sandbox metadata populated for containers.

Risks: despite a generic `nsName` parameter, only network namespace is implemented. Tests using other namespace names fail immediately.

Test signals: helper-only; provides a common way for network integration tests to locate container network namespaces.
