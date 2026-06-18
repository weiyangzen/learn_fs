# File Research: sources/cow-pools/openzfs/module/zfs/blake3_zfs.c

## Scope

Provides ABD-backed BLAKE3 keyed checksum/MAC routines for OpenZFS checksum infrastructure.

## APIs And Behavior

- `abd_checksum_blake3_native()` copies a keyed BLAKE3 context template, iterates over the ABD contents, updates the context incrementally, and writes the 256-bit digest into `zio_cksum_t`.
- `abd_checksum_blake3_byteswap()` computes the native checksum and byte-swaps each 64-bit checksum word for the byteswap variant.
- `abd_checksum_blake3_tmpl_init()` allocates and initializes a keyed BLAKE3 template from the 32-byte checksum salt.
- `abd_checksum_blake3_tmpl_free()` zeroes and frees the template context.
- Kernel builds use per-CPU BLAKE3 contexts under disabled preemption; userspace builds allocate a temporary context per call.

## State And Dependencies

Depends on BLAKE3 context functions, ABD iteration, zio checksum salt/checksum types, kmem allocation, and kernel per-CPU `blake3_per_cpu_ctx`.

## Risks And Invariants

The checksum functions require a non-null template created by the matching initializer. Kernel callers rely on preemption being disabled while using the per-CPU context. Template and temporary contexts are wiped on free/userspace cleanup, preserving keyed checksum material hygiene.
