# sources/control-plane/csi-driver-smb/pkg/csi-common/driver.go

## Purpose
Shared CSI driver metadata and capability helper implementation.

## Important APIs, Types, and Functions
Defines `CSIDriver` with name, node ID, version, controller capabilities, volume access modes, and node capabilities. Functions include `NewCSIDriver`, validation methods, and add/get capability helpers.

## Control Flow
Driver construction validates nonempty name and node ID, logs empty version, and returns metadata. Validation methods allow UNKNOWN and otherwise check configured capability slices.

## State and Persistence
In-memory driver capability state only.

## Dependencies
Depends on CSI protobuf types, gRPC status/codes, and klog.

## Integration Points
Embedded by `pkg/smb.Driver`; used during driver startup and CSI RPC validation.

## Risks and Edge Cases
Empty version logs but still constructs a driver. Add methods replace existing capability slices instead of appending. Validation returns InvalidArgument with only enum string detail.

## Test Signals
`driver_test.go` covers constructor validation and capability add/validate behavior.
