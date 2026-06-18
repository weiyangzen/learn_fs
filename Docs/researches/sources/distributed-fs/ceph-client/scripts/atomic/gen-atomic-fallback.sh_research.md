# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-fallback.sh

## Purpose
`gen-atomic-fallback.sh` generates `linux/atomic/atomic-arch-fallback.h`, providing raw atomic fallbacks and compile-time failures when architectures omit required primitives.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and implements `gen_template_fallback()`, `gen_order_fallback()`, `gen_proto_fallback()`, `gen_proto_order_variant()`, and special fallback emitters for `xchg`, `cmpxchg`, `try_cmpxchg`, local cmpxchg, and sync cmpxchg.

## Control Flow
The script prints header guards and helper includes, emits exchange/cmpxchg fallback macros, processes `atomics.tbl` rows for `atomic`/`int`, includes generic atomic64 when configured, processes rows for `atomic64`/`s64`, and closes the header. Each variant prefers `arch_*`, then relaxed/full-order fallbacks when legal, then template-generated fallback or an error.

## State And Persistence
State is shell-local and stdout text. Persistence occurs when `gen-atomics.sh` redirects output to the include tree.

## Dependencies And Integration Points
It depends on `atomics.tbl`, fallback templates, kerneldoc templates, and kernel macros such as `__atomic_op_acquire/release/fence`. It integrates architecture atomic definitions with generic kernel APIs.

## Risks And Test Signals
Risks include generating invalid fallback ordering, missing template coverage, and differences between macro and function arch definitions. Test signals are successful regenerated header compilation across architectures and expected errors when mandatory raw ops are absent.
