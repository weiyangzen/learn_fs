<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unsupported.go -->
# sources/cloud-native/containerd/core/mount/temp_unsupported.go

Purpose: Windows stub implementation for temporary mount location configuration and cleanup.

Important APIs/types/functions: `SetTempMountLocation` returns nil and `CleanupTempMounts` returns nil warnings/error.

Control flow: both functions are no-ops.

State and persistence: no state changes and no cleanup.

Dependencies and integration points: selected by Windows build tag. Windows mount lifecycle is handled through Windows layer primitives rather than Unix temp mount cleanup.

Risks: callers expecting cleanup warnings will see success even though no scanning occurs. This is intentional platform behavior.

Test signals: no direct tests in this subset.
<!-- END_FILE_RESEARCH: sources/cloud-native/containerd/core/mount/temp_unsupported.go -->
