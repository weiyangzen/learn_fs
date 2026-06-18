# sources/control-plane/mayastor/io-engine/src/core/fault_injection/fault_method.rs

## Purpose
Defines the concrete effect of a fault injection: return a synthetic I/O status or corrupt buffers.

## Important APIs, Types, and Functions
- `FaultMethod::Status(IoCompletionStatus)` returns an error or status to the caller.
- `FaultMethod::Data` overwrites I/O buffers with deterministic pseudo-random bytes and returns success.
- `FaultMethod::DATA_TRANSFER_ERROR` is a shorthand NVMe data transfer error.
- `inject(state, ctx)` applies the method to an active injection.
- `parse(s)` parses URI method strings such as `status-nvme-sct-sc`, `status-lvol-nospace`, `status-submit-read`, `status-submit-write`, and `status-admin`.

## Control Flow and State
The injection dispatcher calls `FaultMethod::inject` after an `Injection` has matched domain, operation, stage, device, range, time, and retry constraints. Status methods return a copied `IoCompletionStatus`. Data methods call `ctx.iovs_mut()` and replace every byte of every initialized I/O vector using the injection state's seeded RNG.

No independent persistence exists. Data corruption advances the `InjectionState` RNG.

## Dependencies and Integration Points
Depends on `IoCompletionStatus`, `IoSubmissionFailure`, `LvolFailure`, `NvmeStatus`, regex parsing, and `InjectIoCtx`. Used by URI parser and injection runtime.

## Risks and Test Signals
`FaultMethod::Data` mutates raw I/O buffers through context pointers, so context validity and lifetime are critical. Parsing supports only selected lvol/submission/admin names plus NVMe code pairs. Tests should cover display/parse round trips, unsupported strings, deterministic data corruption, and success status after data injection.
