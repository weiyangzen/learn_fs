<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk_test.go -->
# sources/control-plane/rook/pkg/clusterd/disk_test.go

Purpose: unit tests for local disk discovery helpers in `clusterd/disk.go`.

Important APIs/types/functions: `TestDiscoverDevices`, `TestDeviceMatchWithFilter`, and `TestIgnoreDevice` use `exectest.MockExecutor` and testify assertions.

Control flow: `TestDiscoverDevices` verifies an empty mock command output yields no devices and no error. `TestDeviceMatchWithFilter` covers negative regex matches, positive NVMe regex matches, `all`, explicit meta-device allowance, and `dm-` allowance. `TestIgnoreDevice` table-tests acceptable and unacceptable RBD-like names.

State and persistence behavior: tests are in-memory and do not touch host disks; the mock executor isolates command execution.

Dependencies and integration points: depends on the production discovery functions, Rook exec test helpers, and `stretchr/testify/assert`.

Risks: current tests do not cover lsblk property parsing, udev fallback, unsupported device types, child-device skipping, invalid regex behavior, or loop-device environment handling.

Test signals: these tests protect the highest-risk filter and RBD ignore policies while leaving deeper device population behavior to other tests or integration coverage.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/pkg/clusterd/disk_test.go -->
