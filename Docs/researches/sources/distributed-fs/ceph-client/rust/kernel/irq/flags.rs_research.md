# sources/distributed-fs/ceph-client/rust/kernel/irq/flags.rs

## Purpose
`irq/flags.rs` wraps Linux IRQ registration flags in a Rust bitmask type with documented constants and bitwise operators.

## Important APIs, Types, and Functions
`Flags(c_ulong)` exposes constants for trigger modes, sharing, timer, per-CPU, balancing, polling, oneshot, suspend/resume, threading, auto-enable, and debug behavior. `into_inner` returns the raw `c_ulong` for request code. `BitOr`, `BitAnd`, and `Not` combine and manipulate masks. `new` compile-time checks that C `u32` constants fit in `c_ulong`.

## Control Flow
Callers combine constants with bitwise operators and pass the raw value to IRQ registration internals. Lower C IRQ layers validate invalid combinations, sharing mismatches, and trigger conflicts.

## State and Persistence
`Flags` values are plain copyable masks. Actual IRQ registration state persists in the C IRQ subsystem after request code consumes the flags.

## Dependencies and Integration Points
The module depends on C `IRQF_*` bindings and `build_assert`. It is re-exported by `irq.rs` and used by IRQ request wrappers.

## Risks
`Not` inverts all bits of `c_ulong`, not only known IRQ flags, so callers should use it carefully, usually in masks rather than direct registration. Semantic validity is not enforced by the Rust type.

## Test Signals
Tests should cover raw value conversion, OR/AND composition, representative trigger/shared/oneshot combinations, compile-time constant fit, and integration with IRQ registration failure paths for invalid combinations.
