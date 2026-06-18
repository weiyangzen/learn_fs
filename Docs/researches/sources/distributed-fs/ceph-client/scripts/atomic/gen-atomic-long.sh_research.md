# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-long.sh

## Purpose
`gen-atomic-long.sh` generates `linux/atomic/atomic-long.h`, mapping `atomic_long_*` raw operations to either `atomic64_*` or `atomic_*` depending on `CONFIG_64BIT`.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and implements `gen_cast()`, `gen_args_cast()`, and `gen_proto_order_variant()`. It also emits `atomic_long_t`, `ATOMIC_LONG_INIT`, and conditional read aliases.

## Control Flow
The script prints header guards, typedefs `atomic_long_t` to `atomic64_t` on 64-bit or `atomic_t` otherwise, processes every `atomics.tbl` row, and emits raw `atomic_long` inline wrappers that cast pointer arguments to the correct underlying atomic type.

## State And Persistence
No state is persisted except generated stdout redirected by callers.

## Dependencies And Integration Points
It depends on generated raw atomic/atomic64 APIs, architecture type definitions, and `CONFIG_64BIT`. It integrates word-sized atomic operations with generic atomic code.

## Risks And Test Signals
Risks include incorrect pointer casts, mismatch between `long` width and atomic backend, and missing conditional-read aliases. Test signals include correct preprocessed output on 32-bit and 64-bit builds and passing atomic API compile tests.
