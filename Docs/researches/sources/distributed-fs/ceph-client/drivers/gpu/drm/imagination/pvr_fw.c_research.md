# sources/distributed-fs/ceph-client/drivers/gpu/drm/imagination/pvr_fw.c

## Purpose
Implements common firmware validation, image processing, firmware heap/address management, boot-time FWIF structure creation, firmware object allocation, cleanup requests, MTS scheduling, boot wait, and hard-reset reinitialization for all supported firmware processors.

## Important APIs, types, and functions
- Firmware image handling: `pvr_fw_validate()`, `pvr_fw_get_device_info()`, `pvr_fw_validate_init_device_info()`, `layout_get_sizes()`, `pvr_fw_process()`.
- Section lookup and relocation helpers: `pvr_fw_find_layout_entry()`, `pvr_fw_find_mmu_segment()`, `pvr_fw_find_private_data()`.
- Lifecycle: `pvr_fw_init()`, `pvr_fw_fini()`, `pvr_wait_for_fw_boot()`, `pvr_fw_hard_reset()`.
- FW object APIs: `pvr_fw_object_create()`, `pvr_fw_object_create_and_map()`, `pvr_fw_object_create_and_map_offset()`, `pvr_fw_object_destroy()`, `pvr_fw_object_get_fw_addr_offset()`, `pvr_fw_obj_get_gpu_addr()`.
- Firmware communication support: `pvr_fw_structure_cleanup()` and `pvr_fw_mts_schedule()`.

## Control flow
Validation treats the last 4 KiB of the firmware file as the info header and layout table, checks version, layout entry sizes/count, open-source firmware flag, supported major version, GPU BVNC match, and non-wrapping section ranges. Device-info data immediately before the header initializes quirks, enhancements, features, and feature parameters.

`pvr_fw_init()` chooses a processor definition table by `processor_type`, calls processor `init()`, initializes the firmware `drm_mm`, processes the firmware image, initializes KCCB/FWCCB and return slots, creates FWIF structures, starts the processor, then polls `fwif_sysinit->firmware_started`. Failure unwinds in strict reverse order. `pvr_fw_fini()` destroys FWIF structures, CCBs, code/data objects, checks that no FW objects remain, tears down the FW address allocator, and calls processor `fini()`.

Firmware processing sizes allocations by layout section type, maps code at firmware heap offset 0, maps private data either at a fixed layout address for processors that require it or from the general heap, optionally maps coremem code/data, asks the processor-specific parser to populate host-side shadow buffers, copies those buffers to FW memory, unmaps CPU mappings, and creates the connection-control object in the fixed config heap.

FW object creation wraps GEM allocation, implicit PM/FW protection, firmware `drm_mm` allocation or reservation, processor-specific VM mapping, CPU mapping, optional init callback, and insertion into `fw_objs.list`. Destroy removes the object from the list, unmaps from processor address space, drops GEM, and frees the wrapper.

## State and persistence
`pvr_dev->fw_dev` stores the firmware handle, parsed header/layout pointers, version, processor definitions, firmware heap geometry, `drm_mm`, booted flag, persistent CPU mappings for FWIF structures, and a tracked list of FW objects. Firmware code/data shadow copies in `pvr_fw_mem` persist after boot so hard reset can repopulate memory. FW objects persist in both GPU/FW address spaces until explicitly destroyed. Objects without `PVR_BO_FW_NO_CLEAR_ON_RESET` are zeroed and reinitialized on hard reset.

## Dependencies and integration points
Depends on Linux firmware loading, DRM managed locks/MM allocator, GEM helpers, processor definitions from META/MIPS/RISC-V files, KCCB/FWCCB CCB code, FW trace setup, start/stop sequencing, PVR feature/quirk metadata, device clocks, VM mapping, and Rogue FWIF structures. Cleanup requests are used by context, HWRT, and freelist teardown.

## Risks
Firmware format parsing is trust-boundary code; it validates many sizes but ELF-specific parsing is delegated. `pvr_wait_for_fw_boot()` busy-polls for up to 5 seconds. FW object destroy intentionally leaks memory if unmap fails, preventing use-after-unmap but leaving allocations behind. Hard reset maps every tracked object and warns but continues if mapping returns an error, so a failed vmap could still lead to invalid access. Address calculations depend on processor-specific cacheability encodings and fixed config heap offsets.

## Test signals
Test validation should cover bad header versions, closed-source flag, unsupported major version, wrong BVNC, malformed layout table, missing private-data section, processor-type selection, boot timeout, init unwind paths, cleanup busy/timeout/EIO returns, FW object fixed-offset reservation, hard reset reinitialization, and FW object leak warnings on final teardown.
