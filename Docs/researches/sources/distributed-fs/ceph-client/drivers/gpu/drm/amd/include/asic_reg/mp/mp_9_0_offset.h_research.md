<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_9_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_9_0_offset.h

## Purpose

`mp_9_0_offset.h` is the generated MP 9.0 register-offset header used by older SOC15-era AMDGPU PSP, SMU, SR-IOV, and reset code. It maps MP0 and MP1 SMN mailbox registers, interrupt registers, response registers, FPS/scratch registers, and MP1 public-control reset register to symbolic `mm...` names with `_BASE_IDX` values. It allows driver code for Vega-era hardware to use common register-access macros instead of raw MP offsets.

## Important APIs, Types, And Macros

The file exports preprocessor constants only. There are no functions, structs, enums, or runtime data.

Important macro groups:

- `mmMP0_SMN_C2PMSG_32` through `mmMP0_SMN_C2PMSG_103`, offsets `0x0060` through `0x00a7`, all `_BASE_IDX` `0`. These are MP0 mailbox registers used heavily by PSP boot, ring, reset, and command flows.
- `mmMP0_SMN_ACTIVE_FCN_ID`, `mmMP0_SMN_IH_CREDIT`, `mmMP0_SMN_IH_SW_INT`, and `mmMP0_SMN_IH_SW_INT_CTRL`, offsets `0x00c0` through `0x00c3`.
- `mmMP1_SMN_ACP2MP_RESP`, `mmMP1_SMN_DC2MP_RESP`, `mmMP1_SMN_UVD2MP_RESP`, `mmMP1_SMN_VCE2MP_RESP`, and `mmMP1_SMN_RLC2MP_RESP`, offsets `0x0240` through `0x0244`.
- `mmMP1_SMN_C2PMSG_32` through `mmMP1_SMN_C2PMSG_103`, offsets `0x0260` through `0x02a7`.
- `mmMP1_SMN_ACTIVE_FCN_ID`, `mmMP1_SMN_IH_CREDIT`, `mmMP1_SMN_IH_SW_INT`, `mmMP1_SMN_IH_SW_INT_CTRL`, and `mmMP1_SMN_FPS_CNT`, offsets `0x02c0` through `0x02c4`.
- `mmMP1_SMN_EXT_SCRATCH0` through `mmMP1_SMN_EXT_SCRATCH8`, offsets `0x03c0` through `0x03c8`.
- `mmMP1_SMN_PUB_CTRL`, offset `0x02c5`, in the `mp_SmuMp1Pub_CruDec` address block.

Every `_BASE_IDX` in this file is `0`, reflecting the older generated layout and SOC15 address calculation for MP 9.0.

## Control Flow

There is no local control flow. Runtime consumers include:

- `amdgpu/psp_v3_1.c`, which uses MP0 C2PMSG registers for PSP bootloader readiness, system-driver and secure-OS loading, ring creation/destruction, SR-IOV alternate ring setup, IH rerouting, mode1 reset, and firmware-response polling.
- `amdgpu/mxgpu_ai.c`, which uses MP0 registers in SR-IOV or virtualization-related paths.
- `amdgpu/soc15.c`, which includes the header for SOC15 common logic.

Typical PSP flow writes a command or parameter into `mmMP0_SMN_C2PMSG_*`, delays for firmware handshaking where needed, and waits for firmware-owned response bits with `psp_wait_for(psp, SOC15_REG_OFFSET(MP0, 0, mm...), mask, expected, flags)`.

## State And Persistence Behavior

The header has no state. The registers it names hold live hardware/firmware state:

- MP0 C2PMSG mailboxes carry PSP bootloader commands, secure OS loading state, ring memory addresses, ring sizes, SR-IOV GPCOM commands, IH routing commands, and reset commands.
- MP1 C2PMSG mailboxes and response registers carry SMU/MP1 firmware protocol values and responses from ACP, DC, UVD, VCE, and RLC clients.
- Active function ID fields expose SR-IOV VF/PF state.
- Software interrupt and credit registers affect interrupt delivery.
- Scratch registers hold firmware/driver scratch data until reset or overwrite.
- `mmMP1_SMN_PUB_CTRL` exposes MP1 reset control.

Hardware and firmware own persistence; this header only names the addresses.

## Dependencies

Consumers depend on:

- `mp_9_0_sh_mask.h` for field-level masks used with the offsets here.
- SOC15 helpers, especially `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and direct `WREG32` where a computed offset is reused.
- PSP helper logic such as `psp_wait_for`, `psp_copy_fw`, and ring management code.
- Firmware command constants such as `PSP_BL__LOAD_SYSDRV`, `GFX_CTRL_CMD_ID_GBR_IH_SET`, `GFX_CTRL_CMD_ID_DESTROY_RINGS`, and `GFX_CTRL_CMD_ID_MODE1_RST`.

The include guard is `_mp_9_0_OFFSET_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c` includes this header and uses MP0 mailbox offsets throughout PSP boot and ring setup.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c` includes this header for virtualization-era MP register access.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c` includes this header in common SOC15 code.
- Other AMDGPU files for later ASICs show similar mailbox protocol patterns but use newer `reg...` headers, so this file anchors the MP 9.0 naming and offset convention.

## Risks

- MP0 mailbox offsets are critical PSP boot registers. A wrong value can prevent secure OS loading, ring creation, reset completion, or IH rerouting.
- The MP 9.0 header uses `mm...` symbols and base index `0`, unlike newer MP headers. Mechanical porting to `reg...` names or other base indices can break address calculation.
- C2PMSG register numbers have firmware-defined roles. Swapping `C2PMSG_64`, `69`, `70`, `71`, `101`, `102`, or `103` changes command semantics and may hang the PSP.
- The file does not describe protocol bit meanings such as response bit 31. Consumers must use the correct firmware-specific masks and wait conditions.
- Pairing this offset header with a newer shift/mask header can compile only if names overlap, but the interrupt field layout may be incompatible.

## Test Signals

- Compile coverage of `psp_v3_1.c`, `mxgpu_ai.c`, and `soc15.c` catches missing offset names.
- Vega/MP 9.0 hardware boot tests should load sysdrv and SOS firmware, create/destroy PSP rings, and complete mode1 reset without PSP wait timeouts.
- SR-IOV tests should cover the alternate C2PMSG_101/102/103 ring path.
- Register traces should verify MP0 mailbox writes at offsets `0x0060` through `0x00a7` and MP1 mailbox writes at `0x0260` through `0x02a7` when those paths run.
- Failure diagnostics should capture the C2PMSG status registers used in waits, especially `mmMP0_SMN_C2PMSG_35`, `64`, `81`, and `101`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_9_0_offset.h -->
