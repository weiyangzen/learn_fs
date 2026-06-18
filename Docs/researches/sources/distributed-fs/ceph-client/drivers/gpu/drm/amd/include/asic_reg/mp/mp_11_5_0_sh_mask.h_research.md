# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_sh_mask.h

## Purpose

`mp_11_5_0_sh_mask.h` is the generated field mask/shift companion to `mp_11_5_0_offset.h`. It describes the bit layout of MP0/MP1 SMN and MP1 public CRU registers for MP 11.5.0 hardware. It is used by display and SMU-facing code to extract mailbox response fields, interrupt state, firmware flags, and scratch/control fields without local numeric bit constants.

The file is preprocessor-only and has no functions or types. Its correctness is part of the ABI between AMDGPU driver code and the GPU firmware/hardware register map.

## Important APIs, Types, and Macros

The header exports 617 `#define` entries. Major exported groups are:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`, each with full-width `CONTENT` fields.
- `MP0_SMN_IH_CREDIT`, `MP0_SMN_IH_SW_INT`, and `MP0_SMN_IH_SW_INT_CTRL`, with the same `CREDIT_VALUE`, `CLIENT_ID`, `ID`, `VALID`, `INT_MASK`, and `INT_ACK` field pattern as nearby MP generations.
- `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_103`, again full-width `CONTENT` fields.
- `MP1_SMN_IH_CREDIT`, `MP1_SMN_IH_SW_INT`, `MP1_SMN_IH_SW_INT_CTRL`, `MP1_SMN_FPS_CNT`, and `MP1_SMN_EXT_SCRATCH0` through `MP1_SMN_EXT_SCRATCH7`.
- `MP1_CRU1_MP1_FIRMWARE_FLAGS`, `MP1_CRU1_MP1_PUB_SCRATCH0` through `MP1_CRU1_MP1_PUB_SCRATCH3`, `MP1_CRU1_MP1_C2PMSG_0` through `MP1_CRU1_MP1_C2PMSG_103`, P2C/P2S/S2P message fields, interrupt status fields, and external scratch fields under the `mp_SmuMp1Pub_CruDec` address block.

Most mailbox and scratch fields are `CONTENT` or `DATA` at shift `0x0` with mask `0xFFFFFFFFL`. Important narrow fields include:

- `MP1_CRU1_MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` and `...__SHIFT`.
- `MP1_CRU1_MP1_P2CMSG_INTEN__INTEN_MASK`.
- `MP1_CRU1_MP1_P2CMSG_INTSTS__INTSTS0..3_MASK`.
- `MP1_CRU1_MP1_P2SMSG_INTSTS__INTSTS0..3_MASK`.
- interrupt helper fields for MP0/MP1 SMN `IH_*` registers.

## Control Flow and Runtime Behavior

There is no local control flow. Runtime behavior is in consuming SMU/display code.

The direct observed consumer, `display/dc/clk_mgr/dcn301/dcn301_smu.c`, includes this header with `mp_11_5_0_offset.h`, defines `FN(reg_name, field)` as `FD(reg_name##__##field)`, and uses display register helpers to wait for SMU mailbox responses and send messages. The code path mainly reads/writes full `CONTENT` registers, so the field definitions matter both for helper compatibility and any future masked updates.

The CRU1 `FIRMWARE_FLAGS`, interrupt status, and scratch definitions also make the header usable in broader MP1 firmware-status and interrupt paths if this ASIC generation needs those checks.

## State and Persistence Behavior

The header itself is stateless. It describes device state in:

- command, response, and parameter mailboxes;
- firmware interrupt-enabled state;
- interrupt enable/status/ack bits;
- public and external scratch registers;
- frame or frequency-related counters such as `FPS_CNT`.

Mailbox state is inherently persistent across a command transaction until firmware or driver code updates the relevant register. Full-width `CONTENT` masks mean callers can preserve or replace entire register payloads.

## Dependencies and Integration Points

This header must be synchronized with:

- `mp_11_5_0_offset.h`, which provides the `mmMP0_SMN_*` and `mmMP1_SMN_*` offsets.
- Display-core register-helper macros `FD`, `REG_READ`, `REG_WRITE`, and any masked update helpers that derive field names from `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT`.
- Firmware message protocols in code such as `dcn301_smu.c`, where C2PMSG indices have semantic meaning: response register `91`, parameter register `83`, and message trigger register `67`.

The CRU1 macro namespace is distinct from the SMN namespace. Consumers must pass the exact register name expected by the helper macro; `MP1_SMN_C2PMSG_91` and `MP1_CRU1_MP1_C2PMSG_91` are different macro prefixes.

## Risks and Edge Cases

- Field-header and offset-header drift is the main risk. A register can compile with a field name from one block and an address from another if code mixes generations or namespaces incorrectly.
- The file contains MP1 CRU public fields that are not represented by the direct `mmMP1_SMN_*` offset set in the 11.5.0 offset header. Those fields require the correct address source from another matching offset namespace.
- Full-width masks hide semantic constraints. For example, C2PMSG contents are 32-bit payloads, but firmware protocols may accept only certain command or parameter values.
- Interrupt status fields are bit-granular; using the full register as a payload field where status bits are expected could clear or acknowledge unintended bits depending on hardware write semantics.
- The header is generated and repetitive, so manual edits are especially risky. Format deviations could break macro-generation assumptions or make future diffs difficult.

## Test Signals

Validation signals include:

- Build display DCN301 SMU code and any MP 11.5.0 firmware-status consumers with both offset and mask headers.
- Exercise `dcn301_smu_wait_for_response()` and message-send paths for display clock, DPP clock, DPREF clock, DCFCLK, FCLK, and table-transfer operations.
- Confirm that `FN(MP1_SMN_C2PMSG_91, CONTENT)`-style macro expansion succeeds if masked helpers are used.
- Runtime failures usually surface as SMU response busy timeouts, unknown/rejected VBIOS SMC messages, bad display clock programming, or missing firmware-interrupt readiness.
