## sources/distributed-fs/ceph-client/mm/kasan/kasan.h

Purpose: private KASAN runtime header defining mode-specific constants, metadata layouts, report structures, tag helpers, poisoning APIs, compiler ABI declarations, and KUnit hooks.

Important APIs and types: includes `struct kasan_track`, `struct kasan_report_info`, `struct kasan_global`, Generic metadata structs, tag-mode stack ring structs, report helpers, metadata accessors, quarantine hooks, tag helpers `set_tag()`/`get_tag()`, hardware tag wrappers, poison/unpoison APIs, `kasan_random_tag()`, KUnit suite hooks, and compiler-generated `__asan_*` and `__hwasan_*` entry point declarations.

Control flow: the header selects behavior by config. Generic KASAN requires per-object metadata and uses shadow byte values for stack/global/slab/page states. Tag-based modes use invalid tags, optional stack ring tracking, and hardware or software tag accessors. Hardware-tag inline poison/unpoison maps directly to arch tag range operations; non-hardware modes use out-of-line implementations.

State and persistence: defines the shape of persistent metadata stored in slab redzones or objects, stack depot handles, tag-mode stack rings, static keys for stacktrace/vmalloc behavior, and page allocation sampling globals.

Dependencies and integration: integrates compiler ABI, slab internals, KFENCE, stackdepot, architecture MTE hooks, KUnit, Rust test linkage, and public KASAN headers.

Risks and test signals: ABI structs and magic values must not drift from compiler expectations. Risks include wrong granule size, tag mismatch semantics, metadata offset misuse, and config stubs hiding missing implementations. Tests should span all KASAN modes, compiler-generated instrumentation, Rust helper linkage, report formatting, quarantine, and hardware-tag KUnit exports.
