# sources/cloud-native/cri-o/internal/oci/oci_test.go

## Purpose
Unit tests for the runtime dispatcher and selected checkpoint/restore behavior.

## Test Signals
The suite verifies `New` with default config, runtime map retrieval, handler validation, default/VM runtime type reporting, seccomp lookup failures, allowed annotation filtering, privileged-without-host-devices behavior, and checkpoint/restore behavior when CRIU is available. Restore tests cover missing checkpoint inventory and expected failures when runtime/conmon paths are dummy binaries.

## Dependencies and Risks
Uses CRI-O default config, temporary attach dirs, CRIU availability skips, runtime-spec inputs, and test helper containers. It gives good signals for configuration dispatch but does not exercise real runtime lifecycle success paths.
