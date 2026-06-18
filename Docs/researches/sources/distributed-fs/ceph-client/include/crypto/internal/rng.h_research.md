# sources/distributed-fs/ceph-client/include/crypto/internal/rng.h

Purpose: defines internal RNG registration and transform helpers for crypto API random number generators.

Important APIs, types, and flow: `crypto_register_rng*()` and `crypto_unregister_rng*()` manage RNG algorithms. `crypto_del_default_rng()` is available only when RNG support is built. Inline helpers expose transform context and call the algorithm `set_ent` callback to inject entropy.

State and persistence: state lives in RNG transform contexts and default-RNG global state owned by the implementation. No file persistence is declared here.

Dependencies and integration: depends on public RNG API and algorithm registry. It integrates with DRBG/stdrng implementations and callers needing default RNG cleanup during module/runtime transitions.

Risks and test signals: risks include entropy injection into an uninitialized transform, default RNG deletion in disabled Kconfig builds, and missing reseed behavior. Signals include RNG/DRBG self-tests, default RNG lifecycle tests, entropy reset tests, and Kconfig matrix builds with RNG disabled or modular.
