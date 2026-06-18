# Research group subset-b-003718

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.c

### Purpose

`evergreen.c` is the Radeon DRM/KMS ASIC support implementation for AMD Evergreen-class GPUs and closely related Northern Islands/Fusion-era variants handled through the same callback family. It programs hardware registers for display, memory controller, GART, command processor, RLC, interrupts, UVD, power management, PCIe link policy, reset, suspend/resume, and full device initialization/finalization. The file is a hardware sequencing hub: most routines translate `struct radeon_device` state and ASIC family flags into ordered MMIO writes, firmware uploads, ring setup, and DRM/KMS integration callbacks.

### Important APIs, types, and functions

The public entry points include indirect register helpers `eg_cg_rreg()`, `eg_cg_wreg()`, `eg_pif_phy0_rreg()`, `eg_pif_phy0_wreg()`, `eg_pif_phy1_rreg()`, and `eg_pif_phy1_wreg()`, all protected by index-register spinlocks. `evergreen_get_allowed_info_register()` whitelists status registers for userspace info queries, and `evergreen_tiling_fields()` converts Evergreen tiling flag encodings into hardware field values.

Initialization and lifecycle are centered on `evergreen_init()`, `evergreen_startup()`, `evergreen_resume()`, `evergreen_suspend()`, and `evergreen_fini()`. `evergreen_gpu_init()` derives per-family geometry and resource limits, programs backend/SIMD/tile configuration, shader and scan converter resource registers, cache settings, render backend maps, and default 3D block state. `evergreen_init_golden_registers()` applies large family-specific register tables such as Cypress, Juniper, Redwood, Cedar, Sumo, Barts, Turks, and Caicos golden/MGCG sequences.

Memory and address-space APIs include `evergreen_mc_init()`, `evergreen_mc_program()`, `evergreen_mc_stop()`, `evergreen_mc_resume()`, `evergreen_mc_wait_for_idle()`, `evergreen_get_number_of_dram_channels()`, `evergreen_pcie_gart_tlb_flush()`, the internal `evergreen_pcie_gart_enable()`, `evergreen_pcie_gart_disable()`, `evergreen_pcie_gart_fini()`, and `evergreen_agp_enable()`. Display/KMS helpers include `dce4_program_fmt()`, `dce4_wait_for_vblank()`, `evergreen_page_flip()`, `evergreen_page_flip_pending()`, `evergreen_get_vblank_counter()`, HPD routines, line-buffer allocation, and watermark programming.

Command submission and firmware paths include `evergreen_ring_ib_execute()`, `evergreen_cp_load_microcode()`, `evergreen_cp_start()`, `evergreen_cp_resume()`, `sumo_rlc_init()`, `sumo_rlc_fini()`, `evergreen_rlc_resume()`, and `evergreen_rlc_start()`. Reset and hang detection are handled by `evergreen_print_gpu_status_regs()`, `evergreen_is_display_hung()`, `evergreen_gpu_check_soft_reset()`, `evergreen_gpu_soft_reset()`, `evergreen_gpu_pci_config_reset()`, `evergreen_asic_reset()`, and `evergreen_gfx_is_lockup()`. Interrupt handling is split across `evergreen_disable_interrupt_state()`, `evergreen_irq_set()`, `evergreen_irq_ack()`, `evergreen_irq_suspend()`, `evergreen_get_ih_wptr()`, and `evergreen_irq_process()`.

Power, thermal, UVD, and PCIe helpers include `evergreen_get_temp()`, `sumo_get_temp()`, `sumo_pm_init_profile()`, `btc_pm_init_profile()`, `evergreen_pm_misc()`, `evergreen_pm_prepare()`, `evergreen_pm_finish()`, `sumo_set_uvd_clocks()`, `evergreen_set_uvd_clocks()`, `evergreen_uvd_init()`, `evergreen_uvd_start()`, `evergreen_uvd_resume()`, `evergreen_fix_pci_max_read_req_size()`, `evergreen_pcie_gen2_enable()`, and `evergreen_program_aspm()`.

Important local data includes `crtc_offsets`, DIG/TX/DP/display interrupt offset arrays, family-specific golden register tables, `sumo_rlc_save_restore_register_list`, and `struct evergreen_wm_params`, which carries calculated display watermark inputs.

### Control flow

Cold initialization starts in `evergreen_init()`. It reads and validates ATOMBIOS, resets or posts the card if needed, programs golden registers, initializes scratch/surface/clock/fence state, optionally initializes AGP, probes MC sizing through `evergreen_mc_init()`, initializes the BO manager, loads required firmware, initializes power management, creates GFX and DMA rings, initializes UVD and the interrupt handler ring, initializes PCIe GART metadata, then calls `evergreen_startup()`. If startup fails after acceleration setup, it unwinds CP, DMA, IRQ, RLC buffers, writeback, IB pool, IRQ KMS, and GART before marking acceleration disabled.

`evergreen_startup()` performs the operational hardware bring-up. It enables PCIe gen2 and ASPM where policy and hardware allow, initializes the VRAM scratch page, reprograms the MC aperture while displays are stopped and blacked out, loads NI MC firmware for DCE5 when needed, enables either AGP-style VM registers or the PCIe GART, initializes GPU blocks, allocates RLC buffers for IGPs, initializes writeback, starts fence drivers for GFX and DMA rings, starts UVD, initializes and enables IRQ/IH, initializes GFX and DMA rings, uploads PFP/ME microcode, resumes CP and DMA engines, resumes UVD, initializes the IB pool, and starts audio.

MC programming is carefully sequenced. `evergreen_mc_stop()` saves VGA state, blanks active CRTCs or disables display read requests, waits for frame changes, manually blanks DP SST streams on DCE5 when needed, waits for MC idle, disables CPU framebuffer access, enters MC blackout, and locks double-buffered display registers. `evergreen_mc_program()` writes aperture, FB location, HDP, AGP, and scratch defaults while the controller is quiesced. `evergreen_mc_resume()` rewrites scanout base addresses to VRAM start, restores VGA base, unlocks updates, leaves blackout, re-enables CPU FB access, unblanks displays, waits for frame changes, and restores VGA access.

Display control flow covers format truncation/dither programming, vblank waits, page flips, HPD setup/fini, bandwidth updates, and watermarks. `evergreen_bandwidth_update()` counts enabled CRTCs, adjusts paired line buffers, then calls `evergreen_program_watermarks()` for each CRTC. Watermark calculation derives active and blank times, low/high clocks from DPM or current clocks, DRAM channels, scaler ratios, bytes per pixel, line buffer size, available/average bandwidth, latency hiding, and priority marks before writing PIPE and CRTC priority registers.

Command processor startup initializes the ring through `evergreen_cp_resume()`: reset CP-related GRBM blocks, program ring size and pointers, write WB/scratch addresses, program CP ring base/debug registers, emit ME initialization and clear-state packets through `evergreen_cp_start()`, then run a ring test. IB execution emits mode-control, optional next-rptr bookkeeping through a register or WB memory write, and a `PACKET3_INDIRECT_BUFFER` packet. The default clear-state packet payload comes from `evergreen_blit_shaders.h`.

Reset flow first classifies busy blocks with `evergreen_gpu_check_soft_reset()`, using GRBM/SRBM/DMA/VM/display status and intentionally clearing MC reset from the mask because MC busy is often not a true hang. `evergreen_gpu_soft_reset()` halts CP/PFP, disables DMA if selected, stops/blackouts MC, asserts GRBM/SRBM soft-reset bits for the selected engines, resumes MC, and prints status before and after. `evergreen_asic_reset()` optionally performs PCI config reset directly for hard resets, otherwise tries soft reset and falls back to PCI config reset when the module policy allows.

Interrupt flow separates register programming, acknowledgement, and IH ring decoding. `evergreen_irq_set()` builds CP/DMA/thermal/vblank/pflip/HPD/audio masks from `rdev->irq` atomics and flags, writes CP/DMA/GRBM/display/HPD/audio thermal registers in a hardware-sensitive order, and disables all state if IH is not enabled. `evergreen_irq_process()` snapshots and acknowledges display/AFMT status, serializes IH parsing with `rdev->ih.lock`, decodes 16-byte IH vectors, handles vblank/page flip/HPD/DP/audio/UVD/VM fault/CP/DMA/thermal events, advances IH read pointer, schedules deferred work, and restarts if the write pointer advanced during processing.

Suspend and resume mirror startup. `evergreen_suspend()` shuts down PM, audio, UVD, CP, DMA, IRQ/RLC, WB, and GART. `evergreen_resume()` resets and posts the ASIC, reapplies golden registers, resumes PM for DPM, marks acceleration working, and reruns startup.

### State and persistence behavior

Persistent driver state is stored primarily in `struct radeon_device`. The file mutates `rdev->config.evergreen` with ASIC topology, tile config, active SIMD count, backend map, queue/resource limits, and hardware context count. It fills `rdev->mc` with VRAM width, aperture, visible/real VRAM sizes, and VRAM/GTT locations. It controls `rdev->gart.ready` and pins/unpins the GART table object. It initializes and toggles `rdev->ring[]` objects, `ring->ready`, ring pointers, firmware references, and fence driver state.

Display state is represented by DRM CRTC state and Radeon CRTC side fields such as `line_time`, `wm_high`, `wm_low`, and `lb_vblank_lead_lines`. HPD and interrupt enablement is represented in `rdev->irq` atomics and bit arrays, with last-read hardware status cached under `rdev->irq.stat_regs.evergreen`. IH state persists in `rdev->ih.rptr`, `ptr_mask`, `enabled`, and the writeback/ring buffer. Page flip state is coordinated through CRTC interrupt handlers and pflip atomics.

Power-management state is updated in `rdev->pm`: profile tables, current/requested power states, voltage/current VDDC/VDDCI, DPM thermal flags, and `vblank_sync`. UVD state is represented by `rdev->has_uvd`, the UVD ring size/object, UVD BOs managed by common UVD helpers, and UVD clock PLL registers. RLC state persists through VRAM buffer objects and GPU addresses for save/restore, clear-state, and CP tables; `sumo_rlc_fini()` explicitly unpins and unreferences those BOs.

Hardware state is mostly volatile MMIO state and firmware uploads. Golden registers, MC apertures, GART context registers, CP/RLC microcode, display watermarks, and PCIe ASPM/link settings must be reprogrammed after reset or resume. Firmware blobs are held through `rdev->me_fw`, `pfp_fw`, `rlc_fw`, and `mc_fw`, but the actual microcode in hardware is not persistent across reset.

### Dependencies

The file depends on the Linux PCI, firmware, slab, and DRM headers plus many Radeon-internal headers: ATOMBIOS, AVIVO/DCE register definitions, CIK/NI/SI/RV770 helpers, Evergreen register and bit definitions, Radeon core structs, ASIC callbacks, audio, and ucode helpers. It uses core Radeon services for register access macros, ATOM clock/voltage operations, BIOS posting, BO allocation/pinning/kmap, GART table management, fence and ring initialization, IB pool management, IRQ KMS/IH setup, UVD helpers, audio init/fini, power management, AGP, and PCI config reset.

External integration points include DRM/KMS CRTC, connector, encoder, vblank, framebuffer, and workqueue paths; Linux PCIe read request size and link-speed APIs; firmware loading through the Radeon microcode helpers; and kernel delay/synchronization primitives such as spinlocks, atomics, wait queues, `udelay()`, `mdelay()`, and memory barriers.

### Integration points

`evergreen.c` is selected by Radeon ASIC callback tables for Evergreen and adjacent families. It is called by the Radeon device initialization path, suspend/resume path, reset path, KMS page flip/vblank callbacks, HPD callbacks, power-management callbacks, ring/IB submission logic, and interrupt handler dispatch. It also deliberately calls into shared generation-specific code: R600/R700/RV770 helpers for scratch, VGA, DMA, CP stop/fini, GART init, ring init, and microcode; NI helpers for DCE5 MC firmware and Cayman IRQ/VM decode; SI/CIK helpers for RLC clear-state and CP table formats.

Display integration spans up to six CRTCs and HPD pins through `crtc_offsets`, HPD register macros, DIG/DP offset arrays, and KMS connector enumeration. UVD integration starts a separate UVD ring and handles source ID 124 interrupts. Audio integration enables AFMT watermark interrupts and schedules `audio_work`. Thermal DPM integration enables thermal interrupts and schedules the DPM thermal work item on threshold crossings. VM fault interrupts are decoded via Cayman VM helpers even though this file owns the IH vector dispatch.

### Risks

The highest risk is register sequencing. MC stop/resume, blackout, VGA lockout, display blanking, DP SST blanking, and CRTC update locks are tightly ordered; changing them can corrupt scanout, break resume, or hang the memory controller. Reset paths must preserve enough display/MC state to restore access after soft or PCI config reset. Many loops wait only for `rdev->usec_timeout`, so hardware that never reports idle or frame changes degrades into warnings and best-effort continuation.

Family conditionals are dense and easy to regress. Different paths exist for Evergreen discrete GPUs, DCE5/Northern Islands, Fusion IGPs, Cayman and later rings, Aruba/TN RLC, AGP, PCIe, and big-endian command buffers. Adding a chip or changing a family range can select the wrong golden registers, backend mapping, RLC microcode size, GART L1 TLB registers, UVD PLL sequence, thermal register, or interrupt programming path.

The interrupt handler is sensitive to ordering and concurrency. `evergreen_irq_ack()` must snapshot and clear display status before IH vector processing; `evergreen_irq_process()` uses an atomic lock and restarts if new vectors arrive. Incorrect pointer masking or overflow recovery can lose events or loop. Deferred work scheduling for HPD, DP, HDMI, and thermal events depends on the decoded `src_id/src_data` pairing matching hardware.

Memory object lifetime is another risk. RLC init creates, pins, maps, fills, unmaps, and unreserves multiple VRAM BOs with several failure exits. GART enable pins a VRAM table and marks `gart.ready`; disable must unpin. Startup failure unwinds many but not all subsystems depending on where it fails, so future changes should preserve reverse-order cleanup and avoid double-fini paths.

Several calculations assume valid mode and clock data. Display watermark math divides by available bandwidth, display clock, source width, and head count after guard checks; invalid modes or zero clocks can still be risky if upstream invariants change. Temperature conversion is family-specific and relies on encoded sensor status bits. PCIe ASPM/gen2 programming has policy guards but writes low-level PHY/link registers and can affect stability on marginal platforms.

### Test signals

Build coverage should include Radeon with Evergreen, Northern Islands, Fusion/IGP, UVD, AGP, PCIe, DPM, and big-endian packet conditionals where practical. Runtime smoke tests should cover probe, firmware load, startup, ring tests for GFX/DMA/UVD, GART enable/TLB flush, IB submission, page flips, vblank counters, HPD hotplug, HDMI audio work, suspend/resume, and both soft and hard reset paths.

Useful log signals include golden register programming succeeding silently, `PCIE GART ... enabled`, CP/DMA/UVD fence driver starts, no `ring test` failures, no `Wait for MC idle timedout` warnings, no IH overflow warnings, no VM fault messages under normal workloads, and no startup failure that disables acceleration. Display validation should exercise one to six CRTCs, paired line-buffer allocation, DP SST blanking during MC stop, pflip IRQs, vblank IRQs, DCE4 FMT dithering/truncation, and DPM watermark updates. Fault-injection tests should force missing firmware, GART pin failures, RLC BO allocation failures, UVD init failures, and interrupt disabled/IH disabled paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.h

### Purpose

`evergreen.h` is the private Radeon driver header that exposes Evergreen-family ASIC helper functions to the rest of the Radeon driver. It does not define hardware registers or structures itself; instead it forward-declares key structs and declares the cross-file API implemented mainly by `evergreen.c` and used by ASIC callback tables, reset paths, memory-controller setup, IRQ setup, power management, and RLC support.

### Important APIs, types, and functions

The header forward-declares `struct evergreen_mc_save`, `struct evergreen_power_info`, and `struct radeon_device`. Its declarations cover display hang/status helpers (`evergreen_is_display_hung()`, `evergreen_print_gpu_status_regs()`), memory-controller sequencing (`evergreen_mc_stop()`, `evergreen_mc_resume()`, `evergreen_mc_wait_for_idle()`, `evergreen_mc_program()`, `evergreen_mc_init()`), interrupt shutdown (`evergreen_irq_suspend()`), PCIe policy (`evergreen_fix_pci_max_read_req_size()`, `evergreen_pcie_gen2_enable()`, `evergreen_program_aspm()`), RLC lifecycle (`sumo_rlc_fini()`, `sumo_rlc_init()`, `evergreen_rlc_resume()`), reset/status (`evergreen_gpu_pci_config_reset()`, `evergreen_gpu_check_soft_reset()`), DRAM topology (`evergreen_get_number_of_dram_channels()`), and power-info access (`evergreen_get_pi()`).

### Control flow

The header participates in compile-time dependency control. Source files that need Evergreen routines can include this header without pulling in the full implementation or concrete private struct definitions. In runtime terms, callers use these declarations as lifecycle hooks: MC stop/resume bracket unsafe aperture updates and reset sequences, IRQ suspend disables IH/interrupt state during suspend or reset, RLC init/resume/fini wraps firmware-controlled low-power state handling, and PCIe helpers are invoked during startup.

### State and persistence behavior

No state is stored in this header. All declared functions operate on `struct radeon_device *` and mutate hardware registers or fields inside the Radeon device object. The forward declaration of `struct evergreen_mc_save` makes MC save/restore state opaque to users of this header; callers can pass the save object only if they include a definition from another internal header or source context that knows its layout.

### Dependencies

This header depends only on include guards and pre-existing kernel/Radeon type availability for `bool`, `u32`, and the forward-declared structs. It intentionally avoids including register definition headers, DRM headers, or the full `radeon.h`, keeping it lightweight for internal inclusion.

### Integration points

`evergreen.h` is included by Evergreen-related Radeon implementation files and by other generation files that share reset, RLC, PCIe, or MC helper code. The functions declared here are part of the Radeon-internal ASIC callback boundary rather than a public UAPI. The naming also shows that some routines are Sumo/Fusion-specific but still live in the Evergreen support family.

### Risks

The main risk is API drift. Because this header is the contract between Evergreen implementation and other Radeon modules, changing prototypes or removing declarations can break ASIC tables or cross-generation helpers. The opaque forward declarations reduce compile-time coupling, but they also require the actual struct definitions and function implementations to remain consistent elsewhere. Declaring Sumo-specific functions in an Evergreen header can obscure ownership and make future refactors more error-prone.

### Test signals

Build tests with Radeon enabled are the primary validation signal for this header. Runtime coverage comes indirectly from any path that calls the declared functions: init/startup, suspend/resume, reset, MC reprogramming, IRQ suspend, RLC resume/fini, PCIe gen2/ASPM setup, and display hang detection. Header-specific failures typically appear as compile errors, missing symbol/link errors, or type mismatches after refactors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_blit_shaders.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_blit_shaders.h

### Purpose

`evergreen_blit_shaders.h` provides a statically generated Evergreen 3D clear/default state packet table used by the DRM driver when it needs the 3D engine for blit-related operations without embedding the full userspace 3D driver state generator. The file is intentionally data-heavy: it stores command-stream words that configure depth, stencil, rasterization, viewport/scissor, color buffer masks, shader input/output, VGT, SQ, and related state to a known baseline.

### Important APIs, types, and functions

The main exported data is `static const u32 evergreen_default_state[]`, a sequence of PM4 packet words and register payloads. The companion `static const u32 evergreen_default_size = ARRAY_SIZE(evergreen_default_state);` gives callers the number of dwords to emit. There are no functions or structs in this header. The packet comments name many target registers, including `SQ_LDS_ALLOC_PS`, `DB_Z_INFO`, `DB_STENCIL_INFO`, `DB_DEPTH_CONTROL`, `DB_RENDER_CONTROL`, `PA_SC_WINDOW_OFFSET`, `PA_SC_CLIPRECT_*`, `PA_SC_VPORT_SCISSOR_*`, `PA_SC_VPORT_ZMIN/ZMAX`, `PA_SC_MODE_CNTL_*`, `PA_SU_VTX_CNTL`, `PA_CL_*`, `CB_COLOR_CONTROL`, `DB_SHADER_CONTROL`, `VGT_*`, `CB_BLEND0_CONTROL`, `SPI_*`, and `VGT_VERTEX_REUSE_BLOCK_CNTL`.

### Control flow

The table is consumed in `evergreen_cp_start()` in `evergreen.c`. That function locks the GFX ring, emits `PACKET3_PREAMBLE_CNTL` with `PACKET3_PREAMBLE_BEGIN_CLEAR_STATE`, writes every dword from `evergreen_default_state[]`, emits `PACKET3_PREAMBLE_END_CLEAR_STATE`, then submits a `PACKET3_CLEAR_STATE` packet and a few additional setup packets. The header therefore contributes to CP startup rather than being executed directly.

### State and persistence behavior

The header contains immutable compile-time data. At runtime, the state becomes persistent only after the command processor consumes the packet stream and records the clear/default context state in GPU hardware. That hardware state is volatile across reset, CP restart, and power transitions, so `evergreen_cp_start()` re-emits it during CP resume/startup. The array itself has internal linkage because it is `static const` in a header, so each including translation unit would get a private copy; in practice this file is intended for inclusion by the Evergreen implementation.

### Dependencies

The data requires `u32` and `ARRAY_SIZE` to be defined by prior includes. It relies on PM4 packet encodings and Evergreen register layouts but avoids symbolic register macros, using precomputed packet/register dwords instead. Its functional dependency is the GFX ring emitter in `evergreen.c`.

### Integration points

This header is included by `evergreen.c` and integrated into GFX command processor startup. It is part of the Radeon DRM kernel driver’s minimal internal 3D state setup path for Evergreen cards. Userspace does not call it directly, and no public ABI is exposed. The table bridges kernel blit/ring bring-up requirements with register state that would normally be generated by a full 3D driver.

### Risks

The primary risk is data correctness. The packet words are opaque constants; a wrong value, wrong packet length, or register mismatch can break CP clear-state setup, corrupt later blit state, or hang the GPU. The `evergreen_default_size` value must exactly match the array length because `evergreen_cp_start()` uses it for ring allocation and emission. Since the data is register-generation-specific, reusing it for an incompatible ASIC or after register definition changes would be unsafe. The static-header pattern can also duplicate the array if included from multiple C files, though that is a size issue rather than a behavioral issue.

### Test signals

Validation comes from successful Evergreen CP resume/startup and GFX ring tests. Runtime signals include `evergreen_cp_start()` completing, `radeon_ring_test()` succeeding, blit or clear operations not hanging, no CP/GRBM busy reset mask after startup, and no GPU faults attributable to invalid command stream setup. Build coverage should ensure `ARRAY_SIZE` and `u32` are in scope wherever the header is included.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/radeon/evergreen_blit_shaders.h -->
