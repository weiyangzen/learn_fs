# subset-b-003354 grouped research

Work item: `subset-b-003354`

This grouped report covers three AMDGPU OSSSYS register-definition headers. Each section is bounded by the required reconciliation markers and is intended to split directly into the mapped source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_sh_mask.h

## Purpose

`osssys_6_0_0_sh_mask.h` is a generated AMD OSSSYS 6.0.0 register bitfield header for the OSS system decode block, mostly the interrupt handler (IH) register space plus SEM mailbox and IH client/drop controls. It exports C preprocessor constants only. For each hardware register field it provides the canonical generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the starting bit position.
- `<REGISTER>__<FIELD>_MASK`, the 32-bit mask for extracting or composing that field.

The file does not define functions, structs, variables, storage, or executable logic. Its purpose is to keep AMDGPU IH/GFX11/KFD/GMC code from hard-coding bit positions while programming or decoding SOC15 OSSSYS registers.

## Important APIs, Types, and Macro Families

The public API is the macro namespace guarded by `_osssys_6_0_0_SH_MASK_HEADER`. Important families include:

- `IH_VMID_0_LUT` through `IH_VMID_15_LUT` and `_MM` variants: map VMID entries to 16-bit PASIDs for graphics and multimedia interrupt paths.
- `IH_COOKIE_0` through `IH_COOKIE_7`: describe interrupt cookie payload layout, including client/source/ring/VM identifiers, timestamp low/high fields, PASID source, and 128-bit context ID fragments.
- `IH_RB_CNTL`, `IH_RB_BASE`, `IH_RB_BASE_HI`, `IH_RB_RPTR`, `IH_RB_WPTR`, `IH_RB_WPTR_ADDR_*`, and `IH_DOORBELL_*`: define ring-buffer enablement, size, read/write pointer fields, writeback address fields, overflow bits, drain controls, MC/VMID address-space fields, and doorbell read-pointer configuration.
- `IH_RB_*_RING1`: mirror the core ring-buffer control, base, pointer, and doorbell definitions for ring 1, with a reduced control set compared with ring 0.
- `IH_RETRY_CAM_ACK`, `IH_RETRY_INT_CAM_CNTL`, and related status fields: define retry interrupt CAM indexing, sizing, backpressure, enable, GC/MM backpressure, and per-VF entry sizing.
- `IH_VERSION`, `IH_CNTL`, `IH_CNTL2`, `IH_STATUS`, `IH_RB_STATUS`, and `IH_PERFMON_*`: expose version decoding, write-pointer timer/hysteresis/high-water settings, self-interrupt write-pointer update controls, idle/full/overflow status, and two perf counter selector/result lanes.
- `IH_DSM_MATCH_*`, `IH_INT_DROP_*`, and `IH_INT_FLOOD_*`: define matching, filtering, flood control, drop accounting, and last-dropped interrupt metadata by client/source/VF/context identifiers.
- `IH_STORM_CLIENT_LIST_CNTL`, `IH_MSI_STORM_*`, `IH_INT_FLAGS`, `IH_CLIENT_CREDIT_ERROR`, and `IH_CREDIT_STATUS`: represent per-client storm/flood/credit/error bitmaps, client-indexed MSI storm table fields, and returned-credit state.
- `IH_LAST_INT_INFO*`, `IH_GPU_IOV_*` is not present in this version, `IH_COOKIE_REC_VIOLATION_LOG`, and `IH_MMHUB_ERROR`: define diagnostic fields for last interrupt, cookie receiver violations, and MMHUB write response/user nack errors.
- `IH_MEM_POWER_CTRL` and `IH_MEM_POWER_CTRL2`: configure memory power control for IH buffer, retry CAM, and PASID LUT memories.
- `SEM_MAILBOX`, `SEM_MAILBOX_CLEAR`, and register-last sentinels: define SEM hostport mailbox fields and reserved end markers.
- `IH_CLIENT_CFG`, `IH_RING1_CLIENT_CFG_*`, `IH_CLIENT_CFG_INDEX`, `IH_CLIENT_CFG_DATA`, `IH_CID_REMAP_*`, `IH_CHICKEN`, and `IH_INT_DROP_MATCH_*`: describe client count/configuration tables, ring selection, interface/client type, client ID remap, miscellaneous control bits, and interrupt-drop match values/masks.

The header must be used with the matching 6.0.0 offset header, especially `osssys_6_0_0_offset.h`, because this file provides bit positions but no register addresses.

## Control Flow

There is no runtime control flow in the header. It affects compiled control flow indirectly because AMDGPU code uses these macros with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

The typical consumer flow is:

1. Include the matching offset and shift/mask headers.
2. Read a register with a SOC15 helper or compute its absolute address with `SOC15_REG_OFFSET`.
3. Extract status fields with `REG_GET_FIELD`-style helpers using the `__SHIFT` and `_MASK` values.
4. Compose control values using the same macro pairs and write the register back.

Source-tree usage confirms the version pairing: `amdgpu/ih_v6_0.c` includes this header with `osssys_6_0_0_offset.h`; `amdgpu/amdgpu_amdkfd_gfx_v11.c` also includes the 6.0.0 pair; `amdgpu/gmc_v11_0.c` includes the 6.0.0 offset header. `ih_v6_0.c` programs registers such as `regIH_RB_CNTL`, `regIH_RB_CNTL_RING1`, and related ring fields whose masks are defined here.

## State and Persistence Behavior

The header itself has no state. The persistent state it names is hardware state in the OSSSYS/IH register file:

- Ring-buffer state includes enable bits, base address, read/write pointers, write-pointer writeback address, overflow, full/drain status, MC snoop/read-only/space fields, and doorbell enable/offsets.
- VM/PASID mapping state persists in the VMID LUT and MM LUT registers until reprogrammed or reset.
- Interrupt-cookie fields describe the format of interrupt vector metadata as stored or reported by hardware.
- Flood/drop/storm/client-credit fields represent hardware counters, sticky status, clear bits, and per-client status maps; several are command-like or write-one-to-clear by hardware convention, even though the header only exposes masks.
- Memory-power and clock/power-gating status bits describe hardware-managed power state for IH internal memories.
- Client configuration/remap/drop-match state configures how the IH interprets clients and filters interrupt records.

Because generated masks do not encode access mode, reset value, or write-clear semantics, callers must consult the owning driver flow and hardware specification before treating a field as ordinary read/write state.

## Dependencies and Integration Points

Primary dependencies are generated AMD register infrastructure and AMDGPU SOC15 helpers:

- `osssys_6_0_0_offset.h` supplies `regIH_*` register offsets and base indices.
- AMDGPU SOC15 helpers supply register access and field composition/extraction.
- `amdgpu/ih_v6_0.c` is the central integration point for IH v6.0 ring setup, interrupt enablement, pointer handling, and ring 1 initialization.
- `amdgpu/amdgpu_amdkfd_gfx_v11.c` uses the 6.0.0 definitions for KFD/GFX11 interrupt, PASID, and VMID-facing behavior.
- `amdgpu/gmc_v11_0.c` includes the offset side and participates in memory-controller integration where VMID/PASID and MMHUB-related fields matter.

This header should not be mixed with adjacent ASIC-generation offset headers. Field names are similar across OSSSYS versions, but reserved bits, added registers, and masks differ.

## Risks

- Bitfield drift is high impact. A wrong mask or shift can disable interrupts, corrupt ring pointers, mis-handle overflow, or write reserved hardware bits.
- Ring-buffer fields are especially sensitive: `RB_SIZE`, base address, read/write pointer offsets, overflow clear, and MC space/VMID fields must match the hardware ABI or IH events can be lost.
- VMID/PASID LUT mistakes can attribute interrupts to the wrong process or VM context.
- Interrupt flood/drop/storm controls are security and reliability relevant; over-aggressive matching can drop valid interrupts, while under-filtering can leave storm protection ineffective.
- Repetitive client bitmaps (`CLIENT_1` through `CLIENT_31`, flags, credits, and errors) are copy-paste-prone. Off-by-one bit positions would misdiagnose or clear the wrong client.
- The 6.0.0 file lacks 6.1.0-only virtualization/reset/MMHUB control fields such as `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, `IH_CLIENT_CFG_DATA2`, `IH_GPU_IOV_VIOLATION_LOG*`, and `IH_MMHUB_CNTL`; code that expects those fields must include the 6.1.0 header instead.

## Test Signals

Useful validation signals are mostly build and hardware integration tests:

- Compile AMDGPU with `ih_v6_0.c`, KFD GFX11, and GMC v11 consumers enabled to catch missing or renamed macros.
- Boot supported hardware and verify IH ring initialization, interrupt delivery, read/write pointer movement, writeback pointer updates, and ring 1 setup.
- Exercise interrupt overflow/full/drain paths and confirm `IH_RB_WPTR`, `IH_RB_STATUS`, and `IH_STATUS` decode correctly.
- Exercise VMID/PASID interrupt attribution through KFD workloads and page-fault/interrupt paths.
- Validate flood/drop/storm controls under interrupt-storm or fault-injection scenarios.
- Confirm suspend/resume and reset paths reprogram ring buffers, LUTs, memory-power controls, and client configuration correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_1_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_1_0_offset.h

## Purpose

`osssys_6_1_0_offset.h` is the generated OSSSYS 6.1.0 register offset map for AMDGPU. It covers the OSS system decode block with base address `0x4280` and exports `reg*` register offset macros plus `<reg>_BASE_IDX` selectors. It provides addresses only; the companion `osssys_6_1_0_sh_mask.h` provides the bit layout of each register.

The file contains no functions, types, variables, or executable control flow. Its API is a flat macro list used by SOC15 register access helpers.

## Important APIs, Types, and Register Families

The header guard is `_osssys_6_1_0_OFFSET_HEADER`. Each register appears as:

- `reg<REGISTER_NAME>`: the dword offset within the OSSSYS block.
- `reg<REGISTER_NAME>_BASE_IDX`: the generated base-index selector, consistently `0` in this file.

Important offset ranges and families:

- `regIH_VMID_0_LUT` through `regIH_VMID_15_LUT` at `0x0000` through `0x000f`, followed by `regIH_VMID_0_LUT_MM` through `_15_LUT_MM` at `0x0010` through `0x001f`.
- `regIH_COOKIE_0` through `regIH_COOKIE_7` at `0x0020` through `0x0027`, and `regIH_REGISTER_LAST_PART0` at `0x003f`.
- IH ring 0 registers from `regIH_RB_CNTL` at `0x0080` through `regIH_DOORBELL_RETRY_CAM` at `0x0088`.
- IH ring 1 registers from `regIH_RB_CNTL_RING1` at `0x008c` through `regIH_DOORBELL_RPTR_RING1` at `0x0093`.
- Control/status/performance/match/flood registers from `regIH_RETRY_CAM_ACK` (`0x00a4`) through `regIH_LAST_INT_INFO2` (`0x00df`) and `regIH_SCRATCH` (`0x00e0`).
- Diagnostic and error registers including `regIH_CLIENT_CREDIT_ERROR`, `regIH_GPU_IOV_VIOLATION_LOG`, `regIH_GPU_IOV_VIOLATION_LOG2`, `regIH_COOKIE_REC_VIOLATION_LOG`, `regIH_CREDIT_STATUS`, and `regIH_MMHUB_ERROR`.
- `regIH_VF_RB_STATUS3`, `regIH_VF_RB_STATUS4`, and `regIH_VF_RB1_STATUS3`, plus MSI storm table registers at `0x00f1` through `0x00f3`.
- SEM mailbox registers at `regSEM_MAILBOX` (`0x010a`) and `regSEM_MAILBOX_CLEAR` (`0x010b`), with a part sentinel at `0x017f`.
- 6.1.0 virtualization and client-configuration region from `regIH_ACTIVE_FCN_ID` (`0x0180`) and `regIH_VIRT_RESET_REQ` (`0x0181`) through `regIH_REGISTER_LAST_PART1` (`0x019f`), including `regIH_CLIENT_CFG_DATA2` and `regIH_MMHUB_CNTL`.

Compared with the 6.0.0 offset layout, the 6.1.0 map adds offsets for `IH_ACTIVE_FCN_ID`, `IH_VIRT_RESET_REQ`, `IH_CLIENT_CFG_DATA2`, `IH_MMHUB_CNTL`, and the GPU IOV violation log registers. These additions align with the extra fields present in `osssys_6_1_0_sh_mask.h`.

## Control Flow

There is no control flow in this header. Runtime code uses it as an address source. A typical call site passes a macro such as `regIH_RB_CNTL` to `SOC15_REG_OFFSET`, `RREG32_SOC15`, or `WREG32_SOC15`, then combines the returned register value with masks from `osssys_6_1_0_sh_mask.h`.

`amdgpu/ih_v6_1.c` includes this file together with `osssys_6_1_0_sh_mask.h`. Local references show `ih_v6_1.c` using offsets such as `regIH_RB_CNTL`, `regIH_RB_CNTL_RING1`, and other IH ring registers to set up the interrupt handler for OSSSYS 6.1.0 devices.

## State and Persistence Behavior

The offset header stores no state. The offsets point at persistent or transient hardware state in the OSSSYS register block:

- VMID/PASID LUT entries and MM LUT entries.
- IH cookie metadata registers.
- IH ring base, pointer, doorbell, overflow, full, and drain state.
- IH control, status, clock, retry CAM, memory power, performance, DSM match, and flood/drop state.
- VF/ring status and GPU IOV violation diagnostic state.
- SEM mailbox state.
- Active function ID, virtualization reset requests, client configuration tables, client ID remap state, MMHUB control, chicken/debug/firewall controls, and interrupt-drop match registers.

Persistence and side effects are determined by the hardware and by the corresponding mask/default headers, not by this offset file.

## Dependencies and Integration Points

This file depends on AMDGPU generated-register conventions:

- It must be paired with `osssys_6_1_0_sh_mask.h` for field-level manipulation.
- It is consumed by `amdgpu/ih_v6_1.c` and any other OSSSYS 6.1.0 client that programs IH registers through SOC15 helpers.
- It shares naming conventions with older and newer OSSSYS headers, but offsets must remain version-matched to the target IP block. Similar register names in 6.0.0 or 7.x do not guarantee identical availability or bit layout.

The `reg*` prefix matters because this header is part of the newer SOC15-style generated offset convention in this source tree, while older headers sometimes use `mm*` prefixes.

## Risks

- Wrong offsets can redirect writes to the wrong hardware register, which is more dangerous than a decode-only error.
- Mixing this offset header with the 6.0.0 or 7.x mask header can compile if names overlap, but it can silently program the wrong bits or touch missing registers.
- The added 6.1.0 virtualization range must be preserved: active function, virtual reset, client configuration, MMHUB control, and firewall/chicken offsets are privilege-sensitive.
- Ring offsets are dense and repetitive. Offsets around ring 0/ring 1 and write-pointer writeback registers are easy to transpose.
- Register-last sentinel offsets mark hardware decode boundaries and should not be treated as normal programmable registers unless the consuming code explicitly expects reserved sentinel behavior.

## Test Signals

Useful validation signals include:

- Build `amdgpu/ih_v6_1.c` and SOC15 register consumers that include the 6.1.0 pair.
- On supported hardware, verify IH v6.1 ring 0 and ring 1 initialization, interrupt delivery, pointer updates, and writeback/doorbell programming.
- Read back key registers through debugfs, tracepoints, or driver instrumentation and confirm addresses match expected OSSSYS base-plus-offset layout.
- Exercise virtualization paths that touch active function ID, virtual reset requests, GPU IOV violation logs, and client configuration offsets.
- Compare the generated offset map against AMD register XML/spec sources or adjacent upstream kernel versions when regenerating.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_1_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_1_0_sh_mask.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/oss/osssys_6_1_0_sh_mask.h -->
