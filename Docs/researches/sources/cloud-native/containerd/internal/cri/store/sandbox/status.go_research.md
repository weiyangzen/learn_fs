# Research: sources/cloud-native/containerd/internal/cri/store/sandbox/status.go

This file defines the internal sandbox state machine and in-memory status storage. `State` has three values: `StateReady`, `StateNotReady`, and `StateUnknown`. `State.String` maps ready/not-ready to CRI enum string names, maps unknown to `SANDBOX_UNKNOWN` even though CRI has no unknown enum, and formats invalid values with the numeric value.

`Status` records sandbox process PID, creation time, exit time, exit status, internal state, and optional pod-level `Overhead` and `Resources` as CRI `ContainerResources`. These resource fields are updated by `UpdatePodSandboxResources` and later surfaced by status verbose info.

`StatusStorage` is intentionally simpler than container status storage: comments state sandbox status is not checkpointed, and future checkpointing should combine with the container status storage pattern. `StoreStatus` returns a mutex-protected `statusStorage`. `Get` returns the status value. `Update` applies an `UpdateFunc` transaction under lock and rolls back on error.

There is no disk persistence. Dependencies include CRI runtime types, time, strconv, and sync. Risks include no deep-copy for pointer resource fields, in-memory-only loss across restart, unknown state mapping requiring later CRI conversion to not-ready, and callers needing to use `Update` for atomicity. Tests cover update rollback/success and state string conversion.
