## sources/distributed-fs/ceph-client/mm/kasan/generic.c

Purpose: implements Generic KASAN shadow-byte checking, compiler ABI entry points, global and alloca poisoning, and slab metadata layout.

Important APIs and functions: `kasan_init_generic()`, `kasan_check_range()`, `kasan_byte_accessible()`, `__asan_load/store{1,2,4,8,16,N}()`, noabort aliases, `__asan_alloca_poison()`, `__asan_allocas_unpoison()`, `__asan_set_shadow_*()`, `kasan_cache_create()`, metadata accessors, `kasan_record_aux_stack()`, `kasan_save_alloc_info()`, and `kasan_save_free_info()`.

Control flow: inline checkers map an address to shadow memory, specialize constant access sizes, detect partial-granule violations, report invalid regions, and short-circuit when KASAN is disabled. Global registration unpoisons the object and poisons its redzone. Alloca poisoning installs left/right stack redzones. Cache creation expands object sizes for allocation/free metadata and adaptive redzones while respecting kmalloc max size, constructors, `SLAB_TYPESAFE_BY_RCU`, and slub debug metadata.

State and persistence: Generic mode uses shadow memory bytes plus per-object `kasan_alloc_meta` and `kasan_free_meta`. Free metadata validity is encoded through the object's first shadow byte as `KASAN_SLAB_FREE_META`; allocation metadata is zeroed when invalid.

Dependencies and integration: depends on compiler-emitted ASAN ABI calls, slab cache creation, stackdepot, module global registration, kmemleak, KFENCE bypass, and quarantine hooks.

Risks and test signals: risks include compiler ABI mismatch, false negatives in optimized inline checks, incorrect partial-granule handling, metadata overlap with slab debug data, and cache-size overflow. Tests should include compiler-instrumented loads/stores, memintrinsics, globals, stack/alloca redzones, cache metadata sizing, auxiliary stacks, quarantine, and KUnit generic-only cases.
