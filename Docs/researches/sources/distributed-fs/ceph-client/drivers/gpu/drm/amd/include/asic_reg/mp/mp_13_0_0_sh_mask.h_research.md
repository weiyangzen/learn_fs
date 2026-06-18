# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_0_sh_mask.h

## Purpose

`mp_13_0_0_sh_mask.h` defines field shifts and masks for MP 13.0.0 registers. It is used with `mp_13_0_0_offset.h` so AMDGPU code can address a register and then safely isolate, set, or preserve individual fields in that register value.

The header covers MP0 and MP1 SMN-decoded mailbox/interrupt registers, MP1 SMN scratch/control registers, MP1 public firmware flags, and MPIO public firmware flags.

## Important APIs, Types, And Macros

This header exports preprocessor constants only.

Important macro families:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`: full-width `CONTENT` fields with shift `0x0` and mask `0xFFFFFFFFL`.
- `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_127`: full-width MP1 SMN mailbox payload fields.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT`: `CREDIT_VALUE` in low two bits and `CLIENT_ID` in bits 23:16.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT`: 8-bit `ID` plus `VALID` bit at bit 8.
- `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL`: `INT_MASK` bit 0 and `INT_ACK` bit 8.
- `MP1_SMN_FPS_CNT`: full-width `COUNT`.
- `MP1_SMN_PUB_CTRL`: `LX3_RESET` bit 0, a sensitive control field for MP1 public control.
- `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH31`, with no scratch 9 macro: full-width `DATA` fields.
- `MP1_FIRMWARE_FLAGS` and `MPIO_FIRMWARE_FLAGS`: `INTERRUPTS_ENABLED` bit 0 and `RESERVED` bits 31:1.

## Control Flow

There is no executable flow. The include guard `_mp_13_0_0_SH_MASK_HEADER` is the only compile-time control structure. Runtime sequencing is owned by caller code that performs read-modify-write operations or extracts fields after reading hardware registers.

## State And Persistence Behavior

The header does not store state. It describes bit layouts of hardware state held by MP/SMU registers. Mailbox `CONTENT` fields carry transient protocol payloads, interrupt fields reflect interrupt routing/status, scratch registers provide firmware/driver communication storage, and firmware flags report or control firmware interrupt state. Durability is limited to the device/firmware behavior of those registers.

## Dependencies And Integration Points

The file depends on the C preprocessor and on consumers following AMD's register macro naming convention. It integrates with:

- `mp_13_0_0_offset.h`, whose register names match these field-prefix names.
- AMDGPU SMU mailbox routines that consume `C2PMSG` content fields.
- Interrupt handling paths that manipulate `IH_SW_INT`, `IH_SW_INT_CTRL`, and credit fields.
- Firmware initialization/reset code that may use `MP1_SMN_PUB_CTRL__LX3_RESET_MASK`.
- Diagnostics or firmware protocol code that reads/writes MP1 extended scratch registers.
- MPIO firmware code that distinguishes `MPIO_FIRMWARE_FLAGS` from `MP1_FIRMWARE_FLAGS`.

## Risks And Maintenance Notes

The main correctness risk is using the correct field set for the correct ASIC offset set. The MP 13.0.0 mask header includes `MP1_SMN_PUB_CTRL`, scratch registers through `EXT_SCRATCH31`, and `MPIO_FIRMWARE_FLAGS`; those fields should not be assumed present on every MP 13 variant.

Read-modify-write callers must use masks to preserve reserved bits, especially in `FIRMWARE_FLAGS` and `PUB_CTRL`. `LX3_RESET` is particularly risky because an unintended write could reset MP1 microcontroller state. Full-width `CONTENT` and `DATA` fields do not protect callers from protocol-level mistakes: writing the wrong mailbox or scratch register can still break SMU firmware sequencing.

## Test Signals

Relevant test signals include:

- Compile coverage for all MP 13.0.0 consumers.
- Static generated-header comparison confirming every offset register has matching field macros.
- Hardware mailbox tests that validate `C2PMSG` command/response behavior.
- Interrupt tests covering `VALID`, `INT_ACK`, and credit handling.
- Firmware reset/scratch diagnostics that verify `MP1_SMN_PUB_CTRL` and extended scratch fields are accessed only on supported ASICs.
