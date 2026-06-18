# sources/distributed-fs/ceph-client/arch/arm64/kernel/kuser32.S

Purpose: Defines fixed-address AArch32 kuser helper code mapped for legacy 32-bit applications.

Important symbols: `__kuser_helper_start`, `__kuser_cmpxchg64`, `__kuser_memory_barrier`, `__kuser_cmpxchg`, `__kuser_get_tls`, `__kuser_helper_version`, and `__kuser_helper_end`. Instructions are emitted with `.inst` in ARM state.

Control flow: helpers implement 64-bit compare-exchange, memory barrier, 32-bit compare-exchange, and TLS read using ARM load-exclusive/store-exclusive or CP15 instructions. The version word encodes helper size in 32-byte units.

Dependencies and integration: used by AArch32 compatibility mapping code (`aarch32_setup_additional_pages()`) and documented fixed ABI addresses. It depends on compatibility mode, ARM instruction encoding, and the historical kernel user helpers ABI.

Risks and test signals: risks are changing instruction layout or helper size, breaking fixed offsets, or exposing helpers on systems without compat support. Test with AArch32 userland atomics/TLS, helper mapping inspection, compat signal/syscall tests, and ABI conformance to `kernel_user_helpers.rst`.
