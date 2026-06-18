<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_9_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_9_0_sh_mask.h

## Purpose

`mp_9_0_sh_mask.h` is the MP 9.0 bitfield companion to `mp_9_0_offset.h`. It defines shifts and masks for MP0/MP1 SMN mailbox registers, active-function ID registers, software interrupt registers, public scratch/message registers, interrupt status/enable registers, clock/light-sleep controls, firmware flags, and MP1 public reset control. It lets older AMDGPU PSP/SMU code use `REG_SET_FIELD`, `REG_GET_FIELD`, and direct mask checks against MP 9.0 hardware registers.

## Important APIs, Types, And Macros

The file exports macros only. There are no functions, structs, enums, or runtime variables.

Important macro groups:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103` and `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_103`, each with full-width `CONTENT`.
- MP1 client response registers `MP1_SMN_ACP2MP_RESP`, `MP1_SMN_DC2MP_RESP`, `MP1_SMN_UVD2MP_RESP`, `MP1_SMN_VCE2MP_RESP`, and `MP1_SMN_RLC2MP_RESP`, each full-width.
- `MP0_SMN_ACTIVE_FCN_ID`, `MP1_SMN_ACTIVE_FCN_ID`, `MP0_ACTIVE_FCN_ID`, and `MP1_ACTIVE_FCN_ID`, with `VFID` in bits `3:0` and `VF` at bit `31`.
- SMN interrupt fields for MP0 and MP1: `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL`. In the SMN variants, `IH_SW_INT.VALID` is bit `0`, `ID` is bits `8:1`, and control fields are named `SW_TRIG_MASK` and `SW_INT_ACK`.
- Public interrupt fields for MP0 and MP1: `MP0_IH_SW_INT`, `MP1_IH_SW_INT`, `MP0_IH_SW_INT_CTRL`, and `MP1_IH_SW_INT_CTRL`. In these variants, `ID` is bits `7:0`, `VALID` is bit `8`, and control fields are named `INT_MASK` and `INT_ACK`.
- MP0 public registers: `MP0_SOC_INFO`, `MP0_PUB_SCRATCH0` through `3`, `MP0_FW_INTF.SS_SECURE`, `MP0_C2PMSG_0` through `103`, `MP0_P2CMSG_0` through `3`, `MP0_P2CMSG_INTEN`, `MP0_P2CMSG_INTSTS`, C2PMSG attribute registers, P2S/S2P message registers, and P2S interrupt status.
- MP1 public registers: `MP1_FIRMWARE_FLAGS`, `MP1_PUB_SCRATCH0` through `3`, `MP1_C2PMSG_0` through `103`, `MP1_P2CMSG_*`, `MP1_P2SMSG_*`, response registers, `MP1_FPS_CNT`, `MP1_PUB_CTRL`, and `MP1_EXT_SCRATCH0` through `7`.
- Miscellaneous control fields: `CGTT_DRM_CLK_CTRL0` for clock delay/divider/soft override bits and `DRM_LIGHT_SLEEP_CTRL.MEM_LIGHT_SLEEP_EN`.

## Control Flow

There is no local control flow. Runtime behavior appears in consumers:

- `amdgpu/psp_v3_1.c` checks `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` in `psp_v3_1_smu_reload_quirk()` after reading a hard-coded MP1 public firmware-flag address.
- PSP boot and ring flows use the offset header for full-width C2PMSG reads/writes; the full-width content masks here document that those registers are payload registers rather than structured bitfields.
- Other SOC15-era SMU code uses similar MP1 interrupt masks to set interrupt IDs, mask/unmask software interrupts, and acknowledge firmware-to-host interrupts.

The main control-flow risk is that MP 9.0 has both SMN-prefixed and public non-SMN interrupt field families, with different bit positions and field names.

## State And Persistence Behavior

The header is stateless. The described registers carry hardware state:

- C2PMSG, P2CMSG, P2SMSG, and S2PMSG registers are mailbox payloads whose persistence is limited to the hardware register lifetime and firmware protocol.
- P2C/P2S interrupt enable and status fields expose interrupt routing and pending status for message channels.
- Active function ID registers expose current SR-IOV VF/PF identity.
- Firmware flags indicate interrupt readiness and other firmware-owned status.
- Public scratch and extended scratch registers are persistent scratch slots until overwritten or reset.
- Clock and light-sleep fields control or report power/clock behavior.

The driver must provide synchronization and sequencing around all writes; this header only supplies bit positions.

## Dependencies

Consumers depend on:

- Matching offsets from `mp_9_0_offset.h`.
- AMDGPU bitfield helpers that consume the `<REG>__<FIELD>_MASK` and `<REG>__<FIELD>__SHIFT` naming convention.
- SOC15 and PCIe register access helpers.
- PSP/SMU firmware protocols that define mailbox values, response bits, and wait conditions.

The include guard is `_mp_9_0_SH_MASK_HEADER`.

## Integration Points

Direct integration found in this tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c` includes this header and uses `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` for SMU reload behavior.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v3_1.c` also relies on the full-width C2PMSG model while programming MP0 mailboxes from `mp_9_0_offset.h`.
- Older SW SMU code uses the same logical MP1 firmware flag and interrupt field patterns, while newer MP headers rename or reposition some fields. This file is the MP 9.0 source of truth for Vega-era mask definitions.

## Risks

- The file contains similarly named SMN and non-SMN/public field families with different layouts. Using `MP1_SMN_IH_SW_INT` field assumptions on `MP1_IH_SW_INT`, or the reverse, will set `VALID`, `ID`, mask, or ACK bits incorrectly.
- The full-width mailbox masks do not encode protocol ownership. Driver code can write any 32-bit value even when firmware expects only specific command IDs, address halves, or response values.
- Reserved and attribute masks should not be treated as stable software feature fields unless the firmware/register specification explicitly says so.
- Cross-generation reuse is dangerous. MP 15.0.8 uses newer `reg...` offsets and its SMN `IH_SW_INT` layout matches the public-style ID/VALID ordering, not the MP 9.0 SMN layout.
- Clock and light-sleep masks are exposed in the same header as PSP/SMU mailbox masks, so broad includes can make unrelated low-power fields available to code that should not touch them.

## Test Signals

- Compile coverage of `psp_v3_1.c` verifies the firmware flag macro names and offset/mask pairing.
- PSP boot tests on MP 9.0 hardware should confirm mailbox handshakes for sysdrv load, SOS load, ring creation, ring destruction, and mode1 reset.
- SR-IOV tests should verify `ACTIVE_FCN_ID` decoding and the C2PMSG_101-based ring path.
- Interrupt tests should explicitly validate both SMN and public interrupt field layouts if both access paths are used.
- Register dumps on failure should decode `MP1_FIRMWARE_FLAGS`, C2PMSG payload registers, P2C/P2S interrupt status, and active function fields using this header's masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_9_0_sh_mask.h -->
