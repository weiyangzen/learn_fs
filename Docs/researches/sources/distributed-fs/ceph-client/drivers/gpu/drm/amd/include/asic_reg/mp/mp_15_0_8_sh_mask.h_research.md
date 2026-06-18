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
