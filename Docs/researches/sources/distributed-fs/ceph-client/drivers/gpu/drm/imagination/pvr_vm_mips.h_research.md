<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm_mips.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm_mips.h

Purpose: Declares the MIPS firmware VM page-table lifecycle and map/unmap API.

Important APIs/types/functions: Public declarations are `pvr_vm_mips_init()`, `pvr_vm_mips_fini()`, `pvr_vm_mips_map()`, and `pvr_vm_mips_unmap()`.

Control flow: No implementation flow.

State and persistence behavior: The declared functions operate on per-device firmware processor data and firmware object mappings.

Dependencies: Forward-declares `struct pvr_device` and `struct pvr_fw_object`.

Integration points: Included by firmware setup/teardown and firmware object mapping code for MIPS-based Rogue firmware processors.

Risks: Callers must initialize before mapping and unmap/finalize in the correct order to avoid stale firmware PTEs or DMA mapping leaks.

Test signals: Build coverage and firmware lifecycle tests that exercise init-map-unmap-fini ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm_mips.h -->
