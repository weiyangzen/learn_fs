# Research: sources/cloud-native/moby/daemon/cluster/executor/container/validate_test.go

## sources/cloud-native/moby/daemon/cluster/executor/container/validate_test.go

Purpose: tests mount validation through controller construction, which exercises `newContainerConfig` and `validateMounts` in a realistic path.

Important helpers and tests: `newTestControllerWithMount` creates a synthetic task with one mount; `TestControllerValidateMountBind` checks relative bind source rejection and absolute bind source acceptance even if nonexistent; `TestControllerValidateMountVolume` rejects absolute volume sources; `TestControllerValidateMountTarget` rejects relative targets; `TestControllerValidateMountTmpfs` rejects non-empty tmpfs sources; `TestControllerValidateMountInvalidType` rejects unknown mount types.

State is local temporary directories and synthetic daemon/task structs. Dependencies include daemon, random string IDs, SwarmKit API types, and platform constants from `validate_unix_test.go` or `validate_windows_test.go`. Risks covered are API ambiguity and cross-platform absolute-path handling. Gaps include cluster mounts, bind option validation, and deeper Engine-side mount availability.
