# Group Research: subset-b-001348

This grouped report covers AMDGPU MMHUB, MMSCH, and AI SR-IOV mailbox files from `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu`. Each file section is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c

## Purpose

`mmhub_v3_0_1.c` implements the `amdgpu_mmhub_funcs` backend for MMHUB 3.0.1 hardware selected by `gmc_v11_0.c`. It programs the multimedia memory hub side of GPU virtual memory: VMID0 GART aperture, system aperture, L1 TLB, L2 cache, protection-fault defaults, VMID context registers, invalidation engines, framebuffer location reads, page-table-base updates, and MMHUB clock-gating state. It also installs an MMHUB client-id table so VM fault logs name display, ISP, HDP, LSDMA, JPEG, VCN, and firmware clients rather than only numeric IDs.

## Important APIs, Types, And Functions

The exported API is `const struct amdgpu_mmhub_funcs mmhub_v3_0_1_funcs`. Its callbacks include `init`, `get_fb_location`, `get_mc_fb_offset`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `set_clockgating`, `get_clockgating`, and `setup_vm_pt_regs`. Internal helpers include `mmhub_v3_0_1_get_invalidate_req`, `mmhub_v3_0_1_print_l2_protection_fault_status`, `mmhub_v3_0_1_init_gart_aperture_regs`, `mmhub_v3_0_1_init_system_aperture_regs`, `mmhub_v3_0_1_init_tlb_regs`, `mmhub_v3_0_1_init_cache_regs`, `mmhub_v3_0_1_setup_vmid_config`, and `mmhub_v3_0_1_program_invalidation`.

## Control Flow

`mmhub_v3_0_1_init()` fills `adev->vmhub[AMDGPU_MMHUB0(0)]` register offsets and spacing values, sets VM fault interrupt masks, assigns `amdgpu_vmhub_funcs`, and registers the local client-id map. Runtime enable flows through `mmhub_v3_0_1_gart_enable()`: program VMID0 page-table base from `adev->gart.bo`, set GART start/end, program AGP/system apertures and default/fault pages, enable TLB and L2 cache, enable system-domain context0, disable identity aperture, configure VMIDs 1 through 15, and set all 18 invalidation engines to full-range invalidation. Disable reverses the critical hardware state by clearing context controls, disabling L1 TLB advanced model, disabling L2 cache, and clearing `MMVM_L2_CNTL3`.

## State And Persistence Behavior

This file persists hardware state in MMHUB registers, not on disk. It records derived register offsets and cached `hub->vm_cntx_cntl` in `adev->vmhub`. Aperture values come from persistent device setup fields such as `adev->gmc.gart_start`, `adev->gmc.gart_end`, `adev->gmc.fb_start`, `adev->gmc.agp_start`, `adev->mem_scratch.gpu_addr`, and `adev->dummy_page_addr`. Fault policy is controlled dynamically by `mmhub_v3_0_1_set_fault_enable_default()`, which redirects faults to the dummy/default page when enabled and sets crash-on-fault bits when disabled.

## Dependencies And Integration Points

The file depends on generated MMHUB 3.0.1 register offset/sh_mask headers, `navi10_enum.h` for MTYPE values, `soc15_common.h`, AMDGPU VM/GMC structures, and SOC15 register access macros. It integrates with the common VM invalidation path via `hub->vmhub_funcs->get_invalidate_req`, with fault logging through `print_l2_protection_fault_status`, with GMC discovery through `get_fb_location` and `get_mc_fb_offset`, and with power management through MC medium-grain clock gating and light-sleep flags.

## Risks

The register programming order is sensitive: enabling contexts before aperture/default-page setup can expose invalid translations. VMID programming assumes 15 user contexts and 18 invalidation engines. `PAGE_TABLE_BLOCK_SIZE` uses `adev->vm_manager.block_size - 9`, so invalid manager setup would underflow hardware fields. Unlike later variants, this file does not guard system-aperture, L2-cache, or fault-control writes for SR-IOV VFs, so using it on hardware where the PF owns those registers would cause access faults or ineffective programming. Fault handling also depends on the global `amdgpu_noretry`.

## Test Signals

Useful tests are boot/resume on a MMHUB 3.0.1 ASIC, GART allocation and GPU page-table access, VM fault injection verifying client names and fault bits, suspend/resume preserving `setup_vm_pt_regs`, SR-IOV negative coverage if this backend is accidentally selected for a VF, and clock-gating tests checking `MM_ATC_L2_MISC_CG` flags for `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.h

## Purpose

`mmhub_v3_0_1.h` is the public declaration header for the MMHUB 3.0.1 backend. It gives other AMDGPU compilation units, primarily GMC setup code, a stable symbol for selecting the implementation in `mmhub_v3_0_1.c`.

## Important APIs, Types, And Functions

The only exported symbol is `extern const struct amdgpu_mmhub_funcs mmhub_v3_0_1_funcs;`. The header relies on includers already knowing `struct amdgpu_mmhub_funcs`, normally via `amdgpu.h` or adjacent driver headers. It defines an include guard `__MMHUB_V3_0_1_H__`.

## Control Flow

There is no runtime control flow in this header. Its compile-time role is to make the function table visible to device-family selection logic. At runtime, callers assign `adev->mmhub.funcs = &mmhub_v3_0_1_funcs` and invoke callbacks through the generic MMHUB interface.

## State And Persistence Behavior

The header stores no state. It exposes an immutable function table allocated by the C file. Any hardware or device state lives in `amdgpu_device`, `amdgpu_vmhub`, and MMHUB registers initialized by that function table.

## Dependencies And Integration Points

The header integrates with `gmc_v11_0.c`, which includes it and selects `mmhub_v3_0_1_funcs` for matching ASIC/IP combinations. Its correctness depends on the C object being built into the AMDGPU module, as listed in the driver `Makefile`.

## Risks

The main risk is declaration/definition drift. If the function table is renamed, removed from the build, or its type changes, GMC selection will fail at build or link time. Because the header contains no version checks, wrong backend selection must be prevented by the caller.

## Test Signals

Build coverage is the main signal: compile AMDGPU with the header included by `gmc_v11_0.c` and ensure the final module links `mmhub_v3_0_1_funcs`. Runtime coverage comes indirectly from probing a device that selects this table and completing MMHUB init/GART enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c

## Purpose

`mmhub_v3_0_2.c` implements the MMHUB 3.0.2 function table for GMC v11 devices. It follows the same core GART/VM programming model as v3.0.1 but adapts client IDs and adds explicit SR-IOV VF guards for registers owned by the PF. It initializes the MMHUB VM hub registers, names MMHUB fault clients, programs VMID contexts and invalidation engines, and supplies callbacks used by generic AMDGPU memory-management code.

## Important APIs, Types, And Functions

The exported table is `mmhub_v3_0_2_funcs`. Important functions are `mmhub_v3_0_2_init`, `mmhub_v3_0_2_gart_enable`, `mmhub_v3_0_2_gart_disable`, `mmhub_v3_0_2_set_fault_enable_default`, `mmhub_v3_0_2_setup_vm_pt_regs`, `mmhub_v3_0_2_get_fb_location`, and `mmhub_v3_0_2_get_mc_fb_offset`. The VM hub sub-interface is `mmhub_v3_0_2_vmhub_funcs`, with invalidation-request construction and fault-status printing. `mmhub_client_ids_v3_0_2` maps VMC, DCE, MP, MPIO, HDP, LSDMA, JPEG, VSCH, VCNU, and VCN clients for read/write fault decoding.

## Control Flow

Initialization fills `adev->vmhub[AMDGPU_MMHUB0(0)]` offsets for page-table base registers, invalidation sem/request/ack, context controls, L2 fault status/control, spacing between contexts/engines, VM fault interrupt masks, and `vm_l2_bank_select_reserved_cid2`. GART enable programs VMID0, system apertures, TLB, cache, context0, identity aperture, VMIDs, and invalidation ranges. Several stages return early on `amdgpu_sriov_vf(adev)`: system-aperture high/low programming, L2 cache programming, identity aperture disable, and L2 fault-control writes are skipped because the PF programs them.

## State And Persistence Behavior

Register programming persists until reset, suspend, or explicit `gart_disable`. The function stores register offsets and the last VM context control value in `adev->vmhub`. It updates page-table-base registers from `adev->gart.bo`, and page-table ranges from `adev->gmc` and `adev->vm_manager`. Fault default state is written into `MMVM_L2_PROTECTION_FAULT_CNTL`, but only when not running as a VF. Clock-gating helpers are present but intentionally empty TODOs, so this backend currently does not mutate clock-gating hardware.

## Dependencies And Integration Points

The file depends on generated `mmhub_3_0_2` register headers, `navi10_enum.h`, SOC15 macros, AMDGPU GMC/VM state, and SR-IOV helpers. It is included in the AMDGPU build and selected by `gmc_v11_0.c`. It also integrates with VM fault reporting through `amdgpu_mmhub_client_name` and `amdgpu_mmhub_init_client_info`.

## Risks

The SR-IOV guards are central: missing one can cause VF register access failures, while over-skipping could leave a PF path uninitialized. The no-op clock-gating callbacks can make feature reporting misleading if callers expect `set_clockgating` or `get_clockgating` to reflect actual state. The client map includes sparse indices such as `32+20`; mistakes here affect diagnosis rather than memory translation. As with v3.0.1, VMID loops and invalidation-engine counts are hardware assumptions.

## Test Signals

Probe tests should cover both bare-metal/PF and VF modes. On PF, verify GART enable, fault-default toggling, and MMHUB VM fault naming. On VF, verify no unauthorized writes occur and VM setup still succeeds with PF-owned registers skipped. Regression signals include successful GPUVM workloads, page faults that do not storm under no-retry settings, and build coverage for the exported function table.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.h

## Purpose

`mmhub_v3_0_2.h` declares the public MMHUB 3.0.2 function table used by GMC v11 device setup. It is a narrow connector between ASIC selection code and the implementation file.

## Important APIs, Types, And Functions

It exports `extern const struct amdgpu_mmhub_funcs mmhub_v3_0_2_funcs;` and defines the include guard `__MMHUB_V3_0_2_H__`. It declares no local structures, macros, or inline functions.

## Control Flow

There is no executable control flow. Runtime dispatch happens after another file assigns the exported function table into `adev->mmhub.funcs`.

## State And Persistence Behavior

No state is stored in this header. The referenced table is read-only and all mutable state is in the device structure or MMHUB registers managed by `mmhub_v3_0_2.c`.

## Dependencies And Integration Points

The header is included by `gmc_v11_0.c` and depends on the AMDGPU core type declarations visible to includers. Linkage depends on `mmhub_v3_0_2.o` being part of the AMDGPU module build.

## Risks

Risks are limited to compile/link integration: stale declarations, missing object inclusion, or accidental use by unsupported hardware. The header itself cannot enforce that v3.0.2-specific SR-IOV behavior is selected only for the right IP.

## Test Signals

Compile the AMDGPU driver with `gmc_v11_0.c` and confirm it links. Runtime signal is a device path that selects `mmhub_v3_0_2_funcs` and successfully completes MMHUB initialization and GART enable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0_2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c

## Purpose

`mmhub_v3_3.c` implements MMHUB 3.3/3.4 support for later GMC v11 devices. It keeps the familiar GART, aperture, TLB, cache, VMID, fault-control, invalidation, framebuffer, and clock-gating callbacks, but adds client maps selected by exact MMHUB IP version plus standalone walker and TLS setup used by this generation.

## Important APIs, Types, And Functions

The exported symbol is `mmhub_v3_3_funcs`. Core callbacks are `mmhub_v3_3_init`, `mmhub_v3_3_gart_enable`, `mmhub_v3_3_gart_disable`, `mmhub_v3_3_set_fault_enable_default`, `mmhub_v3_3_setup_vm_pt_regs`, `mmhub_v3_3_get_fb_location`, `mmhub_v3_3_get_mc_fb_offset`, `mmhub_v3_3_set_clockgating`, and `mmhub_v3_3_get_clockgating`. Generation-specific helpers include `mmhub_v3_3_init_client_info`, `mmhub_v3_3_init_saw_regs`, and `mmhub_v3_3_enable_tls`. It contains three client maps: `mmhub_client_ids_v3_3`, `mmhub_client_ids_v3_3_1`, and `mmhub_client_ids_v3_4`.

## Control Flow

`init` populates VM hub offsets and calls `mmhub_v3_3_init_client_info`, which switches on `amdgpu_ip_version(adev, MMHUB_HWIP, 0)` for 3.3.0, 3.3.1, 3.3.2, or 3.4.0 maps. `gart_enable` runs the standard sequence, then configures the standalone walker with VMID0 page-table base/start/end, enables only SAW context0, sets snooped PDE/PTE requests, and writes DAGB L1TLB TLS registers. Fault printing special-cases CID `0x140` as `UMSCH`, then falls back to the registered client table.

## State And Persistence Behavior

Persistent state is in MMHUB registers and `adev->vmhub[AMDGPU_MMHUB0(0)]`. SAW context registers persist independently of normal VM context registers. TLS state is written directly to two DAGB L1TLB registers. `get_invalidate_req` uses `flush_type ? : 1`, ensuring a nonzero hardware flush type if callers pass zero. Clock-gating state is reflected in `MM_ATC_L2_MISC_CG` bits.

## Dependencies And Integration Points

The file uses generated `mmhub_3_3_0` register definitions, `navi10_enum.h`, SOC15 helpers, VM/GMC fields, and IP-version dispatch. It is selected by `gmc_v11_0.c`. It integrates with common VM invalidation and fault printing via `amdgpu_vmhub_funcs`, with fault diagnostics through `amdgpu_mmhub_init_client_info`, and with power management through MC MGCG/LS callbacks.

## Risks

The exact IP-version-to-client-map mapping is a diagnostic correctness risk; wrong maps make faults hard to triage. SAW and TLS register writes are extra hardware state that must stay synchronized with normal VMID0 programming. No SR-IOV guards are used around several PF-owned-looking registers, so selection must match hardware virtualization policy. The hard-coded SAW context disable mask `0xfffe` assumes 16 contexts and context0-only usage.

## Test Signals

Test by probing each supported MMHUB IP version and forcing VM faults from VCN/JPEG/VPE/ISP clients to validate names. GART tests should confirm both normal and SAW walkers translate VMID0 addresses. Clock-gating tests should validate `MM_ATC_L2_MISC_CG` bit changes. Suspend/resume and GPU reset should verify SAW/TLS registers are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.h

## Purpose

`mmhub_v3_3.h` exposes the MMHUB 3.3 function table to AMDGPU GMC setup code. It is the public selection header for the implementation in `mmhub_v3_3.c`.

## Important APIs, Types, And Functions

The header declares `extern const struct amdgpu_mmhub_funcs mmhub_v3_3_funcs;` and wraps it with `__MMHUB_V3_3_H__`. It intentionally contains no register definitions; those stay in generated IP headers included by the C file.

## Control Flow

The header has no control flow. Runtime behavior begins when a device-family switch assigns `mmhub_v3_3_funcs` to `adev->mmhub.funcs`.

## State And Persistence Behavior

The header stores no mutable state. The function table it declares causes later code to write MMHUB registers, populate `adev->vmhub`, and install client-id tables.

## Dependencies And Integration Points

It integrates with `gmc_v11_0.c` and the AMDGPU module build. Its declaration depends on the surrounding include graph providing `struct amdgpu_mmhub_funcs`.

## Risks

The main risks are stale symbol names and unsupported selection. Because the header does not expose `mmhub_v3_3` sub-variant details, all exact IP-version behavior is hidden in the C implementation.

## Test Signals

Build/link coverage ensures the symbol exists. Runtime probe coverage on MMHUB 3.3/3.4 hardware confirms the selection path reaches the function table and the C callbacks complete MMHUB bring-up.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.c

## Purpose

`mmhub_v4_1_0.c` provides the MMHUB 4.1.0 backend for GMC v12-era devices. It programs the same MMHUB VM plumbing as v3 files but adapts to v4 register names, LO32 fault-status fields, updated client IDs, SR-IOV host-owned register policy, and DAGB-based clock-gating controls.

## Important APIs, Types, And Functions

The exported table is `mmhub_v4_1_0_funcs`. Key callbacks are `init`, `get_fb_location`, `get_mc_fb_offset`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `set_clockgating`, `get_clockgating`, and `setup_vm_pt_regs`. Internal helpers build invalidation requests, print L2 fault status, initialize system/GART apertures, TLB/cache, VMID contexts, invalidation engines, and medium-grain clock gating.

## Control Flow

`mmhub_v4_1_0_init()` fills the single `AMDGPU_MMHUB0(0)` VM hub offsets, including v4-specific `regMMVM_L2_PROTECTION_FAULT_STATUS_LO32`, `regMMVM_L2_BANK_SELECT_RESERVED_CID2`, and `regMMVM_CONTEXTS_DISABLE`. `gart_enable` sets VMID0 page-table base and GART range, skips full system aperture setup on VFs, initializes TLB/cache, enables context0, disables identity aperture on PF paths, configures VMIDs 1-15, and programs 18 invalidation engines. Invalidation requests intentionally force `FLUSH_TYPE` to zero because this backend uses legacy MMHUB invalidation.

## State And Persistence Behavior

Hardware registers retain aperture, cache, TLB, context, and invalidation-range state across normal execution until reset or `gart_disable`. Default page address is computed as `mem_scratch.gpu_addr - vram_start + vm_manager.vram_base_offset`, which differs from older variants using `amdgpu_gmc_vram_mc2pa`. Clock-gating state is only partially maintained: active code toggles DAGB0/DAGB1 read/write return tap-chain FGCG disable bits, while older `MM_ATC_L2_MISC_CG` and light-sleep reporting paths are behind `#if 0`.

## Dependencies And Integration Points

The file depends on generated `mmhub_4_1_0` headers, `soc24_enum.h`, SOC15 macros, SR-IOV helpers, and core AMDGPU GMC/VM structures. It is selected by `gmc_v12_0.c`. It uses `amdgpu_mmhub_init_client_info` for fault-client decoding and participates in generic VM invalidation via `amdgpu_vmhub_funcs`.

## Risks

`get_clockgating` is disabled by `#if 0`, so it does not report active flags even if hardware is gated. Light-sleep control is similarly inactive. V4 fault status is read only from LO32; if future fields needed by diagnostics are in HI32, this implementation will omit them. The `setup_vmid_config` initial read uses offset `i` before writing with `i * hub->ctx_distance`, which is worth preserving only if intentional for this register layout.

## Test Signals

Probe on v4.1.0 hardware, run GPUVM/GART workloads, inject MMHUB faults and verify LO32 field decoding, exercise PF versus VF paths, and toggle MC MGCG flags while checking DAGB registers. Suspend/resume and GPU reset should ensure `vm_contexts_disable`, fault-control, and aperture registers are restored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.h

## Purpose

`mmhub_v4_1_0.h` declares the MMHUB 4.1.0 function table for GMC v12 selection logic.

## Important APIs, Types, And Functions

It exposes `extern const struct amdgpu_mmhub_funcs mmhub_v4_1_0_funcs;` under the include guard `__MMHUB_V4_1_0_H__`.

## Control Flow

There is no executable logic. Runtime control begins after GMC assigns the function table to the device's MMHUB dispatch pointer.

## State And Persistence Behavior

The header does not store state. It references a static implementation table whose callbacks mutate MMHUB hardware registers and `adev->vmhub`.

## Dependencies And Integration Points

It is included by `gmc_v12_0.c` and relies on the AMDGPU build linking `mmhub_v4_1_0.o`. Includers must have a visible declaration of `struct amdgpu_mmhub_funcs`.

## Risks

The header provides no compile-time guard that the selected ASIC actually uses MMHUB 4.1.0. Incorrect caller selection is the main risk; declaration drift is caught by compile/link failures.

## Test Signals

Build/link coverage and a v4.1.0 probe path that selects `mmhub_v4_1_0_funcs` are the practical signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c

## Purpose

`mmhub_v4_2_0.c` is the MMHUB 4.2.0 backend for newer GMC v12 hardware with multiple addressable MMHUB/MID instances and XCP partition support. It generalizes VM hub initialization and GART programming across `adev->aid_mask`, handles VMID0 page-table mode, exposes XGMI fabric information for CPU-connected configurations, and provides standard MMHUB VM, fault, clock-gating, and page-table callbacks.

## Important APIs, Types, And Functions

The exported table is `mmhub_v4_2_0_funcs`; it includes `get_xgmi_info` in addition to the usual MMHUB callbacks. Local XCP callbacks are defined in `struct amdgpu_xcp_ip_funcs mmhub_v4_2_0_xcp_funcs`. Most hardware operations have a `mid_` variant that takes an instance mask: `mid_setup_vm_pt_regs`, `mid_init_gart_aperture_regs`, `mid_init_system_aperture_regs`, `mid_init_tlb_regs`, `mid_init_cache_regs`, `mid_enable_system_domain`, `mid_disable_identity_aperture`, `mid_setup_vmid_config`, `mid_program_invalidation`, `mid_gart_enable`, `mid_gart_disable`, `mid_set_fault_enable_default`, and `mid_init`.

## Control Flow

Top-level callbacks derive `mid_mask = adev->aid_mask` and call the MID helpers. Each helper iterates `for_each_inst(i, mid_mask)` and writes the corresponding `GET_INST(MMHUB, i)` registers. If `adev->gmc.pdb0_bo` exists, VMID0 page-table base comes from that BO and the VMID0 range starts at `fb_start`; system and AGP apertures are disabled because VMID0 page tables cover the path. Otherwise, it uses the normal GART BO and AGP/system aperture programming. `xcp_resume` restores fault defaults and GART setup for a partition mask; `xcp_suspend` disables GART for that mask.

## State And Persistence Behavior

State is per-MMHUB instance in `adev->vmhub[AMDGPU_MMHUB0(i)]` and hardware registers. `mmhub_v4_2_0_get_xgmi_info()` reads `MMMC_VM_XGMI_LFB_*` registers and persists `num_physical_nodes`, `physical_node_id`, and `node_segment_size` in `adev->gmc.xgmi`, returning `-EINVAL` if register values exceed the hard-coded four-node A+A limits. Fault control uses LO32 registers and sets `CRASH_ON_NO_RETRY_FAULT` when default redirection is disabled. `ENABLE_RETRY_FAULT_INTERRUPT` is enabled in CNTL2 during aperture setup.

## Dependencies And Integration Points

The file depends on generated `mmhub_4_2_0` registers, SOC24 enums, SOC15 macros, `for_each_inst`, `GET_INST`, XCP infrastructure, SR-IOV helpers, and GMC VMID0 page-table fields. `gmc_v12_0.c` selects `mmhub_v4_2_0_funcs`. XCP code may use `mmhub_v4_2_0_xcp_funcs` even though the matching header in this subset only declares the function table.

## Risks

Multi-instance code makes mask correctness critical; missing an AID leaves a hub uninitialized, while a bad mask writes nonexistent instances. `hub->vm_cntx_cntl = tmp` after nested loops stores only the final hub's final VMID control. Fault status has a TODO noting important fields moved to HI32, so current logging can omit newer critical fault details. Header/API mismatch around `mmhub_v4_2_0_xcp_funcs` should be checked against external declarations. XGMI limits are fixed at four nodes.

## Test Signals

Test on single- and multi-AID devices, with and without `pdb0_bo`, verifying VMID0 translations, GPUVM workloads, and per-instance invalidation. Exercise XCP suspend/resume with partial masks. Validate XGMI info on CPU-connected A+A systems, SR-IOV VF skip paths, MMHUB fault logging, retry-fault interrupts, and MC MGCG/LS toggling on instance 0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.h

## Purpose

`mmhub_v4_2_0.h` declares the public MMHUB 4.2.0 function table used by GMC v12 selection code.

## Important APIs, Types, And Functions

The header exports `extern const struct amdgpu_mmhub_funcs mmhub_v4_2_0_funcs;` and uses the include guard `__MMHUB_V4_2_0_H__`. It does not declare the `mmhub_v4_2_0_xcp_funcs` object defined by the C file.

## Control Flow

No executable control flow is present. The exported table is assigned by platform setup and later invoked through generic MMHUB callbacks.

## State And Persistence Behavior

The header is stateless. Per-instance VM hub state and MMHUB register state are managed in the C implementation.

## Dependencies And Integration Points

It is included by `gmc_v12_0.c` and depends on the surrounding AMDGPU include graph for the `amdgpu_mmhub_funcs` type. The build must include `mmhub_v4_2_0.o`.

## Risks

If XCP users need `mmhub_v4_2_0_xcp_funcs`, this header does not provide the declaration, so integration must rely on another declaration or local extern. Wrong ASIC selection is the main runtime risk.

## Test Signals

Compile and link AMDGPU with `gmc_v12_0.c`, then probe a v4.2.0 device and confirm `mmhub_v4_2_0_funcs` dispatches successfully. XCP build paths should also be checked for symbol visibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v4_2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c

## Purpose

`mmhub_v9_4.c` implements the Arcturus-era MMHUB 9.4 backend used by GMC v9. It handles two MMHUB instances separated by a fixed register offset, programs GART/VM translation state, configures SDMA snoop overrides, manages clock gating, and exposes MMHUB RAS error-count/status operations.

## Important APIs, Types, And Functions

The exported MMHUB table is `mmhub_v9_4_funcs`; the exported RAS descriptor is `mmhub_v9_4_ras`, backed by `mmhub_v9_4_ras_hw_ops`. Core functions include `mmhub_v9_4_init`, `mmhub_v9_4_gart_enable`, `mmhub_v9_4_gart_disable`, `mmhub_v9_4_set_fault_enable_default`, `mmhub_v9_4_setup_vm_pt_regs`, `mmhub_v9_4_get_fb_location`, `mmhub_v9_4_update_medium_grain_clock_gating`, and `mmhub_v9_4_update_medium_grain_light_sleep`. RAS helpers include `mmhub_v9_4_query_ras_error_count`, `mmhub_v9_4_reset_ras_error_count`, and `mmhub_v9_4_query_ras_error_status`.

## Control Flow

`init` fills two VM hub structures, `AMDGPU_MMHUB0(0)` and `AMDGPU_MMHUB1(0)`, by adding `MMHUB_INSTANCE_REGISTER_OFFSET` to base SOC15 offsets. `gart_enable` loops over both instances and programs VMID0, AGP/system aperture, TLB, L2 cache on PF paths, SDMA snoop overrides, system domain, identity aperture on PF paths, VMID contexts, and invalidation engines. `setup_vm_pt_regs` writes a page-table base into both hubs. RAS count query scans a table of EDC counter registers, decodes matching field descriptors, logs nonzero SEC/DED subblock counts, and updates `ras_err_data`.

## State And Persistence Behavior

The backend writes persistent MMHUB register state for two instances. `get_fb_location` reads base/top from shared VC0 registers and also updates `adev->gmc.fb_start` and `adev->gmc.fb_end`. VMID setup adjusts page-table depth/block size when `adev->gmc.translate_further` is active and uses `adev->gmc.noretry` for retry behavior. RAS counters are read-to-clear during reset; error status registers are sampled to warn about fatal SDP read/write/parity states before reset.

## Dependencies And Integration Points

The file depends on `amdgpu_ras.h`, generated `mmhub_9_4_1` and `athub_1_0` headers, Vega10 enums, SOC15 helpers, and the GMC v9 selection code. `gmc_v9_0.c` assigns `mmhub_v9_4_funcs` and `mmhub_v9_4_ras`. It integrates with generic RAS infrastructure through `amdgpu_ras_block_hw_ops` and with clock/power management only for `CHIP_ARCTURUS`.

## Risks

The two-instance arithmetic is hard-coded; an offset error corrupts the wrong hub. `mmhub_v9_4_get_clockgating` appears to read `mmATCL2_0_ATC_L2_MISC_CG` twice instead of reading a DAGB register for `data1`, so MGCG reporting may be unreliable. The RAS field table is very large and repetitive across MMEA0-MMEA7; copy/paste field mistakes would miscount SEC/DED errors. The comment spelling `Acrturus/arcturas` is cosmetic, but the behavior is ASIC-specific and must not be generalized casually.

## Test Signals

Test signals include Arcturus boot, GART enable on both MMHUB instances, VM page-table updates reaching both hubs, SDMA cache-coherency workloads validating snoop overrides, fault-default toggling, clock-gating flag checks, and RAS injection or register mocking that confirms SEC/DED accumulation, read-to-clear reset, and fatal status warnings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.h

## Purpose

`mmhub_v9_4.h` declares the MMHUB 9.4 backend and its RAS descriptor for GMC v9/Arcturus integration.

## Important APIs, Types, And Functions

It exports `extern const struct amdgpu_mmhub_funcs mmhub_v9_4_funcs;` and `extern struct amdgpu_mmhub_ras mmhub_v9_4_ras;`. The include guard is `__MMHUB_V9_4_H__`.

## Control Flow

The header has no executable flow. GMC code selects the function table, and RAS setup attaches the `amdgpu_mmhub_ras` block to the device.

## State And Persistence Behavior

The header stores no state. The declared RAS object contains pointers to RAS operations, while mutable RAS counts and hardware state live in device registers and AMDGPU RAS data structures.

## Dependencies And Integration Points

It is included by `gmc_v9_0.c` and KFD Arcturus integration code. Includers must have the AMDGPU MMHUB and RAS types visible. Linkage requires `mmhub_v9_4.o`.

## Risks

Declaration drift affects both memory-management and RAS paths. Because the RAS object is non-const, accidental external mutation would affect RAS behavior. Runtime correctness depends on only Arcturus/MMHUB 9.4 paths selecting these symbols.

## Test Signals

Build/link coverage for `mmhub_v9_4_funcs` and `mmhub_v9_4_ras` plus runtime GMC v9 probing and MMHUB RAS registration are the primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v1_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v1_0.h

## Purpose

`mmsch_v1_0.h` defines the version 1 multimedia scheduler command-table ABI used by older virtualized VCE/UVD/VCN paths. It provides table headers, command encodings, and helper macros used by engine code to build initialization command buffers consumed by MMSCH firmware.

## Important APIs, Types, And Functions

The header defines `MMSCH_VERSION 0x1`, `enum mmsch_v1_0_command_type`, `struct mmsch_v1_0_init_header`, `struct mmsch_vf_eng_init_header`, `struct mmsch_v1_1_init_header`, direct and indirect command header structs, write/read-modify-write/poll/end/indirect command structs, inline insertion helpers, and macros `MMSCH_V1_0_INSERT_DIRECT_RD_MOD_WT`, `MMSCH_V1_0_INSERT_DIRECT_WT`, and `MMSCH_V1_0_INSERT_DIRECT_POLL`.

## Control Flow

There is no standalone runtime flow. Caller code allocates an init table, initializes local command templates such as `direct_wt`, `direct_rd_mod_wt`, and `direct_poll`, and invokes insertion macros. Each macro copies a packed command struct into `init_table`, then advances the pointer and `table_size` by the command size in dwords.

## State And Persistence Behavior

The header defines an in-memory binary layout shared with firmware. Persistent effects occur only after caller code submits the populated table to MMSCH. The macros mutate caller-local variables `init_table` and `table_size`, so they rely on names existing in the caller's scope.

## Dependencies And Integration Points

It is included by `uvd_v7_0.c`, `vce_v4_0.c`, and `vcn_v2_5.c`. It relies on `uint32_t` and `memcpy` being available through the include chain. The v1.0 header covers VCE/UVD table offsets and v1.1 generic engine table info for two engines.

## Risks

The bitfield layout is ABI-sensitive and compiler/layout assumptions matter. The macros are not hygienic: they require specific variable names and are statement blocks without `do { } while (0)`. They do not set `command_type`; caller templates must be initialized correctly. Buffer bounds are not checked before `memcpy`, so callers must size tables correctly.

## Test Signals

Build all callers, verify command table sizes and offsets against firmware expectations, boot SR-IOV/media paths that consume v1 tables, and test polling/write/read-modify-write commands by observing successful VCE/UVD/VCN engine initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v2_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v2_0.h

## Purpose

`mmsch_v2_0.h` defines MMSCH 2.0 register offsets and command-table ABI for VCN virtualization. It combines a generated-style register map for the MMSCH block with the init-header and command structures needed to build firmware initialization tables.

## Important APIs, Types, And Functions

The first half defines `mmMMSCH_*` register offsets and base indices for ucode/SRAM access, VF context, mailbox, GPUIOV scheduling/status, scratch, FIFO, NACK, active function, and VM busy registers. The ABI section defines major/minor version macros, `enum mmsch_v2_0_command_type`, `struct mmsch_v2_0_init_header`, command header structs, direct write/read-modify-write/poll/end/indirect command structs, inline insertion helpers, and macros `MMSCH_V2_0_INSERT_DIRECT_RD_MOD_WT`, `MMSCH_V2_0_INSERT_DIRECT_WT`, and `MMSCH_V2_0_INSERT_DIRECT_POLL`.

## Control Flow

The header itself does not run. VCN code uses register offsets for direct MMSCH programming and uses insertion macros to append commands into an init table. The inline helpers populate fields and `memcpy` structs into the caller's table pointer; macros advance `init_table` and `table_size`.

## State And Persistence Behavior

The register constants describe hardware-visible state. The command structs define a firmware-visible memory layout that persists in the init table until consumed by MMSCH. The macros mutate caller-local table pointers and counters and perform no allocation, locking, or bounds checking.

## Dependencies And Integration Points

`vcn_v2_0.c` includes this header for VCN MMSCH initialization. It depends on fixed register offsets matching the hardware IP and on common kernel types and `memcpy`. Mailbox response and GPUIOV register names align this header with SR-IOV media scheduling.

## Risks

Large register maps are vulnerable to offset drift if copied across IP revisions. Macro hygiene and missing bounds checks mirror v1.0 risks. The command bitfield layout must remain compatible with firmware and compiler packing. Register constants are untyped, so wrong block/base usage in callers will compile.

## Test Signals

Test VCN v2 SR-IOV initialization, MMSCH mailbox communication, command table upload, engine pass status, and VM busy/status polling. Static checks should confirm table sizes and register offsets match the IP headers or hardware spec used by this tree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v3_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v3_0.h

## Purpose

`mmsch_v3_0.h` defines the MMSCH 3.0 firmware init-table ABI for VCN generation 3 media engines. It drops the large v2 register map and focuses on versioned table layout and command construction macros.

## Important APIs, Types, And Functions

It includes `amdgpu_vcn.h`, defines `MMSCH_VERSION_MAJOR 3`, `MMSCH_VERSION_MINOR 0`, `MMSCH_VERSION`, and `MMSCH_V3_0_VCN_INSTANCES 0x2`. It declares `enum mmsch_v3_0_command_type`, `struct mmsch_v3_0_table_info`, `struct mmsch_v3_0_init_header`, direct/indirect command header structs, direct write/read-modify-write/poll/end/indirect command structs, and insertion macros including `MMSCH_V3_0_INSERT_END`.

## Control Flow

Callers build an init table by maintaining `table_loc`, `table_size`, `size`, and `size_dw`. Each macro computes the structure size, fills a command template, copies it into `table_loc`, advances `table_loc` by dwords, and increments `table_size`. `MMSCH_V3_0_INSERT_END` appends the preinitialized end command.

## State And Persistence Behavior

The ABI state is the firmware table in memory. The init header has a total size and per-VCN-instance table info array, allowing two VCN instances to be described. The macros mutate caller-local variables and assume command structs are already zeroed or have `command_type` set as needed.

## Dependencies And Integration Points

`vcn_v3_0.c` uses this header when building VCN MMSCH init tables. It depends on `amdgpu_vcn.h` for surrounding VCN definitions and on firmware interpreting version `3.0` layouts.

## Risks

The macros are scope-dependent and lack bounds checks. Failing to initialize the `end` command or command-type fields will produce malformed tables. `MMSCH_V3_0_VCN_INSTANCES` is fixed at two, so callers must not use this layout for hardware with a different instance model.

## Test Signals

Boot VCN v3 hardware, verify MMSCH table upload and engine init status for both instances, confirm end markers are present, and run encode/decode workloads after SR-IOV/media initialization. Build tests should include all macro callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v3_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0.h

## Purpose

`mmsch_v4_0.h` defines the MMSCH 4.0 init-table ABI for VCN/JPEG generation 4 media virtualization. It extends the VCN instance table with JPEG decoder table metadata and mailbox/status constants used by VF media initialization.

## Important APIs, Types, And Functions

The header defines version macros, ring-buffer enable flags `RB_ENABLED` and `RB4_ENABLED`, VF engine status and mailbox response constants, `MMSCH_V4_0_VCN_INSTANCES`, command-type enum, `mmsch_v4_0_table_info`, `mmsch_v4_0_init_header`, command structs, and insertion macros for read-modify-write, write, poll, and end commands.

## Control Flow

It has no independent flow. Callers such as VCN/JPEG v4 code create headers and command tables, then use macros to append commands to `table_loc`. Each macro copies one command struct and advances the caller's location and size counters.

## State And Persistence Behavior

The init header persists per-engine table metadata for two VCN instances and one JPEG decoder table. Mailbox response constants encode firmware-visible completion states such as OK, incomplete, failed, small context, and unknown command. The macros mutate caller-local command table construction variables only.

## Dependencies And Integration Points

It includes `amdgpu_vcn.h` and is used by `vcn_v4_0.c`, `vcn_v4_0_5.c`, `jpeg_v4_0.c`, and `jpeg_v4_0_5.c`. `mmsch_v4_0_3.h` also includes it to reuse table-info and command structures with a revised header layout.

## Risks

ABI compatibility with MMSCH firmware is the main risk. The macros are not bounds-checked and require specific caller variable names. The generic v4.0 header supports only a single `jpegdec` table; later hardware with multiple MJPEG decoders must use the v4.0.3-specific header instead.

## Test Signals

Validate VCN/JPEG v4 SR-IOV initialization, VF mailbox response handling, ring-buffer enable flags, command-table total sizes, and media decode/encode smoke tests after MMSCH setup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0_3.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0_3.h

## Purpose

`mmsch_v4_0_3.h` defines a revised MMSCH 4.0.3 init-header layout for hardware with one VCN table and multiple MJPEG decoder table entries. It reuses the command ABI from `mmsch_v4_0.h`.

## Important APIs, Types, And Functions

The header includes `amdgpu_vcn.h` and `mmsch_v4_0.h`, then declares `struct mmsch_v4_0_3_init_header` with `version`, `total_size`, `vcn0`, `mjpegdec0[4]`, and `mjpegdec1[4]`, each using `struct mmsch_v4_0_table_info`.

## Control Flow

There is no executable flow. VCN/JPEG v4.0.3 callers instantiate this header, fill table metadata, and use v4.0 command macros from the included base header to populate individual engine command streams.

## State And Persistence Behavior

The header defines only the firmware-visible memory layout. It records table offsets, sizes, and init status for one VCN block and two groups of four MJPEG decoders. State persists in the command table memory until firmware consumes and updates it.

## Dependencies And Integration Points

`vcn_v4_0_3.c` and `jpeg_v4_0_3.c` include this header. It depends on `mmsch_v4_0.h` for command structures and table-info definitions, keeping the command encoding consistent while changing only the top-level table layout.

## Risks

Array sizes are ABI constraints. Using the base v4.0 header for this hardware would lose per-MJPEG metadata, while using this header for a different decoder count would misalign firmware parsing. Because it imports v4.0 macros, it inherits their caller-scope and bounds-check risks.

## Test Signals

Test VCN v4.0.3 and JPEG v4.0.3 initialization, verify all eight MJPEG table-info entries are filled and status is read back, and run decode workloads that exercise both decoder groups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v4_0_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v5_0.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v5_0.h

## Purpose

`mmsch_v5_0.h` defines the MMSCH 5.0 command-table ABI for newer VCN/JPEG generation 5 media virtualization. It is structurally similar to v4.0.3 but increases MJPEG decoder table capacity to five entries per group and uses version 5.0 identifiers.

## Important APIs, Types, And Functions

It includes `amdgpu_vcn.h`, defines version, ring-buffer, VF engine status, and mailbox response constants, declares `enum mmsch_v5_0_command_type`, `struct mmsch_v5_0_table_info`, `struct mmsch_v5_0_init_header`, command structs, and macros `MMSCH_V5_0_INSERT_DIRECT_RD_MOD_WT`, `MMSCH_V5_0_INSERT_DIRECT_WT`, `MMSCH_V5_0_INSERT_DIRECT_POLL`, and `MMSCH_V5_0_INSERT_END`.

## Control Flow

Callers build command tables by filling a v5.0 header and appending command structs through macros. The macros compute command size, copy from caller-local command templates into `table_loc`, and update dword counts.

## State And Persistence Behavior

The init header stores firmware-visible metadata for `vcn0`, `mjpegdec0[5]`, and `mjpegdec1[5]`. Mailbox constants represent firmware response state. The header itself stores no persistent kernel state; caller-created tables and firmware-updated init status carry runtime state.

## Dependencies And Integration Points

`vcn_v5_0_1.c`, `jpeg_v5_0_1.c`, and `jpeg_v5_0_2.c` include this header. The command layout must match MMSCH 5.0 firmware expectations.

## Risks

Macro hygiene and no bounds checks remain risks. Command-type fields and `end` command initialization are caller responsibilities. The five-entry MJPEG arrays are fixed ABI assumptions and should not be reused for variants with different decoder counts without a new header.

## Test Signals

Test generation 5 VCN/JPEG VF initialization, verify header total size and all MJPEG table statuses, validate mailbox response handling, and run media workloads after table submission. Build coverage should include all v5 macro callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmsch_v5_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c

## Purpose

`mxgpu_ai.c` implements SR-IOV virtualization mailbox operations for AMDGPU AI-era hardware. It lets a VF communicate with the PF for full-GPU access, reset coordination, init-data exchange, RAS poison/bad-page handling, and mailbox interrupt setup. It exports `xgpu_ai_virt_ops` and several IRQ setup helpers used by SOC15 virtualization code.

## Important APIs, Types, And Functions

Externally visible functions are `xgpu_ai_mailbox_set_irq_funcs`, `xgpu_ai_mailbox_add_irq_id`, `xgpu_ai_mailbox_get_irq`, `xgpu_ai_mailbox_put_irq`, and `const struct amdgpu_virt_ops xgpu_ai_virt_ops`. Internal helpers include mailbox valid/ack primitives, `xgpu_ai_mailbox_trans_msg`, polling functions for ACK/messages/reset completion, access request/release wrappers, workqueue handlers for FLR and RAS bad pages, IRQ set/process callbacks, `xgpu_ai_ras_poison_handler`, and `xgpu_ai_rcvd_ras_intr`.

## Control Flow

Message transmission clears TRN valid until ACK deasserts, writes request/data dwords, sets valid, polls PF ACK, and clears valid. Full-GPU init/fini/reset requests then poll for `IDH_READY_TO_ACCESS_GPU`; init/reset also capture a checksum key from receive DW2. Reset requests retry up to `AI_MAILBOX_POLL_MSG_REP_MAX`. IRQ setup registers BIF client interrupt IDs 135 for receive and 138 for ACK, enables their interrupt bits, and initializes work items. Receive IRQ dispatches mailbox events: bad-page ready/notification schedules data-exchange work, unrecoverable error marks RAS RMA and schedules FLR recovery, FLR notification schedules reset-domain work, and query-alive is acknowledged.

## State And Persistence Behavior

State is held in hardware mailbox registers, `adev->virt` work items/IRQ sources, `adev->virt.fw_reserve.checksum_key`, `adev->virt.req_init_data_ver`, reset-domain scheduling state, and RAS context `is_rma`. Polling uses fixed millisecond timeouts. Work handlers call `amdgpu_virt_fini_data_exchange`, `amdgpu_virt_init_data_exchange`, `amdgpu_virt_request_bad_pages`, and `amdgpu_device_gpu_recover` under reset-domain constraints.

## Dependencies And Integration Points

The file depends on NBIO, GC, MP, SOC15, Vega10 IH, AMDGPU reset, RAS, IRQ, SR-IOV runtime, and reset-domain infrastructure. `soc15.c` includes the header and wires these ops into virtualized AI devices. It uses `RREG/WREG*_NO_KIQ` because mailbox access may occur in contexts where KIQ is unsuitable.

## Risks

Mailbox handshakes are timing-sensitive. `xgpu_ai_mailbox_peek_msg` is documented as IRQ-only but is also used by reset wait and RAS interrupt checks, so callers must understand validity assumptions. Busy wait/poll loops can delay recovery. Receive IRQ accesses `ras->is_rma` without a visible null check after `amdgpu_ras_get_context`. Work scheduling is best-effort via reset-domain queues and can fail with warnings. The typo `AI_MAIBOX` is baked into macro names but harmless if used consistently.

## Test Signals

Test PF/VF mailbox access negotiation, init-data request, reset request/release, FLR notification and completion waits, IRQ enable/disable, ACK/receive interrupts, RAS poison and bad-page flows, unrecoverable error handling, and timeout logging. SR-IOV runtime tests should validate no KIQ dependency and correct reset-domain work scheduling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.h

## Purpose

`mxgpu_ai.h` declares the AI SR-IOV mailbox interface and protocol constants used by `mxgpu_ai.c` and SOC15 virtualization setup. It defines request/event IDs shared between VF driver and PF mailbox firmware.

## Important APIs, Types, And Functions

It defines timeout constants for ACK, message, FLR, and retry count; `enum idh_request` for GPU init/fini/reset access, init data, VF error logging, ready-to-reset, RAS poison, and bad-page requests; `enum idh_event` for PF responses and notifications; `extern const struct amdgpu_virt_ops xgpu_ai_virt_ops`; IRQ helper prototypes; and byte-offset macros for transmit and receive mailbox control fields.

## Control Flow

No executable flow is present. The constants drive `mxgpu_ai.c` control flow: polling durations, request selection, receive IRQ event dispatch, reset wait, RAS handling, and mailbox control byte access.

## State And Persistence Behavior

The header stores no state. The enums and macros define protocol state values written to or read from PF0 mailbox registers. The control offsets are byte offsets into `mmBIF_BX_PF0_MAILBOX_CONTROL`.

## Dependencies And Integration Points

It integrates with SOC15/NBIO register definitions for `SOC15_REG_OFFSET` and `mmBIF_BX_PF0_MAILBOX_CONTROL`, and with AMDGPU virtualization via `struct amdgpu_virt_ops`. `soc15.c`, `amdgpu_vf_error.c`, and `mxgpu_ai.c` include it.

## Risks

Protocol numeric values are ABI-sensitive. Changing enum values or timeouts can break PF/VF negotiation. The misspelled `AI_MAIBOX_*` macro names are part of local API compatibility. The header assumes includers have already included types and register macros needed by prototypes and offset definitions.

## Test Signals

Build all includers, verify mailbox offsets compile with NBIO register headers, run SR-IOV mailbox negotiation and reset tests, and confirm PF event IDs decode correctly in receive IRQ paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.h -->
