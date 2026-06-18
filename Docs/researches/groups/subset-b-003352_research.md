# subset-b-003352 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_4_2_sh_mask.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_4_2_sh_mask.h

### Purpose
`osssys_4_4_2_sh_mask.h` is an AMDGPU generated register bitfield contract for the OSSSYS 4.4.2 block. It defines `__SHIFT` and `_MASK` macros for interrupt handler (IH) and semaphore (SEM) registers so driver code can pack and unpack MMIO register fields without hard-coded bit positions. The file is data-only C preprocessor API: it has no functions, no executable control flow, and no runtime storage.

### Important APIs, Types, And Functions
The public surface is the macro namespace, grouped by register name. `IH_VMID_0_LUT` through `IH_VMID_15_LUT` and the `_MM` variants expose 16-bit PASID fields used to map IH VMIDs to process address spaces. `IH_COOKIE_0` through `IH_COOKIE_7` describe interrupt vector metadata fields: client ID, source ID, ring ID, VM ID, timestamp fragments, PASID, source selectors, and 128 bits of context ID. `IH_RB_CNTL`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_RPTR`, `IH_RB_WPTR`, writeback address, and doorbell macros describe the primary IH ring buffer, while `*_RING1` and `*_RING2` describe additional IH rings.

Later groups cover diagnostic and control registers: `IH_VERSION`, `IH_CNTL`, `IH_CNTL2`, `IH_STATUS`, `IH_PERFMON_CNTL`, perf counter results, DSM match registers, interrupt-rate limiting, VF ring status, interrupt flood/drop status, storm client masks, clock and memory power controls, client credit/error status, GPU IOV and cookie violation logs, retry interrupt CAM control, active function/virtual reset state, client configuration, client-ID remap tables, chicken bits, interrupt-drop match values/masks, and MMHUB control. SEM coverage is narrower in this header, with mailbox and last-register marker bitfields.

### Control Flow
There is no runtime control flow in the header. The effective flow appears in consumers that combine this header with an offset header and register helpers. Typical AMDGPU code reads a register, applies `REG_SET_FIELD(value, REG, FIELD, new_value)` or masks directly, then writes the register back via `WREG32`, `WREG32_SOC15`, or PSP-mediated register programming under SR-IOV. For example, IH setup code uses ring-buffer field macros to set `RB_ENABLE`, `RB_SIZE`, `WPTR_WRITEBACK_ENABLE`, `MC_SPACE`, `MC_VMID`, `RPTR_REARM`, and overflow-clear bits before enabling interrupt delivery.

### State, Persistence, And Dependencies
The header itself has no state and persists nothing. Its values encode hardware state layout: writes using these masks persist in GPU MMIO registers until reset, power management, firmware, or later driver writes change them. The file depends only on inclusion order and C preprocessor visibility, but it is intended to be paired with `oss/osssys_4_4_2_offset.h` and AMDGPU helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `SOC15_REG_OFFSET`, and low-level MMIO accessors. The include guard `_osssys_4_4_2_SH_MASK_HEADER` prevents duplicate macro definition in one translation unit.

### Dependencies
The critical dependency is agreement with the corresponding hardware register specification for OSSSYS 4.4.2. Driver sources such as `amdgpu_amdkfd_gc_9_4_3.c` include this file alongside GC, ATHUB, SDMA, and OSSSYS offset headers for GFX 9.4.3/Aldebaran-style KFD paths. Cross-generation headers reuse many names, so consumers rely on selecting the matching `*_offset.h` and `*_sh_mask.h` pair for the active IP version. The macros also depend on fixed-width 32-bit register semantics even though they are expressed as unsuffixed or `L`-suffixed constants.

### Integration Points
This header integrates with AMDGPU interrupt handling, KFD process scheduling, SR-IOV virtualization, and GPU fault reporting. IH ring fields are consumed by interrupt ring initialization and enable/disable paths. Cookie and last-interrupt fields align with `amdgpu_iv_entry` parsing, where client, source, VMID, PASID, and context metadata become software interrupt records. VF status, active function, virtual reset, and IOV violation fields support virtualization isolation and diagnostics. Client configuration and remap fields connect IH clients to ring selection, function identity, credit return, and client ID translation.

### Risks
The main risk is silent hardware misprogramming: a wrong bit position can enable the wrong ring behavior, break write-pointer writeback, corrupt PASID attribution, or hide overflow/flood conditions. Cross-generation similarity is risky because OSSSYS 4.4.2 fields differ from nearby 5.x/6.x headers in places such as client configuration and retry CAM naming; including a mismatched header can still compile while targeting incorrect hardware layout. Reserved fields should not be written casually, especially around cookie metadata, clock/power controls, and chicken bits. Multi-bit fields require callers to shift values through helpers rather than ORing unbounded values into masks.

### Test Signals
Compile coverage is the first signal: all translation units selecting OSSSYS 4.4.2 should build with no undefined register-field macros. Register-programming tests should confirm IH ring initialization writes expected `IH_RB_CNTL*`, base, read/write pointer, writeback, and doorbell values on supported devices. Interrupt validation should cover normal IV delivery, PASID/VMID attribution, timestamp/context propagation, overflow clearing, and ring1/ring2 behavior. Virtualization tests should exercise VF ring status, active function, virtual reset, IOV violation logging, and PSP indirect register programming. Hardware bring-up or register-dump comparison against AMD reference tables is the strongest regression signal for this generated contract.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_4_4_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_5_0_0_offset.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_5_0_0_offset.h

### Purpose
`osssys_5_0_0_offset.h` is the generated MMIO register offset map for the AMD OSSSYS 5.0.0 block, whose comments identify the `osssys_osssysdec` address block with base address `0x4280`. It gives each IH and SEM register a `mm...` macro containing the register index within the SOC15 OSSSYS block and a matching `mm..._BASE_IDX` macro, almost always `0`. Driver code combines these offsets with SOC15 address translation helpers to access the right hardware register.

### Important APIs, Types, And Functions
The API is entirely preprocessor macros. The file maps `mmIH_VMID_0_LUT` through `mmIH_VMID_15_LUT` at offsets `0x0000` to `0x000f`, then MM variants at `0x0010` to `0x001f`, interrupt cookie registers at `0x0020` to `0x0027`, and early partition markers. IH ring 0 starts at `mmIH_RB_CNTL` `0x0080` and includes base, base high, read pointer, write pointer, writeback address, and doorbell read pointer registers. Ring 1 starts at `0x008c`; ring 2 starts at `0x0098`. Global IH control/status/perf/DSM/rate-limit/VF/flood/clock/diagnostic/memory-power registers occupy the `0x00a5` and `0x00c0` to `0x00ff` ranges.

The SEM block begins at `mmSEM_CLK_CTRL` `0x0100` and includes UTC credit/configuration, translation-enable LUT, MCIF config, perf monitor/counters, status, mailbox and mailbox control/configuration, chicken bits, IOV violation logs, outstanding thresholds, and memory power control through `0x017f`. The virtualization and client-management region maps IH active function, reset request, client configuration/index/data, CID remap, chicken, MMHUB, and interrupt-drop registers from `0x0180` through `0x019f`, followed by SEM active function, reset, response registers, SEM CID remap, atomic op LUT, EDC config, chicken bits 2, MMHUB control, and final markers through `0x01bf`.

### Control Flow
There is no control flow in this header. Its offsets become executable behavior in consumers through access macros such as `SOC15_REG_OFFSET(OSSSYS, 0, mmIH_RB_CNTL)`, `RREG32_SOC15(OSSSYS, 0, mmIH_CNTL2)`, and `WREG32_SOC15(OSSSYS, 0, mmIH_RB_CNTL_RING1, value)`. `navi10_ih.c` uses these macros to populate `amdgpu_ih_regs` for ring0, ring1, and ring2, toggle ring interrupts, set write-pointer update behavior, and program ring pointers. `gmc_v10_0.c` includes this map for GFX10-era interrupt/fault integration.

### State, Persistence, And Dependencies
The header carries no state. The offsets are a static address contract; persistent effects occur only when driver code writes to the corresponding MMIO locations. It depends on the SOC15 register addressing model, the OSSSYS IP block instance selected by consumers, and the matching `oss/osssys_5_0_0_sh_mask.h` bitfield header for value packing. The include guard `_osssys_5_0_0_OFFSET_HEADER` prevents duplicate macro expansion.

### Dependencies
Correctness depends on the generated table matching the OSSSYS 5.0.0 hardware and firmware-visible register layout. AMDGPU consumers include this file with `soc15.h`, `soc15_common.h`, and IP-specific modules such as `navi10_ih.c`, `amdgpu_amdkfd_gfx_v10.c`, `amdgpu_amdkfd_gfx_v10_3.c`, and `gmc_v10_0.c`. `*_BASE_IDX` fields are part of the AMD register header convention; consumers that address alternate register bases or instances rely on these values remaining consistent with SOC15 translation tables.

### Integration Points
The strongest integration point is IH setup for Navi/GFX10 devices. The header tells AMDGPU where each IH ring control register, base register, read/write pointer, writeback address, and doorbell register lives. It also supports self-interrupt write-pointer update configuration through `mmIH_CNTL2`, rate/flood diagnostics, VF status tracking, and interrupt drop filtering. KFD integration uses OSSSYS offsets when configuring GFX10 process/queue behavior and interrupt metadata. GMC fault handling includes this offset map as part of the GFX10 register universe used to decode and route VM fault interrupts.

### Risks
Offset mistakes are high impact because register names remain valid at compile time while the driver reads or writes the wrong hardware location. The ring spacing differs across generations, so using a 4.x offset header with 5.0.0 masks, or vice versa, can misconfigure ring1/ring2 without compiler errors. Some registers are diagnostics or write-one-to-clear controls; accidental writes through an incorrect offset can clear useful fault evidence or change interrupt-drop behavior. The fixed base index of `0` should not be assumed for future blocks without checking the matching generated table.

### Test Signals
Build tests should confirm GFX10/Navi and KFD translation units compile with all `mm...` names resolved. Runtime register-dump tests should verify that `SOC15_REG_OFFSET(OSSSYS, 0, mmIH_RB_CNTL*)` maps to the documented ring-control addresses and that ring0/ring1/ring2 initialization touches the expected locations. Interrupt tests should validate ring enable/disable, read/write pointer movement, doorbell read pointer handling, overflow clearing, and write-pointer writeback. Fault and virtualization tests should cover VM fault interrupt delivery, VF ring status registers, active function/reset registers, SEM mailbox behavior, and interrupt-drop/flood diagnostics on supported hardware or emulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_5_0_0_offset.h -->
