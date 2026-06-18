# sources/distributed-fs/beegfs-go/common/beegfs/storagebench.go

## Purpose
`storagebench.go` defines common BeeGFS storage benchmark actions, benchmark types, statuses, and error codes.

## APIs and Control Flow
`StorageBenchAction` covers start, stop, status, cleanup, and unspecified with string output. `StorageBenchType` covers read, write, and unknown. `StorageBenchStatus` covers uninitialized, initialized, error, running, stopping, stopped, finishing, and finished. `StorageBenchError` implements `error` and maps communication, worker, initialization, and runtime error constants to user-friendly strings.

## State, Dependencies, and Integration
These constants are protocol/domain enums likely shared by CLI and management interactions. There are no external dependencies.

## Risks and Test Signals
Numeric values must remain compatible with BeeGFS protocol/server expectations. Unknown values stringify generically, which is safe for display but loses diagnostics. No listed tests verify the enum string mappings.
