# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_offset.h lines 7452-7789

## Scope

This chunk is the tail of the generated AMD MMHUB 9.4.1 register-offset header. It contains only C preprocessor register-address macros and `_BASE_IDX` companion macros; there are no functions, structs, enums, or executable control-flow statements in the chunk. The covered range closes the `mmhub_utcl2_vml2vcdec:1` VM-context address block, then defines instance-1 shared PF/VC/HV MMHUB aperture and virtualization registers, ATC L2 and VM L2 performance-counter registers, and finally the header guard terminator.

The header is included by `drivers/gpu/drm/amd/amdgpu/mmhub_v9_4.c` along with the matching `mmhub_9_4_1_sh_mask.h` and `mmhub_9_4_1_default.h` files. The offset macros are the symbolic register numbers passed to AMDGPU/SOC15 access helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15_OFFSET()`, and `WREG32_SOC15_OFFSET()`.

## Purpose

The purpose of this chunk is to publish the hardware register map for the second MMHUB instance's VM-facing address blocks on MMHUB 9.4.1 ASICs. Each `mm...` macro gives the register index within the SOC15 MMHUB register space, and each `_BASE_IDX` macro selects base-index `1` for the SOC15 register lookup tables. Driver code can then address the register either directly by the instance-1 symbol or by using an instance-0 symbol plus `MMHUB_INSTANCE_REGISTER_OFFSET` when programming both hubs.

The range is important to GPU memory-management setup because it names registers for:

- VM context page-table start and end bounds for `VML2VC1`.
- Shared PF-visible aperture, default page, DRAM/HBM, XGMI, and reset controls for `VMSHAREDPF1`.
- Shared VC-visible framebuffer, AGP, system aperture, and L1 TLB control for `VMSHAREDVC1`.
- Hypervisor/SR-IOV controls for per-VF framebuffer partitioning, MARC regions, IOMMU/ATS, active function selection, clock gating, and XGMI GPUIOV enables for `VMSHAREDHV1`.
- ATC L2 and VM L2 performance-counter programming and result registers for instance 1.

## Register Groups

### VML2VC1 page-table address bounds

The first part of the chunk continues the `mmhub_utcl2_vml2vcdec:1` address block. It starts mid-series at `mmVML2VC1_VM_CONTEXT9_PAGE_TABLE_START_ADDR_HI32` and then defines start-address low/high pairs for contexts 10 through 15:

- `mmVML2VC1_VM_CONTEXT9_PAGE_TABLE_START_ADDR_HI32` at `0x3a9e`.
- `mmVML2VC1_VM_CONTEXT10_PAGE_TABLE_START_ADDR_LO32` through `mmVML2VC1_VM_CONTEXT15_PAGE_TABLE_START_ADDR_HI32`, covering offsets `0x3a9f` through `0x3aaa`.

It then defines page-table end-address low/high pairs for VM contexts 0 through 15:

- `mmVML2VC1_VM_CONTEXT0_PAGE_TABLE_END_ADDR_LO32` and `_HI32` at `0x3aab` and `0x3aac`.
- Sequential pairs through `mmVML2VC1_VM_CONTEXT15_PAGE_TABLE_END_ADDR_LO32` and `_HI32` at `0x3ac9` and `0x3aca`.

The matching shift/mask header identifies the LO32 fields as `LOGICAL_PAGE_NUMBER_LO32` and the HI32 fields as `LOGICAL_PAGE_NUMBER_HI4`. The matching default header initializes these start/end bounds to zero. In `mmhub_v9_4.c`, the driver primarily uses the instance-0 `VML2VC0` names plus `hubid * MMHUB_INSTANCE_REGISTER_OFFSET` and per-context distances to program both MMHUB instances, so these `VML2VC1` names are the generated direct-address aliases for the same second-instance hardware window.

### VMSHAREDPF1 shared PF controls

The `mmhub_utcl2_vmsharedpfdec:1` block begins at source line 7543 with base address comment `0x76b90`. This group defines offsets `0x3ae4` through `0x3af9`:

- Northbridge/MMIO and PCI aperture controls: `MC_VM_NB_MMIOBASE`, `MC_VM_NB_MMIOLIMIT`, `MC_VM_NB_PCI_CTRL`, `MC_VM_NB_PCI_ARB`, `MC_VM_NB_TOP_OF_DRAM_SLOT1`, `MC_VM_NB_LOWER_TOP_OF_DRAM2`, and `MC_VM_NB_UPPER_TOP_OF_DRAM2`.
- Framebuffer and default-page controls: `MC_VM_FB_OFFSET`, `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB`, and `MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_MSB`.
- Routing, reset, and low-power controls: `MC_VM_STEERING`, `MC_SHARED_VIRT_RESET_REQ`, and `MC_MEM_POWER_LS`.
- Aperture and locality controls: `MC_VM_CACHEABLE_DRAM_ADDRESS_START`, `MC_VM_CACHEABLE_DRAM_ADDRESS_END`, `MC_VM_APT_CNTL`, `MC_VM_LOCAL_HBM_ADDRESS_START`, `MC_VM_LOCAL_HBM_ADDRESS_END`, and `MC_VM_LOCAL_HBM_ADDRESS_LOCK_CNTL`.
- XGMI and cacheable-DRAM controls: `MC_VM_XGMI_LFB_CNTL`, `MC_VM_XGMI_LFB_SIZE`, and `MC_VM_CACHEABLE_DRAM_CNTL`.

The paired mask header shows these registers carry MMIO base/limit fields, MMIO enable, VGA-hole, top-of-memory, physical page-number pieces for the system aperture default address, default steering, PF/VF reset request bits, local HBM start/end windows, lock state, PF XGMI local-framebuffer region/size, and cacheable-DRAM aperture enable. The paired default header sets most to zero, with notable non-zero defaults including `MC_VM_NB_PCI_ARB_DEFAULT` (`0x00000008`), `MC_VM_STEERING_DEFAULT` (`0x00000001`), `MC_MEM_POWER_LS_DEFAULT` (`0x00000208`), and `MC_VM_LOCAL_HBM_ADDRESS_END_DEFAULT` (`0x000fffff`).

`mmhub_v9_4_init_system_aperture_regs()` programs the analogous instance-0 PF default-address registers using `mmVMSHAREDPF0_MC_VM_SYSTEM_APERTURE_DEFAULT_ADDR_LSB/MSB` plus a hub offset. This chunk's `PF1` definitions are therefore part of the same register map for the second MMHUB instance and must stay numerically aligned with the PF0 stride scheme.

### VMSHAREDVC1 shared VC aperture and TLB controls

The `mmhub_utcl2_vmsharedvcdec:1` block has base address comment `0x76c00` and defines offsets `0x3b00` through `0x3b07`:

- `mmVMSHAREDVC1_MC_VM_FB_LOCATION_BASE` and `_TOP` for framebuffer location discovery.
- `mmVMSHAREDVC1_MC_VM_AGP_TOP`, `_BOT`, and `_BASE` for AGP aperture programming.
- `mmVMSHAREDVC1_MC_VM_SYSTEM_APERTURE_LOW_ADDR` and `_HIGH_ADDR` for logical system aperture bounds.
- `mmVMSHAREDVC1_MC_VM_MX_L1_TLB_CNTL` for the L1 TLB, advanced driver model, memory type, and ATC enable bits.

The shift/mask header gives `FB_BASE`, `FB_TOP`, `AGP_TOP`, `AGP_BOT`, `AGP_BASE`, logical low/high aperture fields, and TLB fields such as `ENABLE_L1_TLB`, `SYSTEM_ACCESS_MODE`, `SYSTEM_APERTURE_UNMAPPED_ACCESS`, `ENABLE_ADVANCED_DRIVER_MODEL`, `MTYPE`, and `ATC_EN`. The default header sets `MC_VM_MX_L1_TLB_CNTL_DEFAULT` to `0x00002501`.

`mmhub_v9_4_get_fb_location()` reads `VMSHAREDVC0` framebuffer base/top for MMHUB0. `mmhub_v9_4_init_system_aperture_regs()` and `mmhub_v9_4_init_tlb_regs()` write the corresponding VC registers using `mmVMSHAREDVC0...` plus a per-hub offset. These `VMSHAREDVC1` direct names represent the second instance's same register family and are coupled to the constant `MMHUB_INSTANCE_REGISTER_OFFSET` used by that code.

### VMSHAREDHV1 virtualization, IOMMU, ATS, and XGMI controls

The `mmhub_utcl2_vmsharedhvdec:1` block has base address comment `0x76c80` and defines offsets `0x3b20` through `0x3b5e`. It is the largest group in this chunk.

The first sixteen registers, `mmVMSHAREDHV1_MC_VM_FB_SIZE_OFFSET_VF0` through `_VF15`, provide per-virtual-function framebuffer size and offset control. The mask header shows each packs `VF_FB_SIZE` in the low 16 bits and `VF_FB_OFFSET` in the high 16 bits. These fields are central to SR-IOV framebuffer partitioning because a bad size/offset pair would map a VF to the wrong physical VRAM window.

The next register, `mmVMSHAREDHV1_VM_IOMMU_MMIO_CNTRL_1`, is followed by four MARC region groups:

- `MC_VM_MARC_BASE_LO_0` through `_3`.
- `MC_VM_MARC_BASE_HI_0` through `_3`.
- `MC_VM_MARC_RELOC_LO_0` through `_3`.
- `MC_VM_MARC_RELOC_HI_0` through `_3`.
- `MC_VM_MARC_LEN_LO_0` through `_3`.
- `MC_VM_MARC_LEN_HI_0` through `_3`.

These define up to four memory address relocation/control regions with split low/high base, relocation, and length fields. The paired defaults are all zero for the MARC registers.

The block then defines IOMMU and PCIe ATS controls:

- `mmVMSHAREDHV1_VM_IOMMU_CONTROL_REGISTER`.
- `mmVMSHAREDHV1_VM_IOMMU_PERFORMANCE_OPTIMIZATION_CONTROL_REGISTER`.
- `mmVMSHAREDHV1_VM_PCIE_ATS_CNTL`.
- `mmVMSHAREDHV1_VM_PCIE_ATS_CNTL_VF_0` through `_VF_15`.

The per-VF ATS offsets are contiguous from `0x3b4c` through `0x3b5b`, which makes them suitable for indexed programming if the caller uses the generated stride correctly. The default header initializes the ATS registers to zero.

The block ends with:

- `mmVMSHAREDHV1_UTCL2_CGTT_CLK_CTRL` at `0x3b5c`, default `0x00000080`.
- `mmVMSHAREDHV1_MC_SHARED_ACTIVE_FCN_ID` at `0x3b5d`.
- `mmVMSHAREDHV1_MC_VM_XGMI_GPUIOV_ENABLE` at `0x3b5e`.

The mask header indicates `MC_VM_XGMI_GPUIOV_ENABLE` has enable bits for VF0 through VF15 plus an `ENABLE_PF` bit at bit 31. This ties the block into multi-function and XGMI GPU I/O virtualization behavior.

### ATC L2 performance counters

The `mmhub_utcl2_atcl2pfcntrdec:1` block at base address comment `0x76dc0` defines result registers:

- `mmATCL2PFCNTR1_ATC_L2_PERFCOUNTER_LO` at `0x3b70`.
- `mmATCL2PFCNTR1_ATC_L2_PERFCOUNTER_HI` at `0x3b71`.

The `HI` register includes both counter high bits and a compare-value field in the mask header. These registers are paired with the control block below.

The `mmhub_utcl2_atcl2pfcntldec:1` block at base address comment `0x76dd0` defines:

- `mmATCL2PFCNTL1_ATC_L2_PERFCOUNTER0_CFG` at `0x3b74`.
- `mmATCL2PFCNTL1_ATC_L2_PERFCOUNTER1_CFG` at `0x3b75`.
- `mmATCL2PFCNTL1_ATC_L2_PERFCOUNTER_RSLT_CNTL` at `0x3b76`.

The mask header gives each config register `PERF_SEL`, `PERF_SEL_END`, `PERF_MODE`, `ENABLE`, and `CLEAR` fields. The result-control register selects the counter and trigger behavior, with `ENABLE_ANY`, `CLEAR_ALL`, and `STOP_ALL_ON_SATURATE`. The default result-control value is `0x04000000`, corresponding to the stop-on-saturate default bit in the paired mask definitions.

### VM L2 performance counters

The `mmhub_utcl2_vml2pldec:1` block at base address comment `0x76e00` defines eight VM L2 performance-counter configuration registers:

- `mmVML2PL1_MC_VM_L2_PERFCOUNTER0_CFG` through `_7_CFG`, offsets `0x3b80` through `0x3b87`.
- `mmVML2PL1_MC_VM_L2_PERFCOUNTER_RSLT_CNTL` at `0x3b88`.

The config fields mirror the ATC L2 counter config pattern: select range, mode, enable, and clear. The result-control register similarly selects a counter, start/stop triggers, global enable, clear-all, and stop-on-saturate behavior. Its default is also `0x04000000`.

The `mmhub_utcl2_vml2prdec:1` block at base address comment `0x76e40` defines the VM L2 performance-counter result pair:

- `mmVML2PR1_MC_VM_L2_PERFCOUNTER_LO` at `0x3b90`.
- `mmVML2PR1_MC_VM_L2_PERFCOUNTER_HI` at `0x3b91`.

The low register is the 32-bit counter low field. The high register carries a 16-bit high counter field plus a 16-bit compare-value field. These registers are observability hooks rather than core VM setup knobs.

## APIs, Types, and Macros

There are no runtime APIs or C types declared in this chunk. The exported interface is the macro namespace itself:

- `mm<register>` macros are integer register offsets.
- `mm<register>_BASE_IDX` macros are all `1`, selecting the MMHUB base-index table used by SOC15 register accessors.
- The symbols depend on the companion `mmhub_9_4_1_sh_mask.h` field macros for safe bit manipulation through `REG_SET_FIELD()` and on `mmhub_9_4_1_default.h` reset values where driver code wants a known hardware default.

The integration API is indirect: callers pass these constants to AMDGPU register helpers such as `SOC15_REG_OFFSET(MMHUB, instance, reg)`, `RREG32_SOC15_OFFSET(MMHUB, instance, reg, offset)`, and `WREG32_SOC15_OFFSET(MMHUB, instance, reg, offset, value)`.

## Control Flow

This chunk has no local control flow. Runtime sequencing lives in `mmhub_v9_4.c`:

- `mmhub_v9_4_init()` computes VM hub register addresses and register distances from generated offsets.
- `mmhub_v9_4_gart_enable()` iterates over `MMHUB_NUM_INSTANCES` and programs GART, system aperture, TLB, cache, snoop override, VM context, and invalidation registers.
- `mmhub_v9_4_init_system_aperture_regs()` writes shared VC and PF aperture/default-address registers for each hub.
- `mmhub_v9_4_init_tlb_regs()` writes shared VC L1 TLB control.
- `mmhub_v9_4_setup_vmid_config()` writes VM-context start/end ranges for VMIDs using context address distances.

The direct `...1` symbols in this chunk are generated aliases for instance-1 registers, while much of the current setup code addresses instance 1 by taking the `...0` symbol and adding `MMHUB_INSTANCE_REGISTER_OFFSET`. This means the numerical spacing between the instance-0 and instance-1 definitions is part of the driver's implicit control-flow contract.

## State and Persistence

The chunk itself has no memory allocation, persistence, or software state. It defines hardware state locations. Values written to these registers persist in MMHUB hardware until changed by the driver, reset by the device, or affected by power-management/virtualization transitions.

The most stateful hardware areas represented here are:

- VM context page-table start/end bounds, which gate GPU virtual-address validity.
- Shared aperture registers, which define framebuffer, AGP, and system logical windows.
- PF default-page physical addresses and protection behavior, which determine fault redirection behavior.
- HV/SR-IOV framebuffer size/offset and ATS controls, which partition and translate memory for VFs.
- Performance-counter config/result registers, which retain counter selections, enable states, clear requests, and sampled counts until reprogrammed.

Defaults are documented in `mmhub_9_4_1_default.h`, but driver initialization actively overwrites many aperture/TLB/VM registers from `adev->gmc`, `adev->vm_manager`, and other runtime device state.

## Dependencies and Integration Points

Primary dependencies:

- SOC15 register access infrastructure in AMDGPU (`RREG32_SOC15*`, `WREG32_SOC15*`, `SOC15_REG_OFFSET`).
- `mmhub_9_4_1_sh_mask.h` for field-level masks and shifts.
- `mmhub_9_4_1_default.h` for reset/default values.
- `amdgpu_vmhub` fields such as `ctx_distance`, `ctx_addr_distance`, and invalidation-engine distances, which are derived from adjacent generated offsets.
- Runtime GPU memory-management state in `adev->gmc`, `adev->vm_manager`, `adev->gart`, `adev->mem_scratch`, and SR-IOV state from `amdgpu_sriov_vf(adev)`.

Important integration points:

- GART setup depends on correct VM page-table base/start/end offsets.
- VMID configuration depends on the context address stride matching the generated register layout.
- System aperture setup depends on shared VC/PF register offsets and the same second-instance stride represented by the `...1` macros.
- SR-IOV and XGMI virtualization code can use the HV registers in this chunk for VF framebuffer slicing, active-function targeting, ATS control, and XGMI GPUIOV enablement.
- Performance tooling can program the ATC L2 and VM L2 perf-counter config/result registers to observe translation and cache behavior.

## Risks and Edge Cases

- Offset drift is high impact. These macros are generated hardware ABI constants; an incorrect value can make the driver read or write a different MMHUB register without compile-time errors.
- Instance alignment is critical. `mmhub_v9_4.c` uses `MMHUB_INSTANCE_REGISTER_OFFSET` (`0x3000`) with instance-0 symbols to reach the second hub. The direct instance-1 offsets in this chunk must remain consistent with that addressing model.
- Context-bound writes must preserve 64-bit page-number splitting. LO32 and HI32 page-table range registers encode low 32 bits plus a high 4-bit field; callers must continue to shift GPU addresses consistently before writing.
- SR-IOV partitioning errors can cross isolation boundaries. The per-VF `FB_SIZE_OFFSET`, ATS, active-function, and XGMI GPUIOV registers are security-sensitive because they define which VF can access which memory and interconnect resources.
- Default zero values do not imply safe runtime configuration. Many aperture and virtualization registers reset to zero but need explicit programming from device topology and memory layout before normal GPU VM operation.
- Performance-counter registers may be shared diagnostic state. Counter config, clear, and result-control writes can perturb concurrent observability or debug tooling if not serialized at a higher layer.
- The header closes with `#endif`; missing or duplicate guard closure would affect every include site, but this generated file currently has a conventional guard around the whole offset namespace.

## Test Signals

Useful validation signals for this chunk are mostly build-time, register-map consistency, and hardware bring-up checks:

- The AMDGPU driver compiles with `mmhub_v9_4.c` including `mmhub_9_4_1_offset.h`, `_sh_mask.h`, and `_default.h` together.
- Static checks confirm every `mm...` symbol in this chunk has a matching `_BASE_IDX`, and corresponding `_DEFAULT` and shift/mask definitions where applicable.
- Register spacing checks confirm context start/end pairs are contiguous, per-VF arrays are contiguous, and instance-1 offsets remain reachable through the instance-0 symbol plus `MMHUB_INSTANCE_REGISTER_OFFSET`.
- Runtime GART enable succeeds without VM fault storms, GPU page faults resolve to the expected default/dummy page when configured, and `adev->gmc.fb_start/fb_end`, AGP aperture, and system aperture values match hardware expectations.
- SR-IOV validation should verify VF framebuffer windows, ATS enablement, active function selection, and XGMI GPUIOV enable bits under PF and VF modes.
- Performance-counter smoke tests should be able to program ATC L2 and VM L2 counter config registers, clear counters, enable counting, and read non-stuck LO/HI results under translation traffic.
