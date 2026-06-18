# sources/control-plane/csi-driver-iscsi/pkg/iscsilib/multipath.go

Purpose: supplies command execution with timeout plus multipath device flush and resize operations used during iSCSI volume cleanup and expansion.

Important APIs and types: `ExecWithTimeout(command, args, timeout)` runs a command under `context.WithTimeout`. `FlushMultipathDevice(*Device)` invokes `multipath -f <path>`. `ResizeMultipathDevice(*Device)` invokes `multipathd resize map <name>`.

Control flow: `ExecWithTimeout` builds an `exec.CommandContext`, returns deadline errors explicitly, and otherwise returns stdout plus command error. `FlushMultipathDevice` resolves a device path, runs `multipath -f`, tolerates the device already disappearing, rewrites `map in use` into a clearer error, and logs the outcome. `ResizeMultipathDevice` runs `multipathd` and wraps combined output in the error.

State and persistence: these functions mutate host device-mapper/multipath state. No repository state is persisted.

Dependencies and integration: depends on Linux `multipath`, `multipathd`, `os.Stat`, `exec`, `context`, and `klog`. `iscsi.go` calls flush during `DisconnectVolume`; resize is available for expansion paths elsewhere in the driver.

Risks: `ExecWithTimeout` uses `errors.Is(err, ee)` with a nil `*exec.ExitError`, so stderr replacement is unlikely to behave as intended; `errors.As` would be the normal pattern. Five-second multipath flush may be too short on busy systems. Flush trusts `Device.GetPath`, so wrong `Type`/`Name` fields can target the wrong path.

Test signals: no direct tests are present; host command hooks inherited from package variables allow stubbing in unit tests.
