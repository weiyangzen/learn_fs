# sources/distributed-fs/ceph-client/drivers/gpu/drm/lima/lima_regs.h

Purpose: central register and bitfield catalog for the Lima Mali Utgard DRM driver. It defines PMU, L2 cache, GP, PP, MMU, VM page-table, DLBU, and broadcast register offsets used by the Lima device, scheduler, MMU, L2, GP, PP, and DLBU code.

Important APIs/types/functions: this header exports macros only. Key groups include `LIMA_PMU_*`, `LIMA_L2_CACHE_*`, `LIMA_GP_*`, `LIMA_PP_*`, `LIMA_MMU_*`, `LIMA_VM_FLAG_*`, `LIMA_VM_FLAGS_CACHE`, and `LIMA_VM_FLAGS_UNCACHE`.

Control flow: no executable flow exists here; runtime code consumes the constants when powering blocks, flushing cache, starting GP/PP jobs, masking/clearing interrupts, switching MMU page directories, and forming PTE values.

State and persistence: the header encodes hardware state layout, not driver-owned state. VM flag macros are persistent ABI assumptions for page-table entries and must match the Mali MMU format.

Dependencies and integration points: depends on Linux `BIT()`/`GENMASK()` style bit helpers from includers. Integrated by `lima_vm.c`, GP/PP/MMU/L2/PMU modules, and error recovery paths.

Risks and test signals: wrong masks or offsets can cause hangs, bogus page faults, missed interrupts, or memory corruption. Test by exercising GP and PP submits, MMU faults, cache flushes, suspend/resume power sequencing, and register dumps on Mali-400 and Mali-450 variants.
