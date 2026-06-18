## sources/distributed-fs/ceph-client/arch/arm64/include/asm/atomic_lse.h

Purpose: provides the Large System Extensions implementation bodies for arm64 atomic integer, 64-bit atomic, cmpxchg, and cmpxchg128 operations. It is included by the atomics dispatch layer rather than used directly by generic code.

Important APIs/types/functions: macro families generate `__lse_atomic_*`, `__lse_atomic_fetch_*`, `__lse_atomic*_add_return*`, `__lse_atomic64_dec_if_positive`, `__lse__cmpxchg_case_*`, and `__lse__cmpxchg128*`. The assembly maps arithmetic and bitwise operations to LSE opcodes such as `stadd`, `ldadd`, `stclr`, `ldclr`, `cas`, and `casp`, with relaxed/acquire/release/full variants.

Control flow: most operations are single inline assembly instructions. Subtraction and `and` are built by negating or complementing the add/clear forms. `dec_if_positive` loops with `casal` until the decrement succeeds or the value is negative.

State and persistence: no durable state. It mutates caller-supplied `atomic_t`, `atomic64_t`, or memory operands with architecture-defined ordering semantics.

Dependencies and integration: depends on `__LSE_PREAMBLE`, atomic type definitions, inline-asm constraints, and the LL/SC/LSE selection framework. It integrates with generic Linux atomic APIs through arm64 atomic headers.

Risks: ordering suffixes and memory clobbers are correctness-critical. Any wrong constraint, missing clobber, or return-value adjustment breaks lock-free algorithms. `casp` register pairing and 128-bit alignment are especially sensitive. Test signals are arm64 atomic selftests, LKMM/litmus tests, KCSAN stress, qemu and hardware boot with and without LSE, and compiler build coverage for GCC/Clang.
