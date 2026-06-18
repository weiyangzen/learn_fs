# sources/control-plane/rook/pkg/daemon/ceph/osd/nsenter_test.go

## Purpose
`nsenter_test.go` locks down the host-binary lookup helper's command shape and happy-path behavior. It ensures OSD preparation will call `nsenter` with the expected mount namespace and target binary arguments.

## Important APIs, Types, and Functions
`TestBuildNsEnterCLI()` creates an `NSEnter` for the LVM check binary and asserts the exact argument slice. `TestCheckIfBinaryExistsOnHost()` uses `exectest.MockExecutor` to simulate successful `nsenter` execution when the candidate binary path is `/usr/sbin/lvm` or `/sbin/lvm`.

## Control Flow
The mocked executor inspects the command and argument positions, returning success only for `nsenter --mount=/rootfs/proc/1/ns/mnt -- /usr/sbin/lvm help` or `/sbin/lvm help`. `checkIfBinaryExistsOnHost()` should stop at the first successful candidate and return nil.

## State and Persistence
The tests are in-memory and do not touch real `/rootfs` or run real `nsenter`. They only assert executor calls.

## Dependencies and Integration Points
The suite depends on the executor test mock, Rook `clusterd.Context`, and the package-level LVM command constant used by `volume.go` prerequisites. It indirectly protects `lvmPreReq()` from command argument drift.

## Risks
Coverage is narrow. There is no test for failed `nsenter` plus successful `/rootfs` stat fallback, no error case when all paths fail, and no path ordering assertion beyond the happy path. The mock also assumes argument positions and may need update if `buildNsEnterCLI()` gains options.

## Test Signals
The existing signals are exact CLI assembly and a successful binary discovery path. Additional signals should include all-candidates-fail and fallback stat behavior.
