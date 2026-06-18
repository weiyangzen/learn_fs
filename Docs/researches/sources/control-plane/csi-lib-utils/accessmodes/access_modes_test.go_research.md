# sources/control-plane/csi-lib-utils/accessmodes/access_modes_test.go

## Purpose
This unit test verifies Kubernetes-to-CSI access mode translation for both normal drivers and drivers supporting `SINGLE_NODE_MULTI_WRITER`.

## Important APIs, Types, And Functions
The single test `TestToCSIAccessMode` uses table-driven cases with `pvAccessModes`, expected CSI mode, expected error, and capability flag.

## Control Flow
Each case calls `ToCSIAccessMode`, verifies whether an error is expected, and compares the returned mode for non-error cases.

## State, Persistence, And Dependencies
The test is stateless and depends on Go testing plus Kubernetes/CSI constants.

## Integration Points
It directly covers `access_modes.go`.

## Risks And Test Signals
The table covers empty input, RWO, ROX, RWX, RWOP, ROX+RWO, and ROX+RWOP for both capability modes. It does not explicitly test duplicate modes or RWX combined with other modes. The signal is pass/fail of expected mapping and error behavior.
