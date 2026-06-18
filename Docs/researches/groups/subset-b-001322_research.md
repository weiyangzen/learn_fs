# subset-b-001322 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c

## Purpose
`amdgpu_ttm.c` is the AMDGPU implementation of the DRM TTM memory-management backend. It wires TTM buffer-object operations to AMD GPU memory domains, GART binding, VRAM/GTT/on-chip range managers, DMA-accelerated moves/fills, userptr/HMM page handling, debug memory access, and initialization/teardown of memory-manager state. In this tree it also owns a newer `AMDGPU_PL_MMIO_REMAP` placement used for a fixed MMIO remap page and dma-buf export support.

## Important APIs, Types, And Functions
The file registers `amdgpu_bo_driver`, a `struct ttm_device_funcs`, with callbacks for `ttm_tt_create`, populate/unpopulate/destroy, eviction decisions, move handling, I/O reservation/PFN translation, debug memory access, and delete/release notifications. `struct amdgpu_ttm_tt` extends `struct ttm_tt` with the backing GEM object, GART offset, userptr metadata, a `bound` flag, and optional partition pool ID.

Core exported entry points include `amdgpu_ttm_init`, `amdgpu_ttm_fini`, `amdgpu_ttm_set_buffer_funcs_status`, `amdgpu_copy_buffer`, `amdgpu_ttm_clear_buffer`, `amdgpu_fill_buffer`, `amdgpu_ttm_alloc_gart`, `amdgpu_ttm_recover_gart`, `amdgpu_ttm_domain_start`, userptr helpers, PTE/PDE flag helpers, `amdgpu_ttm_evict_resources`, debugfs init, and `amdgpu_ttm_mmio_remap_alloc_sgt/free_sgt`. Local helpers cover eviction placement, GPU copy-window mapping, blit moves, TTM backend binding/unbinding, VRAM reservation, memory-training reservation, per-partition TTM pools, MMIO remap BO allocation, and SDMA/MMIO debug reads.

## Control Flow
Initialization starts with `ttm_device_init`, optional per-memory-partition TTM pools, VRAM manager setup for discrete GPUs, BAR ioremap of visible VRAM, reservation of firmware/VGA/memory-training regions, GTT manager setup, doorbell and MMIO-remap range managers, the singleton MMIO-remap BO, preempt manager, GDS/GWS/OA managers, and a small SDMA debug-access BO. Teardown reverses those allocations, frees reserved VRAM regions, unmaps the aperture, tears down range managers, and finalizes TTM.

Buffer movement flows through `amdgpu_bo_move`. Simple SYSTEM/GTT transitions use null moves with backend bind/unbind. VRAM-to-SYSTEM and SYSTEM-to-VRAM moves may request a TT hop. Other movable domains prefer accelerated blits through `amdgpu_move_blit`, which delegates to `amdgpu_ttm_copy_mem_to_mem`. That function walks source and destination resources with `amdgpu_res_cursor`, maps inaccessible ranges through temporary GART windows, emits copy packets with TMZ/DCC flags when needed, limits each job to 256 MiB, and returns the last fence. If acceleration is unavailable and both resources are CPU visible/copyable, the fallback is `ttm_bo_move_memcpy`.

GART binding is split between populate/bind/unbind. Userptr BOs allocate an sg table shell during populate, later pin pages with `sg_alloc_table_from_pages` and `dma_map_sgtable`; imported DMA-bufs map attachments on bind; internal TT objects come from TTM pools. Bind computes AMDGPU PTE flags, assigns a GART offset only for TT resources with GART address space, and binds pages into the GART. Reset recovery recomputes PTE flags and rebinds.

## State And Persistence
Long-lived state is in `adev->mman`: the TTM device, VRAM/GTT/preempt managers, optional partition pools, buffer-function scheduler entities and GART windows, reserved VRAM BOs, aperture mapping, and the SDMA debug BO. `struct amdgpu_ttm_tt` persists per-BO userptr/import/binding state. Reserved regions are materialized as kernel BOs so TTM cannot allocate over firmware, VGA, driver usage, or memory-training data. Userptr state persists task and flags until TT destruction; HMM ranges are populated by callers during validation.

## Dependencies And Integration Points
This file is tightly coupled to DRM TTM, DRM scheduler, dma-resv/fence, DMA-buf, Linux DMA mapping, HMM, debugfs, AMDGPU BO/VM/GART/VRAM/GTT managers, SDMA buffer functions, RAS and PSP memory-training state, Atom firmware reserved memory queries, doorbell management, and XGMI/APU partition data. The MMIO-remap path integrates with dma-buf import/export policy by synthesizing `sg_table` entries with `dma_map_resource`, because the remap page has no `struct page` backing.

## Risks
Memory-domain correctness is high risk: wrong PTE flags, GART offsets, TMZ flags, or DCC copy flags can corrupt GPU-visible memory. Error paths in `amdgpu_ttm_set_buffer_funcs_status` and the MMIO-remap singleton need leak and double-free coverage because they allocate scheduler entities, drm_mm nodes, pinned BOs, and range managers in sequence. `amdgpu_ttm_mmio_remap_alloc_sgt` assumes a small contiguous MMIO resource and depends on callers to validate placement and peer-DMA policy. Userptr pin/unpin depends on exactly paired HMM tracking and SG cleanup. Debugfs VRAM/IOMEM access is privileged but still sensitive to IOMMU translation, page mapping checks, and device removal.

## Test Signals
Useful signals include TTM move tests across SYSTEM/GTT/VRAM including multi-hop moves, suspend/resume toggling buffer funcs, GPU reset GART recovery, userptr eviction/revalidation, imported dma-buf bind/unbind, SR-IOV and XGMI firmware-buffer allocation paths, reserved VRAM range accounting, debugfs VRAM/IOMEM read/write smoke tests, and explicit MMIO-remap BO export/import tests checking sg allocation/free, DMA unmap, and teardown ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.h

## Purpose
`amdgpu_ttm.h` is the public AMDGPU TTM memory-management contract. It defines private TTM placement IDs, memory-manager state containers, buffer copy/fill flags, VRAM reservation metadata, and exported helpers used across AMDGPU memory, VM, DMA-buf, userptr, and debug paths.

## Important APIs, Types, And Functions
Private placements are `AMDGPU_PL_GDS`, `AMDGPU_PL_GWS`, `AMDGPU_PL_OA`, `AMDGPU_PL_PREEMPT`, `AMDGPU_PL_DOORBELL`, and `AMDGPU_PL_MMIO_REMAP`; `__AMDGPU_PL_NUM` must track the last private placement. `struct amdgpu_gtt_mgr` wraps a TTM resource manager and `drm_mm`. `struct amdgpu_ttm_buffer_entity` combines a DRM scheduler entity, a mutex, a GART node, and up to two GART window offsets used by blit/fill jobs.

`struct amdgpu_mman` is the central device memory-manager state: TTM device, optional partition pools, aperture mapping, buffer-function ring/entities, VRAM/GTT/preempt managers, reserved regions, and SDMA debug-access BO. `struct amdgpu_copy_mem` describes BO/resource/offset tuples for copy paths. Copy flags encode TMZ, read decompression, write compression, and GFX12 DCC metadata.

The header declares manager lifecycle, GART allocation/recovery, VRAM sg-table export, reservation helpers, accelerated copy/fill helpers, userptr helpers, PTE/PDE flag helpers, debugfs setup, and MMIO-remap sg-table allocation/free. Inline helpers compute an entity GART address and convert a `drm_mm_node` start page to a byte offset.

## Control Flow
Other AMDGPU modules include this header to create and move BOs, bind pages into GART, expose VRAM/GTT manager state, validate userptr pages, and access accelerated copy/fill operations. The placement constants drive switch statements in move, eviction, I/O mapping, and manager initialization paths. The function pointer-free data structures here are initialized by `amdgpu_ttm.c` and later consumed by VM, GEM, DMA-buf, KFD, debugfs, and IP-block code.

## State And Persistence
`struct amdgpu_mman` is persistent for the lifetime of `adev->mman.initialized`. Its reserved-region array tracks BOs and optional CPU mappings for stolen, firmware, driver, and memory-training VRAM spans. Buffer entities persist while accelerated buffer functions are enabled. The header also exposes fields that encode queue-like round-robin state for move/clear entities and per-device debug-access memory.

## Dependencies And Integration Points
The header depends on Linux DMA direction, DRM GPU scheduler, DRM TTM placement, and AMDGPU VRAM/HMM/GMC headers. It forms the compile-time interface between TTM implementation, GTT/VRAM managers, VM/userptr handling, dma-buf export/import, doorbell and MMIO-remap resource managers, and copy emitters.

## Risks
Changing placement IDs is ABI-like inside the driver because TTM manager indices, switch statements, and resource-manager initialization must remain synchronized. `AMDGPU_COPY_FLAGS_SET/GET` must match packet emitter expectations. `struct amdgpu_mman` lifetime and initialization order are delicate because many modules assume subfields exist only after `amdgpu_ttm_init` and buffer funcs exist only after explicit enablement. The declared `amdgpu_ttm_tt_has_userptr` and `amdgpu_ttm_tt_userptr_invalidated` are not implemented in the paired `.c` file, so build coverage across configurations is important.

## Test Signals
Build all relevant AMDGPU configs, especially userptr on/off, debugfs on/off, and MMIO-remap users. Runtime signals include manager debugfs presence for each private placement, successful GART/VRAM allocation, correct copy flag behavior on GFX12 DCC buffers, and source-tree users compiling against the added `AMDGPU_PL_MMIO_REMAP` placement and sg-table API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ttm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.c

## Purpose
`amdgpu_ucode.c` centralizes AMDGPU firmware metadata handling. It prints typed firmware headers for debugging, validates firmware blobs, determines firmware load strategy, exposes firmware versions through sysfs, packs firmware payloads into the PSP/SMU load buffer, derives legacy and IP-version-based firmware names, handles required/optional `request_firmware`, and releases firmware references.

## Important APIs, Types, And Functions
The `amdgpu_ucode_print_*_hdr` family decodes MC, SMC, GFX, RLC, SDMA, PSP, and GPU-info headers by major/minor version. `amdgpu_ucode_validate` checks the firmware file size against the common header. `amdgpu_ucode_hdr_version` compares header versions. `amdgpu_ucode_get_load_type` maps ASIC generation and module load type to direct, SMU, PSP, or RLC-backdoor firmware loading. `amdgpu_ucode_name` maps `enum AMDGPU_UCODE_ID` to human-readable strings, including UMSCH MM, VPE, RS64, JPEG, and ISP IDs.

Sysfs firmware version reporting is generated with `FW_VERSION_ATTR`, then filtered by `amdgpu_ucode_sys_visible`. BO handling is split into `amdgpu_ucode_create_bo`, `amdgpu_ucode_init_bo`, and `amdgpu_ucode_free_bo`. The critical payload extraction is `amdgpu_ucode_init_single_fw`, which switches on ucode ID for PSP-loaded firmware and computes the exact byte range to copy from the firmware blob into `adev->firmware.fw_buf_ptr`. `amdgpu_ucode_patch_jt` appends MEC jump-table data for non-PSP loading. `amdgpu_ucode_ip_version_decode` chooses legacy names or generic `gc_maj_min_rev`, `sdma_...`, `psp_...`, etc. `amdgpu_ucode_request` formats the filename, performs required or no-warn optional firmware request, validates size, and returns errors without directly releasing the firmware on validation failure.

## Control Flow
IP-block early init code typically calls `amdgpu_ucode_ip_version_decode` and `amdgpu_ucode_request` to load firmware and populate `adev->firmware.ucode[]` entries. During PSP-style loading, `amdgpu_ucode_create_bo` allocates a shared firmware BO in VRAM or GTT depending on SR-IOV/debug/XGMI constraints. `amdgpu_ucode_init_bo` chooses `max_ucodes`, refreshes the firmware buffer MC address for XGMI migration, iterates all registered `ucode` records, calls `amdgpu_ucode_init_single_fw`, and advances a page-aligned offset by the copied payload size. Later PSP/SMU code consumes the buffer and the per-ucode MC/kaddr/size metadata.

## State And Persistence
State lives in `adev->firmware`: load type, `fw_buf`, buffer size, current max ucode count, per-ID firmware descriptors, sysfs-visible versions stored elsewhere on `adev`, GPU-info firmware pointer, MC address, and PLDM version. Firmware pointers are retained until matching release paths in IP blocks or `amdgpu_ucode_release`.

## Dependencies And Integration Points
This file depends on Linux firmware loading, DRM sysfs/device attributes, AMDGPU ASIC/IP-version metadata, PSP firmware loading, SR-IOV, XGMI migration, Kicker firmware identification, and all IP-block firmware header layouts from `amdgpu_ucode.h`. It directly integrates with UMSCH MM by recognizing `AMDGPU_UCODE_ID_UMSCH_MM_UCODE`, `AMDGPU_UCODE_ID_UMSCH_MM_DATA`, and command-buffer IDs.

## Risks
Payload extraction is offset-heavy and version-specific; a wrong `ucode_size` or offset can make PSP load invalid data. Validation only checks total size, not per-section bounds or CRC. The filename buffer check tests `r == sizeof(fname)` rather than `r >= sizeof(fname)`, so truncation edge cases deserve attention. Sysfs visibility depends on zero firmware versions being invalid. `amdgpu_ucode_request` documents that callers must release firmware even after validation failure, so caller consistency matters.

## Test Signals
Exercise firmware requests for required and optional files, validation failure paths, sysfs visibility with zero/nonzero versions, PSP buffer packing for MES/RLC/RS64/VPE/UMSCH entries, non-PSP MEC jump-table packing, legacy and generic firmware name generation across IP versions, SR-IOV zeroed firmware buffers, and XGMI migration MC-address refresh.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.h

## Purpose
`amdgpu_ucode.h` defines the binary firmware header schemas, firmware ID/status/load enums, PSP package descriptors, GPU-info payload structures, and `struct amdgpu_firmware` state consumed by AMDGPU firmware loading code.

## Important APIs, Types, And Functions
`struct common_firmware_header` is the prefix shared by all firmware blobs. Specialized headers cover MC, SMC v1/v2 soft PPTables, PSP v1/v2 descriptors, TA firmware, GFX v1/v2 including RS64 code/data starts, MES, RLC v1 through v2.5, SDMA v1/v2/v3, VPE, UMSCH MM, GPU-info, DMCU, DMCUB, and IMU. `union amdgpu_firmware_header` provides a fixed-size view for common parsing.

`enum AMDGPU_UCODE_ID` is the master index for firmware records, covering classic CP/SDMA/SMC/UVD/VCE/VCN firmware plus RS64 stacks, MES data, IMU, RLC sub-images, VPE, UMSCH MM ucode/data/cmd buffer, P2S table, JPEG RAM, and ISP. `struct amdgpu_firmware_info` stores per-payload ID, firmware pointer, MC address, CPU address, size, and TMR MC address words. `struct amdgpu_firmware` stores all per-device firmware state and the shared firmware BO. The header declares print helpers, request/release helpers, BO lifecycle, sysfs lifecycle, load-type selection, firmware name mapping, IP-version decoding, and kicker detection.

## Control Flow
IP-specific code fills `adev->firmware.ucode[]` entries with IDs and firmware pointers using these schemas. `amdgpu_ucode.c` then interprets the concrete header type to copy sub-images into the load buffer or expose version metadata. PSP package headers use flexible arrays, so consumers must use the count fields before iterating descriptors.

## State And Persistence
The schema definitions are immutable contracts for firmware blobs. Device runtime state is represented by `struct amdgpu_firmware`, which persists across firmware setup, PSP/SMU loading, resets, and teardown until the shared BO and firmware references are released.

## Dependencies And Integration Points
The header includes `amdgpu_socbb.h` for GPU-info bounding-box payloads and is included by PSP, SMU, GFX, SDMA, VCN, VPE, UMSCH, display, and firmware management code. It mirrors external firmware binary layout, so it is coupled to linux-firmware packaging and PSP/SMU expectations.

## Risks
Structure layout changes can silently break binary parsing. Flexible array descriptors require strict bounds checking in users. The union reserves `raw[0x100]`, so new headers larger than that need careful audit. `PSP_FW_TYPE_UNKOWN` and `TA_FW_TYPE_UNKOWN` preserve misspelled enum names that may be externally referenced. New firmware IDs must be added consistently to name mapping, max counts, PSP packing, and IP-block registration.

## Test Signals
Compile-time size/layout checks for representative firmware headers, firmware load tests for each major IP family, PSP package descriptor iteration, UMSCH/VPE/RS64 payload extraction, and sysfs firmware-version visibility are the most valuable signals. Fuzzing malformed header sizes and offsets would strengthen validation coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_ucode.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.c

## Purpose
`amdgpu_umc.c` implements common UMC RAS orchestration: memory error address conversion, bad-page retirement, poison-consumption handling, ECC interrupt dispatch, channel iteration, ECC logging, and PA/MCA address translation glue. Version-specific UMC details are delegated through function pointers or IP-specific helpers.

## Important APIs, Types, And Functions
`amdgpu_umc_page_retirement_mca` converts an MCA error address and records retired pages. `amdgpu_umc_handle_bad_pages` queries error counts/addresses from SMU firmware, direct hardware callbacks, or RAS EEPROM, then saves bad pages and notifies DPM of bad-page/channel counts. `amdgpu_umc_pasid_poison_handler` handles poison events with optional PASID callbacks and reset policy, routing to direct retirement, UniRAS manager, deferred page-retirement queue, SR-IOV hooks, or CPU-connected/APU reset-only handling. `amdgpu_umc_ras_sw_init` and `amdgpu_umc_ras_late_init` register the RAS block and ECC IRQ. `amdgpu_umc_process_ecc_irq` and `amdgpu_umc_uniras_process_ecc_irq` dispatch interrupts. Utility APIs include `amdgpu_umc_fill_error_record`, `amdgpu_umc_loop_channels`, `amdgpu_umc_update_ecc_status`, `amdgpu_umc_logs_ecc_err`, `amdgpu_umc_lookup_bad_pages_in_a_row`, `amdgpu_umc_mca_to_addr`, and `amdgpu_umc_pa2mca`.

## Control Flow
On ECC/poison events, callers reach `amdgpu_umc_poison_handler` or `amdgpu_umc_pasid_poison_handler`. Non-SR-IOV pre-UMC12 devices do immediate page retirement and aggregate counts into the UMC RAS manager. UniRAS-enabled devices package interrupt info for the central RAS manager. Other devices enqueue poison requests and wake the page-retirement worker. SR-IOV delegates to virtualization ops.

Page retirement initializes `ras_err_data`, allocates an error-address array sized by `adev->umc.max_ras_err_cnt_per_query`, runs conversion/query callbacks, adds bad pages if the threshold allows, saves EEPROM state, and may trigger GPU reset for uncorrectable/deferred errors or RMA state. Channel iteration walks active AIDs using `active_mask`, node/UMC/channel geometry, or the older flat loops.

## State And Persistence
UMC state is held under `adev->umc`: geometry, active mask, channel offsets, retire unit, RAS callbacks, current `ras_if`, flip-bit data, and last error count. Persistent bad-page data lives in the global RAS context EEPROM control and bad-page tables. `con->page_retirement_lock`, workqueue counters, `gpu_reset_flags`, channel-update flags, and ECC radix trees coordinate longer-lived RAS behavior.

## Dependencies And Integration Points
The file depends on RAS manager APIs, SMU/DPM ECC queries, PSP RAS address translation, KFD SRAM ECC flagging, virtualization RAS hooks, IRQ dispatch, radix tree tags, and UMC v6.7-specific address conversion. It is the common layer between hardware/IP-specific UMC callbacks and driver-wide page retirement/reset policy.

## Risks
Allocation and clearing of `err_data->err_addr` is repeated in several paths, so double allocation/leak risk should be watched. The code intentionally calls query callbacks even when allocation fails to clear hardware status; tests must verify callback behavior with null storage. Reset decisions combine `reset`, UE/DE counts, and RMA state, so incorrect counts can over-reset or miss required recovery. Address conversion support is version-limited in the direct helper and otherwise delegated; unsupported versions can return success in some callback-free paths.

## Test Signals
Inject CE/UE/DE errors through direct and firmware query modes, validate bad-page EEPROM updates, exercise no-memory paths while confirming hardware status clears, cover SR-IOV and UniRAS routing, test active-mask channel iteration on multi-AID devices, verify PASID poison callbacks and reset policies, and validate PA-to-MCA/MCA-to-PA conversion for supported NPS modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.h

## Purpose
`amdgpu_umc.h` defines shared UMC address macros, channel-iteration macros, RAS callback interfaces, UMC device state, and exported common UMC RAS helpers.

## Important APIs, Types, And Functions
Address macros derive 4 KiB, 8 KiB, 32 KiB, 256-byte block, and 256-byte offset values from MCA/error address fields. Loop macros iterate UMC instances, channels, and node instances using `adev->umc` geometry and active masks. EEPROM encoding helpers include `UMC_ECC_NEW_DETECTED_TAG`, `UMC_CHANNEL_IDX_V2`, `UMC_NPS_SHIFT`, and `UMC_NPS_MASK`. `struct amdgpu_umc_flip_bits` records physical-address bit positions used for bad-page retirement expansion. `struct amdgpu_umc_ras` is the version-specific callback table for RAS registration, poison mode, ECC count/address queries, ECC status updates, error address conversion, die ID lookup, flip-bit discovery, and MCA IPID parsing. `struct amdgpu_umc` stores per-device geometry, callbacks, active masks, RAS interface, and retire-unit data.

## Control Flow
IP-specific UMC implementations fill `adev->umc` and `adev->umc.ras`, then call common RAS init helpers. The common `.c` file uses the function pointers and macros to register RAS blocks, walk UMC topology, translate addresses, log ECC errors, and retire pages.

## State And Persistence
The header defines the state that persists for the UMC IP lifetime: channel/UMC/node counts, active masks, channel interleave table, RAS callback table, and flip-bit configuration. Error address counts and RAS interface pointers are updated as events are processed.

## Dependencies And Integration Points
It includes AMDGPU RAS and MCA headers and exposes interfaces used by IP-version-specific UMC files, PSP RAS queries, DPM/SMU ECC handling, and global RAS manager code.

## Risks
The loop macros assume `adev` is in lexical scope and that geometry fields are initialized correctly. EEPROM bit encodings reuse fields with limited width, so compatibility between legacy and v2/NPS encodings is fragile. Callback presence is optional; common code must consistently guard null pointers and define clear behavior when conversion is unsupported.

## Test Signals
Build all UMC IP implementations, test loop coverage on node-less, node-aware, and multi-AID topologies, validate EEPROM channel/NPS encodings, and exercise callback-null fallbacks versus fully implemented RAS callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umr.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umr.h

## Purpose
`amdgpu_umr.h` defines debugfs ioctl ABI structures for UMR-style register, SRBM/GRBM, and GPR/wave access. It is a small shared header for debug tooling state passed through debugfs file operations.

## Important APIs, Types, And Functions
`struct amdgpu_debugfs_regs2_iocdata` carries register access state: whether SRBM/GRBM selection is active, page-lock behavior, GRBM SE/SH/instance, and SRBM ME/pipe/queue/VMID. `struct amdgpu_debugfs_regs2_iocdata_v2` adds `xcc_id` for multi-XCC devices. `struct amdgpu_debugfs_gprwave_iocdata` selects GPR or wave reads by SE/SH/CU/wave/SIMD/XCC and per-thread VGPR/SGPR index. File-private state structs pair an `amdgpu_device`, a mutex, and the current selector data. The `_IOWR` macros define debugfs ioctl commands for setting register and GPR/wave state.

## Control Flow
Debugfs open paths allocate state, ioctl handlers copy one of these structures from userspace, and read/write handlers use the stored selector to choose register addressing mode or wave/GPR target. This header does not implement behavior; it defines the shared ABI contract for those handlers.

## State And Persistence
State is per debugfs file handle. The mutex in each data struct serializes ioctl state updates with subsequent accesses. No persistent device state is changed by the declarations themselves, though the selected state can affect later debugfs reads and writes through the same file descriptor.

## Dependencies And Integration Points
The header depends on Linux ioctl encoding and AMDGPU device definitions included by consumers. It integrates with AMDGPU debugfs register access, GRBM/SRBM selection, multi-XCC debug support, and user-space UMR tooling.

## Risks
Because this is debugfs ABI, structure layout changes can break tools. IOCTL command numbering must remain stable. Consumers must validate selector fields against hardware topology and privilege expectations; this header alone does not constrain ranges. The v1/v2 register state split requires handlers to initialize `xcc_id` safely when old ioctls are used.

## Test Signals
Run UMR/debugfs register access with v1 and v2 state ioctls, multi-XCC selector coverage, invalid selector rejection in consumers, and GPR/wave reads across representative GFX generations. ABI-size checks help protect userspace compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.c

## Purpose
`amdgpu_umsch_mm.c` implements the common AMDGPU IP-block glue for the UMSCH MM firmware scheduler. It initializes the UMSCH ring, loads firmware metadata and VRAM buffers, submits packets and command buffers, manages firmware logs, and wires the UMSCH v4.0 IP block into AMDGPU lifecycle callbacks.

## Important APIs, Types, And Functions
`amdgpu_umsch_mm_submit_pkt` writes packets directly to the no-scheduler UMSCH ring. `amdgpu_umsch_mm_query_fence` polls the ring sync sequence with the device timeout. Ring callbacks implement read/write pointer access through either doorbells or MMIO registers. `amdgpu_umsch_mm_ring_init` creates a 1024-DW ring using MMHUB0, a fixed doorbell index, and `AMDGPU_RING_TYPE_UMSCH_MM`.

`amdgpu_umsch_mm_init_microcode` requests `amdgpu/umsch_mm_4_0_0.bin` for VCN 4.0.5/4.0.6, reads `umsch_mm_firmware_header_v1_0`, records ucode/data sizes and start addresses, and registers UMSCH ucode/data entries in the global PSP firmware array. `amdgpu_umsch_mm_allocate_ucode_buffer` and `amdgpu_umsch_mm_allocate_ucode_data_buffer` copy firmware sections into VRAM BOs. `amdgpu_umsch_mm_psp_execute_cmd_buf` asks PSP to execute the generated command buffer. Lifecycle functions implement early/sw/hw init/fini, suspend/resume, and debugfs firmware-log setup.

## Control Flow
Early init selects v4.0 function tables based on VCN IP version and sets register addresses. SW init allocates a writeback slot, command buffer, debug-log BO, initializes hidden mutex and AGDB indices, initializes the firmware log buffer, initializes the ring, and requests firmware. HW init loads microcode through version-specific callbacks, starts the ring, and sets hardware resources. HW fini stops the ring and frees firmware ucode/data BOs; SW fini releases firmware, ring resources, mutex, command buffer, log BO, and writeback slot.

## State And Persistence
`adev->umsch_mm` stores ring state, MMIO register offsets, firmware pointer/version fields, ucode/data BOs and GPU addresses, command-buffer BO and current pointer, writeback index and scheduler context address, VMID/engine/HQD masks, AGDB doorbell indices, a hidden mutex, and a firmware log BO. Firmware log state is a circular buffer with header, rptr, wptr, size, and wrap fields.

## Dependencies And Integration Points
The file depends on Linux firmware, debugfs, DRM ring helpers, AMDGPU BO allocation, PSP firmware loading, doorbell assignment, VCN IP versioning, `umsch_mm_v4_0` function providers, and `amdgpu_ucode` UMSCH header definitions. It integrates with VPE/VCN queue scheduling through UMSCH resource and queue packets.

## Risks
Only VCN 4.0.5 and 4.0.6 are accepted. The fixed doorbell formula and AGDB index derivation must not collide with other assignments. Firmware BO allocation uses VRAM and alignment requirements that can fail under pressure. SW init error paths after command/log BO allocation do not unwind every earlier allocation locally, relying on upper-level teardown. Debugfs log reads trust firmware-maintained pointers within size checks and update `rptr` from the CPU side.

## Test Signals
Boot devices with VCN 4.0.5/4.0.6, verify firmware request and PSP UMSCH entries, run HW init/fini and suspend/resume loops, submit packets and poll fences, read `amdgpu_umsch_fwlog`, check doorbell writes versus MMIO fallback, inject allocation failures in SW init, and validate no leaks across repeated IP block teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.h

## Purpose
`amdgpu_umsch_mm.h` defines the UMSCH MM scheduler interface: engine and priority enums, packet input layouts, firmware-log format, function pointer table, device state container, register-write macro, helper wrappers, and exported lifecycle/utility APIs.

## Important APIs, Types, And Functions
`enum UMSCH_SWIP_ENGINE_TYPE` names VCN0, VCN1, combined VCN, and VPE engines. `enum UMSCH_CONTEXT_PRIORITY_LEVEL` defines idle, normal, focus, realtime, and count. `struct umsch_mm_set_resource_input` configures VMID masks, collaboration, logging VMID, engine mask, and feature flags. Queue add/remove packet structures carry process, page-table, VA range, quantum, CSA, priority, doorbell, engine, MQD, context handles, VM context control, and suspend/collaboration flags. `struct MQD_INFO` mirrors queue ring state. `struct umsch_mm_funcs` abstracts version-specific set-resource, queue, register, microcode, and ring operations. `struct amdgpu_umsch_mm` is the persistent scheduler state.

The header declares packet submission, fence polling, microcode init/allocation, PSP command-buffer execution, ring init, firmware-log setup, and the `umsch_mm_v4_0_ip_block`. The `WREG32_SOC15_UMSCH` macro either appends register writes to the PSP command buffer or writes registers directly depending on firmware load type.

## Control Flow
Common code calls wrapper macros like `umsch_mm_set_hw_resources`, `umsch_mm_load_microcode`, and `umsch_mm_ring_start`, which dispatch only when the selected version table provides an implementation. IP-version-specific code fills the function table and register offsets during early init.

## State And Persistence
The `amdgpu_umsch_mm` struct persists across IP-block lifetime and owns ring, firmware, command buffer, writeback, masks, AGDB indices, mutex, and log memory. Command-buffer pointer state is especially important under PSP load because register writes become serialized PSP commands.

## Dependencies And Integration Points
The header is consumed by common UMSCH code and `umsch_mm_v4_0` implementation files, and it depends on AMDGPU ring, BO, firmware, VCN, VPE, PSP, and doorbell infrastructure.

## Risks
Packet structure layout must match firmware exactly. The register-write macro assumes `adev` is available in lexical scope and that `cmd_buf_curr_ptr` has enough space. Function wrapper macros silently return success when callbacks are absent, which is convenient for optional hooks but can hide missing version implementations. Locking is exposed as thin mutex helpers and must be consistently used by queue users.

## Test Signals
Compile v4.0 UMSCH with PSP and non-PSP load types, validate command-buffer register programming, add/remove queue packet binary layout, priority and engine masks, firmware-log struct interpretation, and callback presence for supported VCN versions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_umsch_mm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.c

## Purpose
`amdgpu_userq.c` implements usermode queue management for AMDGPU. It exposes queue create/free ioctl behavior, validates queue/rptr/wptr VM mappings, pins doorbells, creates MQDs through IP-specific callbacks, maps/preempts/restores/unmaps queues, integrates eviction fences and VM validation, processes userqueue fence IRQs, detects hangs, participates in suspend/resume and GPU reset, and supports scheduling isolation controls.

## Important APIs, Types, And Functions
`amdgpu_userq_get_supported_ip_mask` reports supported userqueue IPs from `adev->userq_funcs`. Reset/hang logic is handled by `amdgpu_userq_is_reset_type_supported`, `amdgpu_userq_detect_and_reset_queues`, `amdgpu_userq_start_hang_detect_work`, `amdgpu_userq_process_fence_irq`, and `amdgpu_userq_reset_work`. VM/VA helpers include `amdgpu_userq_input_va_validate`, `amdgpu_userq_buffer_vas_mapped`, and cleanup helpers. Queue state helpers wrap IP-specific `preempt`, `restore`, `unmap`, and `map` callbacks and transition `AMDGPU_USERQ_STATE_*`.

Object and doorbell helpers are `amdgpu_userq_create_object`, `amdgpu_userq_destroy_object`, and `amdgpu_userq_get_doorbell_index`. The ioctl path is `amdgpu_userq_ioctl`, which delegates to `amdgpu_userq_create` or queue free. Eviction/restore uses `amdgpu_userq_ensure_ev_fence`, `amdgpu_userq_vm_validate`, `amdgpu_userq_restore_worker`, `amdgpu_userq_evict_all`, and `amdgpu_userq_evict`. Manager lifecycle is `amdgpu_userq_mgr_init`, cancel/fini, suspend/resume, isolation stop/start, VA unmap validation, and pre/post reset hooks.

## Control Flow
Queue creation checks priority permissions, resumes runtime PM, validates IP support and input addresses, allocates a queue object, records queue metadata, reserves the VM root BO, validates queue/rptr/wptr virtual mappings, pins the doorbell BO in the doorbell domain, allocates a fence driver, creates an MQD, ensures a live eviction fence, optionally maps the queue, allocates a queue ID, stores the queue in both per-file and global doorbell xarrays, initializes debugfs and hang detection, increments type count, and returns the queue ID.

Queue free erases the queue from the per-file xarray and drops the kref. Destruction cancels resume/hang work, reserves the root BO, removes VA mapping marks, waits the last fence, removes debugfs, unmaps the queue, decrements type count, destroys MQD/fence/doorbell xarray state under reset-domain protection, unpins doorbell and wptr BOs, frees the queue, and drops runtime PM.

Eviction waits all last fences, preempts mapped queues, and on failure triggers queue reset detection. Restore worker runs when the eviction fence has signaled, validates the whole VM, repins userptr pages through HMM, updates page tables, rearms eviction fences, and restores all queues whose VA mappings remain present.

## State And Persistence
Per-process state lives in `struct amdgpu_userq_mgr`: queue xarray, mutex, delayed resume work, device/file pointers, and per-type counts. Per-queue state persists queue type, VM, doorbell object/index, wptr object, MQD data owned by IP callbacks, fence driver, last fence, VA cursor list, delayed hang work, priority, xcp ID, and state enum. Global interrupt lookup is `adev->userq_doorbell_xa`.

## Dependencies And Integration Points
The file depends on DRM auth/master checks, runtime PM, DRM exec locking, AMDGPU VM and HMM, TTM validation, BO reservation/pinning, doorbell BAR indexing, userqueue fence driver, IP-specific `amdgpu_userq_funcs`, reset domains, KFD-adjacent SRAM ECC/reset behavior indirectly through recovery, debugfs, and eviction fence manager integration.

## Risks
This is concurrency-heavy. Queue state is accessed by ioctl, delayed work, IRQ, suspend/resume, eviction, and reset paths. The create path has multiple cleanup labels and must keep runtime PM, MQD, fence driver, VA marks, doorbell pinning, xarray entries, and mutex state paired. The visible source shows success and some cleanup paths calling `mutex_unlock(&uq_mgr->userq_mutex)` in `amdgpu_userq_create`; tests should confirm the lock is actually held on all paths in this tree. `amdgpu_userq_cleanup` calls `list_del(&queue->userq_va_list)` after individual cursor cleanup, so list-head ownership should be audited. VA mapping marks are atomic bo_va flags shared with unmap validation; missed cleanup can leave false positives. IRQ-side xarray lookup and delayed hang work cancellation must avoid use-after-free.

## Test Signals
Create/free queues for GFX, compute, and SDMA; invalid VA/size/priority/doorbell inputs; high priority with and without `CAP_SYS_NICE` or DRM master; VA unmap while queues exist; eviction fence signaling and restore with userptr BOs; suspend/resume for S0ix and normal paths; per-queue reset fallback to full GPU reset; IRQ fence processing with pending fences; isolation stop/start by XCP; runtime PM reference balancing; lockdep/KASAN/KCSAN coverage for xarray, delayed work, and queue teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_userq.c -->
