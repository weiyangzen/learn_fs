# sources/distributed-fs/ceph-client/include/crypto/internal/simd.h

Purpose: provides shared SIMD-crypto registration helpers and a centralized runtime predicate for whether crypto code may use SIMD registers.

Important APIs, types, and flow: `simd_register_aeads_compat()` registers compatible SIMD AEAD wrappers and returns wrapper handles; `simd_unregister_aeads()` tears them down. `crypto_simd_usable()` normally delegates to `may_use_simd()`, but under full crypto self-tests it also checks a per-CPU flag that temporarily disables SIMD to exercise non-SIMD fallbacks.

State and persistence: state is per-CPU `crypto_simd_disabled_for_test` when full self-tests are enabled and wrapper state returned by registration. No persistence exists.

Dependencies and integration: depends on architecture SIMD permission logic, per-CPU state, AEAD algorithms, and crypto self-test infrastructure.

Risks and test signals: using SIMD in forbidden contexts can corrupt task/FPU state; failing to test fallback paths can hide bugs. Signals include SIMD/non-SIMD self-test parity, preemption/softirq context tests, full self-test runs with forced disable, and architecture-specific FPU state checks.
