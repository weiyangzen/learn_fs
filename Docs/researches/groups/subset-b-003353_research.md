# subset-b-003353 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_5_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_5_0_0_sh_mask.h

## Purpose

`osssys_5_0_0_sh_mask.h` is a generated AMDGPU ASIC register bitfield contract for the OSSSYS 5.0.0 address block. It does not implement executable logic; it gives C preprocessor names for register field shifts and masks used by SOC15-era AMD GPU kernel code when programming the interrupt handler (IH) and semaphore/mailbox (SEM) portions of OSSSYS.

The file is guarded by `_osssys_5_0_0_SH_MASK_HEADER` and is paired with the corresponding offset header, normally `oss/osssys_5_0_0_offset.h`, so driver code can combine an address macro such as `mmIH_RB_CNTL` with field macros such as `IH_RB_CNTL__RB_ENABLE_MASK` or the `REG_SET_FIELD(..., IH_RB_CNTL, RB_ENABLE, ...)` helper expansion. This header is used by Navi/GFX10 code paths, including `amdgpu/navi10_ih.c`, `amdgpu/amdgpu_amdkfd_gfx_v10.c`, and `amdgpu/amdgpu_amdkfd_gfx_v10_3.c`.

## Important APIs, Types, and Definitions

The exported surface is entirely macro definitions. The most important groups are:

- `IH_VMID_0_LUT` through `IH_VMID_15_LUT` and matching `_MM` variants, each exposing a 16-bit `PASID` field. KFD/GMC code writes these registers to map VMIDs to PASIDs for interrupt attribution and VM fault handling.
- `IH_COOKIE_0` through `IH_COOKIE_7`, which describe the interrupt vector cookie format: client ID, source ID, ring ID, VM ID, timestamp, PASID, and 128-bit context ID slices.
- `IH_RB_CNTL`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_RPTR`, `IH_RB_WPTR`, writeback address, and `IH_DOORBELL_RPTR` fields for the primary IH ring buffer. These define enable state, ring size, timestamp enable, write pointer writeback, overflow handling, interrupt enable, memory controller address-space selection, VMID, snoop/read-only attributes, doorbell read-pointer offset, and doorbell enable bits.
- `IH_RB_*_RING1` and `IH_RB_*_RING2` mirrors for secondary IH rings. Navi10 uses up to three IH rings and programs each through `amdgpu_ih_regs`.
- `IH_CNTL`, `IH_CNTL2`, `IH_STATUS`, and `IH_VERSION` for global IH control, self-interrupt write-pointer force update, idle/full/overflow status, and version reporting.
- `IH_PERFMON_CNTL` and `IH_PERFCOUNTER*_RESULT` for two IH performance counters.
- `IH_DSM_MATCH_*`, `IH_LIMIT_INT_RATE_CNTL`, `IH_INT_FLOOD_*`, `IH_STORM_CLIENT_LIST_CNTL`, `IH_MSI_STORM_*`, and `IH_INT_DROP_*` for interrupt filtering, rate limiting, storm detection, and drop/match handling.
- `IH_LAST_INT_INFO*`, `IH_CLIENT_CREDIT_ERROR`, `IH_CREDIT_STATUS`, `IH_MMHUB_ERROR`, `IH_COOKIE_REC_VIOLATION_LOG`, and GPU IOV violation log fields for diagnostics and virtualization fault reporting.
- `IH_CLIENT_CFG`, `IH_CLIENT_CFG_INDEX`, `IH_CLIENT_CFG_DATA`, ring1 client config, and `IH_CID_REMAP_*` for client table programming, credit return routing, ring selection, active function ID behavior, and client ID remapping.
- `IH_CHICKEN`, `IH_ACTIVE_FCN_ID`, and `IH_VIRT_RESET_REQ` for feature workarounds, SR-IOV function selection/protection, register firewall behavior, and virtual reset request state.
- SEM macros including `SEM_REQ_INPUT_*`, clock/power controls, UTC/UTCL2 configuration, MC interface credits, SEM perf counters, SEM status, mailbox client configuration, mailbox/control, SEM chicken bits, SEM IOV violation logs, active function/reset request, response address tables, CID remap, atomic operation LUT, EDC config, and MMHUB controls.

There are no structs, functions, enums, or storage definitions in this file. Consumers rely on the naming convention `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`, and on AMDGPU helpers that synthesize those names from `REG_SET_FIELD` and `REG_GET_FIELD`.

## Control Flow

This header has no runtime control flow. Its control-flow significance appears in consuming drivers:

- `navi10_ih_init_register_offset()` binds IH ring slots to OSSSYS register offsets from the matching offset header, while this mask header supplies the bit layout for later updates.
- `navi10_ih_rb_cntl()` constructs `IH_RB_CNTL` values by setting `MC_SPACE`, `WPTR_OVERFLOW_CLEAR`, `WPTR_OVERFLOW_ENABLE`, `RB_SIZE`, `WPTR_WRITEBACK_ENABLE`, `MC_SNOOP`, `MC_RO`, and `MC_VMID`.
- `navi10_ih_toggle_ring_interrupts()` sets `RB_ENABLE`, `RB_GPU_TS_ENABLE`, and ring0-only `ENABLE_INTR`; disable paths clear software state and hardware read/write pointers.
- `navi10_ih_get_wptr()` tests `IH_RB_WPTR.RB_OVERFLOW`, masks the write pointer with the ring pointer mask, and toggles `IH_RB_CNTL.WPTR_OVERFLOW_CLEAR` to acknowledge overflow.
- `force_update_wptr_for_self_int()` programs `IH_CNTL2.SELF_IV_FORCE_WPTR_UPDATE_*` and ring1/ring2 `RB_USED_INT_THRESHOLD` for self-interrupt write pointer propagation.
- KFD/GMC paths write `IH_VMID_0_LUT + vmid` and sometimes `IH_VMID_0_LUT_MM + vmid` so interrupt and page-fault records can be associated with the active process address-space ID.

Because the C preprocessor expands these macros at build time, any field mismatch immediately changes the bit patterns written to hardware rather than changing ordinary branch behavior.

## State and Persistence Behavior

The header itself is stateless and persistent only as source code. The hardware state described by it is persistent across driver-managed initialization, suspend/resume, reset, and SR-IOV transitions until registers are reprogrammed by the kernel or firmware.

Key state domains represented by the macros are:

- IH ring state: base GPU address, high address bits, ring size, read/write pointer registers, write pointer writeback memory address, doorbell read-pointer control, enable state, overflow latch/clear bits, and interrupt enable.
- Interrupt attribution state: VMID-to-PASID LUTs, cookies, last interrupt information, active function ID, VF/PF identifiers, and context ID slices.
- Throttling/filtering state: flood control high-water settings, storm client bits, MSI storm client index/data registers, interrupt drop match values/masks, and rate-limit counters.
- Virtualization and diagnostics state: IOV violation logs, cookie recognition violation logs, credit error/status bits, MMHUB error bits, and VF ring full/overflow status masks.
- SEM state: mailbox pending/enable bits, mailbox client routing, UTC/UTCL2 enablement, MC request credits, memory power state, response address lookup tables, atomic op lookup fields, and SEM idle/fault indicators.

Consumers must manage ordering and acknowledgment semantics. For example, overflow clear bits are written as a 0-to-1 transition and then returned to 0 so future overflow latches can be detected. Doorbell and writeback fields must match memory allocations and doorbell range programming, or interrupt processing loses synchronization.

## Dependencies and Integration Points

This header depends only on inclusion order and macro naming conventions; it includes no other headers. It integrates with:

- `oss/osssys_5_0_0_offset.h`, which supplies the `mm...` register offsets used with these masks.
- `soc15_common.h` and AMDGPU register helper macros such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, `REG_SET_FIELD`, and `REG_GET_FIELD`.
- `amdgpu_ih` ring management, where `amdgpu_ih_ring` and `amdgpu_ih_regs` store runtime ring buffer, writeback, doorbell, and offset state.
- PSP-mediated register programming in SR-IOV paths. Some `IH_RB_CNTL` writes are routed through `psp_reg_program()` instead of direct MMIO when a VF must program IH indirectly.
- KFD PASID/VMID management. `amdgpu_amdkfd_gfx_v10.c` and related files update `IH_VMID_*_LUT` entries after programming ATC/ATHUB mappings.
- NBIO IH setup, especially doorbell range and low-level interrupt control called before enabling IH rings.
- GMC VM fault processing, where later generations read the IH VMID LUT to recover PASID information for faults and retry handling.

The field definitions are part of the contract between generated register headers, AMDGPU common helpers, firmware expectations, and ASIC-specific source files. A consumer often references only the register family name and field name, so changing one macro name can be a compile-time break, while changing a mask value can be a runtime hardware break.

## Risks and Edge Cases

- Register drift is the primary risk. If the 5.0.0 field layout is used with a different OSSSYS IP revision, ring enable, pointer, overflow, or storm-control bits may program the wrong hardware fields.
- Some fields are ring-specific. `ENABLE_INTR` is treated as ring0-only in consumer code, while ring1/ring2 paths share many but not all `IH_RB_CNTL` semantics.
- Secondary-ring support differs by generation. OSSSYS 5.0.0 includes ring2 masks and Navi10 uses a third IH ring; later generations may remove ring2 or change the address map.
- The VMID LUT `PASID` field is only 16 bits in these macros. Consumers that handle wider PASIDs elsewhere must ensure truncation is intended for this hardware block.
- Overflow clear bits are transition-sensitive. Leaving `WPTR_OVERFLOW_CLEAR` asserted, or failing to clear it after acknowledgment, can hide subsequent overflow events.
- Doorbell offsets and writeback addresses are bitfield-constrained. Wrong shifts/masks can corrupt adjacent control bits or program an invalid doorbell index.
- Some diagnostic, IOV, and SEM fields may be rarely used or firmware-owned. Direct driver writes without hardware-specific sequencing could interfere with virtualization isolation, mailbox semantics, or power gating.
- The file is generated-looking and repetitive; manual edits are high risk because a single typo in a mask constant is not naturally covered by type checking.

## Test Signals

Useful validation signals are mostly build-time and hardware/integration oriented:

- Compile coverage for `navi10_ih.c`, `amdgpu_amdkfd_gfx_v10.c`, `amdgpu_amdkfd_gfx_v10_3.c`, and other GFX10/Navi users confirms macro names match helper expansions.
- Boot or module-load logs on Navi/GFX10 hardware should show IH initialization completing without PSP `IH_RB_CNTL` programming timeouts.
- Interrupt delivery should remain stable across enable/disable, suspend/resume, GPU reset, and runtime power transitions; missing or repeated interrupts point toward ring enable, doorbell, or pointer field issues.
- Ring overflow paths should log and recover using `IH_RB_WPTR.RB_OVERFLOW` and `IH_RB_CNTL.WPTR_OVERFLOW_CLEAR`; persistent overflow flags suggest clear-bit sequencing or mask drift.
- KFD process scheduling and VM fault attribution should report correct PASID/VMID associations after writes to `IH_VMID_*_LUT`.
- MSI storm/flood mitigation can be observed through page-fault storm scenarios and relevant IH flood/status registers.
- SR-IOV VF testing should exercise PSP indirect IH writes, active function ID fields, IOV violation logs, and VF ring full/overflow status.
- Header consistency can be checked mechanically by comparing masks against vendor register XML or adjacent generated revisions, and by verifying each mask aligns with its shift and expected field width.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_5_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_offset.h

## Purpose

`osssys_6_0_0_offset.h` is a generated AMDGPU ASIC register address contract for the OSSSYS 6.0.0 block. It maps symbolic register names to register offsets relative to the OSSSYS base address noted in the file (`0x4280`) and gives every listed register a `BASE_IDX` value of `0`.

This header is the address-side partner to `oss/osssys_6_0_0_sh_mask.h`. Runtime code combines `reg...` macros from this file with field masks/shifts from the sh/mask file through SOC15 helpers. It is used by GFX11-era and later AMDGPU paths such as `amdgpu/ih_v6_0.c`, `amdgpu/ih_v7_0.c`, `amdgpu/gmc_v11_0.c`, and `amdgpu/amdgpu_amdkfd_gfx_v11.c`.

## Important APIs, Types, and Definitions

The file exports only preprocessor macros:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT`, contiguous offsets `0x0000` through `0x000f`, and matching `regIH_VMID_*_LUT_MM` offsets `0x0010` through `0x001f`.
- `regIH_COOKIE_0` through `regIH_COOKIE_7`, offsets `0x0020` through `0x0027`, plus `regIH_REGISTER_LAST_PART0` at `0x003f`.
- Primary IH ring registers: `regIH_RB_CNTL`, `regIH_RB_BASE`, `regIH_RB_BASE_HI`, `regIH_RB_RPTR`, `regIH_RB_WPTR`, `regIH_RB_WPTR_ADDR_HI`, `regIH_RB_WPTR_ADDR_LO`, `regIH_DOORBELL_RPTR`, and `regIH_DOORBELL_RETRY_CAM`.
- Ring1 IH registers: `regIH_RB_CNTL_RING1`, `regIH_RB_BASE_RING1`, `regIH_RB_BASE_HI_RING1`, `regIH_RB_RPTR_RING1`, `regIH_RB_WPTR_RING1`, and `regIH_DOORBELL_RPTR_RING1`.
- Global IH control/status/perf/diagnostic registers: `regIH_RETRY_CAM_ACK`, `regIH_VERSION`, `regIH_CNTL`, `regIH_CNTL2`, `regIH_STATUS`, `regIH_PERFMON_CNTL`, `regIH_PERFCOUNTER*_RESULT`, DSM match registers, limit-rate control, VF ring status, ring status, flood/storm controls, clock control, interrupt flags, last interrupt info, scratch, credit/error/status, MMHUB error, cookie-recognition violation log, memory power controls, retry CAM control, MSI storm index/data, and register-last sentinels.
- SEM-facing registers are much smaller in this 6.0.0 offset file than in older mask files: `regSEM_MAILBOX`, `regSEM_MAILBOX_CLEAR`, and `regSEM_REGISTER_LAST_PART2`.
- IH client configuration/remap/drop registers: `regIH_CLIENT_CFG`, `regIH_RING1_CLIENT_CFG_INDEX`, `regIH_RING1_CLIENT_CFG_DATA`, `regIH_CLIENT_CFG_INDEX`, `regIH_CLIENT_CFG_DATA`, `regIH_CID_REMAP_INDEX`, `regIH_CID_REMAP_DATA`, `regIH_CHICKEN`, `regIH_INT_DROP_CNTL`, `regIH_INT_DROP_MATCH_VALUE*`, `regIH_INT_DROP_MATCH_MASK*`, and `regIH_REGISTER_LAST_PART1`.

Every register also has a matching `reg..._BASE_IDX` macro, always `0`, indicating the base index passed to SOC15 address construction for this block.

## Control Flow

This header has no executable control flow. In consumers it controls which MMIO address is touched:

- `ih_v6_0_init_register_offset()` maps `adev->irq.ih` and `adev->irq.ih1` register slots to `SOC15_REG_OFFSET(OSSSYS, 0, regIH_...)` values. Unlike OSSSYS 5.0.0/Navi10, the comment states ring2 is removed and only ring0/ring1 are available.
- `ih_v6_0_enable_ring()` writes ring base, base high, read/write pointers, writeback address, and doorbell register addresses selected from this header.
- `ih_v6_0_irq_init()` uses `regIH_STORM_CLIENT_LIST_CNTL`, `regIH_INT_FLOOD_CNTL`, `regIH_MSI_STORM_CTRL`, `regIH_RING1_CLIENT_CFG_INDEX`, and `regIH_RING1_CLIENT_CFG_DATA` to configure storm handling and dGPU ring1 redirection.
- `force_update_wptr_for_self_int()` reads/writes `regIH_CNTL2` and `regIH_RB_CNTL_RING1` to force write pointer propagation for self interrupts.
- `gmc_v11_0.c` reads or writes `regIH_VMID_0_LUT + vmid` and `regIH_VMID_0_LUT_MM + vmid` for PASID lookup and VMID mapping.
- `amdgpu_amdkfd_gfx_v11.c` writes the `regIH_VMID_0_LUT + vmid` address when KFD maps a process PASID to an interrupt VMID.

Since the file supplies constants, the build has no branching here; the runtime branch decisions live in the IH/GMC/KFD source that selects which register macro to use.

## State and Persistence Behavior

The header itself is stateless. The state represented by these offsets lives in GPU registers and is re-established during device load, resume, reset, and interrupt subsystem initialization.

Important state domains addressed by the file are:

- VMID/PASID attribution tables for both regular and MMHUB-related interrupt paths.
- IH ring0 and ring1 buffer base addresses, write/read pointers, write pointer writeback addresses, control words, and doorbell read-pointer controls.
- IH global control, status, retry-CAM, performance counter, clock, memory-power, flood, storm, drop, and diagnostic registers.
- Ring1 client redirection state used to steer selected interrupts to the second IH ring on dGPU configurations.
- Client configuration and client-ID remap tables used by firmware/driver integration paths.
- Minimal SEM mailbox offsets used for OSSSYS 6.0.0 semaphore mailbox interaction.

Register state can persist until explicitly overwritten by the driver or reset by hardware. Consumers must pair these offsets with correct field definitions from the same IP generation; using the right address with the wrong field mask can still corrupt state.

## Dependencies and Integration Points

This file has no `#include` dependencies. Its effective dependencies are:

- `oss/osssys_6_0_0_sh_mask.h` for field layouts of the registers named here.
- SOC15 address helpers such as `SOC15_REG_OFFSET(OSSSYS, instance, reg...)`.
- MMIO helpers `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and related no-KIQ variants after offsets are stored in `amdgpu_ih_regs`.
- IH v6/v7 driver code that assigns offsets into `amdgpu_ih_regs`, programs ring buffers, acknowledges overflow, and configures storm controls.
- KFD PASID mapping for GFX11, which uses the VMID LUT offsets to keep IH attribution aligned with process VMIDs.
- GMC v11 fault handling, which reads the same LUT offsets to recover PASIDs for VM fault processing.
- PSP/SR-IOV register programming paths, because some addresses are written indirectly through PSP register IDs rather than direct MMIO when running as a virtual function.

The file is also implicitly tied to the generated register namespace. OSSSYS 6.0.0 uses the `reg...` prefix rather than the `mm...` prefix used by many older offset headers; consumers for this generation must include and reference the right naming style.

## Risks and Edge Cases

- Address drift across IP revisions is the largest risk. If an OSSSYS 6.0.0 offset is used on 5.x, 6.0.1, or another block revision without checking compatibility, the driver may write a valid field value to the wrong register.
- Ring topology differs from earlier generations. `ih_v6_0.c` explicitly treats ring2 as removed; adding ring2 logic using old 5.0.0 assumptions would require new offsets that are not present here.
- VMID LUTs are contiguous and consumers add `vmid` to `regIH_VMID_0_LUT` or `_MM`. That relies on the contiguous layout remaining true and on caller-side VMID bounds checks.
- Every `BASE_IDX` is `0`. If future block instances or base-index selection change, blindly copying this file's pattern would address the wrong SOC15 base.
- Register families in the sh/mask file may include fields for registers omitted from this offset file, or vice versa, depending on generated package scope. Code must compile against the matching offset and mask pair for the target ASIC.
- Storm/flood and interrupt-drop offsets affect interrupt throttling. Wrong addresses here can produce missing interrupts, interrupt floods, or inability to diagnose the first dropped interrupt.
- The `reg...` namespace can coexist with older `mm...` headers in nearby code. Accidental cross-generation inclusion may compile if names overlap through other headers but touch incompatible addresses.

## Test Signals

Validation should focus on both compile-time symbol coverage and hardware behavior:

- Build GFX11/OSSSYS 6.0.0 users including `ih_v6_0.c`, `ih_v7_0.c`, `gmc_v11_0.c`, and `amdgpu_amdkfd_gfx_v11.c` to verify all referenced `reg...` symbols exist.
- Device load and resume on GFX11 hardware should initialize IH ring0/ring1 without MMIO faults, PSP programming timeouts, or missing interrupt-enable state.
- Interrupt smoke tests should confirm ring write pointers advance, read pointers are acknowledged through MMIO or doorbells, and no unexpected ring2 access occurs.
- KFD process creation and teardown should update `regIH_VMID_0_LUT + vmid` and produce correct PASID attribution in VM faults and interrupts.
- VM fault tests in `gmc_v11_0` should recover the expected PASID from the IH LUT and handle retry/write fault flags consistently.
- Page-fault storm scenarios can exercise `regIH_STORM_CLIENT_LIST_CNTL`, `regIH_INT_FLOOD_CNTL`, and `regIH_MSI_STORM_CTRL` programming.
- Suspend/resume and GPU reset should reprogram all ring base/pointer/control registers selected from this offset table and restore interrupt delivery.
- Mechanical generation checks should compare offsets and `BASE_IDX` values against vendor register XML or the authoritative generated source for OSSSYS 6.0.0.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_offset.h -->
