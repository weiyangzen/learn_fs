# subset-b-001347 Research

Grouped research report for AMDGPU MES v12.1 and MMHUB generation-specific support files. Each section preserves the source path in its title and is wrapped in reconciliation markers for the split lane.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c

Purpose: implements the AMDGPU Micro Engine Scheduler IP block for GC 12.1 hardware. It loads MES scheduler/KIQ firmware, initializes MES rings and MQDs per XCC, exposes the `amdgpu_mes_funcs` queue-management API, handles legacy queue mapping, submits scheduler API packets, configures cooperative multi-XCC mode, and runs late self-tests for MES-managed compute queues.

Important APIs and functions: the exported object is `mes_v12_1_ip_block`, whose `amd_ip_funcs` wire `early_init`, `sw_init`, `hw_init`, suspend/resume, and teardown into the AMDGPU IP lifecycle. `mes_v12_1_funcs` supplies MES operations: add/remove/reset queue, map/unmap legacy queues, misc register/debug ops, and PASID TLB invalidation. `mes_v12_1_submit_pkt_and_poll_completion()` is the core packet path: it allocates writeback status storage, serializes access with the per-ring spinlock, writes a caller packet plus a scheduler-status fence packet, commits the MES ring, then polls the fence and API completion status with longer timeouts for emulation and SR-IOV. Firmware and runtime setup are split across `mes_v12_1_allocate_ucode_buffer()`, `mes_v12_1_load_microcode()`, `mes_v12_1_enable()`, `mes_v12_1_mqd_init()`, `mes_v12_1_queue_init_register()`, and ring/MQD allocation helpers.

Control flow: early init requests MES firmware for both pipes. Software init installs function pointers, enables legacy queue mapping, computes event-log size, calls generic `amdgpu_mes_init()`, and for every XCC and MES pipe allocates EOP buffers, MQD memory, rings, and optional shared command buffers for unified MES. Hardware init iterates XCCs and calls `mes_v12_1_xcc_hw_init()`, which optionally loads firmware directly, enables MES, enables unmapped doorbell handling, initializes the scheduler pipe queue, sends SET_HW_RSRC packets, configures cooperative resources for unified MES, initializes aggregated doorbells, queries scheduler status, and marks the MES scheduler ready while disabling driver KIQ use. KIQ init separately programs the RLC scheduler pointer, initializes the KIQ pipe, sets KIQ resources in unified MES, and can bootstrap scheduler initialization through legacy queue mapping.

State and persistence: persistent state lives in `adev->mes`, `adev->gfx.kiq[]`, ring writeback memory, GEM BOs for firmware/data/EOP/MQD/shared-command buffers, firmware handles, doorbell indices, scheduler version fields, cooperative-mode master XCC tables, and `sched.ready` flags. The file writes many GC registers through SOC15 helpers, updates ring write/read pointers through CPU writeback and doorbells, and maps test buffers into temporary VMs during self-test. It also mutates isolation behavior through the SET_HW_RSRC `limit_single_process` bit and handles `halt_if_hws_hang` by parking after timeouts.

Dependencies and integration points: depends on AMDGPU core device, BO, ring, fence, VM, PASID, firmware, doorbell, SRBM/GRBM selection, SOC15 register helpers, GC 12.1 register headers, MES API packet definitions, GFX packet definitions, SDMA packet definitions, and xCP partition mode helpers. It integrates with KFD/user queues through MES add-queue fields such as process context, gang context, AQL flag, trap addresses, GWS fields, and queue size. It integrates with VM invalidation by converting AMDGPU hub IDs to MES hub IDs and with debug tooling through MES misc register and shader-debugger operations.

Risks and test signals: the main risks are firmware/API layout drift, packet size/status offset mismatches, ring-full or fence timeout handling, cooperative-mode master-XCC routing, direct register routing through RRMT, duplicated AQL/gds assignment in add-queue setup, and cleanup asymmetry because `hw_fini()` is effectively empty while KIQ fini performs the real disable path. Self-test allocates VM metadata and user context buffers, adds a compute queue, writes a SET_UCONFIG packet to scratch registers, rings a doorbell, polls for `0xDEADBEEF`, then removes the queue; SDMA self-test is present but disabled in the queue type list. Runtime signals include MES firmware version reads from `CP_MES_GP3_LO`, scheduler status query success, `dev_err` timeout logs from packet submission, and late-init self-test pass/fail messages.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.h

Purpose: declares the GC 12.1 MES IP block descriptor for registration by the AMDGPU device discovery/IP-block assembly code.

Important APIs and types: the only exported symbol is `extern const struct amdgpu_ip_block_version mes_v12_1_ip_block;`, implemented in `mes_v12_1.c`. The header relies on consumers already seeing the AMDGPU type declarations for `struct amdgpu_ip_block_version`.

Control flow, state, and persistence: this header has no runtime control flow or storage. Its include guard prevents duplicate declarations, and all persistent MES state is maintained by the implementation through `adev->mes`, firmware objects, rings, and hardware registers.

Dependencies and integration points: included by code that needs to select or register the MES v12.1 IP block. Its correctness depends on the implementation exporting a matching const object. Risks are limited to declaration drift or missing type visibility in including files. Test signals are compile/link coverage: the driver must resolve `mes_v12_1_ip_block` and match the expected IP-block interface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mes_v12_1.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c

Purpose: implements MMHUB 1.0 support for Vega/Raven-era hardware. It programs framebuffer location discovery, GART VMID0, system and AGP apertures, L1 TLB, L2 cache, VMID contexts, invalidation engines, fault-default policy, power/clock gating, and MMHUB RAS EDC counter reporting.

Important APIs and functions: exports `mmhub_v1_0_funcs` and `mmhub_v1_0_ras`. Core callbacks are `get_fb_location`, `init`, `gart_enable`, `gart_disable`, `set_fault_enable_default`, `set_clockgating`, `get_clockgating`, `setup_vm_pt_regs`, and `update_power_gating`. Initialization records register offsets and spacing in `adev->vmhub[AMDGPU_MMHUB0(0)]`; `gart_enable()` applies the ordered programming sequence; `mmhub_v1_0_init_saw()` additionally configures SAW context registers when ISP hardware is present.

Control flow: `gart_enable()` repairs SR-IOV VF framebuffer base/top registers when needed, programs VMID0 page-table base and GART start/end, sets AGP/system/default/fault apertures, enables L1 and L2 cache paths for non-VF devices, enables context0 as the system domain, disables identity aperture, programs VMID1-15 context controls and VA ranges, optionally initializes SAW, and initializes all invalidation-engine address ranges. Disable reverses the VM contexts and TLB/L2 enable bits. Fault default toggling modifies L2 protection-fault default routing and sets crash-on-fault bits when defaults are disabled.

State and persistence: state is held in hardware registers and in `adev->gmc` framebuffer fields populated by `get_fb_location()`. The implementation consumes `adev->gmc` aperture ranges, `adev->gart.bo`, `adev->vm_manager` depth/block/max_pfn, dummy page address, scratch memory address, SR-IOV flags, APU flags, clock/power gating flags, and RAS support state. RAS query reads EDC count registers, accumulates correctable and uncorrectable totals in `ras_err_data`, and reset clears counters by reading them back.

Dependencies and integration points: depends on SOC15 MMHUB 1.0 register definitions, AMDGPU GMC/GART/VM/RAS helpers, SMU power-gating calls, ASIC type flags, SR-IOV checks, and optional ISP discovery. It integrates with the generic VM hub by filling register offset/distance fields used by common invalidation and fault code. Risks include generation-specific register naming, SR-IOV registers skipped or programmed by PF, Raven2/Renoir/Green Sardine aperture workaround correctness, `translate_further` depth/block adjustment, and EDC field-table accuracy. Test signals are hardware boot, GART access, VM fault handling, clock-gating flag reporting, RAS injection/counter reads, and absence of VM fault storms under `noretry`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.h

Purpose: declares the MMHUB 1.0 function table and RAS block used by the AMDGPU memory-controller/GMC initialization code.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v1_0_funcs;` for MMHUB operations and `extern struct amdgpu_mmhub_ras mmhub_v1_0_ras;` for RAS hardware callbacks. The concrete structures are defined elsewhere in AMDGPU headers and initialized in `mmhub_v1_0.c`.

Control flow, state, and persistence: this header has no runtime logic. It exposes implementation-owned global objects; persistent state is in device registers, `adev->vmhub`, `adev->gmc`, and RAS data maintained by the implementation and generic AMDGPU subsystems.

Dependencies, integration, risks, and tests: consumers must include it in contexts with visible `struct amdgpu_mmhub_funcs` and `struct amdgpu_mmhub_ras` declarations. Integration is through ASIC/IP version selection that assigns function pointers and optional RAS handlers. Risks are declaration/export mismatch or selecting this table for unsupported hardware. Compile/link coverage and successful MMHUB/RAS registration are the primary test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c

Purpose: implements MMHUB 1.7 support, mainly Aldebaran-era MMHUB behavior. It follows the v1.x GART and VM programming model while adding optional VMID0 page-table coverage for VRAM-through-GART translation, SDMA snoop override programming, XGMI-to-CPU cache behavior, and broader RAS EDC/status handling.

Important APIs and functions: exports `mmhub_v1_7_funcs` and `mmhub_v1_7_ras`. The function table provides framebuffer discovery, VM hub register initialization, GART enable/disable, fault-default control, clock-gating controls, and VM page-table register setup. `mmhub_v1_7_init_gart_aperture_regs()` selects `adev->gmc.pdb0_bo` over the normal GART BO when present. `mmhub_v1_7_init_snoop_override_regs()` sets SDMA snoop override bits across five DAGB instances. RAS support includes EDC count parsing plus EA error status query/reset callbacks.

Control flow: GART enable programs VMID0 page-table base and range, system/AGP/default/fault apertures, L1 TLB, L2 cache, SDMA snoop overrides, context0, identity aperture disable, VMID1-15 context controls, and invalidation ranges. If `pdb0_bo` exists, VMID0 covers from framebuffer start to GART end and the normal FB/AGP apertures are disabled. VMID contexts always enable retry faults to support per-process XNACK. Clock gating separately respects `AMD_CG_SUPPORT_MC_MGCG` and `AMD_CG_SUPPORT_MC_LS`.

State and persistence: writes MMHUB registers and stores VM hub offsets/distances in `adev->vmhub[AMDGPU_MMHUB0(0)]`. Uses `adev->gmc` aperture and translation settings, `adev->vm_manager` geometry, XGMI CPU connectivity, SR-IOV state, and clock-gating flags. RAS state is not cached locally; queries read EDC/status registers, accumulate CE/UE counts into `ras_err_data`, and reset by writing zeros to EDC counters or setting `CLEAR_ERROR_STATUS`.

Dependencies and integration points: depends on MMHUB 1.7 register headers, SOC15 helpers, AMDGPU RAS helpers, and generic MMHUB/GMC integration through `amdgpu_mmhub_funcs`. The VM hub fields populated here are used by common VM invalidation and fault paths. Risks include `pdb0_bo` aperture programming errors, unconditional retry-fault policy for workloads not expecting XNACK retry, register-table accuracy across six MMEA ranges, and SR-IOV register accessibility. Test signals are boot and GART validation on Aldebaran-class hardware, peer/XGMI and VRAM-through-GART scenarios, SDMA coherency behavior, VM fault logs, clock-gating status, and RAS counter/status injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.h

Purpose: declares the MMHUB 1.7 operation table and RAS block for AMDGPU ASIC selection code.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v1_7_funcs;` and `extern struct amdgpu_mmhub_ras mmhub_v1_7_ras;`. The function table provides GART/VM/fault/clock callbacks; the RAS object provides EDC counter and EA status callbacks.

Control flow, state, and persistence: none in the header. It is a declaration boundary for global objects whose implementation stores state in MMHUB registers, VM hub metadata, and generic RAS reporting structures.

Dependencies, integration, risks, and tests: consumers need AMDGPU MMHUB and RAS type definitions. Integration happens when IP-version matching assigns these exports to `adev->mmhub`/RAS setup. Risks are limited to mismatched declarations or accidental selection for a different MMHUB generation. Compile/link coverage plus successful ASIC bring-up and RAS registration are the key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_7.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c

Purpose: implements MMHUB 1.8 support for multi-AID devices. It extends the v1.7 programming model across `adev->aid_mask`, adds PSP-mediated L1 TLB programming for restricted SR-IOV cases, supports virtual XGMI migration when choosing VMID0 start, and provides newer RAS status-register and ACA integration.

Important APIs and functions: exports `mmhub_v1_8_funcs` and `mmhub_v1_8_ras`. The MMHUB function table covers framebuffer discovery, per-AID VM hub initialization, GART enable/disable, fault-default policy, page-table setup, and placeholder clock-gating callbacks. Core helpers iterate `for_each_inst(i, adev->aid_mask)` for page table, aperture, cache, context, invalidation, and fault-control programming. RAS helpers include per-instance CE/UE status register lists, memory ID translation, `mmhub_v1_8_inst_query_ras_error_count()`, reset callbacks, ACA bank validation/parsing, and `mmhub_v1_8_ras_late_init()`.

Control flow: GART enable selects the normal GART root or `pdb0_bo`, uses `vram_start` rather than `fb_start` when virtual XGMI migration is enabled, writes VMID0 ranges on every active AID, programs apertures/default/fault pages on every non-SR-IOV instance, enables L1 TLB directly or through `psp_reg_program_no_ring()`, configures L2 cache and physical request bits for XGMI-to-CPU or APP APU cases, sets SDMA snoop overrides, enables context0, disables identity aperture, programs VMID1-15 with retry faults enabled, and sets invalidation ranges. Disable clears all contexts and L2 state per AID, then disables L1 TLB using the same direct-or-PSP path.

State and persistence: state resides in per-AID MMHUB registers and `adev->vmhub[AMDGPU_MMHUB0(i)]`. Inputs include `adev->aid_mask`, `adev->gmc` ranges and flags, `adev->psp`, SR-IOV register-access policy, dummy page, mem scratch, VM manager geometry, XGMI/APP APU flags, and RAS/SMUIO helpers. RAS query accumulates per-die CE/UE statistics using socket/die IDs, and ACA integration binds MMHUB SMU banks into the generic RAS cache-log path.

Dependencies and integration points: depends on MMHUB 1.8 register headers, SOC15 helpers, AMDGPU PSP no-ring register programming, RAS status-register helpers, SMUIO MCM config, ACA bank helpers, and generic MMHUB/GMC selection. Risks include missing an AID in loops, PSP/direct register path mismatch under SR-IOV, incorrect die mapping from AID index, placeholder clock-gating functions returning no flags, ACA error-code list drift from SMU definitions, and aperture start differences under XGMI migration. Test signals include multi-AID GART/VM invalidation, SR-IOV L1 TLB programming, XGMI migration, RAS CE/UE status injection, ACA bank reporting, and per-instance VM fault behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.h

Purpose: declares the MMHUB 1.8 operations and RAS integration objects.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v1_8_funcs;` and `extern struct amdgpu_mmhub_ras mmhub_v1_8_ras;`. The implementation supplies multi-AID VM/GART callbacks and status-register/ACA-based RAS callbacks.

Control flow, state, and persistence: this header has no runtime behavior. It exposes implementation globals; all state is in `adev->vmhub[]`, MMHUB registers, PSP-mediated register state, and generic AMDGPU RAS structures.

Dependencies, integration, risks, and tests: requires consumers to have AMDGPU MMHUB/RAS type declarations. It integrates through ASIC discovery and RAS block registration. Main risks are selecting this multi-AID implementation for an incompatible ASIC or declaration mismatch. Compile/link coverage, MMHUB function-table assignment, and RAS late-init binding are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v1_8.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c

Purpose: implements MMHUB 2.0/2.1 support for Navi-era ASICs. It programs the `MMVM`/`MMMC` register set, provides VM invalidation request construction and L2 protection fault decoding, initializes client-ID tables for Navi1x, Sienna Cichlid, and Beige Goby, and handles generation-specific clock/light-sleep controls.

Important APIs and functions: exports `mmhub_v2_0_funcs`. The VM hub function table `mmhub_v2_0_vmhub_funcs` provides `get_invalidate_req()` and `print_l2_protection_fault_status()`. `mmhub_v2_0_init()` records register offsets, context/invalidation distances, VM fault interrupt masks, attaches VM hub functions, and calls `mmhub_v2_0_init_client_info()` based on MMHUB IP version. `gart_enable()` follows the usual aperture/TLB/L2/context/invalidation sequence, with RLC-safe register writes for many context operations.

Control flow: invalidation requests set per-VMID invalidate, flush type, L2 PTE/PDE and L1 PTE invalidation bits. GART enable programs VMID0 page-table base/range, AGP/system/default/fault apertures, L1 TLB, L2 cache including default-page-out-to-system-memory and L2 CNTL5, context0, identity aperture disable, VMID1-15 controls/ranges, and invalidation address ranges. VMID context setup stores the final `vm_cntx_cntl` in the hub. Fault status printing decodes CID/RW and resolves client names through the initialized client tables. Clock gating handles 2.0.x ATC_L2 plus DAGB registers and 2.1.x DAGB-only variants.

State and persistence: state is written to MMHUB registers and stored in `adev->vmhub[AMDGPU_MMHUB0(0)]` and `adev->mmhub` client-name tables. Inputs include `adev->gmc`, `adev->gart.bo`, `adev->vm_manager`, `adev->dummy_page_addr`, `adev->mem_scratch`, SR-IOV state, `cg_flags`, and MMHUB IP version. No RAS object is exported here; fault diagnostics come through the generic VM hub callbacks.

Dependencies and integration points: depends on MMHUB 2.0 register/default headers, SOC15 and RLC register helpers, AMDGPU MMHUB client-name helpers, Navi enum definitions, and generic VM/GMC code. It integrates with common VM invalidation and page-fault handling via `hub->vmhub_funcs`, offsets, fault masks, and client-name lookup. Risks include client-ID table drift across ASIC revisions, SR-IOV PF/VF register ownership, 2.1.x absence of ATCL2 affecting clock status, use of `adev->gmc.noretry` for retry-fault policy, and RLC write path consistency. Test signals are VM fault logs with named clients, TLB invalidation correctness, GART access, SR-IOV VF bring-up, and clock-gating flag readback on each supported IP version.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.h

Purpose: declares the MMHUB 2.0/2.1 function table for AMDGPU ASIC initialization.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v2_0_funcs;`, implemented by `mmhub_v2_0.c`. No RAS object is declared for this generation in this header.

Control flow, state, and persistence: no runtime logic. The implementation owns VM hub register metadata, client-ID mappings, and hardware register programming state.

Dependencies, integration, risks, and tests: consumers must have `struct amdgpu_mmhub_funcs` visible. Integration is through IP-version selection that assigns this table to the device MMHUB callbacks. Risks are declaration/export mismatch and incorrect table selection for unsupported MMHUB 2.x variants. Compile/link coverage and successful GART/VM/fault callback registration are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_0.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c

Purpose: implements MMHUB 2.3 support for VanGogh-class hardware. It is a focused single-instance MMHUB implementation with VanGogh client IDs, MMVM invalidation/fault callbacks, GART and VM context programming, SR-IOV framebuffer fixup in GART enable, and CGTT-based clock/light-sleep control.

Important APIs and functions: exports `mmhub_v2_3_funcs`. `mmhub_v2_3_vmhub_funcs` provides invalidation request construction and L2 fault status printing. `mmhub_v2_3_init()` records MMVM register offsets/distances, VM fault interrupt masks, VM hub functions, and VanGogh client names. GART helpers program VMID0, apertures, TLB, L2 cache, context controls, invalidation ranges, and fault-default routing.

Control flow: `gart_enable()` first repairs VF framebuffer base/top copy registers when running as SR-IOV VF, then programs page-table base/range for GART, AGP/system/default/fault apertures, L1 TLB, L2 cache and CNTL5, context0, identity aperture disable, VMID1-15 controls, and invalidation ranges. `set_fault_enable_default()` toggles all L2 protection-fault default bits and sets crash-on-retry/no-retry when defaults are disabled. Clock gating toggles `SOFT_OVERRIDE` and DAGB disable bits; light sleep toggles MM_ATC and DAGB read/write LS override bits.

State and persistence: stores register offset and spacing metadata in `adev->vmhub[AMDGPU_MMHUB0(0)]` and VanGogh client IDs in `adev->mmhub`; persistent hardware state is in MMHUB registers. Inputs include `adev->gmc`, `adev->gart.bo`, `adev->vm_manager`, `dummy_page_addr`, `mem_scratch`, SR-IOV state, and `cg_flags`. There is no generation-specific RAS export in this file.

Dependencies and integration points: depends on MMHUB 2.3 register/default headers, SOC15 helpers, Navi enum definitions, AMDGPU MMHUB client helper, and generic VM/GMC code. It integrates with common VM invalidation/fault code through `hub->vmhub_funcs` and client-name lookup. Risks include SR-IOV accessibility assumptions because fewer routines skip VF writes than v2.0/v3.0, VanGogh client ID table drift, retry-fault policy tied to `adev->gmc.noretry`, and CGTT register differences from other v2.x parts. Test signals are VanGogh boot, GART/VM access, VF framebuffer programming, VM fault printouts with correct client names, TLB invalidation, and clock/light-sleep flag readback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.h

Purpose: declares the MMHUB 2.3 function table used by AMDGPU generation selection code.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v2_3_funcs;`. The implementation provides GART, VM fault, invalidation, page-table, and clock-gating callbacks.

Control flow, state, and persistence: none in the header. Runtime state is maintained by `mmhub_v2_3.c` in MMHUB registers, `adev->vmhub`, and `adev->mmhub` client information.

Dependencies, integration, risks, and tests: requires AMDGPU MMHUB type definitions. Integration is via assigning the declared table to matching MMHUB 2.3 ASICs. Risks are declaration mismatch or wrong ASIC matching. Compile/link coverage and successful VM hub callback registration are primary signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v2_3.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c

Purpose: implements MMHUB 3.0 support. It programs the MMVM/MMMC register set for GART and VM contexts, reports framebuffer base and MC framebuffer offset, provides VM invalidation and L2 fault diagnostics with v3.0 client IDs, tracks additional VM hub registers for reserved client/bank selection and context-disable support, and handles ATC_L2-only clock/light-sleep gating.

Important APIs and functions: exports `mmhub_v3_0_funcs`. Its function table adds `get_fb_location` and `get_mc_fb_offset` in addition to init, GART enable/disable, fault-default control, clock-gating, and page-table setup. `mmhub_v3_0_vmhub_funcs` supplies invalidation request construction and L2 fault status printing. `mmhub_v3_0_init()` records VM hub offsets/distances, VM fault interrupt masks, `vm_l2_bank_select_reserved_cid2`, `vm_contexts_disable`, VM hub callbacks, and client-name mappings.

Control flow: GART enable programs VMID0 GART page-table base/range, skips system aperture programming entirely for SR-IOV VF because the host owns those registers, programs TLB with ECO bits cleared, L2 cache and CNTL5 for non-VF, context0, identity aperture disable for non-VF, VMID1-15 controls with retry policy based on global `amdgpu_noretry`, and invalidation ranges. Disable clears 16 context controls, disables L1 TLB advanced mode, disables L2 cache, and clears L2 CNTL3. Fault-default control is skipped on VF and otherwise toggles all L2 default-fault routing bits plus crash-on-fault bits when disabled.

State and persistence: persists hardware programming in MMHUB registers and metadata in `adev->vmhub[AMDGPU_MMHUB0(0)]` and `adev->mmhub`. Inputs include GART and GMC address ranges, VM manager geometry, dummy page and scratch addresses, SR-IOV state, global `amdgpu_noretry`, and `cg_flags`. `get_fb_location()` only returns the base from `regMMMC_VM_FB_LOCATION_BASE`; unlike v1.x, it does not update `adev->gmc.fb_start/fb_end`.

Dependencies and integration points: depends on MMHUB 3.0 register headers, SOC15 helpers, Navi enum/client naming, generic AMDGPU VM/GMC/MMHUB code, and common VM fault handlers. It integrates with fault handling through client-name lookup and with invalidation through `get_invalidate_req()`. Risks include global rather than per-device noretry policy, SR-IOV host/guest register ownership, incomplete DAGB clock-gating code left under `#if 0`, and framebuffer location semantics differing from older generations. Test signals are GART bring-up, VM invalidation, named VM fault logs, `get_mc_fb_offset()` correctness, clock-gating flag readback, and SR-IOV VF boot without protected-register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.h

Purpose: declares the MMHUB 3.0 function table for AMDGPU IP-version selection.

Important APIs and types: exports `extern const struct amdgpu_mmhub_funcs mmhub_v3_0_funcs;`, implemented in `mmhub_v3_0.c`. The table includes VM/GART/fault/clock callbacks plus framebuffer base and MC framebuffer offset helpers.

Control flow, state, and persistence: this header has no behavior or storage. The implementation persists state in MMHUB registers and AMDGPU device metadata.

Dependencies, integration, risks, and tests: consumers need `struct amdgpu_mmhub_funcs` visible. Integration is via ASIC-specific assignment to `adev->mmhub.funcs`. Risks are limited to declaration mismatch or wrong generation selection. Compile/link coverage and successful v3.0 MMHUB callback registration are the test signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.h -->
