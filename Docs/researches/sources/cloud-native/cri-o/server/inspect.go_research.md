# sources/cloud-native/cri-o/server/inspect.go

Purpose: implements CRI-O's extended HTTP inspection interface and helper serialization for `/config`, `/info`, `/containers/{id}`, pause/unpause, goroutine stacks, heap dumps, and optional pprof routes.

Important APIs and functions: `getIDMappingsInfo` reports configured UID/GID mappings or a full host mapping when none are configured. `getInfo` projects storage, cgroup, and default ID mapping data into `types.CrioInfo`. `getContainerInfo` resolves regular and infra containers, validates state and sandbox existence, selects an infra PID fallback from another running pod container, and returns `types.ContainerInfo`. `GetExtendInterfaceMux` builds the chi router and binds all inspect endpoints.

Control flow: container inspection first tries `GetContainer`, then `getInfraContainer`, then uses `StateNoLock` and the sandbox lookup before constructing JSON. HTTP handlers map known sentinel errors to 404 or 500 responses. Pause and unpause validate container state before calling runtime pause/unpause and status refresh. Heap dumps are written through a temporary file and copied to the response.

State and persistence: the file reads server config, container state, sandbox IPs, runtime status, and temporary heap data. Pause/unpause mutate runtime/container state through `ContainerServer.Runtime()` and then persist status through the runtime status update path.

Dependencies and integration: uses chi for routing, goccy JSON for response encoding, CRI-O internal `oci`, `sandbox`, `types`, and runtime interfaces, Go pprof/debug utilities, and `utils.WriteGoroutineStacksTo`.

Risks: pause/unpause are exposed as GET routes with side effects and depend on the extended-interface listener being appropriately protected. `getContainerInfo` uses `context.TODO()` in HTTP handlers, so cancellation/deadline propagation is absent. Heap dump generation can be expensive and writes a temp file. Infra PID fallback may hide missing infra PIDs by choosing an arbitrary running pod container.

Test signals: covered by both unit and Ginkgo tests for `/info`, `/containers`, pause/unpause error mapping, `getInfo`, successful `getContainerInfo`, and sentinel error returns for missing containers, nil state, and missing sandbox.
