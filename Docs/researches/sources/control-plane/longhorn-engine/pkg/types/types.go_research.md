## sources/control-plane/longhorn-engine/pkg/types/types.go

### Purpose
`types.go` centralizes engine-wide constants, enums, and interfaces used by controller, replica, backend, frontend, and sync packages.

### Important APIs, Types, And Functions
The file defines replica modes `WO`, `RW`, `ERR`, process states, engine states, backup credential environment variable names, frontend names, retry constants, `VolumeHeadName`, snapshot limits, data-server protocols, replica lifecycle states, and sync retry/concurrency defaults.

Interfaces include `ReaderWriterUnmapperAt`, `UnmapperAt`, `DiffDisk`, `Backend`, `BackendFactory`, `SharedTimeouts`, `Controller`, `Server`, `Frontend`, and `DataProcessor`. Data structs include `Replica`, `ReplicaSalvageInfo`, `Metrics`, `RWMetrics`, and `FileLocalSync`. Helpers convert between internal `Mode` and `enginerpc.ReplicaMode` and detect already-purging errors.

### Control Flow
Most behavior is declarative interface definition. Conversion helpers switch on known replica modes and default unknown values to `ERR`. `IsAlreadyPurgingError` performs substring matching on error messages.

### State, Persistence, And Dependencies
The file persists no state. It defines contracts implemented by replica backends and frontends that do persist volume data and expose monitor channels. Dependencies are `io`, `strings`, `time`, and generated `enginerpc`.

### Integration Points
Nearly every Longhorn engine package imports this file for modes, states, and interfaces. `SharedTimeouts` is implemented by `pkg/util/shared_timeouts.go`; disk/sync packages use `VolumeHeadName`, `SyncRetryCount`, and process state constants; gRPC adapters use mode conversion helpers.

### Risks
Because this is a shared contract file, adding methods to interfaces or changing constants can cascade across the engine. Error substring detection is fragile across message wording changes. Unknown gRPC modes becoming `ERR` is safe but can hide version skew.

### Test Signals
Tests should cover mode conversion round trips, defaulting of unknown modes, `IsAlreadyPurgingError` message compatibility, and compile-time interface conformance for backend/frontend implementations.
