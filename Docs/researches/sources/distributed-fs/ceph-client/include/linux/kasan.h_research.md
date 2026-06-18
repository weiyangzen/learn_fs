# sources/distributed-fs/ceph-client/include/linux/kasan.h

## Purpose
Declares the public Kernel Address Sanitizer integration API for page allocator, slab, kmalloc, mempool, vmalloc, module shadow, stack, and reporting paths. It keeps allocator code buildable across disabled, generic, software-tag, and hardware-tag KASAN modes.

## Important APIs, Types, And Functions
Key types and flags include `kasan_vmalloc_flags_t`, `KASAN_VMALLOC_*`, `struct kasan_cache`, and shadow-memory globals. Public wrappers include range/page/slab poison and unpoison helpers, slab object lifecycle helpers, kmalloc/kfree/krealloc hooks, mempool poison/unpoison hooks, `kasan_check_byte()`, stack unpoison helpers, cache metadata helpers, tag reset/report helpers, mode init functions, vmalloc shadow/unpoison/poison/realloc helpers, module shadow allocation, and `kasan_non_canonical_hook()`.

## Control Flow
Most wrappers check `kasan_enabled()` and then call `__kasan_*` implementations; disabled builds return identity pointers, true/false safety defaults, or no-ops. Generic and software-tag modes maintain shadow memory. Hardware tag mode uses integrated initialization and tag checks. `CONFIG_KASAN_VMALLOC` changes whether vmalloc and module shadows are handled by vmalloc infrastructure or special module helpers.

## State And Persistence
KASAN runtime state includes shadow memory, allocation tags, slab metadata, stack traces, quarantine ownership, and vmalloc/module shadow mappings. It is diagnostic in-memory state and does not persist across reboot.

## Dependencies And Integration Points
Depends on KASAN enablement, architecture KASAN hooks, page/slab/vmalloc/task types, static keys, and MM page-table definitions. Integrates tightly with page allocator, SLAB/SLUB, mempool, vmalloc/vmap, module loader, task stack handling, and bug reporting.

## Risks
Allocator paths must respect ownership returns such as `kasan_slab_free()` taking quarantine ownership. Tag-based modes differ from generic metadata behavior. Missing unpoison before reuse can create false positives; missing poison can hide use-after-free. VMALLOC flags such as `KEEP_TAG` and `PROT_NORMAL` must match mapping semantics.

## Test Signals
Signals include KASAN selftests, allocator use-after-free/out-of-bounds reports, mempool reuse tests, vmalloc/module shadow tests, stack instrumentation tests, hardware/software tag mode coverage, disabled-build no-op behavior, and boot tests with deferred KASAN.
