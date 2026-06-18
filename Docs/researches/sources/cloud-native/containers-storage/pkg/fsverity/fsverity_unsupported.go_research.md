## sources/cloud-native/containers-storage/pkg/fsverity/fsverity_unsupported.go

Purpose: non-Linux stub for fs-verity helpers.

Important APIs/types/functions: `EnableVerity` and `MeasureVerity`.

Control flow: both return formatted unsupported errors.

State and persistence: none.

Dependencies and integration points: keeps fsverity package importable on unsupported platforms.

Risks: callers must gate or tolerate unsupported errors; required fs-verity mode cannot work off Linux.

Test signals: no direct selected tests.
