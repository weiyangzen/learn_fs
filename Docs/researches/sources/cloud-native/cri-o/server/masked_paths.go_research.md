# sources/cloud-native/cri-o/server/masked_paths.go

Purpose: constructs the default masked path list for Linux containers and appends caller-provided additions.

Important APIs and functions: `appendDefaultMaskedPaths` concatenates `defaultLinuxMaskedPaths()` with additional paths, sorts, and compacts duplicates. `defaultLinuxMaskedPaths` is a `sync.OnceValue` combining common defaults with CRI-O-specific `/proc/asound` and `/proc/interrupts`.

Control flow: the default list is computed once per process, then each append call sorts and deduplicates the combined result.

State and persistence: maintains process-local cached default masked paths; no disk persistence.

Dependencies and integration: depends on `go.podman.io/common/pkg/config.DefaultMaskedPaths` and Go slices/sync helpers. Used when generating OCI specs for masked kernel/proc paths.

Risks: because output is sorted, caller-supplied ordering is not preserved. `sync.OnceValue` means changes to external defaults after first call will not be observed.

Test signals: no direct tests in this subset.
