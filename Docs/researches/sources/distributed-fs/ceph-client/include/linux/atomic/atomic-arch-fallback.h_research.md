# sources/distributed-fs/ceph-client/include/linux/atomic/atomic-arch-fallback.h

## Purpose

`atomic-arch-fallback.h` is a generated Linux atomic fallback layer. It is included by `include/linux/atomic.h` after the architecture atomic definitions and before the long-width and instrumented wrappers. Its job is to turn the partial set of `arch_*` atomic primitives supplied by a target architecture into a complete `raw_*`, `raw_atomic_*`, and `raw_atomic64_*` API surface.

The header deliberately exports raw helpers that are safe for `noinstr` code. Higher-level `atomic_*` APIs in `atomic-instrumented.h` wrap these raw helpers with KASAN/KCSAN/instrumentation hooks and are unsafe in `noinstr` paths.

## Important APIs, Types, And Macro Families

- Generic exchange and compare-exchange macros: `raw_xchg*`, `raw_cmpxchg*`, `raw_cmpxchg64*`, `raw_cmpxchg128*`, `raw_try_cmpxchg*`, plus local and sync variants. Each family has full, acquire, release, and relaxed forms where applicable.
- 32-bit atomic API: `raw_atomic_read`, `raw_atomic_set`, arithmetic operations, fetch operations, bitwise operations, exchange, compare-exchange, try-compare-exchange, and predicate helpers over `atomic_t`.
- 64-bit atomic API: the matching `raw_atomic64_*` API over `atomic64_t` and `s64`.
- Ordering variants: full-ordering helpers, `_acquire`, `_release`, and `_relaxed` forms. Full-ordering fallbacks wrap relaxed architecture operations with `__atomic_pre_full_fence()` and `__atomic_post_full_fence()`. Acquire and release fallbacks use `__atomic_acquire_fence()` and `__atomic_release_fence()`.
- Conditional generic 64-bit support: when `CONFIG_GENERIC_ATOMIC64` is set, the file includes `<asm-generic/atomic64.h>` before defining the `raw_atomic64_*` fallbacks.

## Control Flow And Fallback Rules

Most functions follow a strict compile-time selection order:

1. Use the exact architecture implementation when present, for example `arch_atomic_fetch_add_release`.
2. If only a relaxed architecture implementation exists, synthesize stronger ordering with the matching fence sequence.
3. If a full-ordering architecture implementation exists, allow weaker acquire/release/relaxed wrappers to use it.
4. For convenience helpers, compose from more primitive raw operations, such as increment from add, decrement from subtract, `andnot` from `and(~i)`, predicate helpers from return-value helpers, and try-compare-exchange from compare-exchange.
5. If no valid primitive exists for an operation that cannot be composed safely, emit a compile-time `#error` such as `Unable to define raw_atomic_fetch_add`.

The `try_cmpxchg` fallbacks are representative: they load the caller-provided expected value, call the corresponding `cmpxchg`, update `*old` with the observed value on failure, and return whether the exchange succeeded. Conditional update helpers such as `raw_atomic_fetch_add_unless`, `raw_atomic_inc_unless_negative`, `raw_atomic_dec_unless_positive`, and `raw_atomic_dec_if_positive` use read plus `try_cmpxchg` retry loops.

`raw_atomic_read_acquire` and `raw_atomic_set_release` have a special native-word path. If `__native_word(atomic_t)` or `__native_word(atomic64_t)` is true, they use `smp_load_acquire()` or `smp_store_release()` directly against the embedded `counter`; otherwise they combine raw read/set with an explicit acquire or release fence.

## State And Persistence Behavior

The header owns no persistent state. All state changes are direct atomic mutations of the caller-owned `atomic_t`, `atomic64_t`, or pointed-to scalar storage. Persistence is therefore entirely determined by the lifetime of the caller's object. The only hidden state-like behavior is the retry loop state in local temporaries such as `c`, `o`, `r`, and `dec`, which exists only during a single atomic operation.

Because many helpers are inline functions or macros, behavior is resolved at compile time from the set of `arch_*` macros and functions visible before this header is included.

## Dependencies And Integration Points

- Includes `<linux/compiler.h>` and relies on compiler annotations/macros such as `__always_inline`, `typeof`, `likely`, and `unlikely`.
- Depends on architecture-provided `arch_*` atomic primitives and architecture exchange primitives.
- Depends on Linux memory-ordering helpers including `smp_load_acquire`, `smp_store_release`, `__atomic_op_fence`, `__atomic_op_acquire`, `__atomic_op_release`, and the explicit fence helpers.
- Uses `atomic_t`, `atomic64_t`, `s64`, and `bool` definitions supplied by surrounding Linux headers.
- Is pulled into the main atomic stack by `include/linux/atomic.h`, after arch declarations and before `atomic-long.h` and `atomic-instrumented.h`.
- Provides the raw target that `atomic-instrumented.h` calls after adding instrumentation and KCSAN barriers.
- Feeds common kernel users such as refcounting, list helpers, jump labels, context tracking, and Ceph/client inherited kernel code that includes `<linux/atomic.h>`.

## Risks And Edge Cases

- Memory-ordering correctness depends on architecture primitives matching the contracts implied by their suffixes. A mislabeled `arch_*_relaxed` or full-ordering primitive can silently corrupt higher-level synchronization.
- Missing architecture primitives can surface as compile-time `#error` failures only when a required fallback cannot be composed.
- The raw API intentionally bypasses instrumentation. Using it in normal code can hide races or memory bugs from KASAN/KCSAN; conversely, using instrumented `atomic_*` APIs in `noinstr` code is unsafe.
- CAS-loop helpers can spin under contention. They are lock-free only to the extent the underlying compare-exchange primitive makes forward progress.
- Width assumptions matter. 64-bit atomics on 32-bit architectures rely either on correct arch implementations or `CONFIG_GENERIC_ATOMIC64`.
- The file is generated by `scripts/atomic/gen-atomic-fallback.sh`; manual edits are likely to be overwritten and should instead be made in the generator or source templates.
- Integer arithmetic follows kernel atomic semantics and can wrap. Predicate helpers such as negative/positive checks depend on signed interpretation of the updated value.

## Test Signals

- Build coverage across supported architectures is the primary signal: missing or inconsistent `arch_*` primitives should fail compilation at this fallback layer.
- Atomic selftests and litmus-style memory-model tests should exercise full, acquire, release, and relaxed variants for reads, stores, RMW operations, and compare-exchange.
- KCSAN/KASAN runs should target the instrumented `atomic_*` wrappers while also ensuring raw helpers remain reserved for valid `noinstr` contexts.
- Stress tests should cover contended `try_cmpxchg` loops and conditional helpers (`add_unless`, `inc_not_zero`, `inc_unless_negative`, `dec_unless_positive`, `dec_if_positive`) for both success and failure paths.
- Cross-architecture builds with and without `CONFIG_GENERIC_ATOMIC64` are important because the 64-bit fallback surface changes depending on generic atomic64 support.
