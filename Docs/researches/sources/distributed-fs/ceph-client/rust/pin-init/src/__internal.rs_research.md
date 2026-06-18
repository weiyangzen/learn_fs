# sources/distributed-fs/ceph-client/rust/pin-init/src/__internal.rs

## Purpose
`__internal.rs` contains runtime support items used by `pin-init` macros but hidden from normal users: closure initializer wrappers, pin/init data traits, stack initialization storage, drop guards for partially initialized fields, and tokens used to restrict unsafe internal calls.

## Important APIs, Types, And Functions
Key items are `Invariant<T>`, `InitClosure<F, T, E>`, `InitOk`, `HasPinData`, `PinData`, `HasInitData`, `InitData`, `AllData<T>`, `StackInit<T>`, `DropGuard<T>`, `OnlyCallFromDrop`, and `AlwaysFail<T>`. `StackInit::init` initializes stack storage and returns `Pin<&mut T>`.

## Control Flow
`InitClosure` delegates `Init` and `PinInit` calls to its stored closure. `StackInit::init` drops any previously initialized value before reusing the slot, runs the supplied pinned initializer, marks the slot initialized, and returns a pinned mutable reference. `DropGuard` drops its pointer on scope exit unless forgotten. `OnlyCallFromDrop` and `InitOk` are unsafe construction tokens used by generated code.

## State And Persistence
`StackInit` stores `MaybeUninit<T>` plus an `is_init` flag and drops initialized contents in its `Drop`. `DropGuard` owns a raw initialized pointer until forgotten. Other types are zero-sized or marker state for type inference and macro discipline.

## Dependencies And Integration Points
It depends on public `Init`, `PinInit`, `PinnedDrop`, `MaybeUninit`, `Pin`, and pointer APIs. Proc macros in `pin-init-internal` generate calls into these internals, especially field drop guards and data-trait lookups.

## Risks And Edge Cases
These APIs are hidden because their safety contracts are subtle. `StackInit::init` can drop a previously pinned value before reinitialization; it must never expose `&mut T` that would allow moves. `DropGuard` requires a valid, initialized, aligned pointer. `OnlyCallFromDrop` and `InitOk` rely on unsafe constructors not being misused outside generated code.

## Test Signals
Signals include the included `stack_init_reuse` test, failure cleanup with `DropGuard`, stack initialization and reinitialization, `AlwaysFail` with `assert_pinned!`, and compile tests that hidden traits are implemented only by generated code where intended.
