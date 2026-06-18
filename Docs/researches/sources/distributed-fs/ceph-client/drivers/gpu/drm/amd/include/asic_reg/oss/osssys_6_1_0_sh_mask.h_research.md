# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_1_0_sh_mask.h

## Purpose

`osssys_6_1_0_sh_mask.h` is the generated shift/mask companion to `osssys_6_1_0_offset.h`. It defines the bit-level ABI for OSSSYS 6.1.0 IH, SEM, virtualization, client-configuration, MMHUB, and interrupt filtering registers.

The header exports macros only. It defines no C functions, types, variables, memory allocations, or runtime control flow. Consumers combine these constants with SOC15 read/write helpers and the matching 6.1.0 offset header.

## Important APIs, Types, and Macro Families

The public API is the `_osssys_6_1_0_SH_MASK_HEADER` macro namespace. It follows the generated pair pattern:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

Major register families:

- `IH_VMID_0_LUT` through `IH_VMID_15_LUT` and `_MM` variants: 16-bit PASID fields for VMID-to-PASID mapping in graphics and multimedia IH paths.
- `IH_COOKIE_0` through `IH_COOKIE_7`: interrupt cookie decoding for client/source/ring/VM identifiers, timestamps, PASID source, and context ID fragments.
- `IH_RB_CNTL`, `IH_RB_RPTR`, `IH_RB_WPTR`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_WPTR_ADDR_*`, `IH_DOORBELL_RPTR`, and `IH_DOORBELL_RETRY_CAM`: ring 0 control, pointer, address, overflow, doorbell, and MC address-space fields.
- `IH_RB_*_RING1`: ring 1 control, pointer, base, and doorbell fields.
- `IH_RETRY_CAM_ACK` and `IH_RETRY_INT_CAM_CNTL`: retry CAM acknowledgement index, CAM size, backpressure skid, and per-VF entry size. In this 6.1.0 header the retry CAM control masks present in the file are sizing/backpressure/per-VF-entry fields, without the 6.0.0 `ENABLE`, `MM_BACK_PRESSURE_ENABLE`, and `GC_BACK_PRESSURE_ENABLE` masks.
- `IH_VERSION`, `IH_CNTL`, `IH_CLK_CTRL`, `IH_LIMIT_INT_RATE_CNTL`, `IH_MEM_POWER_CTRL`, `IH_MEM_POWER_CTRL2`, `IH_CNTL2`, `IH_STATUS`, and `IH_PERFMON_*`: version fields, write-pointer timers, clock overrides, interrupt rate limiting, memory power controls, self-IV write-pointer update controls, status bits, and performance counters.
- `IH_DSM_MATCH_*`, `IH_INT_DROP_*`, `IH_INT_FLOOD_*`, `IH_STORM_CLIENT_LIST_CNTL`, `IH_INT_FLAGS`, `IH_LAST_INT_INFO*`, and `IH_MSI_STORM_*`: match/filter/drop/flood/storm/last-interrupt metadata fields.
- `IH_VF_RB_STATUS*`, `IH_VF_RB1_STATUS*`, `IH_CLIENT_CREDIT_ERROR`, `IH_CREDIT_STATUS`, `IH_COOKIE_REC_VIOLATION_LOG`, and `IH_MMHUB_ERROR`: per-VF ring status, client credit/error bitmaps, cookie receiver violation logging, and MMHUB response/nack diagnostics.
- `IH_GPU_IOV_VIOLATION_LOG` and `IH_GPU_IOV_VIOLATION_LOG2`: 6.1.0-specific GPU IOV violation status, multiple-violation status, address, opcode, VF/VF_ID, and initiator ID fields.
- `SEM_MAILBOX` and `SEM_MAILBOX_CLEAR`: SEM hostport mailbox and clear masks.
- `IH_ACTIVE_FCN_ID` and `IH_VIRT_RESET_REQ`: 6.1.0 virtualization active-function and virtual-reset request fields.
- `IH_CLIENT_CFG`, `IH_RING1_CLIENT_CFG_*`, `IH_CLIENT_CFG_INDEX`, `IH_CLIENT_CFG_DATA`, `IH_CLIENT_CFG_DATA2`, `IH_CID_REMAP_*`, `IH_CHICKEN`, and `IH_MMHUB_CNTL`: client count/configuration, ring1 client table, indexed client config, credit-return address, client ID remapping, debug/cross-trigger/firewall controls, and MMHUB unit/transaction-level controls.

Compared with `osssys_6_0_0_sh_mask.h`, this file adds `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, `IH_CLIENT_CFG_DATA2`, `IH_GPU_IOV_VIOLATION_LOG`, `IH_GPU_IOV_VIOLATION_LOG2`, and `IH_MMHUB_CNTL`. It also expands several existing fields, such as `IH_CLIENT_CFG_DATA__OVERWRITE_RING_ID_WITH_ACTIVE_FCN_ID` and `IH_CHICKEN__ACTIVE_FCN_ID_PROT_ENABLE`, `DBGU_TRIGGER_ENABLE`, and `REG_FIREWALL_ENABLE`.

## Control Flow

There is no direct control flow. This header controls how compiled driver code reads and writes fields inside OSSSYS 6.1.0 registers. The typical flow is:

1. Use a `regIH_*` offset from `osssys_6_1_0_offset.h`.
2. Read or write the register with SOC15 helpers.
3. Extract or set fields using the `__SHIFT` and `_MASK` values from this file.

Local integration confirms this pairing: `amdgpu/ih_v6_1.c` includes `oss/osssys_6_1_0_offset.h` and `oss/osssys_6_1_0_sh_mask.h`, then uses IH ring register offsets and field macros to initialize and manage IH v6.1 interrupt rings.

## State and Persistence Behavior

The header itself has no state. It names hardware state in the OSSSYS 6.1.0 block:

- Interrupt ring state: enablement, size, base, read/write pointer offsets, overflow/full/drain conditions, writeback address, doorbell offsets, and MC/VMID address-space controls.
- Interrupt metadata state: cookies, last-interrupt info, timestamps, PASIDs, source/client/ring IDs, VMID type, and context IDs.
- Process/virtualization state: VMID/PASID LUTs, active function ID, virtual reset request bits, GPU IOV violation logs, VF ring status, VF selection, and ring-overwrite behavior.
- Filtering and backpressure state: DSM match controls, interrupt drop controls, drop match/mask values, retry CAM sizing/backpressure, flood/drop counters, and MSI storm table entries.
- Reliability and diagnostics: client credit returns/errors, MMHUB response/nack status, cookie receiver violation status, interrupt flags, and scratch data.
- Power and clock state: IH internal memory power controls, PASID LUT power controls, status bits indicating power-gated internal memories, and clock soft overrides.
- Client topology state: total client count, indexed client configuration, ring1 client matching, client ID remapping, credit-return address, and MMHUB transaction-level fields.

Some fields are sticky status or clear-on-write commands, while others are configuration fields. The header cannot distinguish those access semantics; callers must use the hardware spec and existing driver sequencing.

## Dependencies and Integration Points

Primary dependencies:

- `osssys_6_1_0_offset.h` for register addresses.
- AMDGPU SOC15 register helper macros and functions for MMIO access and field operations.
- `amdgpu/ih_v6_1.c` as the central consumer for IH v6.1 ring configuration and interrupt processing.

Secondary integration points are the same subsystems that consume IH state: IRQ handling, KFD/process PASID attribution, SR-IOV/virtualization management, MMHUB diagnostics, reset paths, power management, and interrupt storm/drop protection.

The header is version-specific. Many names overlap with 6.0.0 and 7.x OSSSYS headers, but the presence and meaning of fields such as active function ID, virtual reset request, GPU IOV logs, `IH_CLIENT_CFG_DATA2`, and `IH_MMHUB_CNTL` are tied to the 6.1.0 IP block.

## Risks

- Incorrect shift/mask constants can break interrupt delivery, corrupt ring pointers, lose overflow diagnostics, or write reserved bits.
- Virtualization fields are privilege-sensitive. `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, GPU IOV logs, VF ring status, ring selection, and active-function overwrite/protection bits can affect PF/VF isolation and reset handling.
- MMHUB diagnostic/control fields are low-level fabric integration points; bad masks can misreport write response errors or program the wrong unit/transaction-level values.
- Interrupt drop/flood/storm controls can cause either lost interrupts or ineffective storm mitigation if match masks or enable bits are wrong.
- The changed retry CAM control field set relative to 6.0.0 is a compatibility risk for shared code that assumes `ENABLE` or GC/MM backpressure enable masks exist.
- Repetitive bitmaps for clients, flags, credits, and errors are prone to off-by-one mistakes.
- Mixing this mask header with a 6.0.0 or 7.x offset header may compile for common names but can silently program the wrong hardware layout.

## Test Signals

Useful test and validation signals include:

- Build `amdgpu/ih_v6_1.c` and any SOC15 OSSSYS 6.1.0 consumers to catch missing macro names.
- Verify IH v6.1 interrupt ring setup on hardware: ring enable, base address, read/write pointer movement, writeback, doorbell configuration, overflow handling, and ring 1 operation.
- Exercise VMID/PASID interrupt attribution and KFD/process-facing interrupt flows.
- Validate VF and virtualization behavior: active function ID, virtual reset request, GPU IOV violation logging, VF ring status fields, and client configuration selection.
- Fault-inject or observe MMHUB errors, cookie receiver violations, client credit errors, and interrupt flood/drop events to confirm status decoding.
- Test suspend/resume, reset, and power-management paths that reprogram IH memory power, clock override, LUT, and ring state.
- Compare regenerated headers against AMD register database output or known-good upstream kernel definitions before accepting updates.
