# sources/distributed-fs/ceph-client/arch/arm64/kernel/pi/kaslr_early.c

Purpose: Computes the early virtual KASLR offset in position-independent startup code.

Important APIs: `kaslr_early_init()` returns a high-bit virtual displacement or zero. `get_kaslr_seed()` reads `/chosen/kaslr-seed` from the writable FDT, converts it from big-endian, and clears the property to avoid leaking the seed.

Control flow: if command-line overrides disabled KASLR, return zero. Otherwise use the FDT seed if present; if absent, try architectural RNDR via `__early_cpu_has_rndr()` and `__arm64_rndr()`. The result places the kernel in the middle half of the vmalloc-to-kimage range by multiplying the range by the seed and taking the high 64 bits.

Dependencies and integration: called by `pi/map_kernel.c` during early mapping. Depends on libfdt, arch random, feature override state from `idreg-override.c`, memory layout constants, and the FDT being temporarily mapped writable.

Risks and test signals: risks include not clearing the seed, weak/no entropy disabling KASLR, offset range collision with other virtual allocations, and command-line parsing mismatch. Test with FDT seed, RNDR seed, `nokaslr`, missing entropy, boot log KASLR status, and virtual address placement checks.
