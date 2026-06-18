
# sources/distributed-fs/ceph-client/lib/test_xarray.c

## Purpose
`test_xarray.c` is a loadable kernel self-test module for the XArray API. It exercises both the public helpers (`xa_load`, `xa_store`, `xa_insert`, `xa_erase`, `xa_alloc`, `xa_find`, marks, reserves, compare/exchange, destroy) and the advanced `xas_*` state-machine API used by subsystems such as page cache and workingset shadow-node handling.

## Important APIs, types, and functions
The test centers on `struct xarray`, `XA_STATE`, `XA_STATE_ORDER`, `struct xa_node`, `xa_mk_value()`, `XA_RETRY_ENTRY`, `XA_ZERO_ENTRY`, mark constants, and allocation variants created by `DEFINE_XARRAY`, `DEFINE_XARRAY_ALLOC`, and `DEFINE_XARRAY_ALLOC1`. Local helpers such as `xa_store_index()`, `xa_insert_index()`, `xa_alloc_index()`, and `xa_store_order()` normalize value entries and retry out-of-memory allocation paths with `xas_nomem()`. The broad check functions cover error encoding, retry behavior, loading, marks, shrinking, insertion, `xa_cmpxchg()`, reservation, multi-index storage, cyclic allocation, conflict iteration, find/pause/move traversal, range creation, range storage, splitting, object alignment, workingset update callbacks, accounting, order lookup, and destruction.

## Control flow
`module_init(xarray_checks)` runs a fixed sequence of `check_*()` routines against a global `array` and the allocation arrays `xa0`/`xa1`. Each helper mutates an array, validates invariants through `XA_BUG_ON`, and normally tears state down through `xa_erase()` or `xa_destroy()` before returning. Multi-index tests are guarded by `CONFIG_XARRAY_MULTI`; the non-multi configuration still validates single-entry behavior with reduced order limits. Some advanced loops deliberately stress large index ranges and use `schedule()` in page-cache-like lookups to avoid soft lockups.

## State and persistence
The module persists only in-kernel test counters (`tests_run`, `tests_passed`), the static XArrays, `some_val` sentinel objects, and a temporary `shadow_nodes` list. No filesystem or durable state is written. Concurrency-sensitive paths explicitly use `rcu_read_lock()`, `xa_lock()`, `xas_lock()`, and IRQ-safe locking where the tested API expects them.

## Dependencies and integration points
It depends on `<linux/xarray.h>`, module infrastructure, RCU, scheduler calls, page-size constants, and internal XArray node details. It integrates with the kernel module test path rather than KUnit; pass/fail is reported through `printk()` and the module init return code.

## Risks and edge cases
The test intentionally touches internal node fields (`count`, `nr_values`, `xa_head`, `private_list`) and advanced APIs, so it is sensitive to legitimate XArray implementation refactors. Large multi-order loops can be expensive. Assertions rely on value-entry encoding and may need updates if reserved/retry/internal entry semantics change.

## Test signals
Success is `XArray: <n> of <n> tests passed` and a zero module init return. Failures dump the function/line, XArray contents when available, and a stack trace.
