# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_1_8_0_sh_mask.h lines 21061-22628

## Purpose

This chunk is the tail of the generated MMHUB 1.8.0 register shift/mask header used by the AMDGPU driver. It does not implement executable control flow; it defines C preprocessor constants that describe bit positions and bit masks for MMHUB register fields. The paired offset header supplies register addresses, while this header supplies the field encodings consumed through `REG_SET_FIELD`, `REG_GET_FIELD`, raw mask operations, and SOC15 register read/write helpers.

The covered range spans several hardware programming areas:

- VM invalidate engine request, acknowledgement, and address-range fields for engines 4-17, plus the full ACK and address-range macro sets for engines 0-17.
- Per-VMID page-table base, start, and end address fields for contexts 0-15.
- Shared VM aperture, framebuffer, AGP, DRAM, HBM, XGMI, SR-IOV, IOMMU, MARC, and ATS control fields.
- ATC L2, VM L2, UTC translation-assist, and L2 TLB performance counter fields.
- MM_CANE clock-gating override and correctable/uncorrectable error status fields used by RAS paths.

## Important APIs, Types, and Macros

This file exports macros rather than APIs or types. The important macro families are:

- `VM_INVALIDATE_ENGn_REQ__*`: request fields for invalidation engines. `PER_VMID_INVALIDATE_REQ` occupies bits 0-15, `FLUSH_TYPE` occupies bits 16-17, and one-bit controls select L2 PTE, L2 PDE0/PDE1/PDE2, L1 PTE invalidation, protection-fault status clearing, and request logging.
- `VM_INVALIDATE_ENGn_ACK__*`: acknowledgement fields for invalidation engines. The low 16 bits mirror per-VMID acknowledgement state, and bit 16 is `SEMAPHORE`.
- `VM_INVALIDATE_ENGn_ADDR_RANGE_LO32/HI32__*`: per-engine invalidate address-range fields. The low word carries an `S_BIT` plus low logical page address bits; the high word carries the high 5 logical page address bits.
- `VM_CONTEXTn_PAGE_TABLE_BASE_ADDR_*`, `VM_CONTEXTn_PAGE_TABLE_START_ADDR_*`, and `VM_CONTEXTn_PAGE_TABLE_END_ADDR_*`: per-context page-table root and virtual address bound encodings. Base registers use full 32-bit low/high page-directory-entry pieces; start/end high registers expose only a 4-bit high logical page-number field.
- `MC_VM_*`: shared memory-controller VM aperture and translation controls, including framebuffer location, AGP bounds, system aperture bounds, default physical page address, L1 TLB control, top-of-DRAM fields, cacheable DRAM and local HBM ranges, direct-system aperture behavior, XGMI local framebuffer sizing, SR-IOV VF framebuffer size/offset, active function ID, and GPU IOV enable bits.
- `VM_IOMMU_*`, `MC_VM_MARC_*`, and `VM_PCIE_ATS_CNTL*`: IOMMU enable/performance, MARC base/relocation/length windows, and PCIe ATS enable/STU fields for PF and VFs.
- `ATC_L2_PERFCOUNTER*`, `MC_VM_L2_PERFCOUNTER*`, and `L2TLB_PERFCOUNTER*`: performance counter result, selection, mode, enable, clear, trigger, and saturation-control fields.
- `UTC_GPUVA_VMID_TRANSLATION_ASSIST_*`: request/response fields for software or debug-assisted GPU virtual address translation, including VMID, GPU VA, permissions, client ID, request/ack/nack, fragment size, snoop, SPA/IO, TMZ, memory type, and no-PTE status.
- `MM_CANE_*`: clock-gating soft overrides plus error status fields for SDPM/SDPS response/data/parity status and CE/UE ECC/parity address, memory ID, info, count, poison, and fatal-event fields.

The direct integration point in the AMDGPU code for this ASIC generation is `amdgpu/mmhub_v1_8.c`, which includes both `mmhub_1_8_0_offset.h` and this shift/mask header.

## Control Flow

There is no runtime control flow inside the header. Runtime behavior appears in code that consumes these constants:

- `mmhub_v1_8_setup_vm_pt_regs()` writes `regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32/HI32` plus context-offset distances to program per-VMID page-table roots.
- `mmhub_v1_8_init_gart_aperture_regs()` programs context 0 start/end bounds with `regVM_CONTEXT0_PAGE_TABLE_START_ADDR_*` and `regVM_CONTEXT0_PAGE_TABLE_END_ADDR_*`.
- `mmhub_v1_8_init_system_aperture_regs()` writes AGP, framebuffer, system aperture, default-page, and fault default-address registers whose fields are defined in this header chunk.
- `mmhub_v1_8_init_tlb_regs()` reads and rewrites `regMC_VM_MX_L1_TLB_CNTL` using the `MC_VM_MX_L1_TLB_CNTL__*` field macros for L1 TLB enable, system access mode, advanced driver model, aperture behavior, memory type, and ATC enable.
- `mmhub_v1_8_setup_vmid_config()` iterates VM contexts 1-15 and writes per-context page-table start/end bounds using the register spacing derived from context address register offsets.
- `mmhub_v1_8_program_invalidation()` iterates 18 invalidation engines and initializes each engine address range to the full range using `regVM_INVALIDATE_ENG0_ADDR_RANGE_LO32/HI32` plus `hub->eng_addr_distance`.
- `mmhub_v1_8_init()` caches `vm_inv_eng0_req`, `vm_inv_eng0_ack`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance`, making the repeated register layout in this chunk part of the generic VM hub invalidation path.
- The RAS tables in `mmhub_v1_8.c` add `regMM_CANE_CE_ERR_STATUS_LO/HI` and `regMM_CANE_UE_ERR_STATUS_LO/HI`, which correspond to the MM_CANE CE/UE masks defined at the end of this chunk.

## State and Persistence Behavior

The macros describe hardware register state. Persistence is therefore MMIO/hardware-local, not file-backed:

- Page-table base/start/end registers persist in MMHUB until rewritten by driver initialization, VM context setup, reset, suspend/resume restore, or GPU reset recovery.
- Invalidation request and acknowledgement registers are transient synchronization state between CPU/driver writes and MMHUB completion. The field layout must match hardware because the VM manager polls ACK bits and relies on engine spacing to select the correct invalidation engine.
- Aperture and address-window registers define persistent translation windows while the device is running: framebuffer location, AGP range, system aperture, cacheable DRAM, local HBM, XGMI LFB, MARC regions, and VF framebuffer partitioning.
- TLB/cache control bits persist until changed and directly affect translation behavior, caching, ATS/ATC participation, and fault handling.
- Performance counters persist as hardware counters until cleared through their `CLEAR` or `CLEAR_ALL` fields; result registers split low 32 bits from high 16 counter bits and high 16 compare-value bits.
- MM_CANE CE/UE status registers hold error records, address-valid flags, memory IDs, error info, and counters until cleared or consumed by RAS handling. `MM_CANE_ERR_STATUS__CLEAR_ERROR_STATUS` is the explicit clear bit for the aggregate error-status register.

## Dependencies and Integration Points

This chunk depends on the SOC15 AMDGPU register infrastructure:

- `mmhub_1_8_0_offset.h` provides `reg...` register names; this header provides the matching `__SHIFT` and `__MASK` constants.
- `soc15.h`/`soc15_common.h` provide `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`.
- Generic register helpers such as `REG_SET_FIELD` depend on the naming convention `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- VM hub integration uses `struct amdgpu_vmhub` fields such as `ctx0_ptb_addr_lo32`, `vm_inv_eng0_req`, `vm_inv_eng0_ack`, `ctx_addr_distance`, `eng_distance`, and `eng_addr_distance`.
- GART and VM programming depends on `adev->gmc`, `adev->vm_manager`, `adev->aid_mask`, SR-IOV state, XGMI migration state, PSP indirect register programming, and `for_each_inst()` over AID/MMHUB instances.
- RAS integration depends on `AMDGPU_RAS_REG_ENTRY`, `struct amdgpu_ras_err_status_reg_entry`, and the MMHUB RAS query paths that read MM_CANE CE/UE status pairs.

## Risks and Edge Cases

- The register layout is generated and highly repetitive. A single incorrect shift or mask in a repeated VM context or invalidation-engine family would not be caught by C type checking and could silently program the wrong hardware field.
- The requested range starts in the middle of `VM_INVALIDATE_ENG4_REQ`; lines before the chunk define the matching ENG4 shift fields and earlier engines. Research consumers should merge this chunk with adjacent chunks before treating the per-engine family as complete.
- The driver derives spacing from adjacent offsets (`regVM_INVALIDATE_ENG1_REQ - regVM_INVALIDATE_ENG0_REQ`, `regVM_CONTEXT1_PAGE_TABLE_BASE_ADDR_LO32 - regVM_CONTEXT0_PAGE_TABLE_BASE_ADDR_LO32`). If masks or offsets diverge from the hardware generation, invalidation and VMID programming can target wrong registers across all instances.
- Address fields encode page numbers, not byte addresses. Callers shift GPU/physical addresses before writing; using byte addresses directly would overrun masked fields or translate the wrong aperture.
- High address fields are narrow in several groups: start/end high logical page numbers use 4 bits, invalidate range high uses 5 bits, and system aperture default MSB uses 4 bits. Future address-width changes require ASIC-specific headers and cannot be assumed compatible.
- SR-IOV and PF/VF fields are security-sensitive. `MC_VM_FB_SIZE_OFFSET_VFn`, `MC_SHARED_ACTIVE_FCN_ID`, ATS VF enables, `MC_SHARED_VIRT_RESET_REQ`, and `MC_VM_XGMI_GPUIOV_ENABLE` affect virtual function isolation and reset behavior.
- ATS/ATC/IOMMU/MARC controls interact with CPU-visible translation and migration features. Enabling `ATC_ENABLE`, `IOMMUEN`, `MARC_EN`, or relocation windows with bad ranges can create stale translations or incorrect access permissions.
- RAS masks for MM_CANE encode both status and clear/interrupt bits in the same register group. Clearing or enabling fatal interrupts with the wrong mask can lose diagnostic state or generate unexpected interrupts.

## Test Signals

Useful validation signals are mostly integration and hardware-facing:

- Build-test the AMDGPU driver after header changes; compile failures around `REG_SET_FIELD` or missing masks catch naming and generation regressions.
- Exercise GART enable/disable on MMHUB 1.8 hardware and confirm `mmhub_v1_8_get_fb_location()`, GART aperture setup, VMID page-table setup, and L1 TLB programming complete without VM faults.
- Run VM invalidation stress paths, including many VMIDs and multiple MMHUB/AID instances, and check that invalidation request/ACK polling completes without hangs.
- Validate SR-IOV PF and VF boot paths when touching VF framebuffer, ATS, active-function, or GPUIOV fields.
- Check RAS injection or error-query paths for MM_CANE CE/UE records; expected signals are correct CE/UE counts, memory IDs, address-valid flags, and no spurious fatal interrupt behavior.
- Use performance counter smoke tests or debugfs/perf tooling, where available, to verify ATC L2, VM L2, and L2 TLB counter clear/enable/result paths.
- Suspend/resume and GPU reset are important because the register state described here must be reinitialized consistently after hardware context loss.
