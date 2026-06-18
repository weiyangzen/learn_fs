# sources/distributed-fs/ceph-client/rust/kernel/irq.rs

## Purpose
`irq.rs` is the top-level Rust IRQ abstraction module. It exposes interrupt registration flags and request/handler types.

## Important APIs, Types, and Functions
It declares private `flags` and `request` modules, re-exports `flags::Flags`, and re-exports `Handler`, `IrqRequest`, `IrqReturn`, `Registration`, `ThreadedHandler`, `ThreadedIrqReturn`, and `ThreadedRegistration` from `request`.

## Control Flow
No runtime control flow is defined here. It controls the public namespace for IRQ helpers.

## State and Persistence
No state is stored in this facade. IRQ registration state is owned by the request submodule and C IRQ core.

## Dependencies and Integration Points
The module maps to Linux interrupt handling APIs and is used by drivers registering hard IRQ or threaded IRQ handlers.

## Risks
The visible API depends on `request.rs`, which is not part of this work item. Users importing from this facade must respect handler lifetime and context rules defined there.

## Test Signals
Build tests should verify the re-exported IRQ names remain stable and can be imported from `kernel::irq`.
