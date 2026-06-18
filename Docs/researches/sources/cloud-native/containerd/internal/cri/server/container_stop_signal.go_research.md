# sources/cloud-native/containerd/internal/cri/server/container_stop_signal.go

## Purpose
This helper file converts between CRI enum signal names and OCI/runtime signal strings, including real-time signal names that encode plus/minus signs in enum identifiers.

## Important APIs, Types, and Functions
`criSignalToOCIStopSignal` converts `runtime.Signal` to strings and returns an invalid-argument wrapped error for unknown enum values. `convertFromCRISignal` changes `PLUS`/`MINUS` markers to `+`/`-`. `toCRISignal` performs the reverse for status reporting and returns `RUNTIME_DEFAULT` for unknown strings.

## Control Flow, State, and Persistence
The functions are pure string/enum transforms with no state. Runtime default maps to an empty OCI stop signal on outbound conversion.

## Dependencies and Integration Points
It depends on generated CRI signal name/value maps and `errdefs.ErrInvalidArgument`. It is used during create validation, stop signal selection, and status reporting.

## Risks and Test Signals
Risks include invalid signal acceptance, real-time signal mangling, and status defaulting hiding unsupported image signals. `container_stop_test.go` and `container_status_test.go` cover runtime default, standard signals, real-time plus/minus conversion, unknown enum errors, and unknown string fallback.
