<!-- BEGIN_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/errors.go -->
## sources/control-plane/longhorn-engine/pkg/controller/errors.go

Purpose: shared controller error message constants.

Important APIs/types/functions: `ControllerErrorNoBackendServiceUnavailable` and `ControllerErrorNoBackendReplicaError`.

Control flow/state: no behavior. Constants are used by controller startup to distinguish no backend availability due to service unavailability versus replica errors.

Dependencies and integration points: consumed by `Controller.Start` and likely callers/tests that interpret error strings.

Risks: string constants are brittle API surfaces if external code matches them. Prefer typed errors if behavior grows.

Test signals: startup failure tests should assert the correct class of failure.
<!-- END_FILE_RESEARCH: sources/control-plane/longhorn-engine/pkg/controller/errors.go -->
