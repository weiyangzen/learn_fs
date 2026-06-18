# sources/control-plane/rook/pkg/daemon/ceph/client/crash.go

Purpose: wraps Ceph crash module commands used by Rook to list and archive crash records.

Important APIs/types: `CrashList` models the broad JSON shape of `ceph crash ls`, including crash ID, entity, timestamp, process/version/OS/assertion/IO error fields, and backtrace. `GetCrashList()` runs `ceph crash ls` and unmarshals a slice of `CrashList`. `ArchiveCrash()` runs `ceph crash archive <id>`. `GetCrash()` currently delegates to `GetCrashList()`.

Control flow and state: all state lives in the Ceph crash module; this file persists nothing locally. `ArchiveCrash()` logs before and after archiving. Both operations use `NewCephCommand()`, so standard JSON output, config, keyring, timeout, and context cancellation behavior are inherited from `command.go`.

Dependencies and integration: consumed by health/reconciliation code that monitors cluster crash reports. It depends on `encoding/json`, `clusterd.Context`, `ClusterInfo`, and package logger. Risks include schema drift in Ceph crash output and a likely typo in the struct tag `iio_error_length`, which may prevent `IoErrorLength` from being populated from the expected Ceph field if the real JSON key is `io_error_length`. Test coverage only validates listing with a minimal crash JSON fixture; archive behavior and rich fields are not tested.
