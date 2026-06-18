# sources/control-plane/mayastor/io-engine/src/core/fault_injection/injection_api.rs

## Purpose
Provides the global public API for registering, removing, listing, and applying fault injections in I/O paths.

## Important APIs, Types, and Functions
- `add_fault_injection(inj)` enables injections globally and inserts the injection.
- `remove_fault_injection(uri)` removes matching URI entries from the in-memory list.
- `list_fault_injections()` returns cloned injections.
- `injections_enabled()` is the fast hot-path atomic check.
- `inject_submission_error(ctx)` maps injected submission faults into `CoreError`.
- `inject_completion_error(ctx, status)` replaces successful completions with injected status when configured.

## Control Flow and State
`INJECTIONS_ENABLED` starts false and is set when the first injection is added. `Injections` is a lazily initialized `parking_lot::Mutex<Vec<Injection>>`. Adding a `BdevIo` injection also installs the bdev-level hook. Submission injection returns `Ok(())` if disabled, invalid, unmatched, or method yields success; otherwise it maps to a generic bdev I/O error for the operation. Completion injection only runs for successful original completions and returns either the injected status or success.

State is global and volatile. Removing all injections does not reset the enabled atomic.

## Dependencies and Integration Points
Feature gated under `fault-injection`. Called from bdev device and nexus I/O paths, and managed by test gRPC endpoints.

## Risks and Test Signals
Global enable remains true after removals, so hot paths still take the mutex after the first add. The first matching injection wins. Bdev-level hooks installed by `add_bdev_io_injection` are not undone here. Tests should cover disabled fast path, removal semantics, list clone behavior, first-match ordering, completion only on success, and concurrency around the mutex.
