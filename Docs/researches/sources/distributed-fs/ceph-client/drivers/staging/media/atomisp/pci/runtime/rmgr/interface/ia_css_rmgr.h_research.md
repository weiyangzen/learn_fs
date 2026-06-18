# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/runtime/rmgr/interface/ia_css_rmgr.h

Purpose: top-level resource-manager interface and inline/extern storage-class control for resource pools.

Important APIs/macros: `ia_css_rmgr_init`, `ia_css_rmgr_uninit`, `STORAGE_CLASS_RMGR_H`, `STORAGE_CLASS_RMGR_C`, and the documented per-resource interface pattern for init/uninit/acquire/release/refcount. It includes `ia_css_rmgr_vbuf.h`.

Control flow/state: public init/uninit orchestrate concrete vbuf pools in `rmgr.c`; the header itself owns no state.

Dependencies/integration: depends on CSS error definitions and vbuf resource manager. The storage-class macros allow implementations to be compiled as externs or inlined via `__INLINE_RMGR__`.

Risks: circular inclusion with `ia_css_rmgr_vbuf.h` is intentional but fragile. Adding new resource types requires consistent naming and storage-class usage.

Test signals: both inline and non-inline builds, initialization failure unwinding, and availability of vbuf pool APIs through the top-level header.
