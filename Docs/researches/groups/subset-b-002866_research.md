# subset-b-002866 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_offset.h

## Purpose

`mp_15_0_8_offset.h` is a generated AMDGPU register-offset contract for the MP 15.0.8 block. It gives symbolic names and SOC15 base-index selectors for MP1, MPASP, MPRAS, MPIFOE, and MPIO mailbox, interrupt, scratch, public-control, and firmware-flag registers. The file contains no executable code; its job is to let PSP/SMU driver code address hardware registers through `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PCIe/SMN access paths without embedding raw offsets at each call site.

## Important APIs, Types, And Macros

The file exports preprocessor constants only. There are no functions, structs, enums, or data objects.

Important macro groups:

- `regMP1_SMN_C2PMSG_0` through `regMP1_SMN_C2PMSG_175`, all in the `mp_SmuMp1_SmnDec` address block, with `_BASE_IDX` value `2`. These are the command/message mailbox registers used by host-to-MP1 and firmware-to-host protocols.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_PUB_CTRL`, also under MP1 SMN decode with base index `2`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, a contiguous external scratch range at offsets `0x01c0` through `0x01df`.
- `regMPASP_SMN_C2PMSG_0` through `regMPASP_SMN_C2PMSG_175`, plus MPASP interrupt-credit and software-interrupt registers, in the `mp_SmuMpASP_SmnDec` address block with `_BASE_IDX` value `1`.
- Firmware-flag aliases for CRU0 public decode: `regMPRAS_CRU0_MPRAS_FIRMWARE_FLAGS`, `regMPIFOE_CRU0_MPIFOE_FIRMWARE_FLAGS`, `regMP1_CRU0_MP1_FIRMWARE_FLAGS`, and `regMPIO_CRU0_MPIO_FIRMWARE_FLAGS`, all offset `0xbeb009` with `_BASE_IDX` `3`.
- Firmware-flag aliases for MMIO public decode: `regMPRAS_CRU1_MPRAS_FIRMWARE_FLAGS`, `regMPIFOE_CRU1_MPIFOE_FIRMWARE_FLAGS`, `regMP1_CRU1_MP1_FIRMWARE_FLAGS`, and `regMPIO_CRU1_MPIO_FIRMWARE_FLAGS`, all offset `0x4009` but with block-specific base indices `9`, `26`, `6`, and `23`.

The header uses the `reg...` naming convention common to newer generated AMD register headers, unlike older MP 9.0 headers that use many `mm...` names.

## Control Flow

There is no local control flow. Runtime flow is supplied by consumers. In this tree, `pm/swsmu/smu15/smu_v15_0_8_ppt.c` includes this header and uses `regMP1_SMN_IH_SW_INT_CTRL` and `regMP1_SMN_IH_SW_INT` when processing, masking, unmasking, and acknowledging MP1 software interrupts. That flow reads a register with `RREG32_SOC15(MP1, 0, reg...)`, updates fields with masks from `mp_15_0_8_sh_mask.h`, and writes the value back with `WREG32_SOC15`.

`amdgpu/psp_v15_0_8.c` also includes this header so PSP code can use the same generated MP 15.0.8 register names. SMU firmware-status checks combine a hard-coded MP1 public base with an SMN firmware-flag offset and decode the result using the companion mask header.

## State And Persistence Behavior

The header itself is stateless and compile-time only. The named registers represent live hardware state:

- C2PMSG registers carry mailbox commands, parameters, responses, status flags, ring addresses, and firmware protocol values. Their contents persist in hardware registers until overwritten, reset, or changed by firmware.
- IH software-interrupt registers store interrupt IDs, validity bits, mask state, acknowledgement state, and credit values.
- External scratch registers provide firmware/driver scratch state whose lifetime is tied to the MP block and GPU reset/power state.
- Public firmware flag registers expose whether firmware has enabled interrupts and may be read during PSP/SMU bring-up, resume, reset, and reload paths.

The driver, not this header, is responsible for ordering, polling, and ownership rules around these registers.

## Dependencies

Consumers depend on:

- `mp_15_0_8_sh_mask.h` for field layouts inside the registers named here.
- SOC15 register-access helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, and `WREG32_SOC15`.
- PCIe/SMN register access helpers such as `RREG32_PCIE` where code builds absolute public-register addresses.
- The generated AMD register convention that `<register>_BASE_IDX` selects the register base segment used by SOC15 helpers.

The include guard is `_mp_15_0_8_OFFSET_HEADER`.

## Integration Points

Direct integration found in this source tree:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/swsmu/smu15/smu_v15_0_8_ppt.c` includes this file for MP1 interrupt-control register access and MP1 firmware-status checks.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/psp_v15_0_8.c` includes this file for PSP-side MP 15.0.8 register access.
- The offsets mirror nearby generation families such as `mp_15_0_0_offset.h`, but MP 15.0.8 has its own base-index assignments and MPASP/RAS/IFOE/IO public flag layout.

## Risks

- Register-map drift is high impact. A wrong offset or `_BASE_IDX` can route reads/writes to another hardware block or to the wrong instance of an MP public window.
- Version confusion is likely because many MP generations expose similarly named C2PMSG and interrupt registers with different prefixes, offsets, or base indices. MP 15.0.8 consumers must not silently substitute MP 15.0.0, 14.x, 13.x, or 9.0 constants.
- Mailbox registers are protocol registers. Incorrect writes can wedge PSP/SMU boot, command submission, interrupt routing, or reset/unload flows.
- The CRU0 and CRU1 firmware-flag macros deliberately reuse the same offsets across multiple public blocks with different base indices. Callers must use the correct block name and access path.
- The header gives no locking, bounds, or sequencing rules. Callers must coordinate with firmware and higher-level SMU/PSP state machines before changing interrupt masks, acknowledgements, or mailbox contents.

## Test Signals

- Compile coverage of `smu_v15_0_8_ppt.c` and `psp_v15_0_8.c` catches missing or renamed macros.
- Hardware bring-up should verify that `smu_v15_0_8_check_fw_status()` reads the expected MP1 firmware flag and that interrupt enablement is detected.
- SMU interrupt tests should exercise enable, disable, and ACK paths for `regMP1_SMN_IH_SW_INT` and `regMP1_SMN_IH_SW_INT_CTRL`.
- PSP/SMU mailbox tests should confirm C2PMSG command/response polling reaches expected completion bits and does not time out after reset or resume.
- Register traces can validate the computed SOC15 addresses for base indices `1`, `2`, `3`, `6`, `9`, `23`, and `26`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_sh_mask.h

## Purpose

`mp_15_0_8_sh_mask.h` is the companion bitfield contract for `mp_15_0_8_offset.h`. It defines `__SHIFT` and `_MASK` macros for MP 15.0.8 C2PMSG content fields, interrupt-credit fields, software-interrupt fields, public-control reset fields, scratch data fields, and firmware-flag bits. Driver code uses these macros through AMDGPU helpers such as `REG_SET_FIELD` and direct mask tests to encode and decode 32-bit MP registers.

## Important APIs, Types, And Macros

The file exports macros only. There are no functions, structs, enums, or runtime objects.

Important macro groups:

- `MP1_SMN_C2PMSG_0` through `MP1_SMN_C2PMSG_127` each define a full-width `CONTENT` field at shift `0` with mask `0xFFFFFFFFL`. The offset header defines MP1 C2PMSG registers through 175, but this mask header only supplies explicit full-content masks through 127 for MP1.
- `MP1_SMN_IH_CREDIT` fields: `CREDIT_VALUE` in bits `1:0` and `CLIENT_ID` in bits `23:16`.
- `MP1_SMN_IH_SW_INT` fields: `ID` in bits `7:0` and `VALID` at bit `8`.
- `MP1_SMN_IH_SW_INT_CTRL` fields: `INT_MASK` at bit `0` and `INT_ACK` at bit `8`.
- `MP1_SMN_FPS_CNT` full-width `COUNT`, `MP1_SMN_PUB_CTRL` one-bit `LX3_RESET`, and `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH31` full-width `DATA`.
- `MPASP_SMN_C2PMSG_81` full-width `CONTENT`, plus MPASP interrupt-credit, software-interrupt, and interrupt-control fields with the same layout as the MP1 SMN equivalents.
- Firmware-flag fields for `MPRAS`, `MPIFOE`, `MP1`, and `MPIO`, both CRU0 and CRU1: `INTERRUPTS_ENABLED` at bit `0` and `RESERVED` covering bits `31:1`.

## Control Flow

There is no local control flow. The control-flow significance comes from how consumers use the masks:

- `smu_v15_0_8_check_fw_status()` reads MP1 firmware flags and tests `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` shifted by `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED__SHIFT`. Failure returns `-EIO`.
- `smu_v15_0_8_irq_process()` acknowledges SMU-to-host interrupts by setting `MP1_SMN_IH_SW_INT_CTRL.INT_ACK` to `1`.
- `smu_v15_0_8_set_irq_state()` disables interrupts by setting `MP1_SMN_IH_SW_INT_CTRL.INT_MASK` and enables them by programming `MP1_SMN_IH_SW_INT.ID` to `0xFE`, clearing `VALID`, and clearing `INT_MASK`.

These flows depend on the field layout here matching silicon and firmware expectations exactly.

## State And Persistence Behavior

The header is stateless. The fields describe state in MP hardware registers:

- C2PMSG and scratch fields are full-width payload slots. Their semantics are defined by the PSP/SMU firmware protocol, not by this header.
- `IH_SW_INT` and `IH_SW_INT_CTRL` fields control pending software interrupt IDs, valid state, masking, and acknowledgement. Values can affect live interrupt delivery.
- `IH_CREDIT` fields expose or program interrupt-handler credit accounting for a client.
- Firmware flag bits are persistent hardware/firmware-visible status until firmware changes them or the device resets.
- Public-control reset fields can alter MP block reset state if used by a consumer.

## Dependencies

Consumers depend on:

- Matching register offsets in `mp_15_0_8_offset.h`.
- AMDGPU bitfield helper naming conventions. For example, `REG_SET_FIELD(data, MP1_SMN_IH_SW_INT_CTRL, INT_ACK, 1)` requires `MP1_SMN_IH_SW_INT_CTRL__INT_ACK_MASK` and `MP1_SMN_IH_SW_INT_CTRL__INT_ACK__SHIFT`.
- PSP/SMU firmware protocol definitions that assign meaning to C2PMSG and scratch payloads.
- SOC15 and PCIe register access helpers for the actual reads and writes.

The include guard is `_mp_15_0_8_SH_MASK_HEADER`.

## Integration Points

Direct integration found in this tree:

- `pm/swsmu/smu15/smu_v15_0_8_ppt.c` includes the header and uses MP1 interrupt-control and firmware-flag fields.
- `amdgpu/psp_v15_0_8.c` includes the header for PSP firmware handshakes on this ASIC family.
- Related SMU 14/15 code uses the same logical field names for interrupt setup, so this header must stay consistent with common `smu_v15_0.c` expectations while preserving MP 15.0.8-specific names such as `LX3_RESET` and `MP1_CRU1_MP1_FIRMWARE_FLAGS`.

## Risks

- Field-layout mismatch can break interrupts without compile errors. For example, if `VALID` or `INT_ACK` moved, `REG_SET_FIELD` would still compile but write the wrong bit.
- The MP 9.0 SMN software interrupt layout differs: MP 9.0 `MP1_SMN_IH_SW_INT` puts `VALID` at bit `0` and `ID` at bits `8:1`, while MP 15.0.8 puts `ID` at bits `7:0` and `VALID` at bit `8`. Reusing old assumptions would corrupt interrupt programming.
- Only `MPASP_SMN_C2PMSG_81` gets a mask entry even though the offset header lists a broad MPASP C2PMSG range. New consumers of other MPASP C2PMSG registers may need generated masks or direct full-width access.
- Full-width `CONTENT` and `DATA` masks do not validate firmware protocol values. Callers must ensure command IDs, addresses, and response bits are legal for the firmware version.
- `RESERVED` masks should not be treated as writable feature fields.

## Test Signals

- Build coverage catches missing field names in SMU/PSP consumers.
- SMU interrupt tests should verify that enabling interrupts causes MP1 events to arrive and that ACK through `INT_ACK` prevents repeated stale interrupts.
- Firmware-status tests should validate that `INTERRUPTS_ENABLED` is detected after PMFW initialization and fails cleanly when firmware is not ready.
- Hardware register traces should confirm writes to `IH_SW_INT` produce ID `0xFE` in bits `7:0` and keep `VALID` clear during enable setup.
- Regression tests should compare MP 15.0.8 against MP 15.0.0 and MP 9.0 layouts to catch accidental cross-generation mask reuse.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_15_0_8_sh_mask.h -->

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
