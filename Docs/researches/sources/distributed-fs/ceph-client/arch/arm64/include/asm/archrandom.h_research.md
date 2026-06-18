## sources/distributed-fs/ceph-client/arch/arm64/include/asm/archrandom.h

### Purpose
Implements ARM64 architecture random-number hooks using RNDR/RNDRRS CPU instructions and SMCCC TRNG calls.

### Important APIs, Types, And Functions
Defines `ARM_SMCCC_TRNG_MIN_VERSION`, declares `smccc_trng_available`, and implements `smccc_probe_trng`, `__arm64_rndr`, `__arm64_rndrrs`, `__cpu_has_rng`, `arch_get_random_longs`, `arch_get_random_seed_longs`, and `__early_cpu_has_rndr`.

### Control Flow
Boot can probe SMCCC TRNG version. Runtime random hooks first check max output count and CPU capabilities. `arch_get_random_longs()` uses RNDR for one word. `arch_get_random_seed_longs()` prefers SMCCC TRNG, returning up to three longs from SMCCC registers, and falls back to RNDRRS when available.

### State, Persistence, And Dependencies
State is the global `smccc_trng_available` flag and CPU capability finalization state. Hardware state is the CPU RNG or firmware TRNG. Dependencies include SMCCC, IRQ/preemption rules, cpufeature alternatives, sysreg encodings, and bug/kernel helpers.

### Integration Points
Used by the kernel random subsystem for architecture entropy and seed material on ARM64.

### Risks
Capability checks before finalization must not migrate across CPUs with different features. SMCCC return value interpretation and register ordering must be correct. RNDRRS is a DRBG reseed path, not equivalent to a direct entropy source.

### Test Signals
Boot on RNDR-capable and non-capable CPUs, firmware with/without SMCCC TRNG, test early CPU detection, run random subsystem health tests, and verify preemption-sensitive capability paths with CPU hotplug.
