# sources/control-plane/csi-driver-nfs/pkg/nfs/utils_test.go

Purpose: provides focused unit tests for shared utility functions used by the NFS driver.

Important APIs and helpers: `TestParseEndpoint`, `TestGetLogLevel`, `TestGetMountOptions`, `TestChmodIfPermissionMismatch`, `TestGetServerFromSource`, `TestSetKeyValueInMap`, `TestValidateOnDeleteValue`, `TestWaitForPathNotExistWithTimeout`, `TestRemoveEmptyDirs`, `TestWaitUntilTimeout`, `TestGetVolumeCapabilityFromSecret`, and `TestValidatePath`.

Control flow: table tests cover valid and invalid endpoints, lowered log levels for probe/capability/stats calls, case-insensitive mount option lookup, chmod no-op and mismatch paths, IPv4/IPv6/FQDN formatting, case-insensitive map replacement, supported delete/retain/archive policies, polling timeout, recursive empty-dir cleanup, goroutine timeout behavior, and slash-based path traversal detection.

State and persistence behavior: creates directories in the current working directory for chmod and cleanup tests, waits on real timers, and uses goleak to detect goroutine leaks after timeout tests.

Dependencies and integration points: depends on CSI protobufs and goleak. It verifies helper behavior consumed by controller/node/server paths.

Risks: some expected errors are platform-specific, especially invalid path and chmod behavior. The timeout test intentionally leaves a sleeping goroutine briefly and waits before goleak verification. Backslash traversal is explicitly expected not to fail, documenting the current Unix-centric validation.

Test signals: broad helper-level coverage with useful regression signal for security-sensitive path validation and timeout/cleanup behavior.
