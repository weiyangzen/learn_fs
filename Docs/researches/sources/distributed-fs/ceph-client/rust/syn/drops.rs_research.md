# sources/distributed-fs/ceph-client/rust/syn/drops.rs

## Purpose

This file defines a small internal utility for wrapping values whose destructor can safely be skipped. It is used to avoid running drop glue for iterator types known to have trivial drop behavior, while documenting the invariant through a marker trait.

## Important APIs, Types, and Functions

- `NoDrop<T: ?Sized>`: transparent wrapper around `ManuallyDrop<T>`.
- `NoDrop::new(value)`: constructs a wrapper only when `T: TrivialDrop`.
- `Deref` and `DerefMut` impls: expose references to the wrapped value.
- `TrivialDrop`: internal marker trait for types that do not need destructor execution.
- Handwritten `TrivialDrop` impls for `iter::Empty<T>`, slice iterators, and option iterators over references.
- `test_needs_drop`: unit test verifying the marker impls correspond to `std::mem::needs_drop == false` even when the item type has a destructor.

## Control Flow

Construction wraps the value in `ManuallyDrop`. Because `NoDrop` has no custom destructor and `ManuallyDrop` suppresses dropping the inner value, dropping `NoDrop<T>` does not drop `T`. The type bound on `new` is the guardrail: only types with explicit `TrivialDrop` impls can be wrapped through the safe constructor.

## State and Persistence

State is limited to the wrapped value. No heap storage, global state, or persistence is present. The behavior directly affects destructor execution, so its state semantics are about what does not happen when the wrapper is dropped.

## Dependencies and Integration Points

The module uses `std::mem::ManuallyDrop`, iterator types from `std::iter`, `std::slice`, `std::option`, and deref traits. It is likely consumed by AST iteration utilities that need erased or empty iterators without unnecessary drop bounds or overhead.

## Risks and Edge Cases

The safety model depends on `TrivialDrop` impls being correct. Adding a `TrivialDrop` impl for a type that owns resources would leak or skip required cleanup. The current impls are for iterator/reference wrappers that should remain destructor-free. The wrapper is safe Rust, but misuse through expanding marker impls would create semantic leaks.

## Test Signals

This file has an inline unit test, `test_needs_drop`, that defines a `NeedsDrop` type and asserts all marked iterator types do not need drop even when parameterized with it. Future marker impls should add corresponding assertions.
