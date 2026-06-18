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
