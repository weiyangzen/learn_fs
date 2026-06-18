# sources/cloud-native/cri-o/server/nri-api.go

Purpose: adapts CRI-O pod/container lifecycle to containerd NRI and exposes CRI-O objects through the NRI domain interface.

Important APIs and functions: `nriAPI.start`, lifecycle hooks `runPodSandbox`, `updatePodSandbox`, `stopPodSandbox`, `removePodSandbox`, `createContainer`, `postCreateContainer`, `startContainer`, `postStartContainer`, `updateContainer`, `postUpdateContainer`, `stopContainer`, `removeContainer`, `undoCreateContainer`; upward interface methods `GetName`, `ListPodSandboxes`, `ListContainers`, `GetPodSandbox`, `GetContainer`, `UpdateContainer`, and `EvictContainer`; wrappers `criPodSandbox` and `criContainer`; converters `fromCRILinuxResources` and `toCRIResources`.

Control flow: all downward hooks no-op when NRI is disabled. Pod start undo calls NRI stop/remove if run fails. Container create asks NRI for an adjustment, then applies it through runtime-tools with annotation filtering, resource checks, BlockIO/RDT resolvers, and CDI device injection. Upward updates resolve the target container, ignore missing containers, skip non-running/non-created containers, and call runtime update before updating CRI-O's resource cache. Eviction resolves and stops the target container.

State and persistence: mutates OCI specs during NRI create adjustments, updates container runtime resources, may inject CDI devices, and can stop containers on eviction. Wrapper getters copy labels/annotations where needed to avoid exposing mutable pod maps directly.

Dependencies and integration: deep integration with containerd NRI API, runtime-tools generate wrapper, CDI, goresctrl BlockIO, CRI-O cgroup/runtime/node feature checks, RDT, sandbox/container stores, CRI resource types, and OCI runtime specs.

Risks: many upward paths intentionally ignore missing objects, which is safe for stale NRI requests but can hide lookup failures. `GetID` and `GetPodSandboxID` depend on annotations in the OCI spec. Resource conversion must stay aligned with CRI/NRI semantics; unsupported cgroup features are stripped during adjustment. CDI refresh failures are logged but not fatal before injection.

Test signals: no direct tests in this subset. Lifecycle integration is indirectly exercised by sandbox/container creation and update paths when NRI is enabled or mocked.
