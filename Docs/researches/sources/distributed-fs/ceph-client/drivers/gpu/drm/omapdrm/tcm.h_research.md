# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/tcm.h

Purpose: Defines the TILER container manager abstraction, area geometry helpers, and inline reserve/free/slice operations used by DMM/TILER code.

Important APIs/types/functions: `struct tcm_pt`, `struct tcm_area`, and `struct tcm` with reserve/free/deinit function pointers. Public inline helpers include `tcm_deinit`, `tcm_reserve_2d`, `tcm_reserve_1d`, `tcm_free`, `tcm_slice`, `tcm_area_is_valid`, `__tcm_is_in`, width/height/size helpers, `tcm_1d_limit`, and `tcm_for_each_slice`. `sita_init` is the concrete allocator constructor.

Control flow: Callers allocate a manager, reserve validated 1D or 2D areas through wrappers that set `area->is2d` and `area->tcm`, use geometry helpers to split or inspect areas, and call `tcm_free` to clear reservations and null the parent pointer.

State and persistence: `struct tcm` holds dimensions, LUT ID, y offset, lock, bitmap pointer, map size, and allocator callbacks. `struct tcm_area` persists reservation coordinates and parent pointer until freed.

Dependencies and integration: Implemented by `tcm-sita.c` and consumed by OMAP DMM/TILER block management. Uses Linux integer, bool, and spinlock types through including contexts.

Risks: Inline wrappers rely on caller-provided structures and assume width/height checks outside algorithms. `tcm_1d_limit` mutates an area in place. `__tcm_sizeof` returns `u16`, which can truncate very large slot counts. License block differs from neighboring GPL-only files and must remain respected.

Test signals: Compile all TILER users, validate area validity/slicing macros on multi-row 1D areas, test free idempotence on failed reserves, and verify size helpers on maximum container dimensions.
