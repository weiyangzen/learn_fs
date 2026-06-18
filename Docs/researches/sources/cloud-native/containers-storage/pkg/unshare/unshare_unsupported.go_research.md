# sources/cloud-native/containers-storage/pkg/unshare/unshare_unsupported.go

Purpose: generic non-Linux/non-Darwin unshare compatibility layer.

Important APIs/types/functions: `UsernsEnvName`, `IsRootless`, `GetRootlessUID`, `GetRootlessGID`, `RootlessEnv`, `MaybeReexecUsingUserNamespace`, `GetHostIDMappings`, `ParseIDMappings`, and `HasCapSysAdmin`.

Control flow: reports rootless as `os.Getuid() != 0`, returns current uid/gid, appends an empty userns env marker, no-ops reexec, returns nil host mappings and parsed mappings, and treats euid 0 as CAP_SYS_ADMIN.

State/persistence: reads uid/gid and environment; no namespace mutation.

Dependencies/integration: lets unsupported Unix-like targets compile shared rootless code.

Risks: `ParseIDMappings` ignores inputs and errors, unlike Linux/Darwin, so callers may believe unsupported mappings were accepted. CAP_SYS_ADMIN semantics are approximated by euid.

Test signals: unsupported-platform tests should assert no-op behavior and ensure callers do not rely on actual userns mappings.
