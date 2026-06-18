# sources/control-plane/rook/pkg/daemon/discover/discover_test.go

Purpose: unit tests the discover daemon's device probing, udev filtering, equality heuristics, and ceph-volume inventory parsing using mocked executors and synthetic device data.

Important APIs/types/functions: `TestProbeDevices()` exercises `probeDevices()` through `clusterd.DiscoverDevices()` and `sys` helpers by matching expected executor arguments. `TestMatchUdevMonitorFiltering()` verifies `matchUdevEvent()` emits add/remove and rejects change/device-mapper events. `TestDeviceListsEqual()` directly covers `checkDeviceListsEqual()`. `TestGetCephVolumeInventory()` covers `getCephVolumeInventory()` with normal, empty, error, and partial JSON output.

Control flow: tests build `exectest.MockExecutor` functions that return canned command output based on argument patterns. The probe test simulates one disk with a filesystem and one partitioned disk, validating that parent disk filtering and partition emptiness are represented as expected. Inventory tests sequence executor returns with a `run` counter to validate multiple scenarios through one test body.

State and persistence behavior: no Kubernetes state is persisted in these tests; they focus on pure and executor-backed logic. The tests do mutate global package state indirectly through shared package functions and assume no parallel execution. Environment state is not heavily manipulated here except through command mocking.

Dependencies and integration points: the test relies on Rook's `exectest.MockExecutor`, `clusterd.Context`, `sys.LocalDisk`, and `testify/assert`. It validates the discover package's assumptions about lower-level Linux command parsers without invoking real system commands.

Risks: `TestGetCephVolumeInventory()` depends on exact JSON marshaling order for expected strings; changes to struct fields or Go JSON output would require updates. The mock executor pattern in `TestProbeDevices()` silently returns empty output for unexpected calls, which can hide missing assertion coverage unless downstream behavior fails.

Test signals: coverage is strong for core equality rules, default udev matching, basic probing, and inventory parsing. It does not directly test `Run()`, ConfigMap create/update behavior, signal handling, or udev debounce timing.
