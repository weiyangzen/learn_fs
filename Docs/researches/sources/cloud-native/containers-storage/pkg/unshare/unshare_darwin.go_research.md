# sources/cloud-native/containers-storage/pkg/unshare/unshare_darwin.go

Purpose: Darwin rootless/unshare compatibility implementation for an OS without Linux user namespaces.

Important APIs/types/functions: `UsernsEnvName`, `IsRootless`, `GetRootlessUID`, `GetRootlessGID`, `RootlessEnv`, `MaybeReexecUsingUserNamespace`, `GetHostIDMappings`, and `ParseIDMappings`.

Control flow: Darwin always reports rootless true, returns host uid/gid, appends an empty userns marker to env, makes reexec a no-op, returns nil host mappings, and delegates explicit mapping parsing to `idtools.ParseIDMap`.

State/persistence: reads environment and uid/gid; no namespace mutation.

Dependencies/integration: lets higher-level rootless storage paths compile and run on macOS while avoiding Linux namespace operations.

Risks: always-rootless behavior may affect feature gating. `RootlessEnv` sets `_CONTAINERS_USERNS_CONFIGURED=` with an empty value, unlike Linux's `done`.

Test signals: Darwin tests should cover mapping parsing and rootless env expectations.
