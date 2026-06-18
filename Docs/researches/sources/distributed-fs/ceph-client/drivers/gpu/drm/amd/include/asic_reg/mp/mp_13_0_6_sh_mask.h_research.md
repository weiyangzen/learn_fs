# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_sh_mask.h

## Purpose

`mp_13_0_6_sh_mask.h` defines bit shifts and masks for the MP 13.0.6 registers named in the companion offset header. It lets driver code encode and decode full-register mailbox payloads, interrupt-credit fields, software-interrupt fields, firmware flags, scratch data, and a small set of MCA-style 64-bit status fields.

The file uses `_mp_13_0_6_SH_MASK_HEADER` as its include guard. It contains no executable code and exports only preprocessor constants.

## Important APIs, Types, And Macros

The main exported groups are:

- `MP0_SMN_C2PMSG_32__CONTENT__SHIFT` through `MP0_SMN_C2PMSG_103__CONTENT_MASK`, all representing a 32-bit `CONTENT` field at shift `0x0` with mask `0xFFFFFFFFL`.
- `MP1_SMN_C2PMSG_32__CONTENT__SHIFT` through `MP1_SMN_C2PMSG_127__CONTENT_MASK`, also full 32-bit mailbox payload fields.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` fields: `CREDIT_VALUE` at shift `0x0` with mask `0x00000003L`, and `CLIENT_ID` at shift `0x10` with mask `0x00FF0000L`.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT` fields: `ID` at shift `0x0` and `VALID` at shift `0x8`.
- `MP0_SMN_IH_SW_INT_CTRL` and `MP1_SMN_IH_SW_INT_CTRL` fields: `INT_MASK` at shift `0x0` and `INT_ACK` at shift `0x8`.
- `MP1_SMN_FPS_CNT__COUNT`, `MP1_SMN_PUB_CTRL__LX3_RESET`, and `MP1_SMN_EXT_SCRATCHn__DATA` for scratch registers 0-8 and 10-31.
- `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED` and `MP1_FIRMWARE_FLAGS__RESERVED`.
- 64-bit MCA field masks for `MCMP1_IPIDT0`, `MCMP1_STATUST0`, and `MCMP1_MISC0T0`.

No structs or inline helpers are provided. Consumers usually apply these masks with shifts manually or through AMD register helper macros such as `FD()`.

## Control Flow

The header has no runtime control flow. It influences control paths in consumers that branch on decoded fields, for example PMFW readiness checks that test `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`, software interrupt control that sets or acknowledges interrupt bits, and MCA/RAS paths that test status-valid, uncorrected, or processor-context-corrupt bits.

## State And Persistence

The file stores no state. Its constants describe how hardware state is represented. Mailbox `CONTENT` fields are 32-bit opaque values whose persistence depends on firmware mailbox protocol and reset behavior. Firmware flags are status bits set by MP1 firmware. MCA fields describe error-reporting state and may persist until firmware, hardware, or driver code clears the related status registers.

## Dependencies And Integration Points

This mask header is coupled to `mp_13_0_6_offset.h`; a field macro is meaningful only when used with the corresponding register address. It is included by `smu13/smu_v13_0_6_ppt.c` for PMFW status and by `umc_v12_0.c` for MCA decoding. It follows the same naming pattern as older MP mask files, so common AMDGPU code can refer to stable names such as `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`.

The MCA field macros are notable because they are 64-bit masks with `L` suffixes. On 64-bit Linux builds this is normally safe, but code should use 64-bit storage when reading or combining these fields.

## Risks

The biggest risk is using a mask with the wrong ASIC generation or wrong offset header. Most mailbox fields are full-width, so a wrong mapping may still compile and look plausible while addressing the wrong register. The firmware flag mask names are shared across generations, but the register address can differ or be overridden by consumers.

The MCA masks require correct width handling. If a consumer truncates these values to 32 bits, high status bits such as `PCC`, `UC`, and `Val` will be lost. Another risk is treating `RESERVED_MASK` bits as writable policy bits; they should be preserved or ignored according to hardware guidance.

## Test Signals

Build coverage should compile all consumers with `-Wshift-count-overflow` and related warnings cleanly. Runtime signals include PMFW readiness checks passing, software interrupts being acknowledged without stuck bits, SMU mailbox requests completing, and RAS/MCA paths decoding valid/uncorrected error bits correctly during injected or real error events.
