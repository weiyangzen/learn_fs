# sources/distributed-fs/ceph-client/drivers/gpu/drm/qxl/qxl_object.h

Purpose: This header declares QXL BO helper APIs and provides inline reservation wrappers.

Important APIs, types, and functions: Inline `qxl_bo_reserve()`, `qxl_bo_unreserve()`, and `qxl_bo_size()` wrap TTM reservation and size access. The header declares BO creation, pinning, mapping, reference, placement, and QXL BO type-check helpers implemented in `qxl_object.c`.

Control flow: The only executable logic is inline reservation: it calls `ttm_bo_reserve()` interruptibly, logs non-restart failures, and returns the error. Unreserve directly calls `ttm_bo_unreserve()`.

State and persistence: No state is owned by the header; it manipulates per-BO TTM reservation state through inline helpers.

Dependencies and integration points: Included by most QXL C files that need BO access. It depends on `qxl_drv.h`, DRM device access from `bo->tbo.base.dev`, and TTM reservation semantics.

Risks: Because reservation is exposed as an inline helper, all callers share the same blocking behavior (`interruptible=true`, no deadlock ctx). Misuse inside already-reserved paths would deadlock; locked variants in `qxl_object.c` must be used when the reservation is already held.

Test signals: Compile all QXL files after prototype changes; lockdep for double reservations; static analysis for unbalanced reserve/unreserve and pin/unpin paths.
