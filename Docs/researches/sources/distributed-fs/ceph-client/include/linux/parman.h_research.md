# Research: sources/distributed-fs/ceph-client/include/linux/parman.h

Purpose: `parman.h` declares a manager for linear priority array areas, used by drivers that must keep priority-ordered items packed in hardware or software tables while supporting resize and move operations.

Important APIs/types/functions: it defines `enum parman_algo_type` with `PARMAN_ALGO_TYPE_LSORT`, `struct parman_item` carrying a list node and index, `struct parman_prio` carrying priority and item list, `struct parman_ops` with `base_count`, `resize_step`, `resize()`, `move()`, and algorithm selection, plus `parman_create()`, `parman_destroy()`, priority init/fini, and item add/remove functions.

Control flow and state: callers create a `struct parman`, initialize priority buckets, then add or remove items. The implementation can resize backing storage and move contiguous index ranges through caller-provided callbacks to maintain sorted priority layout. State is in list heads, per-item indices, and the opaque manager.

Dependencies and integration points: depends on `linux/list.h` and caller-provided storage movement. It integrates with networking/switch drivers and other table-backed subsystems that need priority insertion without exposing algorithm internals.

Risks and test signals: risks include failed resize rollback, incorrect move ranges corrupting hardware tables, stale `item->index`, and priority-list lifetime mistakes. Tests should cover add/remove across priorities, resize boundaries, move callback ordering, duplicate/fini misuse, and low-memory failures.
