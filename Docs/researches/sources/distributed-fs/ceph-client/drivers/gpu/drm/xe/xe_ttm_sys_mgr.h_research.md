# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_ttm_sys_mgr.h

Purpose: Declares the system-memory TTM manager initialization entry point.

Important APIs/types/functions: Forward declares `struct xe_device` and declares `int xe_ttm_sys_mgr_init(struct xe_device *xe)`.

Control flow: Memory-manager setup code calls this once during device initialization to register `XE_PL_TT`.

State and persistence behavior: No state in the header; initialized manager state lives in `xe->mem.sys_mgr`.

Dependencies and integration points: Included by device/TTM setup code that needs to register system placement.

Risks: Minimal API surface. Call ordering matters: it should occur before BOs can request TT placement and before teardown actions are needed.

Test signals: Build coverage and successful TT BO allocation after device initialization.
