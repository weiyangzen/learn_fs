# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_sh_mask.h lines 9512-10265

## Scope

This chunk covers the final 754 lines of the generated AMD MMHUB 9.3.0 shift/mask header. The range contains 561 `#define` statements and the closing `#endif`; it has no C functions, structs, enums, variables, allocations, locks, or executable branches.

The chunk starts in the middle of the VM context page-table aperture definitions and then covers these address blocks:

- Tail of the VM context block: `VM_CONTEXT0..15_PAGE_TABLE_START_ADDR_{LO32,HI32}` and `VM_CONTEXT0..15_PAGE_TABLE_END_ADDR_{LO32,HI32}` field masks.
- `mmhub_utcl2_vml2pldec`: MC VM L2 performance-counter configuration and result-control fields.
- `mmhub_utcl2_vml2prdec`: MC VM L2 performance-counter result low/high fields.
- `mmhub_utcl2_vmsharedhvdec`: per-VF framebuffer size/offset fields, IOMMU/MARC/ATS controls, UTCL2 clock-gating controls, active PF/VF selection, and XGMI GPUIOV enable fields.
- `mmhub_utcl2_vmsharedpfdec`: PF/shared northbridge MMIO, DRAM, aperture, local HBM, power, reset, and XGMI local-framebuffer fields.
- `mmhub_utcl2_vmsharedvcdec`: visible client/shared framebuffer, AGP, system aperture, and L1 TLB control fields.
- `mmhub_utcl2_atcl2pfcntrdec` and `mmhub_utcl2_atcl2pfcntldec`: ATC L2 performance-counter result and control fields.

Although the repository path is under `sources/distributed-fs/ceph-client`, this file is AMDGPU DRM register metadata and is not Ceph filesystem logic.

## Purpose

The purpose of this chunk is to provide the bitfield ABI used by driver code when composing or decoding 32-bit MMHUB 9.3.0 register values. Each hardware field is represented by the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset.
- `<REGISTER>__<FIELD>_MASK`, the bit mask.

Consumers combine these macros with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `SOC15_REG_OFFSET`. The companion `mmhub_9_3_0_offset.h` supplies the numeric register offsets, while this file supplies the bit positions and masks for those offsets.

## Important Macro Families

### VM Context Aperture Bounds

The opening section defines low and high logical page-number fields for VM context page-table start and end addresses:

- `VM_CONTEXT0..15_PAGE_TABLE_START_ADDR_LO32__LOGICAL_PAGE_NUMBER_LO32`
- `VM_CONTEXT0..15_PAGE_TABLE_START_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4`
- `VM_CONTEXT0..15_PAGE_TABLE_END_ADDR_LO32__LOGICAL_PAGE_NUMBER_LO32`
- `VM_CONTEXT0..15_PAGE_TABLE_END_ADDR_HI32__LOGICAL_PAGE_NUMBER_HI4`

The low registers expose a full 32-bit logical page number. The high registers expose the upper 4 bits through mask `0x0000000f`, matching the common AMDGPU pattern where virtual memory aperture boundaries are programmed as page numbers split across low 32 bits and high 4 bits. Nearby MMHUB setup code for related generations writes these register families from `adev->gmc.gart_start` and `adev->gmc.gart_end` shifted by 12 and 44 bits.

This chunk begins after the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32` field definition and includes only the `VM_CONTEXT0_PAGE_TABLE_START_ADDR_HI32` mask plus contexts 1-15 start fields. The matching base-address fields and the first context-0 start low field are owned by previous chunks.

### MC VM L2 Performance Counters

`mmhub_utcl2_vml2pldec` defines `MC_VM_L2_PERFCOUNTER0_CFG` through `MC_VM_L2_PERFCOUNTER7_CFG`, plus `MC_VM_L2_PERFCOUNTER_RSLT_CNTL`. Each counter config has the same layout:

- `PERF_SEL` at bits 0-7.
- `PERF_SEL_END` at bits 8-15.
- `PERF_MODE` at bits 24-27.
- `ENABLE` at bit 28.
- `CLEAR` at bit 29.

`MC_VM_L2_PERFCOUNTER_RSLT_CNTL` selects the active counter, start trigger, stop trigger, global enable-any, clear-all, and stop-on-saturate behavior. The result block `mmhub_utcl2_vml2prdec` supplies `MC_VM_L2_PERFCOUNTER_LO__COUNTER_LO` and `MC_VM_L2_PERFCOUNTER_HI`, whose high register combines `COUNTER_HI` with a 16-bit `COMPARE_VALUE`. These fields support hardware performance sampling of the MMHUB VM L2 path.

### SR-IOV VF Framebuffer Apertures

`MC_VM_FB_SIZE_OFFSET_VF0` through `MC_VM_FB_SIZE_OFFSET_VF15` each pack two 16-bit fields:

- `VF_FB_SIZE` in bits 0-15.
- `VF_FB_OFFSET` in bits 16-31.

These registers describe framebuffer partitioning for up to 16 virtual functions. They are hypervisor/PF-owned state in typical SR-IOV deployments; guest/VF code should not assume it can rewrite them.

### IOMMU, MARC, and ATS Control

The chunk defines several memory-translation control families:

- `VM_IOMMU_MMIO_CNTRL_1__MARC_EN` enables MARC handling.
- `MC_VM_MARC_BASE_LO/HI_0..3` encode four MARC base addresses.
- `MC_VM_MARC_RELOC_LO/HI_0..3` encode four relocation targets, with `MARC_ENABLE_n` and `MARC_READONLY_n` bits in each low register.
- `MC_VM_MARC_LEN_LO/HI_0..3` encode region lengths.
- `VM_IOMMU_CONTROL_REGISTER__IOMMUEN` enables IOMMU behavior.
- `VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER__PERFOPTEN` enables an IOMMU performance optimization.
- `VM_PCIE_ATS_CNTL` exposes `STU` and `ATC_ENABLE` for the PF/global path.
- `VM_PCIE_ATS_CNTL_VF_0..15` expose per-VF `ATC_ENABLE` bits.

These fields sit on the boundary between PCIe ATS/ATC, IOMMU address translation, and MMHUB memory routing. The macros only define bit layout; valid sequencing depends on platform firmware, PF/VF policy, and the surrounding AMDGPU VM hub code.

### UTCL2 Clock and Function Selection

`UTCL2_CGTT_CLK_CTRL` defines clock-gating and test/override fields:

- `ON_DELAY`
- `OFF_HYSTERESIS`
- `SOFT_OVERRIDE_EXTRA`
- `MGLS_OVERRIDE`
- `SOFT_STALL_OVERRIDE`
- `SOFT_OVERRIDE`

`MC_SHARED_ACTIVE_FCN_ID` encodes a 4-bit `VFID` plus a high `VF` selector bit. `MC_VM_XGMI_GPUIOV_ENABLE` contains individual enable bits for VF0-VF15 and a PF enable bit at bit 31. These are virtualization and multi-GPU/XGMI integration fields; incorrect programming can expose or hide a function's memory view.

### PF/Shared Aperture and DRAM Controls

The `mmhub_utcl2_vmsharedpfdec` block defines masks for shared PF-side memory layout:

- `MC_VM_NB_MMIOBASE`, `MC_VM_NB_MMIOLIMIT`, `MC_VM_NB_PCI_CTRL`, and `MC_VM_NB_PCI_ARB` describe MMIO and VGA-hole behavior.
- `MC_VM_NB_TOP_OF_DRAM_SLOT1`, `MC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MC_VM_NB_UPPER_TOP_OF_DRAM2` describe top-of-DRAM boundaries.
- `MC_VM_FB_OFFSET` shifts framebuffer placement.
- `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB` encode the physical default page address split across low 32 bits and high 4 bits.
- `MC_VM_STEERING` selects default steering.
- `MC_SHARED_VIRT_RESET_REQ` exposes VF reset-request bits and a PF reset-request bit.
- `MC_MEM_POWER_LS` exposes light-sleep setup/hold timing.
- `MC_VM_CACHEABLE_DRAM_ADDRESS_START/END` and `MC_VM_LOCAL_HBM_ADDRESS_START/END` define address ranges.
- `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL__LOCK` locks the local HBM address range.
- `MC_VM_APT_CNTL` exposes `FORCE_MTYPE_UC` and `DIRECT_SYSTEM_EN`.
- `MC_VM_XGMI_LFB_CNTL` and `MC_VM_XGMI_LFB_SIZE` define PF local-framebuffer region and sizing.

Related MMHUB and GFXHUB generation code programs system aperture default addresses from `adev->mem_scratch.gpu_addr`, configures AGP/framebuffer aperture bounds, and skips or delegates some PF-only state under SR-IOV.

### Visible Client Aperture and L1 TLB Control

The `mmhub_utcl2_vmsharedvcdec` block defines visible/shared client memory aperture fields:

- `MC_VM_FB_LOCATION_BASE` and `MC_VM_FB_LOCATION_TOP` define framebuffer base/top fields.
- `MC_VM_AGP_TOP`, `MC_VM_AGP_BOT`, and `MC_VM_AGP_BASE` define the AGP aperture.
- `MC_VM_SYSTEM_APERTURE_LOW_ADDR` and `MC_VM_SYSTEM_APERTURE_HIGH_ADDR` define low/high logical aperture boundaries.
- `MC_VM_MX_L1_TLB_CNTL` controls the client-side L1 TLB.

`MC_VM_MX_L1_TLB_CNTL` is a high-value integration point. Its fields enable the L1 TLB, set system access mode, configure unmapped-access behavior, enable the advanced driver model, set ECO bits, choose memory type, and enable ATC. Same-family MMHUB code uses `REG_SET_FIELD` on this register while initializing and disabling the MMHUB L1 TLB.

### ATC L2 Performance Counters

The final address blocks define ATC L2 performance-counter results and controls:

- `ATC_L2_PERFCOUNTER_LO__COUNTER_LO`
- `ATC_L2_PERFCOUNTER_HI__COUNTER_HI` and `COMPARE_VALUE`
- `ATC_L2_PERFCOUNTER0_CFG` and `ATC_L2_PERFCOUNTER1_CFG`
- `ATC_L2_PERFCOUNTER_RSLT_CNTL`

The ATC L2 config layout mirrors the MC VM L2 performance-counter config: event selection, event range end, mode, enable, and clear bits. Result control provides selected counter, start/stop triggers, enable-any, clear-all, and stop-on-saturate fields.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution of symbolic shift/mask constants into driver code.

The implied runtime flow is:

1. A MMHUB 9.3.0-aware driver path selects a register offset from `mmhub_9_3_0_offset.h`.
2. The driver uses a matching shift/mask macro from this header, usually through `REG_SET_FIELD` or `REG_GET_FIELD`.
3. SOC15 register helpers compute the actual MMIO address and read, write, or read-modify-write the register.
4. MMHUB hardware applies the programmed VM aperture, translation, ATS, virtualization, power, clock, or performance-counter state.

The exact `mmhub_9_3_0` headers are not referenced by any C source found under `drivers/gpu/drm/amd` in this tree. The active related code paths are same-family MMHUB/GFXHUB implementations such as `mmhub_v3_0.c`, `mmhub_v3_0_1.c`, `mmhub_v3_0_2.c`, and `gfxhub_v3_0_3.c`, which use equivalent generated offset and sh/mask headers for their ASIC revisions.

## State and Persistence Behavior

The macros themselves are stateless. The persistent and volatile state represented by this chunk exists in hardware registers.

Persistent configuration state includes VM context start/end page bounds, per-VF framebuffer partitioning, MARC base/relocation/length windows, IOMMU enable state, PCIe ATS enablement, MMIO/DRAM/FB/AGP/system aperture ranges, default page address, local HBM range and lock state, XGMI local-framebuffer sizing, and L1 TLB policy.

Volatile or command-like state includes performance-counter enable/clear fields, result-control clear-all and stop-on-saturate bits, active VF/PF selection, virtual reset request bits, clock-gating overrides, and ATC/MC VM counter result values. Some fields may be sticky, write-one-to-clear, self-clearing, privileged-only, or reset by GPU reset, suspend/resume, firmware initialization, PF host policy, or clock/power-gating transitions. This generated header does not encode access permissions or side-effect semantics.

## Dependencies and Integration Points

This chunk depends on the generated MMHUB 9.3.0 register set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_3_0_offset.h` contains the matching offsets and base indices for registers named here.
- AMDGPU field helpers such as `REG_SET_FIELD` and `REG_GET_FIELD` depend on the exact `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK` naming convention.
- SOC15 MMIO helpers depend on the matching offset header and ASIC block instance to address the correct MMHUB register aperture.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mmhub_v3_0.c`, `mmhub_v3_0_1.c`, and `mmhub_v3_0_2.c` show the same integration pattern for VM context page-table registers, system aperture default address registers, and `MC_VM_MX_L1_TLB_CNTL`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/gfxhub_v3_0_3.c` shows a related graphics-hub integration pattern for framebuffer location, system aperture default address, and L1 TLB control fields.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/amdgpu_gmc.h` stores hub register addresses such as `MC_VM_MX_L1_TLB_CNTL` in `struct amdgpu_gmc`, showing that these fields are part of the broader GMC/VM setup surface.

Runtime integration areas include GART setup, VMID/context page-table aperture programming, system and AGP aperture setup, VRAM/framebuffer address discovery, default fault-page programming, MMHUB L1 TLB enable/disable, SR-IOV PF/VF framebuffer partitioning, PCIe ATS/ATC configuration, IOMMU/MARC configuration, XGMI GPUIOV enablement, performance monitoring, and reset/suspend/resume restoration.

## Risks and Edge Cases

- Generated-header drift is the main risk. A wrong shift or mask compiles cleanly but silently writes the wrong hardware bits.
- This chunk starts mid logical register family. `VM_CONTEXT0_PAGE_TABLE_START_ADDR_LO32` is in the previous chunk, while this chunk starts with the context-0 high mask and then continues contexts 1-15.
- Repeated register families are easy to mis-index. Context 0-15 aperture bounds, VF0-VF15 framebuffer fields, VF0-VF15 ATS controls, and MARC region 0-3 fields rely on stable naming and ordering.
- Address split assumptions matter. Several fields split page or physical addresses across low 32 bits and high 4 bits; using byte addresses instead of page numbers, or shifting by the wrong amount, corrupts apertures.
- SR-IOV fields are isolation-sensitive. VF framebuffer size/offset, active function ID, reset requests, ATS enable bits, and XGMI GPUIOV enable bits should follow PF/hypervisor policy.
- `MC_VM_MX_L1_TLB_CNTL` affects address translation behavior. Wrong settings for system access, unmapped access, memory type, advanced driver model, or ATC can cause page faults, stale translations, incorrect coherency, or hangs.
- MARC/IOMMU/ATS controls cross firmware, PCIe, and VM boundaries. Enabling or relocating windows in the wrong order can create invalid translations or access-permission bypasses.
- Clock-gating override fields may be needed for debug or bring-up but can affect power/performance if left forced.
- Performance-counter clear/enable/result-control fields are shared hardware resources. Profiling code must avoid racing other users and must respect counter saturation and clear semantics.
- The exact `mmhub_9_3_0` headers have no C consumer in this tree. If support is later wired in, build coverage should verify that the naming prefixes expected by new code match these generated macros.

## Test Signals

Useful validation is mostly generated-data consistency plus hardware integration:

- Build AMDGPU configurations after adding any consumer of `mmhub_9_3_0_sh_mask.h`; missing or renamed macros should fail at compile time.
- Mechanically compare every shift and mask in this line range against AMD's authoritative MMHUB 9.3.0 register database.
- Cross-check that every register family in this chunk has matching offsets in `mmhub_9_3_0_offset.h`, including base indices.
- Verify repeated families for expected counts and contiguous layout: 16 VM contexts, 16 VF framebuffer size/offset registers, 16 per-VF ATS controls, 4 MARC regions, 8 MC VM L2 performance-counter configs, and 2 ATC L2 performance-counter configs.
- Exercise MMHUB initialization on matching hardware or emulation: GART aperture programming, system aperture/default fault page setup, AGP/framebuffer aperture setup, and L1 TLB enable/disable.
- Exercise SR-IOV PF and VF configurations and check that framebuffer partitions, reset requests, ATS enablement, and GPUIOV function enables remain isolated and host-controlled where required.
- Run VM fault injection or invalid mapping tests and confirm that page-table aperture boundaries and default page handling behave as expected.
- Run ATS/ATC/IOMMU workloads with peer/device memory access and check for translation failures, stale translations, or unexpected permission faults.
- Run XGMI or multi-GPU memory tests where available, checking local-framebuffer region/size and GPUIOV enable behavior.
- Use register dumps or debugfs decoding to confirm that `REG_GET_FIELD` extracts sensible values for framebuffer base/top, AGP/system aperture ranges, L1 TLB control, VF framebuffer partitions, and performance-counter status.
- Run MMHUB and ATC performance-counter sampling, checking that event selection, enable/clear, start/stop triggers, compare value, and stop-on-saturate behavior match reference expectations.

## Cross-Chunk Notes

This is only the chunk research document for `subset-b-002834`. The final per-file research should merge this with neighboring chunks for full `mmhub_9_3_0_sh_mask.h` coverage. The previous chunk owns the preceding VM context base-address and context-0 start-low definitions. This chunk owns the file tail and closes the header with `#endif`.
