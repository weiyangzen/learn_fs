# sources/distributed-fs/ceph-client/mm/shuffle.h

Purpose: provides compile-time and static-key guarded declarations/wrappers for page allocator free-list shuffling. It lets page allocator code call shuffle hooks with no-op stubs when `CONFIG_SHUFFLE_PAGE_ALLOCATOR` is disabled.

Important APIs/types/functions: defines `SHUFFLE_ORDER` as `MAX_PAGE_ORDER`. Under `CONFIG_SHUFFLE_PAGE_ALLOCATOR` it declares `page_alloc_shuffle_key`, `__shuffle_free_memory`, `__shuffle_zone`, and `shuffle_pick_tail`, and defines inline wrappers `shuffle_free_memory`, `shuffle_zone`, and `is_shuffle_order`. Without the config it provides no-op `shuffle_free_memory`, no-op `shuffle_zone`, `shuffle_pick_tail` returning false, and `is_shuffle_order` returning false.

Control flow: callers use the inline wrappers. When the config is enabled, each wrapper first checks `static_branch_unlikely(&page_alloc_shuffle_key)` and only calls the implementation when the runtime parameter has enabled shuffling. `is_shuffle_order` additionally requires the requested order to be at least `SHUFFLE_ORDER`, so only high-order free-list behavior is randomized through this hook.

State and persistence behavior: the header owns no state beyond declaring the static key. Runtime state lives in `shuffle.c`; disabled builds compile out behavior through inline stubs.

Dependencies and integration points: depends on jump labels and mm page allocator types such as `pg_data_t` and `struct zone` from included contexts. It is intended for inclusion by internal mm/page allocator code, not external modules.

Risks: incorrect guard use could make page allocator behavior depend on shuffle code even in disabled builds. `SHUFFLE_ORDER` being tied to `MAX_PAGE_ORDER` means call sites must understand which order ranges are intended for tail randomization. Static-key state must be enabled before wrappers are expected to do work.

Test signals: build both with and without `CONFIG_SHUFFLE_PAGE_ALLOCATOR`; disabled builds should have no unresolved shuffle symbols and stable allocator behavior. Enabled builds should show wrappers remain no-op until `page_alloc_shuffle_key` is enabled and `is_shuffle_order(order)` flips only for orders at or above `SHUFFLE_ORDER`.
