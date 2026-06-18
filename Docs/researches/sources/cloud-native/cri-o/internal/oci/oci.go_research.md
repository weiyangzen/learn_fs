# sources/cloud-native/cri-o/internal/oci/oci.go

## Purpose
Defines the runtime abstraction used by CRI-O to dispatch container operations to OCI, VM, or pod-level conmon-rs implementations while centralizing runtime handler lookup and feature queries.

## Important APIs and Types
`Runtime` stores config and a per-container `runtimeImplMap` guarded by `runtimeImplMapMutex`. `RuntimeImpl` is the lifecycle interface: create/start/exec/exec-sync/update/stop/delete/status/pause/stats/attach/port-forward/log-reopen/checkpoint/restore/alive/probe/serve streaming. `New`, `ValidateRuntimeHandler`, `getRuntimeHandler`, feature query methods, `newRuntimeImpl`, `RuntimeImpl`, and wrapper lifecycle methods are the core APIs. `ExecSyncError` preserves stdout/stderr/exit code around exec-sync failures.

## Control Flow and State
`New` ensures the exec notification directory exists. Handler lookup defaults to configured default runtime unless the container has a runtime handler. `newRuntimeImpl` chooses VM for `RuntimeTypeVM`, pod for `RuntimeTypePod`, otherwise OCI. `CreateContainer` constructs a fresh implementation and stores it by container ID; most other methods retrieve the cached implementation. `DeleteContainer` removes the cached implementation only after successful deletion.

## Dependencies and Integration
Integrates CRI-O config, seccomp config, runtime feature detection, cgroup stats, OCI specs, CRI streaming, and Kubernetes CRI types. Server-level CRI operations call this file rather than concrete runtime implementations.

## Risks and Test Signals
Risks include stale implementation cache entries after failed delete, panic potential in pod runtime creation if infra runtime is absent, and defaults when runtime type is empty. `oci_test.go` covers creation, runtime handler validation, type queries, seccomp, allowed annotations, privileged-without-host-devices, and checkpoint/restore failure paths.
