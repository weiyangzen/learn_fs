<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm_mips.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm_mips.c

Purpose: Manages the MIPS firmware page table used to map PowerVR firmware objects into the MIPS firmware address space.

Important APIs/types/functions: Public functions are `pvr_vm_mips_init()`, `pvr_vm_mips_fini()`, `pvr_vm_mips_map()`, and `pvr_vm_mips_unmap()`. Internal helper `get_mips_pte_flags()` assembles EntryLo permission/cache flags.

Control flow: Initialization computes page-table size from firmware heap size, validates the maximum number of pages, reads physical bus width, allocates and DMA-maps page-table pages, vmaps them write-combined, and selects PFN masks/cache policies for 32-bit versus wider buses. Mapping validates the FW object range and alignment, derives PFNs in the FW heap, gets each object page DMA address, writes MIPS PTEs, and requests MMU flush. Unmap clears PTEs and executes a flush.

State and persistence behavior: Stores `struct pvr_fw_mips_data` in `pvr_dev->fw_dev.processor_data.mips_data`, including physical page-table pages, DMA addresses, vmap pointer, PFN mask, and cache policy. PTE writes persist in the firmware page table until unmapped or finalized.

Dependencies: Uses PowerVR device/FW/GEM/MMU helpers, MIPS constants from `pvr_rogue_mips.h`, DRM managed allocation, Linux DMA mapping, pages, and vmap.

Integration points: Firmware object allocation/mapping code calls this to make FW BOs visible to the MIPS processor. Boot data uses the page-table DMA addresses initialized here.

Risks: Off-by-one range checks, mismatched `end` handling, or wrong PFN masks can map wrong physical pages. DMA mappings and vmap teardown must match initialization. Flush failures after PTE changes can leave stale firmware translations.

Test signals: MIPS firmware boot, firmware object map/unmap stress, physical bus width variants, uncached versus cached FW object flags, forced allocation/DMA-map failures, and MMU flush warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_vm_mips.c -->
