# sources/distributed-fs/ceph-client/rust/compiler_builtins.rs

## Purpose
Supplies a minimal in-tree substitute for Rust `compiler_builtins`, defining only redirected intrinsic symbols that the kernel wants to catch rather than use silently.

## APIs, Types, and Functions
`define_panicking_intrinsics!` emits extern C functions exported as `__rust*` symbols for float, 128-bit integer, and selected ARM EABI helper intrinsics. The intrinsic groups cover `__addsf3`, `__muldf3`, `__multi3`, `__udivti3`, ARM float compare/add/mul helpers, and ARM `__aeabi_uldivmod`.

## Control Flow, State, and Persistence
Runtime control flow should never reach these functions; if it does, they panic with a message explaining the unsupported type family. Symbol handling is coordinated with `rust/Makefile`, which redirects matching symbols from `core.o` to `__rust...` and weakens/removes conflicting builtin exports.

## Dependencies and Integration
Depends on unstable Rust compiler builtin features, no-builtins compilation, and Makefile `redirect-intrinsics`. It integrates with the kernel policy that Rust code should avoid floating point and unsupported wide arithmetic paths.

## Risks and Test Signals
Risks include missing a newly required intrinsic, architecture-specific compiler emission differences, panic paths in contexts that cannot tolerate them, and mismatch between this file and `redirect-intrinsics`. Test signals are cross-architecture Rust builds, symbol table inspection of `compiler_builtins.o`, negative tests for accidental float/128-bit use, and boot/module tests ensuring no panicking intrinsic is called.
