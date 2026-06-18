# sources/distributed-fs/ceph-client/lib/raid/xor/arm/xor-neon-glue.c

Purpose: exposes the ARM NEON XOR implementation to the generic XOR template registry while containing NEON use inside the kernel NEON critical section.

Important APIs and flow: `xor_gen_neon()` calls `kernel_neon_begin()`, then `xor_gen_neon_inner()`, then `kernel_neon_end()`. `xor_block_neon` advertises the wrapper as template name `neon`.

State and persistence: no persistent state; the only state concern is CPU SIMD context ownership while parity buffers are mutated in place.

Dependencies and integration: depends on `xor_arch.h` for `xor_gen_neon_inner()` and NEON helpers, and is registered by `arm/xor_arch.h` when `CONFIG_KERNEL_MODE_NEON` and `cpu_has_neon()` are true.

Risks and test signals: risk centers on entering NEON while preemption or kernel-mode SIMD constraints are not satisfied. Signals include ARM KUnit XOR tests, build coverage with `CONFIG_KERNEL_MODE_NEON`, and parity workloads on NEON-capable ARMv7.
