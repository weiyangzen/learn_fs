# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_rogue_fwif_shared_check.h

Purpose: This header verifies the exact binary layout of shared FWIF structs from `pvr_rogue_fwif_shared.h`.

Important APIs/types/functions: `OFFSET_CHECK` and `SIZE_CHECK` assert `rogue_fwif_dma_addr` (16 bytes), `rogue_fwif_ufo` (8), `rogue_fwif_cleanup_ctl` (8), `rogue_fwif_cccb_ctl` (32), `rogue_fwif_geom_registers_caswitch` (184), `rogue_fwif_cdm_registers_cswitch` (56), static render/compute context states (368/56), `rogue_fwif_cmd_common` (4), and `rogue_fwif_cmd_geom_frag_shared` (16).

Control flow: None at runtime. Inclusion makes ABI drift a compile-time error.

State and persistence behavior: No state. It protects the queue/control/context-switch structures that persist in shared memory.

Dependencies and integration points: Depends on `linux/build_bug.h` and prior shared struct declarations. It is included by `pvr_rogue_fwif_shared.h` and therefore indirectly by client and core FWIF headers.

Risks: If a shared struct changes without updating firmware and this file, builds fail. If new shared structs are added but not checked, drift can escape. The geometry/fragment shared-prefix check is particularly important for security and cross-BVNC submission.

Test signals: Kernel build, cross-compiler build, and deliberate layout-change compile-failure checks.
