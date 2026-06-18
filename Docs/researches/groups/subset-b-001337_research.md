# Group Research: subset-b-001337

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c

## Purpose

`gfx_v8_0.c` is the AMDGPU Graphics Core Next 1.2 / GFX8 hardware implementation for VI-family GPUs such as Iceland/Topaz, Tonga, Fiji, Carrizo, Stoney, Polaris 10/11/12, and VegaM. It plugs a GFX IP block into the AMDGPU IP lifecycle and owns firmware loading, golden-register programming, graphics and compute ring setup, RLC save/restore and power-gating setup, MEC/KIQ/KCQ queue management, VMID/GDS/RB/CU configuration, interrupt handling, soft reset, clock and power gating, ring packet emission, and a Carrizo-specific EDC/GPR workaround.

The file is highly hardware-facing. Most persistent state is stored in `struct amdgpu_device` substructures (`adev->gfx`, `adev->gds`, `adev->firmware`, `adev->virt`, ring objects, MQD BOs, RLC BOs), while this file provides the generation-specific register sequences and callback tables that the common AMDGPU core calls.

## Important APIs, Data, and Entry Points

- IP block exports: `gfx_v8_0_ip_block` and `gfx_v8_1_ip_block` register major/minor GFX versions 8.0 and 8.1 with the same `gfx_v8_0_ip_funcs` lifecycle table.
- Firmware declarations and loading: `MODULE_FIRMWARE()` lists CE/PFP/ME/MEC/MEC2/RLC firmware variants for Carrizo, Stoney, Tonga, Topaz, Fiji, Polaris, and VegaM. `gfx_v8_0_init_microcode()` requests firmware, extracts feature/version fields, populates `adev->firmware.ucode[]`, accounts firmware BO size, and enables SR-IOV chained IB metadata if CE/PFP feature versions are high enough.
- Golden register data: ASIC-specific arrays such as `golden_settings_tonga_a11`, `fiji_mgcg_cgcg_init`, `cz_golden_common_all`, and `stoney_mgcg_cgcg_init` are applied by `gfx_v8_0_init_golden_registers()`.
- RLC support: `iceland_rlc_funcs` wires `gfx_v8_0_rlc_init()`, `gfx_v8_0_rlc_resume()`, `gfx_v8_0_rlc_stop()`, `gfx_v8_0_rlc_reset()`, `gfx_v8_0_rlc_start()`, clear-state buffer helpers, safe-mode helpers, and SPM VMID update.
- MEC/KIQ/KCQ support: `gfx_v8_0_mec_init()`, `gfx_v8_0_mqd_init()`, exported `gfx_v8_0_mqd_commit()`, `gfx_v8_0_kiq_init_queue()`, `gfx_v8_0_kcq_init_queue()`, `gfx_v8_0_kiq_kcq_enable()`, and `gfx_v8_0_kcq_disable()` allocate and program hardware queues.
- Ring functions: `gfx_v8_0_ring_funcs_gfx`, `gfx_v8_0_ring_funcs_compute`, and `gfx_v8_0_ring_funcs_kiq` implement read/write pointer handling, IB emission, fences, VM flushes, GDS switches, HDP flushes, packet padding, soft recovery, register read/write packets, memory sync, and wave limiting.
- IRQ sources: EOP, privileged register fault, privileged instruction fault, CP ECC/EDC error, and SQ interrupt sources are wired by `gfx_v8_0_set_irq_funcs()` and registered in `gfx_v8_0_sw_init()` / enabled in `gfx_v8_0_late_init()`.
- Topology/config helpers: `gfx_v8_0_gpu_early_init()`, `gfx_v8_0_tiling_mode_table_init()`, `gfx_v8_0_setup_rb()`, `gfx_v8_0_get_cu_info()`, `gfx_v8_0_constants_init()`, and `gfx_v8_0_set_gds_init()` derive or program shader, RB, tile, GDS, VMID, and memory-layout state.
- Reset and gating: `gfx_v8_0_check_soft_reset()`, `pre_soft_reset`, `soft_reset`, `post_soft_reset`, `gfx_v8_0_set_clockgating_state()`, `gfx_v8_0_get_clockgating_state()`, and `gfx_v8_0_set_powergating_state()` implement GFX8 reset and PM policy.

## Control Flow

Early initialization starts in `gfx_v8_0_early_init()`. It fixes the XCC mask to one, sets one graphics ring, derives the compute ring count from `amdgpu_gfx_get_num_kcq()`, assigns `adev->gfx.funcs`, and attaches ring, IRQ, GDS, and RLC function tables. `gfx_v8_0_sw_init()` then determines MEC count by ASIC, sets four pipes and eight queues per MEC, registers IRQ IDs, initializes SQ work, loads microcode, initializes RLC and MEC BOs, initializes the graphics ring, walks enabled MEC queues to initialize compute rings horizontally across pipes, initializes KIQ, allocates MQD storage, sets CE RAM size, reads early GPU topology, and records supported reset masks.

Hardware initialization is `gfx_v8_0_hw_init()`: program ASIC golden registers, initialize constants and topology-dependent registers, resume RLC, then resume CP. `gfx_v8_0_constants_init()` programs address config into GB/HDP/DMIF, writes tile and macro-tile mode tables, detects RB and CU masks, initializes VMID shader-memory apertures, disables GDS/GWS/OA for nonzero VMIDs, broadcasts raster/FIFO/SPI defaults, and caches RB config for userspace. `gfx_v8_0_rlc_resume()` stops/resets/starts RLC on bare metal, initializes power-gating support when requested, and skips most work for SR-IOV VFs other than clear-state setup.

CP resume proceeds through KIQ, GFX, KCQ, and ring tests. `gfx_v8_0_kiq_resume()` initializes the KIQ MQD and commits it through selected SRBM registers. `gfx_v8_0_cp_gfx_resume()` programs CP RB0 control, ring base, read/write pointer backing, optional doorbells, and emits the clear-state preamble plus CE partition setup. `gfx_v8_0_kcq_resume()` enables MEC, initializes all compute MQDs, programs MEC doorbell range, and emits KIQ packets to set resources and map each compute queue. Finally `gfx_v8_0_cp_test_all_rings()` ring-tests GFX and KIQ fatally and attempts compute ring tests.

Submit-time control flow is through ring callbacks. Graphics IBs use `PACKET3_INDIRECT_BUFFER` or `INDIRECT_BUFFER_CONST`; SR-IOV preempt IBs may emit CE/DE metadata into CSA memory. Compute IBs optionally reset `GDS_COMPUTE_MAX_WAVE_ID` before emitting the IB packet. Fences use graphics `EVENT_WRITE_EOP`, compute `RELEASE_MEM`, and KIQ `WRITE_DATA`. VM flush calls the common GMC TLB flush helper and waits on `VM_INVALIDATE_REQUEST`; graphics then syncs PFP to ME. HDP flush maps ring type and ME/pipe to `GPU_HDP_FLUSH_*` masks.

Shutdown and suspend use `gfx_v8_0_hw_fini()`. It drops IRQ enables, disables KCQ through KIQ unmap packets, skips bare-metal halt for SR-IOV VFs, enters RLC safe mode, halts CP if idle, stops RLC if idle, and exits safe mode. Software fini tears down rings, MQD/KIQ/MEC/RLC BOs, clear-state/CP table BOs, and firmware.

Soft reset starts with status sampling. `gfx_v8_0_check_soft_reset()` inspects GRBM/SRBM status registers and stores GRBM/SRBM reset masks in `adev->gfx`. `pre_soft_reset()` stops RLC, disables GFX parsing as needed, deactivates compute HQDs, and halts MEC. `soft_reset()` asserts `GMCON_DEBUG` stall/clear, toggles GRBM and SRBM soft reset bits, then clears stall/clear. `post_soft_reset()` re-deactivates HQDs, resumes KIQ/KCQ/GFX CP paths as indicated by the masks, tests rings, and restarts RLC.

## State and Persistence Behavior

Firmware state is persisted in `adev->gfx.{pfp,me,ce,rlc,mec,mec2}_fw`, feature/version fields, RLC save/restore offsets and register lists, `adev->firmware.ucode[]`, and cumulative `adev->firmware.fw_size`. Polaris firmware has optional `_2.bin` variants with fallback to required base images. MEC2 firmware is absent on Stoney and Topaz and optional in practice on other ASICs.

Queue state is split across ring objects, MQD allocations, and hardware registers. Ring objects retain `me`, `pipe`, `queue`, doorbell index, EOP GPU address, ring/wptr/rptr BO addresses, scheduler readiness, and function table. `gfx_v8_0_mqd_init()` builds a `struct vi_mqd` snapshot from ring and register defaults, including HQD base, EOP ring, doorbell control, read/write pointer reports, VMID, persistent state, IB control, context-save defaults, static priority, and active bit for KIQ. KIQ and KCQ paths keep MQD backups for reset/suspend restore.

RLC state includes clear-state BO pointers, CP jump-table BOs for Carrizo/Stoney, save/restore register list memory copied out of RLC firmware, SPM VMID, RLC safe-mode state, and power-gating programming. `gfx_v8_0_init_save_restore_list()` rewrites indirect-register list indices, uploads restore data to RLC SRAM/GPM scratch registers, and programs unique index control registers.

Topology state is cached under `adev->gfx.config` and `adev->gfx.cu_info`: ASIC maximums, memory row size, `gb_addr_config`, tile/macrotile arrays, backend enable mask, number of RBs, per-SE/SH RB register snapshots, CU bitmaps, always-on CU masks, wavefront and LDS properties. These values are consumed by userspace info paths, clear-state generation, RLC power-gating, and command submission.

Power and clock state is primarily hardware register state plus `adev->cg_flags` and `adev->pg_flags`. The file does not store a separate desired gating state; it applies requested gate/ungate transitions by programming RLC/CGTS/CP memory sleep registers or by sending SMU PowerPlay messages for Tonga/Polaris-style clock gating. SR-IOV VFs generally return without touching PM registers.

## Dependencies and Integration Points

The file depends on AMDGPU core services for IP lifecycle, ring allocation, fences, IB scheduling, writeback, buffer objects, IRQ registration, GPU reset masks, RLC helper allocation, MQD storage, KIQ setup, KFD queue ownership, CSA addresses, SR-IOV predicates, doorbells, GMC VM/TLB flushing, DPM/SMU clock and power gating, ATOM BIOS topology/I2C quirks, and register access macros. Register definitions come from GFX8, GMC 8.2, OSS 3.0, BIF 5.0, DCE 10, SMU 7.1.3, and VI IV source headers.

The external header `gfx_v8_0.h` exposes the two IP block descriptors and `gfx_v8_0_mqd_commit()`. Other important type dependencies include `struct vi_mqd`, `struct vi_mqd_allocation`, `struct amdgpu_ring`, `struct amdgpu_ip_block`, `struct amdgpu_irq_src`, firmware headers from `amdgpu_ucode.h`, and metadata layouts from `vi_structs.h`.

KFD/HSA integration appears through compute queue ownership, first KFD VMID handling, compute VMID aperture setup, and GDS/GWS/OA access initialization. SR-IOV integration appears through chained IB metadata, KIQ/KCQ reset handling, firmware storage sizing, protected register access variants for SPM VMID, and VF-specific skips in RLC/hw-fini/gating. Power management integrates with RLC safe mode and SMU/DPM messages.

## Risks and Edge Cases

- Firmware feature and size accounting is fragile. Missing `_2.bin` fallback, malformed firmware headers, RLC register-list sizes, or incorrect `fw_size` accounting can break boot or SR-IOV firmware staging.
- `gfx_v8_0_cp_test_all_rings()` ignores compute ring test return values, so compute queue failures after resume/reset may be logged by helpers but not propagated from the aggregate test path.
- MQD commit depends on register layout assumptions from `mmCP_MQD_BASE_ADDR` through HQD ranges. A register definition change or ASIC exception can program wrong HQD fields. Tonga has an explicit EOP RPTR/WPTR erratum that must remain preserved.
- Queue masking in `gfx_v8_0_kiq_kcq_enable()` assumes all enabled KCQs fit in a 64-bit mask and warns otherwise; future queue-count changes would need wider resource encoding.
- Reset paths rely on status bits and idle polling. If CP/RLC remain busy, hardware fini skips halting them; if status bits are stale, soft reset may reset too little or too much. Post-reset also ignores return values from GFX/KCQ resume helpers in some paths.
- PM and clock gating writes require RLC safe mode and correct ASIC branching. Applying Carrizo/Stoney register sequences to Polaris-style SMU-managed chips, or touching PM registers from SR-IOV VF mode, would be unsafe.
- Tiling mode tables are large duplicated hardware constants. Incorrect entries affect memory layout compatibility with display, render, depth, PRT, and userspace tiling assumptions.
- The Carrizo EDC/GPR workaround emits embedded compute shaders and waits synchronously. It is skipped if compute ring is not ready; if the ring later becomes active without the workaround, EDC behavior may differ.
- Several `BUG()`/`BUG_ON()` paths remain in firmware/chip/list parsing code. Bad ASIC type or unexpected RLC list format can panic rather than returning an error.
- Interrupt decoding matches EOP events to rings by ME/pipe/queue and only programs compute EOP interrupts for ME1 in `gfx_v8_0_set_compute_eop_interrupt_state()`, explicitly leaving other pipes/engines to KFD.

## Test and Validation Signals

- Probe and firmware tests should cover every supported ASIC family and Polaris optional firmware fallback: Topaz, Tonga, Fiji, Carrizo, Stoney, Polaris 10/11/12, and VegaM.
- Ring tests should validate GFX, KIQ, and every enabled compute ring after cold boot, suspend/resume, soft reset, and SR-IOV VF reset. A targeted test should assert compute ring test failures are not silently ignored by aggregate paths.
- Queue-management tests should exercise MQD init/commit, KIQ map/unmap queues, high-priority compute queue priority fields, doorbell ranges, KIQ/KCQ MQD backup restore, and reset while in suspend.
- VM/GDS tests should cover VMID aperture setup, GDS/GWS/OA switch packets, GDS max wave-id reset on compute IBs, VM flush packets, HDP flush masks for GFX, KIQ, MEC1, and MEC2.
- PM tests should verify clock-gating and power-gating transitions per ASIC family, including RLC safe-mode entry/exit, MGCG/MGLS/CGCG/CGLS state reporting, SMU message dispatch for Tonga/Polaris, and no-op behavior under SR-IOV VF.
- Reset tests should force GRBM/SRBM busy bits, RLC busy, CP/CPC/CPF/CPG busy, HQD deactivation timeout, and post-reset queue restoration.
- IRQ tests should inject EOP, privileged register fault, privileged instruction fault, CP ECC/EDC, and SQ interrupt messages, including the workqueue path that reads `SQ_EDC_INFO`.
- Topology tests should compare exported CU/RB/tile configuration against expected ASIC values and harvested CU/RB masks, especially APU row-size handling and Polaris ATOM BIOS derived topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.h

## Purpose

`gfx_v8_0.h` is the public internal header for the AMDGPU GFX8 implementation. It exposes the GFX8 IP block descriptors and the MQD commit helper implemented in `gfx_v8_0.c` so other AMDGPU compilation units can register or program GFX8 hardware without including the large implementation file.

The header is intentionally small: it is a declaration boundary, not a policy or state owner.

## Important APIs, Types, and Symbols

- Include guard: `__GFX_V8_0_H__` prevents duplicate declarations.
- `extern const struct amdgpu_ip_block_version gfx_v8_0_ip_block;` declares the GFX IP block descriptor for GFX 8.0 hardware.
- `extern const struct amdgpu_ip_block_version gfx_v8_1_ip_block;` declares the GFX IP block descriptor for GFX 8.1 hardware, which currently uses the same implementation callback table as 8.0.
- Forward declarations: `struct amdgpu_device;` and `struct vi_mqd;` avoid pulling in full AMDGPU and VI MQD structure definitions for users that only need the function prototype.
- `int gfx_v8_0_mqd_commit(struct amdgpu_device *adev, struct vi_mqd *mqd);` exposes the helper that writes a prepared VI MQD/HQD register image into selected hardware queue registers.

## Control Flow

ASIC/IP selection code includes this header to reference `gfx_v8_0_ip_block` or `gfx_v8_1_ip_block` when building the device's IP block list. Once the AMDGPU core walks the selected IP block, the callback table in `gfx_v8_0.c` drives early init, software init, hardware init, suspend/resume, reset, and gating.

Queue setup code can call `gfx_v8_0_mqd_commit()` after selecting a MEC/pipe/queue with SRBM routing. The function expects the caller to provide an initialized `struct vi_mqd` and the correct hardware selection/serialization context; the header itself does not enforce those preconditions.

## State and Persistence Behavior

The header stores no state. The exported IP block descriptors are immutable `const` objects defined in `gfx_v8_0.c`. MQD contents are supplied by the caller and represent persistent queue state stored elsewhere, commonly in ring MQD BOs and backup buffers under `adev->gfx`.

## Dependencies and Integration Points

This header depends on users having declarations for `struct amdgpu_ip_block_version`, typically through AMDGPU internal headers included before or alongside it. It integrates with VI ASIC setup code, the AMDGPU IP block framework, and queue/MQD management paths that need direct access to the GFX8 MQD commit primitive.

The `vi_mqd` forward declaration ties the API to VI-generation MQD layout, so it is not a generation-neutral queue commit interface.

## Risks and Edge Cases

- `gfx_v8_0_mqd_commit()` is low-level and hardware-stateful. Calling it without selecting the intended ME/pipe/queue or without holding the relevant SRBM serialization can write an MQD into the wrong HQD.
- The header does not include the full type definitions. Callers must include the appropriate AMDGPU/VI headers when they need to allocate or inspect `struct vi_mqd`.
- The two exported IP block descriptors share implementation callbacks in the `.c` file; future GFX8.1 divergence would require either additional callbacks or careful branching in the shared implementation.

## Test and Validation Signals

- Build coverage should include all ASIC setup files that reference `gfx_v8_0_ip_block`, `gfx_v8_1_ip_block`, or `gfx_v8_0_mqd_commit()`.
- Queue tests should verify callers select the correct MEC/pipe/queue before invoking `gfx_v8_0_mqd_commit()`.
- IP discovery/probe tests should confirm GFX 8.0 and 8.1 devices register the intended descriptor and execute the `gfx_v8_0.c` lifecycle callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v8_0.h -->
