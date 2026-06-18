# sources/control-plane/ceph-csi/internal/rbd/controllerserver_test.go

## Purpose
Provides focused unit coverage for controller helpers that can be exercised without a Ceph cluster: striping parameter validation, conversion of an `rbdVolume` into a CSI volume, and QoS mutable-parameter validation by mounter type.

## Important APIs, Types, And Functions
`TestValidateStriping` verifies paired `stripeUnit`/`stripeCount` rules and `objectSize` power-of-two parsing. `TestToCSIVolume` verifies `rbdVolume.ToCSI` rejects missing required identity fields and succeeds when volume ID, pool, journal pool, and image name are set. `TestValidateQoSParameters` covers the split between krbd cgroup QoS parameters and rbd-nbd QoS/max-limit parameters.

## Control Flow
Each test is table-driven and runs subtests in parallel. Inputs are plain maps or lightweight `rbdVolume` structs, so the tests stay isolated from external state. Assertions compare only error presence, not exact messages.

## State And Persistence
No persistent state is created. The tests rely on package constants for QoS keys and mounter names, which makes them sensitive to controller/QoS helper API changes.

## Dependencies And Integration Points
The file integrates with unexported helpers in `controllerserver.go` by being in package `rbd`. It indirectly exercises the shape expected by CSI response construction but does not marshal or call gRPC handlers.

## Risks And Test Signals
The tests give useful regression signals for validation rules that run before Ceph resources are created. Coverage gaps remain around full `CreateVolume`, delete, snapshot, fencing, mirroring, and journal cleanup paths. Because assertions are only boolean error checks, changed error codes/messages could regress user-facing CSI behavior without failing these tests.
