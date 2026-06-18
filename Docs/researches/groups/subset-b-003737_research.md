# subset-b-003737 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.c

## Purpose

`si.c` is the Southern Islands Radeon ASIC backend. It brings up Tahiti, Pitcairn, Verde, Oland, and Hainan GPUs by loading firmware, programming golden registers and tiling modes, initializing memory-controller/GART/VM state, starting graphics/compute/DMA/UVD/VCE rings, managing power and clock gating, handling interrupts and VM faults, and implementing suspend/resume/reset callbacks used by the common Radeon core.

## Important APIs, Types, and Functions

- Firmware tables and declarations: `MODULE_FIRMWARE(...)` entries advertise legacy and header-based PFP/ME/CE/MC/RLC/SMC firmware names, including special `si58_mc.bin` and `banks_k_2_smc.bin` cases.
- ASIC register tables: `*_golden_registers`, `*_golden_rlc_registers`, `*_mgcg_cgcg_init`, `verde_pg_init`, and MC IO register arrays encode family-specific register programming sequences consumed by `radeon_program_register_sequence` and MC microcode loading.
- Initialization and lifecycle: `si_init`, `si_startup`, `si_resume`, `si_suspend`, and `si_fini` wire the ASIC into BIOS posting, memory manager setup, firmware loading, rings, IRQs, VM manager, audio, UVD/VCE, and teardown.
- Firmware loaders: `si_init_microcode`, `si_mc_load_microcode`, `si_cp_load_microcode`, and `si_rlc_resume` request, validate, decode, and upload microcode for MC, CP/PFP/CE/ME, and RLC paths.
- Display bandwidth/watermarks: `dce6_bandwidth_update`, `dce6_line_buffer_adjust`, `dce6_program_watermarks`, and `dce6_*bandwidth*` compute DCE6 line-buffer partitioning and latency watermarks from mode timings, clocks, DRAM channels, and scaling.
- GPU configuration: `si_gpu_init`, `si_tiling_mode_table_init`, `si_setup_rb`, `si_setup_spi`, `si_get_cu_active_bitmap`, and helpers fill `rdev->config.si`, program GB/DMIF/HDP/DMA/UVD address config, tile mode registers, active CU counts, backend masks, and graphics defaults.
- Rings and command processor: `si_scratch_init`, `si_fence_ring_emit`, `si_ring_ib_execute`, `si_cp_enable`, `si_cp_start`, `si_cp_resume`, and `si_cp_fini` initialize scratch registers, emit fences/IBs, set clear-state packets from `si_default_state`, and manage three CP rings.
- Reset and lockup: `si_gpu_check_soft_reset`, `si_gpu_soft_reset`, `si_gpu_pci_config_reset`, `si_asic_reset`, and `si_gfx_is_lockup` inspect busy bits, disable engines/gating, save/restore MC state, and choose soft or PCI config reset.
- Memory and VM: `si_mc_init`, `si_mc_program`, `si_vram_gtt_location`, `si_pcie_gart_enable`, `si_pcie_gart_disable`, `si_vm_init`, `si_vm_flush`, `si_ib_parse`, and packet3 validators set apertures, page table bases, VM context limits, IB safety checks, and TLB invalidations.
- Power/clock gating and RLC: `si_init_pg`, `si_fini_pg`, `si_init_cg`, `si_fini_cg`, `si_update_cg`, `si_enable_*`, `si_get_csb_size`, `si_get_csb_buffer`, `si_rlc_start/stop/reset/resume`, and `si_enable_lbpw` manage RLC-backed PG/CG/clear-state buffer programming.
- Interrupts: `si_irq_init`, `si_irq_set`, `si_irq_ack`, `si_irq_process`, and `si_get_ih_wptr` configure the interrupt handler ring, enable per-source masks, acknowledge display/HPD events, process fences, VM faults, thermal events, UVD/DMA/CP interrupts, and schedule work.
- Media/PCIe/clocks: `si_uvd_*`, `si_vce_*`, `si_set_uvd_clocks`, `si_set_vce_clocks`, `si_pcie_gen3_enable`, `si_program_aspm`, `si_get_xclk`, `si_get_temp`, and `si_get_gpu_clock_counter` provide media ring bring-up, PLL programming, PCIe link tuning, sensor reads, and clock snapshots.

## Control Flow

`si_init` is the cold-start entry point. It reads and validates AtomBIOS, posts the card if needed, applies family golden registers, initializes scratch/surface/clock/fence/MC/BO state, loads microcode if firmware pointers are not already supplied, initializes power management and all ring descriptors, initializes optional UVD/VCE rings, prepares the IH ring and PCIE GART backing, then calls `si_startup`.

`si_startup` programs PCIe link behavior, allocates VRAM scratch, programs the memory controller, loads MC firmware when DPM did not already cover it, enables PCIE GART and VM contexts, runs `si_gpu_init`, allocates RLC buffers, starts writeback and fence drivers for GFX/compute/DMA rings, starts optional UVD/VCE firmware objects, initializes KMS IRQs/IH, initializes all rings, uploads CP firmware, resumes CP and DMA engines, resumes media rings, then starts the IB pool, VM manager, and audio.

`si_gpu_init` first derives per-family hardware limits, initializes HDP and BIF access, derives memory row/tile metadata from MC registers, programs address-config registers across graphics/display/DMA/UVD blocks, writes the tile-mode table, discovers disabled render backends and active CUs, then writes graphics defaults and cache invalidation settings.

Reset flow starts with `si_gpu_check_soft_reset`, which maps busy/status bits into `RADEON_RESET_*` flags. `si_asic_reset` marks BIOS scratch as hung if needed, tries `si_gpu_soft_reset`, then optionally falls back to `si_gpu_pci_config_reset`. Soft reset disables PG/CG/RLC/CP/DMA, saves and stops the MC, pulses GRBM/SRBM soft-reset bits, resumes MC, and prints status. PCI config reset additionally bypasses clocks, powers down SPLL, clears bus mastering, and uses PCI config reset.

IB validation is performed by `si_ib_parse`. It rejects packet0, accepts packet2 nops, and routes packet3 validation based on const-IB, GFX, or compute ring. Register-writing packet3 operations are constrained through `si_vm_reg_valid`; `PACKET3_CP_DMA` receives special source/destination register validation.

IRQ flow initializes the IH ring in `si_irq_init`, enables masks in `si_irq_set`, and processes 128-bit interrupt vectors in `si_irq_process`. It acknowledges display status before parsing, advances byte rptr entries by 16, dispatches fence processing by source/ring id, decodes VM faults, schedules DP/hotplug/thermal work after the loop, and restarts if wptr changed while processing.

## State and Persistence Behavior

The file persistently mutates `struct radeon_device`: firmware pointers and `new_fw`, `config.si` topology/tile/backend/CU fields, MC aperture sizes and locations, GART readiness and saved VM context table bases, ring readiness and write pointers, IH enabled/rptr state, RLC BO metadata and clear-state data, UVD/VCE availability and ring sizes, scratch register ownership, power-management clocks/thermal state, and `accel_working`.

Hardware state persists in many register blocks: MC apertures and VM contexts, CP ring bases and microcode RAM, RLC microcode and PG/CG registers, DCE watermarks, PCIe link/ASPM registers, UVD/VCE PLLs, interrupt masks, and tile mode registers. Suspend/fini paths explicitly unwind CP/DMA/media/audio/VM/IRQ/WB/GART state, but many register writes remain until reset or reinitialization.

Firmware ownership is long-lived after `si_init_microcode`; failure paths release all requested firmware objects and null pointers. `si_init` deliberately refuses a final successful init when MC firmware is absent because advanced operations need trained memory clocks/voltages.

## Dependencies and Integration Points

- Linux/DRM: firmware loader, PCI/PCIe capability helpers, delays, mutexes, atomics, workqueues, DRM vblank/KMS helpers, logging, endian helpers, and module firmware metadata.
- Radeon core: BIOS/AtomBIOS, BO/GEM/TTM, GART, VM manager, IB pool, fence driver, ring helpers, writeback, IRQ KMS helpers, power management/DPM, audio, UVD/VCE helpers, and common reset/display/MC helpers from R600/Evergreen/Cayman/Northern Islands code.
- Register headers: `sid.h`, `evergreen.h`, `r600.h`, firmware headers in `radeon_ucode.h`, clear-state data in `clearstate_si.h`, and `si_default_state` from `si_blit_shaders.h`.
- ASIC callback tables in `radeon_asic.c` reference exported SI functions such as `si_init`, `si_fini`, `si_resume`, `si_suspend`, `si_asic_reset`, `si_gfx_is_lockup`, `si_vm_flush`, `si_ib_parse`, `si_get_xclk`, `si_set_uvd_clocks`, and `si_set_vce_clocks`.

## Risks and Edge Cases

- Firmware selection is fragile: all six new-style firmware files must validate together or the driver rejects mixed old/new firmware. Special revision/device cases for SMC and MC firmware are easy to regress.
- Several hardware wait loops only break on timeout without returning an error, so later code may proceed after incomplete training, link changes, RLC serdes idle, or buffer allocation.
- `si_cp_load_microcode` declares the new ME firmware pointer as `const __be32 *` while reading with `le32_to_cpup`; this works as pointer arithmetic but is type-inconsistent and easy to misread.
- `si_setup_spi` mutates `mask` with `mask <<= k` inside the loop, producing a non-linear mask sequence after `k > 1`. If intentional, it needs care; if not, CU selection could be wrong.
- Display watermark calculations assume 4 bytes per pixel and simplified efficiency constants; unusual modes, scaling, and multi-head combinations may be under-modeled.
- VM packet validation whitelists registers and packet types. Missing newly legal packets can reject valid workloads; missing illegal side effects can expose privileged register writes.
- `si_irq_process` relies on IH ring contents and cached display interrupt status staying consistent; overflow handling skips to `wptr + 16`, which may drop events by design.
- Error cleanup in `si_startup` is mostly delegated to the caller's failure block in `si_init`; resume failures can leave partially initialized blocks that later suspend/fini must tolerate.
- Power/clock-gating order is explicitly important around RLC and GUI idle interrupts. Changing order can cause hangs that are hard to reproduce.

## Test Signals

- Boot/resume tests on each SI family should verify firmware selection, golden-register programming, MC firmware training, CP/DMA/RLC ring tests, GART enablement, VM context initialization, and `accel_working`.
- Fault-injection should cover missing/invalid/mixed firmware, absent MC firmware, GART pin failure, IH allocation failure, ring init failure, UVD/VCE init failure, and `si_startup` partial cleanup.
- GPU reset tests should exercise soft reset masks for GFX/CP/DMA/DMA1/RLC/IH/VMC/display and hard PCI config reset, with no persistent hung BIOS scratch after recovery.
- VM/IB parser tests should cover legal and illegal packet3 streams for const CE, GFX, compute, register writes, CP DMA register source/destination validation, and packet0 rejection.
- Display tests should cover single and paired CRTC line-buffer allocation, DPM high/low clocks, interlaced/scaled modes, vblank/page-flip interrupts, HPD/DP events, and thermal IRQ work scheduling.
- Power tests should toggle CG/PG flags across GFX/MC/SDMA/BIF/HDP/UVD and validate RLC clear-state buffer contents from `si_get_csb_size`/`si_get_csb_buffer`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.h

## Purpose

`si.h` is the small private Southern Islands interface shared by SI-specific Radeon implementation files and neighboring ASIC code. It forward-declares core Radeon structs and exposes a focused set of helper entry points implemented in `si.c`.

## Important APIs, Types, and Functions

- `struct radeon_device` and `struct radeon_mc` are forward declarations so callers do not need full definitions from this header alone.
- `si_mc_load_microcode(struct radeon_device *rdev)` uploads MC firmware and associated IO debug register tables.
- `si_gpu_check_soft_reset(struct radeon_device *rdev)` returns a `RADEON_RESET_*` mask based on SI busy/status registers.
- `si_vram_gtt_location(struct radeon_device *rdev, struct radeon_mc *mc)` lays out VRAM and GTT apertures with SI address-space limits.
- `si_rlc_reset(struct radeon_device *rdev)` pulses the RLC soft-reset bit.
- `si_init_uvd_internal_cg(struct radeon_device *rdev)` applies UVD internal clock-gating defaults.
- `si_get_csb_size(struct radeon_device *rdev)` and `si_get_csb_buffer(struct radeon_device *rdev, volatile u32 *buffer)` expose RLC clear-state-buffer sizing and packet generation.

## Control Flow

The header does not implement control flow; it provides cross-file linkage. `si.c` calls some of these internally and other Radeon modules can call them through direct declarations or ASIC callback tables. Typical flow is: memory setup uses `si_vram_gtt_location`, startup or DPM code invokes `si_mc_load_microcode`, reset/lockup logic checks `si_gpu_check_soft_reset`, RLC setup uses `si_rlc_reset` and CSB helpers, and UVD setup can call `si_init_uvd_internal_cg`.

## State and Persistence Behavior

All functions operate on the persistent `struct radeon_device` and, for aperture layout, `struct radeon_mc`. The header itself owns no state. Callers should expect the implementations to write persistent GPU registers and mutate `rdev` fields such as MC layout, firmware state, RLC buffers, UVD clock-gating state, and reset observations.

## Dependencies and Integration Points

- Included by `si.c` and `si_dma.c`; its declarations are also consistent with prototypes in `radeon_asic.h`.
- Depends on fixed-width `u32` being visible before or through common Radeon includes in users.
- Integrates SI reset, MC, RLC, and UVD helpers with the wider Radeon ASIC and VM/DMA code.

## Risks and Edge Cases

- The header relies on external include order for `u32`; it is private to the Radeon tree where that is normally satisfied.
- Exporting only partial SI helpers means prototype drift between this header, `radeon_asic.h`, and implementations can break builds.
- The functions have hardware side effects but no contract comments in this header, so callers must understand required initialization state from implementation context.

## Test Signals

- Build coverage should include `si.c`, `si_dma.c`, and `radeon_asic.c` to catch signature drift.
- Runtime tests should confirm callers only use these helpers after `rdev` register access, firmware pointers, RLC buffers, or MC fields are initialized as required by the implementation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_blit_shaders.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_blit_shaders.h

## Purpose

`si_blit_shaders.h` provides the static SI default clear-context command stream used during command-processor startup. Despite the filename, this snapshot contains default register-state packets rather than shader program text: `si_default_state` is written into the GFX ring by `si_cp_start` between preamble begin/end commands so the CP has a known clear-state baseline.

## Important APIs, Types, and Data

- Include guard `SI_BLIT_SHADERS_H` prevents duplicate definitions.
- `static const u32 si_default_state[]` is an inline array of PM4 packet words and register values. It programs DB, PA_SC, VGT, CB, PA_CL, PA_SU, streamout, centroid, AA, and related context/config registers.
- `static const u32 si_default_size = ARRAY_SIZE(si_default_state)` exposes the dword count to `si.c` for ring-space reservation and iteration.

## Control Flow

The array is consumed in `si_cp_start`. After a first ring submission initializes ME and CE partition bases, CP is enabled, the ring is locked for `si_default_size + 10` dwords, `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE` is emitted, every dword in `si_default_state` is copied to the ring, `PACKET3_PREAMBLE_END_CLEAR_STATE` is emitted, and a `PACKET3_CLEAR_STATE` command applies the baseline. Additional context registers for vertex reuse and output deallocation are then written explicitly.

## State and Persistence Behavior

This header is immutable data, but consuming it changes persistent GPU context state. Because the array is `static const` in a header, each translation unit that includes it gets an internal copy. In this subset, `si.c` includes it and uses the internal copy directly.

## Dependencies and Integration Points

- Requires `u32` and `ARRAY_SIZE` from the Radeon/Linux include context.
- The numeric packet words depend on SI PM4 packet encoding and register offsets from `sid.h`.
- Integrated only by `si.c` in this subset, specifically CP clear-state initialization.

## Risks and Edge Cases

- Raw numeric packet/register words are difficult to review; comments identify many registers but some entries have blank comments.
- `si_default_size` is a `u32` initialized from `ARRAY_SIZE`; any future growth beyond ring reservation assumptions would affect `si_cp_start`.
- Because the data is in a header, accidental inclusion by multiple C files increases object size and can create divergent local copies if modified under conditional compilation.
- Incorrect default state can cause rendering, compute, or clear-state failures that appear far from CP startup.

## Test Signals

- CP startup tests should verify `si_cp_start` reserves enough ring space, emits the full array, and successfully passes subsequent `PACKET3_CLEAR_STATE` and ring tests.
- GPU rendering smoke tests after resume/reset should catch invalid default DB/CB/PA/VGT state.
- Static checks can compare the array length and packet counts against expected PM4 packet payload sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_blit_shaders.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dma.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dma.c

## Purpose

`si_dma.c` implements Southern Islands DMA-ring helpers for lockup detection, VM page-table updates, VM TLB flushes through the DMA engine, and buffer-object page copies. It complements the broader SI ASIC setup in `si.c` and is registered as the SI DMA ring/copy backend through Radeon ASIC tables.

## Important APIs, Types, and Functions

- `si_dma_is_lockup(struct radeon_device *rdev, struct radeon_ring *ring)` maps DMA ring index to `RADEON_RESET_DMA` or `RADEON_RESET_DMA1`, checks `si_gpu_check_soft_reset`, updates lockup tracking when idle, and delegates suspected hangs to `radeon_ring_test_lockup`.
- `si_dma_vm_copy_pages(...)` emits SI `DMA_PACKET_COPY` packets that copy page-table entries from a GART source to a page-entry destination in chunks capped at `0xFFFF8` bytes.
- `si_dma_vm_write_pages(...)` emits `DMA_PACKET_WRITE` packets and writes PTE values inline, using `radeon_vm_map_gart` for system pages, raw `addr` for valid VRAM pages, or zero for invalid entries, then ORs in PTE flags.
- `si_dma_vm_set_pages(...)` emits `DMA_PTE_PDE_PACKET` packets for physically contiguous VRAM updates, carrying mask, value, and increment so the DMA engine generates PTE/PDE entries.
- `si_dma_vm_flush(...)` writes VM page table base registers through `DMA_PACKET_SRBM_WRITE`, flushes HDP, invalidates the selected VM context, and emits `DMA_PACKET_POLL_REG_MEM` to wait for invalidate completion.
- `si_copy_dma(...)` synchronizes a reservation object, locks the configured DMA ring, emits chunked `DMA_PACKET_COPY` packets for GPU-page movement, emits a fence, commits the ring, and returns the fence.

## Control Flow

VM page updates are chosen by the common Radeon VM layer based on flags and contiguity. `si_dma_vm_copy_pages` copies prebuilt PTEs; `si_dma_vm_write_pages` writes individual PTE values for system or sparse/non-contiguous mappings; `si_dma_vm_set_pages` uses the hardware PTE/PDE generation packet for contiguous mappings. All three append packet dwords to a caller-supplied IB and advance `ib->length_dw`.

`si_dma_vm_flush` is a ring-emission path rather than an IB builder. It updates the per-VM page table base, flushes HDP cache, requests invalidation for `vm_id`, then polls `VM_INVALIDATE_REQUEST` with mask `1 << vm_id` until the bit clears.

`si_copy_dma` computes total bytes from GPU pages, reserves enough ring space for all copy packets plus sync/fence overhead, syncs against the supplied reservation object, emits copy packets capped at `0xFFFFF` bytes, emits a fence, commits the ring, and frees sync state. Lock or fence errors undo/unwind the ring and return `ERR_PTR(r)`.

## State and Persistence Behavior

The file mutates command buffers (`radeon_ib::ptr` and `length_dw`) and DMA rings (`radeon_ring` write pointer through `radeon_ring_write`). It updates persistent GPU VM context base registers and invalidation state through ring packets, but does not directly write MMIO except through emitted commands. `si_copy_dma` creates a fence whose lifetime is owned by the caller and synchronization subsystem.

Lockup detection updates per-ring lockup bookkeeping when the DMA engine is not reported busy. Page-table update helpers rely on caller-provided `pe`, `addr`, `src`, `count`, `incr`, and `flags` and do not store state between calls.

## Dependencies and Integration Points

- Includes `radeon.h`, `radeon_asic.h`, `radeon_trace.h`, `si.h`, and `sid.h`.
- Depends on SI DMA packet macros and register definitions from `sid.h`, PTE flags from `radeon.h`, and reset status from `si_gpu_check_soft_reset`.
- Integrated through `radeon_asic.c` as SI DMA ring functions, VM update callbacks, and copy callbacks.
- Uses common Radeon ring, fence, sync, reservation, and VM helpers such as `radeon_ring_lock`, `radeon_ring_write`, `radeon_sync_resv`, `radeon_sync_rings`, `radeon_fence_emit`, and `radeon_vm_map_gart`.

## Risks and Edge Cases

- Chunk-size limits are hardware encoded. Off-by-one mistakes can generate invalid packet lengths; this file caps copy at `0xFFFF8` for PTE copies and `0xFFFFF` for BO copies, and write/set paths cap dwords at `0xFFFFE`.
- `si_dma_vm_write_pages` stores 64-bit `pe` and `value` into `u32` IB slots by implicit truncation for the low dword; this matches the packet format but relies on readers understanding the following upper dword writes.
- `si_dma_vm_flush` uses `1 << vm_id`; SI has 16 VM contexts, so callers must keep `vm_id < 16` to avoid invalid shifts and hardware requests.
- The helpers assume the caller reserved enough IB space. They do not check `ib->ptr` bounds.
- `si_copy_dma` calculates ring space as `num_loops * 5 + 11`; changes to sync/fence emission requirements or packet format must keep this reservation accurate.
- Lockup detection depends on `si_gpu_check_soft_reset`; false negatives there will mark the DMA ring healthy and only update lockup tracking.

## Test Signals

- VM tests should cover copy/write/set page update paths for system, valid VRAM, invalid, contiguous, and non-contiguous mappings, including counts crossing chunk caps.
- DMA VM flush tests should validate context base selection for VM IDs below and above 7, HDP flush emission, invalidate request emission, and poll packet fields.
- BO move tests should cover `si_copy_dma` with zero, one, and multi-chunk transfers, reservation synchronization, fence emission failure, and ring lock failure.
- Lockup tests should simulate reset masks for DMA0 and DMA1 and verify idle rings call `radeon_ring_lockup_update` while busy rings call `radeon_ring_test_lockup`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/si_dma.c -->
