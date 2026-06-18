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
- `IH_LAST_INT_INFO*`, `IH_COOKIE_REC_VIOLATION_LOG`, and `IH_MMHUB_ERROR`: define diagnostic fields for last interrupt, cookie receiver violations, and MMHUB write response/user nack errors.
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
