<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/build_assert.rs -->
# sources/distributed-fs/ceph-client/rust/kernel/build_assert.rs

## Purpose
This file defines build-time assertion macros for Rust kernel code, mirroring and extending C `static_assert` and `BUILD_BUG_ON` patterns.

## Important APIs, Types, and Functions
It re-exports `static_assert!`, `const_assert!`, `build_error!`, and `build_assert!`, plus the hidden `build_error::build_error` function. `static_assert!` emits a const `assert!`; `const_assert!` emits a const block assertion; `build_error!` calls the external build-error mechanism; `build_assert!` calls `build_error!` when the condition is not optimized/proven true.

## Control Flow and State
`static_assert!` is evaluated as an item-level constant and cannot depend on generics or runtime values. `const_assert!` works in statement positions and can depend on generics. `build_assert!` uses an `if !$cond` branch that must be eliminated by constant evaluation or optimization; otherwise linking/build fails through `build_error`.

## State and Persistence Behavior
The module has no runtime state. It intentionally fails compilation or linking for invalid code paths.

## Dependencies and Integration Points
It depends on the `build_error` crate/mechanism and is used by other modules such as `bits.rs` and `cpufreq.rs`. The macros are exported at crate root for general kernel Rust use.

## Risks
`build_assert!` can produce less friendly linker/undefined-symbol style failures when the optimizer cannot prove the branch unreachable. Functions using runtime-like values should be `#[inline(always)]` when the caller provides constants. Misusing the stronger macros where simpler `static_assert!` suffices can defer errors.

## Test Signals
Documentation examples describe allowed and disallowed contexts. Practical signals are compile-fail tests or builds that instantiate generic functions and validate assertion behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/rust/kernel/build_assert.rs -->
