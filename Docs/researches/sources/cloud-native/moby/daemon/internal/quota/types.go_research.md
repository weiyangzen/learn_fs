<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/types.go -->
# sources/cloud-native/moby/daemon/internal/quota/types.go

Purpose: defines shared quota data structures.

Important APIs and types: `Quota` with `Size`, and `Control` with backing block device, embedded RW mutex, and target-path-to-project-ID map.

Control flow: no functions in this file.

State and persistence: `Control` carries in-memory quota bookkeeping; actual quota state is applied by platform implementation.

Dependencies and integration: used by supported and unsupported quota implementations and storage drivers.

Risks: embedding `sync.RWMutex` means `Control` must not be copied after use. Path keys require callers to use consistent canonical paths.

Test signals: exercised indirectly by project quota tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/daemon/internal/quota/types.go -->
