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
