# sources/distributed-fs/ceph-client/rust/kernel/pid_namespace.rs

## Purpose
Provides a transparent, thread-safe Rust reference type for kernel `struct pid_namespace` values.

## APIs, Types, and Functions
`PidNamespace` wraps `Opaque<bindings::pid_namespace>`. `as_ptr` returns the raw C pointer, and unsafe `from_ptr` builds a borrowed reference from a valid raw pointer. `AlwaysRefCounted` increments with `get_pid_ns` and decrements with `put_pid_ns`.

## Control Flow, State, and Persistence
The wrapper itself has no active behavior beyond pointer conversion and refcount operations. Ownership persistence is handled by `ARef` users through the `AlwaysRefCounted` implementation; borrowed references from `from_ptr` rely entirely on the caller's lifetime guarantee.

## Dependencies and Integration
Depends on pid namespace bindings, `Opaque`, `AlwaysRefCounted`, and `NonNull`. It integrates with kernel code that exposes pid namespace pointers to Rust subsystems needing borrowed or owned references.

## Risks and Test Signals
Risks include unsafe `from_ptr` on null or stale namespace pointers, refcount misuse outside `ARef`, and assuming all namespace fields are immutable without C-side synchronization. Test signals include refcount leak checks, null/stale pointer audits at call sites, and thread handoff tests for `ARef<PidNamespace>`.
