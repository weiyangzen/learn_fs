# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_sh_mask.h

## Purpose

`mp_13_0_8_sh_mask.h` defines shift and mask macros for the MP 13.0.8 register offsets. It provides field layouts for mailbox content registers, MP0/MP1 interrupt handoff, MP1 frame/performance count, MP1 scratch registers 0-7, and MP1 firmware flags.

The file is guarded by `_mp_13_0_8_SH_MASK_HEADER` and exports only constants.

## Important APIs, Types, And Macros

Important macro groups include:

- `MP0_SMN_C2PMSG_32__CONTENT` through `MP0_SMN_C2PMSG_103__CONTENT`, all full 32-bit fields at shift `0x0`.
- `MP1_SMN_C2PMSG_32__CONTENT` through `MP1_SMN_C2PMSG_127__CONTENT`, also full 32-bit fields.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` fields for `CREDIT_VALUE` and `CLIENT_ID`.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT` fields for interrupt `ID` and `VALID`.
- `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL` fields for `INT_MASK` and `INT_ACK`.
- `MP1_SMN_FPS_CNT__COUNT`, using the full 32-bit register.
- `MP1_SMN_EXT_SCRATCH0__DATA` through `MP1_SMN_EXT_SCRATCH7__DATA`, full 32-bit scratch data.
- `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED` at bit 0 and `MP1_FIRMWARE_FLAGS__RESERVED` for the remaining bits.

No helper functions are supplied. Consumers must combine masks and shifts directly or through register-field helper macros.

## Control Flow

The header has no control flow. It affects consumer branching only when decoded fields are tested. Display clock-manager code includes this file with the 13.0.8 offset header so `FN(reg, field)` style helpers can refer to field definitions while SMU message code polls status and exchanges mailbox values.

## State And Persistence

No state is stored in the header. It documents hardware state encoding. Mailbox `CONTENT` fields are opaque 32-bit protocol values. Interrupt handoff fields describe pending interrupt and acknowledgement state. Scratch data fields expose firmware/driver scratch values. Firmware flags record PMFW readiness, with bit 0 indicating interrupts enabled.

## Dependencies And Integration Points

This file is tightly coupled to `mp_13_0_8_offset.h`. It is included by `display/dc/clk_mgr/dcn316/dcn316_smu.c`, whose local base-table and register helper macros turn these generated names into usable register addresses and fields. It follows the same field naming conventions as older MP generations, making shared SMU status logic easier to port.

Unlike `mp_13_0_6_sh_mask.h`, this file has no MCA field macros and no `MP1_SMN_PUB_CTRL` field. Code needing MCA status decoding or LX3 reset control must not assume this file provides those definitions.

## Risks

The most likely defect class is wrong-ASIC inclusion. The field names look highly similar across MP 13.0.x files, so a source file could compile while decoding the wrong register set. A second risk is assuming scratch registers beyond scratch7 exist because 13.0.6 exposes many more scratch fields.

The firmware flags field names are stable across many generations, but the address source is not. Consumers should validate both offset and mask header pairing, especially where code overrides `smnMP1_FIRMWARE_FLAGS`.

## Test Signals

Compile checks should catch missing field definitions in DCN316 SMU code. Runtime checks should include PMFW alive/version messages, clock frequency set/get commands, table transfer messages, and interrupt-ready paths. Display regressions, SMU timeouts, or stuck busy responses are strong signs of an offset/mask mismatch.
