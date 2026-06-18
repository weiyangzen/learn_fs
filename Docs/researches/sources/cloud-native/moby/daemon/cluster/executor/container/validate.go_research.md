# Research: sources/cloud-native/moby/daemon/cluster/executor/container/validate.go

## sources/cloud-native/moby/daemon/cluster/executor/container/validate.go

Purpose: validates SwarmKit mount specs before a task is accepted by `newContainerConfig`. The API is `validateMounts`.

Rules are type-specific: non-named-pipe targets must be absolute; bind sources must be absolute; volume sources must not be absolute; tmpfs sources must be empty; named pipe sources must be non-empty; cluster mounts are accepted; unknown mount types are rejected. This protects later Engine create behavior where absolute source paths can otherwise make volume and bind semantics ambiguous.

State is none. Dependencies are `filepath` and SwarmKit `api.Mount`. Risks are platform-specific path semantics because `filepath.IsAbs` follows the build target, and named-pipe target validation is intentionally looser. Tests in `validate_test.go`, `validate_unix_test.go`, and `validate_windows_test.go` cover the major rules.
