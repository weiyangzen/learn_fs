# subset-b-001341 research

This grouped report covers the assigned AMDGPU GFX 9.4.3 compute block, its cleaner shader artifact, and several GFXHUB generations in the Ceph-client source mirror. Each section is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c

Purpose: implements the AMDGPU GFX IP block for GC/GFX 9.4.3-family parts, including MI300-class multi-XCC compute bring-up, RLC and MEC firmware management, KIQ/KCQ queue programming, ring packet emission, interrupt handling, clock gating, RAS error collection, cleaner-shader dispatch support, and XCP partition suspend/resume hooks.

Important APIs/types/functions: exports `gfx_v9_4_3_ip_block`, `gfx_v9_4_3_xcp_funcs`, `gfx_v9_4_3_ras`, and `gfx_v9_4_3_ras_ops`. The `amd_ip_funcs` table wires `early_init`, `sw_init`, `hw_init`, `hw_fini`, suspend/resume, idle/reset, clock-gating, and IP dump callbacks into the AMDGPU IP scheduler. The ring function tables are `gfx_v9_4_3_ring_funcs_compute` and `gfx_v9_4_3_ring_funcs_kiq`; the KIQ packet table is `gfx_v9_4_3_kiq_pm4_funcs`. RLC behavior is exposed through `gfx_v9_4_3_rlc_funcs`. Major helpers include microcode loading (`gfx_v9_4_3_init_microcode`, `gfx_v9_4_3_mec_init`, `gfx_v9_4_3_xcc_rlc_resume`, `gfx_v9_4_3_xcc_cp_compute_load_microcode`), queue/MQD setup (`gfx_v9_4_3_compute_ring_init`, `gfx_v9_4_3_xcc_mqd_init`, `gfx_v9_4_3_xcc_kiq_init_queue`, `gfx_v9_4_3_xcc_kcq_resume`), ring tests and packet emitters, fault IRQ handlers, and RAS walkers.

Control flow: `early_init` chooses the number of compute queues, installs PM4/ring/IRQ/GDS/RLC callbacks, initializes RLCG register access metadata, and requests RLC/MEC firmware. `sw_init` enables cleaner-shader metadata for GC 9.4.3/9.4.4 when MEC firmware is new enough, registers EOP and command-stream fault IRQ sources, initializes RLC and MEC backing BOs, creates compute rings and one KIQ per XCC, allocates MQDs, determines reset capabilities, initializes GFX config/RAS/sysfs, and allocates IP dump buffers. `hw_init` uploads the cleaner shader buffer, programs golden registers for PF mode, initializes constants and VMIDs, resumes RLC, then resumes CP/MEC queues. CP resume handles SR-IOV partition discovery or host-side XCP mode switching, then per XCC loads MEC firmware if PSP did not load it, initializes KIQ and KCQs, maps queues, and ring-tests all compute rings. `hw_fini` drops IRQ references, disables KCQs/KIQ, disables polling in VF teardown, deinitializes queue registers when not resetting/suspending, and halts MECs.

State and persistence behavior: all state is kernel-resident and tied to `struct amdgpu_device`. Persistent runtime objects include firmware handles, RLC and MEC BOs, HPD/EOP memory, KIQ/KCQ ring BOs, MQD allocations/backups, writeback slots, cleaner-shader GPU memory, IP dump arrays, RAS counters read from hardware, and XCP partition metadata. Hardware state is written per XCC via `GET_INST(GC, xcc_id)` and guarded by `srbm_mutex` or `grbm_idx_mutex` where register selection is global. Firmware load type changes behavior: PSP-loaded firmware skips direct RLC/MEC upload, while legacy load writes microcode through registers or GTT buffers. Suspend/reset paths preserve MQD backups and may restore queue state from those backups.

Dependencies and integration points: depends on AMDGPU core structures, SOC15 register access macros, GC 9.4.3 register headers, KIQ/KCQ scheduling helpers, RLC helpers, firmware loading, PSP/XCP partition management, KFD compute VMID expectations, GMC TLB flushing, IRQ source registration, DRM scheduler faulting, RAS/ACA helpers, and the generated `gfx_v9_4_3_cleaner_shader_hex` array. It interacts with doorbell layout (`doorbell_index`), writeback memory, `amdgpu_gfx_compute_queue_acquire()`, `amdgpu_xcp_*` partition APIs, `amdgpu_gfx_enable_kcq()`, `amdgpu_gmc_emit_flush_gpu_tlb()`, and sysfs/RAS registration.

Risks and edge cases: many paths assume a correct `xcc_mask`, queue topology, and firmware feature version; reset and cleaner-shader support are gated by firmware version and SR-IOV state. `gfx_v9_4_3_xcc_init_sq()` writes `regSQ_CONFIG1` with `xcc_id` instead of `GET_INST(GC, xcc_id)`, a detail worth checking against the register-access macro expectations. `gfx_v9_4_3_get_clockgating_state()` sets `*flags = 0` for SR-IOV but does not return immediately, so later KIQ reads may still update flags. Queue reset escalates from queue reset to pipe reset and can return before `amdgpu_ring_reset_helper_end()` on some failures, so caller cleanup assumptions matter. RAS CE/UE tables must stay in matching order for shared loop indices. The interrupt handler maps IH node to XCC with `node_id / 2`; topology changes can misroute fence processing. Several functions use `BUG_ON()` for alignment or unsupported no-doorbell paths, so malformed ring state is fatal.

Test signals: successful boot should request matching `gc_9_4_3`, `gc_9_4_4`, or `gc_9_5_0` MEC/RLC firmware, initialize one KIQ and the enabled compute rings per XCC, and pass `amdgpu_ring_test_helper()` plus the IB writeback test. Runtime signals include correct fence progress from CP EOP IRQs, no command-stream fault IRQs under valid workloads, successful TLB flush and HDP flush packets, valid IP dumps for core and queue registers, cleaner-shader packet emission when enabled, per-queue and per-pipe reset recovery on supported MEC firmware, correct XCP partition suspend/resume, and RAS CE/UE query/reset/watchdog behavior across all XCCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.h

Purpose: provides the public declarations needed by the AMDGPU IP discovery and XCP partition layers for the GFX 9.4.3 implementation.

Important APIs/types/functions: declares `extern const struct amdgpu_ip_block_version gfx_v9_4_3_ip_block` and `extern struct amdgpu_xcp_ip_funcs gfx_v9_4_3_xcp_funcs`. These symbols are defined in `gfx_v9_4_3.c`.

Control flow: no runtime control flow. Inclusion allows device-specific IP tables to reference the GFX block version and optional per-partition suspend/resume hooks.

State and persistence behavior: no state is defined here. The declarations refer to global constant/function-table objects whose lifetime is the driver/module lifetime.

Dependencies and integration points: depends on prior visibility of `struct amdgpu_ip_block_version` and `struct amdgpu_xcp_ip_funcs` from AMDGPU headers. Integrated by ASIC discovery or IP block registration code that selects the GC 9.4.3 implementation.

Risks and test signals: the header intentionally exposes only two symbols; adding private implementation details here would widen coupling. Test signals are successful compilation of source files that include this header and correct link resolution to `gfx_v9_4_3.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.asm -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.asm

Purpose: documents and sources the MI300/GC 9.4.3 cleaner shader used to scrub LDS, VGPRs, SGPRs, flat scratch, VCC, and TTMP registers before or between isolated compute workloads. The compiled form is embedded in `gfx_v9_4_3_cleaner_shader.h` and selected by `gfx_v9_4_3.c` when supported by MEC firmware.

Important APIs/types/functions: this is GPU assembly, not C API. It declares `shader main`, `asic(MI300)`, `type(CS)`, and `wave_size(64)`. The comments describe two launch modes: one wave-group mode clearing VGPRs, LDS, and lower SGPRs, and another mode clearing remaining SGPRs after CP releases halted waves.

Control flow: the shader checks `s0` for a mode bit. In the VGPR/LDS path it starts with `S_BARRIER`, uses indexed VGPR writes to clear 128 VGPRs per wave, lets the first wave clear the 64 KB LDS block with `ds_write2_b64`, then loops through relative SGPR writes to clear allocated SGPRs and scalar special registers before `s_endpgm`. In the SGPR-only path it branches to `label_0023`, executes `s_sethalt 1` so CP can wait for all waves to launch, then clears SGPRs and exits. The loop counters are hard-coded for the expected physical register allocation pattern.

State and persistence behavior: the shader mutates only wave-local register files and LDS of the launched workgroup. It has no persistent software state. Its effect is deliberately destructive to shader-visible state, so it must run only when the queue isolation protocol intends to scrub stale execution context.

Dependencies and integration points: depends on MI300 instruction encoding, wave64 execution, CP setup of `COMPUTE_USER_DATA_3`/SGPR mode state, SPI resource reservation for the second kernel, and the AMDGPU cleaner-shader upload/dispatch path. The C ring layer emits `PACKET3_RUN_CLEANER_SHADER` after programming the shader address through KIQ `SET_RESOURCES`.

Risks and test signals: the shader is tightly coupled to CU/SIMD register allocation assumptions, 64 KB LDS, wave64, and MEC/CP launch sequencing. The comments contain minor typos but also critical sequencing notes: omitting the initial barrier in the first path or the halt/unhalt protocol in the second path can leave physical SGPRs uncleared. Test signals require hardware/firmware validation: successful compilation to the embedded hex, no shader hang, expected scrub coverage for LDS/VGPR/SGPR classes, and no launch on unsupported ASIC or firmware combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.asm -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.h

Purpose: embeds the precompiled GC 9.4.3 cleaner shader as a static `u32` machine-code array for inclusion by `gfx_v9_4_3.c`.

Important APIs/types/functions: defines `static const u32 gfx_9_4_3_cleaner_shader_hex[]`. There are no functions or include guards; the file is intended to be included by a single C translation unit needing the static array.

Control flow: no host-side control flow. The array content corresponds to the assembly in `gfx_v9_4_3_cleaner_shader.asm`; runtime control occurs on the GPU when the ring emits `PACKET3_RUN_CLEANER_SHADER`.

State and persistence behavior: the array is read-only driver text/data. During `gfx_v9_4_3_sw_init`, the driver stores a pointer and size into `adev->gfx.cleaner_shader_ptr` and `adev->gfx.cleaner_shader_size`; `hw_init` uploads it into GPU-visible cleaner-shader memory if the feature is enabled.

Dependencies and integration points: depends on `u32` being defined by including AMDGPU/Linux headers before this file. Integrated directly by `gfx_v9_4_3.c`, which gates use to GC 9.4.3/9.4.4 and sufficiently new MEC firmware.

Risks and test signals: because the blob is static machine code, source/hex drift is the main maintainability risk. There is no local metadata for ASIC, wave size, or checksum, so validation relies on external build review and hardware tests. Test signals are successful compilation, correct `sizeof()` used for upload, valid cleaner-shader GPU address passed through KIQ resources, and successful register/LDS scrubbing without queue hangs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfx_v9_4_3_cleaner_shader.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c

Purpose: implements the GFXHUB VM/GART programming callbacks for GC 11.5.0, covering framebuffer location reads, page-table base programming, GART/system aperture setup, TLB/L2 cache setup, VMID context initialization, invalidation engine ranges, default fault handling, and VM fault status decoding.

Important APIs/types/functions: exports `gfxhub_v11_5_0_funcs` with `.get_fb_location`, `.get_mc_fb_offset`, `.setup_vm_pt_regs`, `.gart_enable`, `.gart_disable`, `.set_fault_enable_default`, and `.init`. The local `gfxhub_v11_5_0_vmhub_funcs` supplies fault-status printing and invalidate-request construction to generic VM hub code. Key helpers are `gfxhub_v11_5_0_init_gart_aperture_regs()`, `gfxhub_v11_5_0_init_system_aperture_regs()`, `gfxhub_v11_5_0_init_tlb_regs()`, `gfxhub_v11_5_0_init_cache_regs()`, `gfxhub_v11_5_0_setup_vmid_config()`, and `gfxhub_v11_5_0_program_invalidation()`.

Control flow: `init` fills `adev->vmhub[AMDGPU_GFXHUB(0)]` with register offsets, context/engine stride distances, the VM fault interrupt mask, and the vmhub callback table. `gart_enable` programs VF framebuffer base/top copies when in SR-IOV VF mode, then initializes context0 page table registers from the GART BO, system aperture and default/fault pages, L1 TLB, L2 cache for PF mode, context0 system domain, identity aperture disable for PF mode, VMID1-15 context controls and address bounds, and all 18 invalidation-engine address ranges. `gart_disable` disables all 16 contexts and turns off L1/L2 controls. Fault default control first disables CP halt-on-UTCL1 error, then updates L2 protection-fault default behavior when not a VF.

State and persistence behavior: the file persists VM hub register addresses and masks in `adev->vmhub[AMDGPU_GFXHUB(0)]`; hardware state persists in GCVM and GCMC registers until reset or `gart_disable`. It uses `adev->gmc`, `adev->gart`, `adev->vm_manager`, `adev->dummy_page_addr`, and `adev->mem_scratch` to derive page table ranges and fallback addresses. No heap memory is allocated here.

Dependencies and integration points: depends on GC 11.5.0 register headers, SOC15 register macros, AMDGPU GMC/GART state, SR-IOV helpers, and generic VM hub invalidation/fault code. It integrates with higher-level GMC init that calls the selected `amdgpu_gfxhub_funcs` for the ASIC.

Risks and test signals: the VMID loop configures VMIDs 1 through 15 by iterating `i <= 14` from context1, so hub distance values must be correct. Cache and identity-aperture registers are skipped in VF mode and assumed to be handled by the PF. Fault printing decodes only the low status register fields and depends on a static client-id table. Test signals include successful GART mapping through VMID0, valid GPUVM mappings for VMIDs 1-15, TLB invalidation acknowledgements from all engines, correct dummy-page behavior when default faulting is enabled, crash/fault behavior when disabled, and meaningful L2 fault logs with client IDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.h

Purpose: declares the GC 11.5.0 GFXHUB function table for AMDGPU ASIC setup code.

Important APIs/types/functions: declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v11_5_0_funcs`, defined by `gfxhub_v11_5_0.c`.

Control flow: no runtime control flow. Including code selects this table when binding a GC 11.5.0 GFXHUB implementation.

State and persistence behavior: no local state. The exported function table has static driver lifetime.

Dependencies and integration points: depends on `struct amdgpu_gfxhub_funcs` being available from AMDGPU headers. Integrates with GMC/GFXHUB selection code.

Risks and test signals: narrow header surface minimizes coupling. Test signal is build/link success for ASIC code referencing `gfxhub_v11_5_0_funcs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v11_5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c

Purpose: provides the GC 12.0.0 GFXHUB/GART implementation. It is structurally close to v11.5.0 but uses GC 12 register names, updated client IDs, a different system default-page physical calculation, and `GCVM_L2_PROTECTION_FAULT_STATUS_LO32` for fault decoding.

Important APIs/types/functions: exports `gfxhub_v12_0_funcs` and defines `gfxhub_v12_0_vmhub_funcs`. Main helpers mirror the standard GFXHUB contract: `gfxhub_v12_0_get_fb_location()`, `gfxhub_v12_0_get_mc_fb_offset()`, `gfxhub_v12_0_setup_vm_pt_regs()`, `gfxhub_v12_0_gart_enable()`, `gfxhub_v12_0_gart_disable()`, `gfxhub_v12_0_set_fault_enable_default()`, and `gfxhub_v12_0_init()`.

Control flow: `init` records context0 page-table base registers, invalidation engine semaphore/request/ack registers, context/fault registers, stride distances, VM fault interrupt mask, and fault/invalidation callbacks in `adev->vmhub[AMDGPU_GFXHUB(0)]`. `gart_enable` optionally programs VF framebuffer base/top registers, then sets VMID0 to the GART page directory, programs GART start/end, AGP and system apertures, scratch default page, dummy fault page, L1 TLB, PF-only L2 cache controls, system domain context0, PF-only identity aperture disable, VMID1-15 context controls and address range, and invalidation ranges for 18 engines. `gart_disable` clears all contexts and disables L1 and L2 cache controls.

State and persistence behavior: persists VM hub metadata in `adev->vmhub[0]` and hardware programming in GCVM/GCMC registers. `hub->vm_cntx_cntl` is set to the last VMID context-control template so generic VM code can reuse it. No dynamic memory is allocated. The system aperture default address is calculated from `mem_scratch.gpu_addr - vram_start + vm_manager.vram_base_offset`, which differs from older `amdgpu_gmc_vram_mc2pa()` paths.

Dependencies and integration points: depends on `gc_12_0_0_offset.h`, `gc_12_0_0_sh_mask.h`, SOC24 enum definitions, SOC15 accessors, AMDGPU GMC/GART/VM manager state, and generic VM hub users. Integrates with fault handling through `amdgpu_vmhub_funcs` and with SR-IOV through VF register programming and PF-owned cache/identity programming.

Risks and test signals: `gfxhub_v12_0_setup_vmid_config()` initially reads `regGCVM_CONTEXT1_CNTL` with offset `i` before writing with `i * hub->ctx_distance`; if read offsets are expected to match write offsets, this is a review point. Fault-status printing still accepts a 32-bit low status value even though newer generations may add high-status fields. The global `amdgpu_noretry` controls retry behavior. Test signals include VMID0 GART access, VMID1-15 GPUVM operation, fault-default toggling, L2 fault logs with GC 12 client IDs, SR-IOV VF base/top programming, and invalidation engine ACK behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.h

Purpose: declares the GC 12.0 GFXHUB function table used by AMDGPU device setup.

Important APIs/types/functions: declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v12_0_funcs`, defined in `gfxhub_v12_0.c`.

Control flow: no runtime control flow; this is a selection/export header.

State and persistence behavior: no local state. The referenced function table persists for the driver/module lifetime.

Dependencies and integration points: depends on AMDGPU core type declarations. Included by ASIC setup code that binds GC 12.0 GFXHUB callbacks.

Risks and test signals: the header is intentionally minimal. Test signal is successful compilation and link resolution of `gfxhub_v12_0_funcs`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.c

Purpose: implements the GC 12.1 GFXHUB callbacks with explicit multi-XCC and XCP partition support. It programs VM/GART state for one or more XCC instances, supports 64-bit split framebuffer-location registers, handles optional VMID0 page-table coverage of VRAM plus GART, and exposes per-partition resume/suspend hooks.

Important APIs/types/functions: exports `gfxhub_v12_1_funcs` and `gfxhub_v12_1_xcp_funcs`. The public GFXHUB callbacks call mask-aware helpers such as `gfxhub_v12_1_xcc_setup_vm_pt_regs()`, `gfxhub_v12_1_xcc_gart_enable()`, `gfxhub_v12_1_xcc_gart_disable()`, `gfxhub_v12_1_xcc_set_fault_enable_default()`, and `gfxhub_v12_1_xcc_init()`. `gfxhub_v12_1_vmhub_funcs` provides low-status fault printing and invalidate-request construction.

Control flow: normal `init` builds a mask covering all logical XCCs from `adev->gfx.xcc_mask` and initializes a separate `adev->vmhub[AMDGPU_GFXHUB(i)]` for each. `gart_enable` does the same all-XCC mask and calls the XCC helper. The XCC enable path optionally programs SR-IOV VF framebuffer location registers, sets VMID0 page-table base and aperture ranges, programs or disables AGP/system apertures depending on `adev->gmc.pdb0_bo`, sets default and dummy fault pages, enables L1 TLB, enables PF-only L2 cache, enables context0 with VMID0 page-table depth/block-size, disables PF identity aperture, configures VMID1-15 contexts, and initializes 18 invalidation engine ranges per XCC. XCP resume first applies fault-default policy from `amdgpu_vm_fault_stop`, then re-enables selected XCC GART state for PF mode; XCP suspend disables selected XCCs for PF mode.

State and persistence behavior: persists one VM hub metadata block per XCC and writes per-XCC GCVM/GCMC register state. The mask-aware helpers allow partition-level reprogramming without touching unselected XCCs. `pdb0_bo` changes VMID0 behavior: with it, VMID0 page tables cover framebuffer-to-GART translation and the legacy FB/AGP/system apertures are disabled. Fault control spans LO32 and HI32 registers, including PDE3 and client no-retry interrupt fields not present in older files.

Dependencies and integration points: depends on GC 12.1 register headers, `amdgpu_xcp.h`, SOC v1 enum definitions, SOC15 register accessors, AMDGPU GMC/GART/VM manager state, SR-IOV helpers, XGMI CPU-connected flag, generic VM hub code, and XCP partition orchestration. Integrates with GPU reset/partition operations through `amdgpu_xcp_ip_funcs`.

Risks and edge cases: several TODOs note uncertain SR-IOV guest access policy and incomplete 64-bit fault status plumbing; `print_l2_protection_fault_status()` only receives/prints LO32 even though important fields moved to HI32. `gfxhub_v12_1_get_mc_fb_offset()` shifts a 32-bit read before casting to `u64`, which is a potential truncation/overflow concern if the register value uses high bits. In `setup_vmid_config`, retry faults are hard-enabled rather than following `amdgpu_noretry`, unlike v11.5/v12.0. Mask construction assumes logical XCCs are densely numbered from zero to `NUM_XCC(xcc_mask)-1`; sparse masks are handled by `for_each_inst()` only after this generated mask is built.

Test signals: validate all-XCC boot and partition-level XCP resume/suspend, VMID0 operation with and without `pdb0_bo`, SR-IOV VF framebuffer base/top programming, TLB invalidation on each per-XCC VM hub, L2 fault-default toggling across LO32/HI32 registers, no access to PF-owned registers in VF paths, and fault logs that identify client IDs while noting the missing HI32 decode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.h

Purpose: declares the GC 12.1 GFXHUB function table and its XCP partition callback table.

Important APIs/types/functions: declares `extern const struct amdgpu_gfxhub_funcs gfxhub_v12_1_funcs` and `extern struct amdgpu_xcp_ip_funcs gfxhub_v12_1_xcp_funcs`, both defined in `gfxhub_v12_1.c`.

Control flow: no runtime control flow. The declarations allow ASIC setup code to bind normal GFXHUB callbacks and XCP partition suspend/resume callbacks.

State and persistence behavior: no local state. The referenced tables have static driver/module lifetime and operate on per-device `adev->vmhub` and GMC state.

Dependencies and integration points: depends on AMDGPU type declarations for `amdgpu_gfxhub_funcs` and `amdgpu_xcp_ip_funcs`. Integrated by GC 12.1 ASIC initialization and XCP manager registration paths.

Risks and test signals: the header is small but exposes an additional mutable-looking non-const XCP table. Test signals are successful build/link and correct registration of both normal and partition-specific callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v12_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.c

Purpose: implements the first-generation SOC15 GFXHUB/GART callbacks for GC 9.0-era ASICs, including Vega/Raven/Aldebaran-era behavior. It programs VMID0 and VMID1-15 page-table registers, AGP/system/framebuffer apertures, L1/L2 TLB/cache controls, invalidation ranges, fault-default policy, and XGMI info delegation.

Important APIs/types/functions: exports `gfxhub_v1_0_funcs` with `.get_mc_fb_offset`, `.setup_vm_pt_regs`, `.gart_enable`, `.gart_disable`, `.set_fault_enable_default`, `.init`, and `.get_xgmi_info = gfxhub_v1_1_get_xgmi_info`. Local helpers include `gfxhub_v1_0_init_gart_aperture_regs()`, `gfxhub_v1_0_init_system_aperture_regs()`, `gfxhub_v1_0_init_tlb_regs()`, `gfxhub_v1_0_init_cache_regs()`, `gfxhub_v1_0_enable_system_domain()`, `gfxhub_v1_0_disable_identity_aperture()`, `gfxhub_v1_0_setup_vmid_config()`, and `gfxhub_v1_0_program_invalidation()`.

Control flow: `init` fills the single `adev->vmhub[AMDGPU_GFXHUB(0)]` with GC 9.0 VM register offsets and stride distances. `gart_enable` chooses the VMID0 page-table base from `gmc.pdb0_bo` when present or from the GART BO otherwise; with `pdb0_bo`, VMID0 covers both VRAM and GART and the legacy apertures are disabled. It then programs system apertures, TLB, PF-only L2 cache, system domain, PF-only identity disable, VMID context controls, and invalidation ranges. `gart_disable` disables all contexts, then for non-VF mode disables L1 advanced model and L2 cache. Fault-default control toggles all common protection-fault default bits and enables crash-on-retry/no-retry when default redirection is disabled.

State and persistence behavior: persists register metadata in one VM hub structure and writes hardware VM/GART state. It derives ranges from `adev->gmc`, page table base from GART or PDB0 BOs, default address from `mem_scratch`, and fault address from `dummy_page_addr`. It does not allocate memory. Hardware state remains until reset or explicit disable.

Dependencies and integration points: depends on GC 9.0 offset/mask/default headers, Vega enum definitions, SOC15 accessors, AMDGPU GMC/GART/VM manager state, SR-IOV helpers, and `gfxhub_v1_1_get_xgmi_info()`. It is selected by older ASIC setup code and used by generic VM update/invalidation paths through `adev->vmhub`.

Risks and edge cases: SR-IOV VF paths avoid some GMC writes; PF/VF division must remain aligned with hypervisor policy. Raven2/Renoir/Green Sardine need a high-aperture workaround to avoid VM faults/hangs. Aldebaran keeps retry faults enabled even when `gmc.noretry` is set because XNACK can be enabled per process in SQ. `pdb0_bo` mode squeezes VRAM into the GART aperture and disables FB/AGP/system apertures, so range programming must match the VM manager layout. Test signals include GART access on VMID0, GPUVM contexts for VMIDs 1-15, aperture workaround coverage on affected APUs, SR-IOV VF no-op safety for blocked registers, L2/TLB invalidation operation, and expected fault/crash behavior when default faulting is toggled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v1_0.c -->
