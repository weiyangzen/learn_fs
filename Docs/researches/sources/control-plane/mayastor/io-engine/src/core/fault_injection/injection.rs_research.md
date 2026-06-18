# sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection.rs

## Purpose
Defines a complete fault-injection rule and its URI representation. It matches I/O context attributes and time/retry constraints, then delegates to `FaultMethod`.

## Important APIs, Types, and Functions
- `Injection` fields include `domain`, `device_name`, `io_operation`, `io_stage`, `method`, `time_range`, `block_range`, `retries`, and internal `InjectionState`.
- `InjectionBuilder` adds `with_offset`, `with_method_nvme_error`, validation, and `build_uri`.
- `Injection::from_uri`, `uri`, and `as_uri` convert to/from `inject://device?...` syntax.
- `is_active()` enforces retry count and begin/end duration.
- `inject(stage, ctx)` performs all matching and applies the method.

## Control Flow and State
Parsing validates an `inject://` URI, derives the target device from host, port, and path, then applies query parameters (`domain`, `op`, `stage`, `method`, `begin_at`, `end_at`, `offset`, `num_blk`, `retries`). `num_blk` is converted into an exclusive end by adding the offset. At runtime `inject` first checks domain, stage, op, device, and block overlap. On first match it starts the state clock and records the first hit. If active, it invokes the selected method.

Injection state is in a `RefCell`, so cloned injections carry cloned state. There is no disk persistence.

## Dependencies and Integration Points
Depends on `url`, `derive_builder`, `NvmeStatus`, `IoCompletionStatus`, and the fault-injection module enums. Used by test gRPC and injection API.

## Risks and Test Signals
`begin_at` timing starts only after the first matching I/O, not at injection creation. Retry counting increments before active-window checking, so delayed injections still consume hits. URI construction formats `begin_at` with debug formatting for milliseconds, which should be checked for round-trip compatibility. Tests should cover bad URI schemes, invalid params, duration ordering, range matching, retries, and parser aliases.
