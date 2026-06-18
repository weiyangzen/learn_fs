# sources/control-plane/ceph-csi/internal/csi-addons/server/server_test.go

Purpose: endpoint parsing tests for the CSI-addons Unix socket server constructor.

Important APIs/types/functions: `TestNewCSIAddonsServer()` exercises `NewCSIAddonsServer()`.

Control flow: subtests run in parallel for `unix:///tmp/csi-addons.sock` success, empty endpoint failure, and non-URL/non-UDS endpoint failure.

State and persistence: no socket is created because `Start()` is not called.

Dependencies and integration points: validates the construction gate before addon services bind sockets.

Risks: does not assert error wrapping with `ErrNoUDS`, nor path fields, service list initialization, start/stop behavior, or socket cleanup.

Test signals: fast guard for endpoint scheme handling.
