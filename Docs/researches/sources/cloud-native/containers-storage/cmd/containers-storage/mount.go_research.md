<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/mount.go -->
# sources/cloud-native/containers-storage/cmd/containers-storage/mount.go

- Purpose: Mounts, unmounts, and checks mounted state for layers/containers.
- Important types/functions: `mountPointOrError`, `mountPointError`, `mount`, `unmount`, and `mounted`.
- Control flow: Resolve one or more IDs, call mount/unmount APIs, collect mount points or errors, and optionally emit JSON.
- State and persistence: Mutates mount state and reference counts in the storage driver/runtime.
- Dependencies and integration: Requires graph-driver mount support and appropriate privileges.
- Risks: Leaked mounts can block deletion; forced unmounts can disrupt users; JSON error aggregation must preserve per-ID failures.
- Test signals: Mount path existence, mounted command status, and unmount cleanup.
<!-- END_FILE_RESEARCH: sources/cloud-native/containers-storage/cmd/containers-storage/mount.go -->
