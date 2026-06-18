# sources/distributed-fs/ceph-client/scripts/atomic/gen-atomic-instrumented.sh

## Purpose
`gen-atomic-instrumented.sh` generates `linux/atomic/atomic-instrumented.h`, wrapping raw atomic operations with instrumentation hooks for KASAN/KCSAN-style checking.

## APIs, Types, And Functions
It sources `atomic-tbl.sh` and defines `gen_param_check()`, `gen_params_checks()`, `gen_proto_order_variant()`, and `gen_xchg()`. It emits calls such as `instrument_atomic_read()`, `instrument_atomic_write()`, `instrument_atomic_read_write()`, `instrument_read_write()`, `kcsan_release()`, and `kcsan_mb()`.

## Control Flow
The script prints header scaffolding, generates instrumented wrappers for `atomic`, `atomic64`, and `atomic_long` rows from `atomics.tbl`, then emits macro wrappers for `xchg`, `cmpxchg`, `try_cmpxchg`, local cmpxchg, and sync cmpxchg variants across memory-order suffixes.

## State And Persistence
It has no persistent state beyond generated stdout. The generated header becomes persistent when redirected by the orchestrator.

## Dependencies And Integration Points
It depends on atomic metadata helpers, raw atomic fallback headers, `linux/instrumented.h`, and KCSAN memory barrier conventions. It integrates sanitizers with normal atomic APIs while leaving raw APIs for noinstr contexts.

## Risks And Test Signals
Risks include wrong read/write classification for pointer parameters, missing ordering barriers, and macro argument evaluation mistakes. Test signals are successful sanitizer builds, generated wrappers invoking raw operations once, and KCSAN reports reflecting atomic accesses.
