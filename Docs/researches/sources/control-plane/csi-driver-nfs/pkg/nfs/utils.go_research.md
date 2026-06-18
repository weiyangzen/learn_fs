# sources/control-plane/csi-driver-nfs/pkg/nfs/utils.go

Purpose: contains shared constants and helpers for CSI capabilities, endpoint parsing, gRPC logging, per-volume locks, mount options, chmod behavior, server address normalization, path cleanup, timeouts, secret-derived mount capabilities, and path traversal validation.

Important APIs and types: constants `separator`, `delete`, `retain`, `archive`, `volumeOperationAlreadyExistsFmt`; `validateOnDeleteValue`; constructors `NewDefaultIdentityServer`, `NewControllerServer`, `NewControllerServiceCapability`, `NewNodeServiceCapability`; `ParseEndpoint`; `getLogLevel`; `logGRPC`; `VolumeLocks`; `getMountOptions`; `unixModeToFileMode`; `chmodIfPermissionMismatch`; `getServerFromSource`; `setKeyValueInMap`; `waitForPathNotExistWithTimeout`; `removeEmptyDirs`; `WaitUntilTimeout`; `getVolumeCapabilityFromSecret`; and `validatePath`.

Control flow: endpoint parsing accepts only `unix://` and `tcp://` with non-empty addresses. `logGRPC` logs sanitized requests/responses and lowers verbosity for chatty calls. `VolumeLocks` uses a mutex-protected set for nonblocking acquire/release. Chmod compares permission plus special bits before calling platform-specific `chmod`. Cleanup helpers poll for deletion and remove empty parent directories up to a depth limit. `WaitUntilTimeout` races a goroutine against `time.After`. `validatePath` rejects path segments exactly equal to `..`.

State and persistence behavior: lock state is in memory. Chmod and directory cleanup mutate filesystem metadata. Logging emits through klog. No durable driver metadata is persisted.

Dependencies and integration points: depends on CSI types, protosanitizer, gRPC interceptors, Kubernetes sets, klog, net IPv6 utilities, OS/filesystem APIs, and platform-specific `chmod` files. Used throughout controller, node, server, and tests.

Risks: `removeEmptyDirs` uses a raw prefix check after `filepath.Abs`, which can misclassify prefix collisions such as `/tmp/a2` under `/tmp/a`; path traversal validation ignores backslash separators; `WaitUntilTimeout` does not cancel a timed-out operation; mount options from secrets are represented as one mount flag string.

Test signals: `utils_test.go` covers endpoint parsing, log levels, mount-option lookup, chmod mismatch handling, IPv6 bracket formatting, case-insensitive map updates, on-delete validation, deletion polling, empty-dir removal, timeout behavior, secret mount options, and path traversal validation.
