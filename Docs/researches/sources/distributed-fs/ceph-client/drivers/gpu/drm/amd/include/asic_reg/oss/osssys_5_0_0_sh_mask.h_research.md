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
