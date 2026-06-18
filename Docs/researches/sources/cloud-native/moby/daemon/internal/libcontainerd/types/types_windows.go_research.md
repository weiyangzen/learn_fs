<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_windows.go -->
# sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_windows.go

Purpose: defines Windows-specific libcontainerd stats, process summaries, resources, and checkpoint metadata.

Important APIs and types: `Summary` aliases runhcs `options.ProcessDetails`; `Stats` holds read time plus HCS statistics; `InterfaceToStats`; empty `Resources`; `Checkpoint`; and `Checkpoints`.

Control flow: `InterfaceToStats` type-asserts the payload to `*hcsshim.Statistics` and wraps it.

State and persistence: none; structs transport HCS data.

Dependencies and integration: used by Windows local and remote clients for stats/top-like summaries and by daemon code that accepts the platform-specific types.

Risks: `InterfaceToStats` will panic for unexpected payload types. Windows resource updates are modeled as an empty struct, so code must handle unsupported behavior elsewhere.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/libcontainerd/types/types_windows.go -->
