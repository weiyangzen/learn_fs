## sources/distributed-fs/ceph-client/arch/arm64/include/asm/kasan.h

Purpose: arm64 KASAN initialization and memory-tag helper interface.

Important APIs/types/functions: maps `arch_kasan_set_tag`, `arch_kasan_reset_tag`, and `arch_kasan_get_tag` to tag helpers, and declares `kasan_early_init` plus `kasan_init` when KASAN is enabled.

Control flow: early boot initializes KASAN shadow/tagging before normal memory use; tag helpers manipulate pointer tags inline.

State and persistence: KASAN shadow memory and tag state persist at runtime; this header only declares accessors and init hooks.

Dependencies and integration: depends on memory layout, MTE-KASAN helpers, page-table types, and generic KASAN.

Risks: early init or tag manipulation bugs cause false reports, missed memory bugs, or boot failures. Test signals are KASAN boot, KASAN selftests, MTE tag tests, slab/page allocator tests, and fault-report decoding.
