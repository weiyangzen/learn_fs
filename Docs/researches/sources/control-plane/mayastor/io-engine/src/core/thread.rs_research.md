# sources/control-plane/mayastor/io-engine/src/core/thread.rs

## Purpose
Provides the `Mthread` type alias for `spdk_rs::Thread`, preserving the older core naming convention used across io-engine.

## Important APIs, Types, and Functions
- `pub type Mthread = spdk_rs::Thread`.

## Control Flow and State
No behavior is implemented here. All methods and state are provided by `spdk_rs::Thread`.

## Dependencies and Integration Points
Re-exported by `core/mod.rs` and used by environment startup/shutdown signal handling to access primary SPDK thread context.

## Risks and Test Signals
The alias can obscure the underlying type for readers, but it avoids broad churn. Tests are covered by `spdk_rs::Thread` integration and callers such as `env.rs`.
