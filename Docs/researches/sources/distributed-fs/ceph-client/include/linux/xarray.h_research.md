# sources/distributed-fs/ceph-client/include/linux/xarray.h

## Purpose
Defines the XArray API, Linux's scalable sparse indexed pointer/value store used as the radix-tree successor. It exposes normal load/store/erase/iteration/allocation helpers and an advanced cursor API for code that needs tight control over locking, RCU traversal, marks, multi-index entries, and node updates.

## Important APIs, Types, and Functions
Entry helpers include `xa_mk_value()`, `xa_to_value()`, `xa_is_value()`, tagged pointer helpers, internal-entry helpers, `XA_ZERO_ENTRY`, `XA_RETRY_ENTRY`, `xa_is_zero()`, `xa_is_err()`, and `xa_err()`. `struct xa_limit` and predefined limits constrain ID allocation. `xa_mark_t` values provide three propagated marks plus `XA_PRESENT`. `struct xarray` embeds `xa_lock`, flags, and the RCU-protected tree head; it is initialized through `XARRAY_INIT`, `DEFINE_XARRAY*`, `xa_init_flags()`, or `xa_init()`. Normal APIs include `xa_load()`, `xa_store()`, `xa_erase()`, `xa_store_range()`, mark get/set/clear, `xa_find()`, `xa_find_after()`, `xa_extract()`, `xa_destroy()`, `xa_insert()`, `xa_alloc()`, `xa_alloc_cyclic()`, `xa_reserve()`, and `xa_release()`, with lock, bh, and irq variants for many mutators. The advanced API centers on `struct xa_state`, `XA_STATE()`, `XA_STATE_ORDER()`, `xas_load()`, `xas_store()`, `xas_find()`, `xas_find_marked()`, `xas_next()`, `xas_prev()`, `xas_retry()`, `xas_nomem()`, `xas_pause()`, multi-index split helpers, and iterator macros.

## Control Flow
Normal callers use the wrapper APIs, which take `xa_lock`, may call `might_alloc()`, delegate to `__xa_*` helpers, and release the lock. Iteration macros repeatedly call `xa_find()`/`xa_find_after()` and may take RCU internally. Allocation APIs require arrays initialized with allocation flags so free marks are maintained. Advanced callers create an `xa_state`, acquire either RCU or `xa_lock`, walk to an index, operate on entries, retry on `XA_RETRY_ENTRY`, handle allocation failure with `xas_nomem()`, and reset or pause the cursor after dropping locks. Inline fast paths handle leaf-node next/marked iteration and fall back to out-of-line functions for tree walks, internal entries, multi-index siblings, and boundary cases.

## State and Persistence
The XArray persists entries in `xa_head` and `struct xa_node` chunks. Nodes track shift, parent, slot count, value count, slot pointers, and mark bitmaps. Array flags persist GFP behavior, lock context requirements, allocation/free tracking, zero-busy behavior, accounting, and summary marks. Entries can be NULL, aligned pointers, value entries, tagged pointers, retry/zero/sibling internal entries, or error-encoded return values. RCU protects readers while writers update slots under `xa_lock`.

## Dependencies and Integration Points
Depends on bitmap, bug, compiler attributes, errno encoding, GFP flags, lockdep, RCU, scheduler allocation checks, spinlocks, and optional `list_lru`. Integrates heavily with the page cache, swap cache, ID allocation, filesystems, memory management, device subsystems, and any kernel code formerly using radix trees or IDR-like indexed maps.

## Risks
Storing internal entries through normal APIs is a bug. Callers must distinguish value entries, tagged pointers, NULL/reserved zero entries, and `xa_err()` results. Locking context must match `XA_FLAGS_LOCK_IRQ` or `XA_FLAGS_LOCK_BH` expectations. Advanced iteration can observe retry entries and must restart correctly after lock drops. Multi-index sibling handling is conditional on `CONFIG_XARRAY_MULTI`. Incorrect mark maintenance can break allocation and marked lookup. RCU readers must revalidate entries that can move or be replaced.

## Test Signals
Signals include XArray/radix-tree test suites, ID allocation wrap tests, page-cache stress, swap-cache tests, lockdep for wrong lock context, KCSAN for RCU misuse, fault-injection around `xas_nomem()`, multi-index split tests, and benchmarks for `xa_for_each*` versus advanced iterators.
