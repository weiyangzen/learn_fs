# sources/distributed-fs/ceph-client/rust/helpers/irq.c

## Purpose
Exposes IRQ request registration to Rust.

## APIs, Types, and Functions
`rust_helper_request_irq()` wraps `request_irq()` with handler, flags, name, and device cookie.

## Control Flow, State, and Persistence
State is IRQ subsystem handler registration and caller-managed device cookie lifetime.

## Dependencies and Integration
Depends on `linux/interrupt.h` and Rust IRQ abstractions.

## Risks and Test Signals
Risks include handler ABI mismatch, freeing device data before `free_irq`, and interrupt context safety. Test signals are Rust interrupt driver tests and shared IRQ registration/removal stress.
