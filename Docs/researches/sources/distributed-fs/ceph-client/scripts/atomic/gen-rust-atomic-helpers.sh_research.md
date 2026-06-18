# sources/distributed-fs/ceph-client/scripts/atomic/gen-rust-atomic-helpers.sh

## Purpose
`gen-rust-atomic-helpers.sh` generates C helper functions that expose selected Linux atomic APIs to Rust code.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and implements `gen_proto_order_variant()` to emit `__rust_helper` functions named `rust_helper_<atomic operation>()`.

## Control Flow
The script prints a generated-file header and includes `linux/atomic.h`, then processes `atomics.tbl` rows for `atomic`/`int` and `atomic64`/`s64`. Each generated helper calls the corresponding C atomic function and returns when the operation metadata requires a value.

## State And Persistence
No state is kept beyond generated stdout. The generated `rust/helpers/atomic.c` is persisted by `gen-atomics.sh`.

## Dependencies And Integration Points
It depends on atomic metadata helpers, Rust helper macro conventions, and the kernel Rust support layer. It integrates C atomic operations into Rust bindings without reimplementing atomic semantics.

## Risks And Test Signals
Risks include exposing operations Rust should not call, mismatched return types, and missing new atomic variants. Test signals are successful Rust-enabled kernel builds and regenerated helper source matching `atomics.tbl`.
