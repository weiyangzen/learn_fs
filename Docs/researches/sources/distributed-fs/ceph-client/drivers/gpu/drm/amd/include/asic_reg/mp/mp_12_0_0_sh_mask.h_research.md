# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_sh_mask.h

## Purpose

`mp_12_0_0_sh_mask.h` defines shift and mask macros for MP 12.0.0 SMU/MP message, interrupt, and firmware flag registers. It complements an offset header for the same ASIC generation: callers use register address macros from an offset header and these `__SHIFT`/`_MASK` macros to pack or extract fields in 32-bit MMIO/SMN register values.

The header covers four documented address blocks: `mp_SmuMp0_SmnDec`, `mp_SmuMp1_SmnDec`, `mp_SmuMp0Pub_CruDec`, and `mp_SmuMp1Pub_CruDec`. Most mailbox registers are full-width payload words, while interrupt and firmware-control registers expose smaller bitfields.

## Important APIs, Types, And Macros

This file exports only preprocessor constants; there are no C types, functions, inline helpers, or storage definitions.

Important macro families:

- `MP0_SMN_C2PMSG_32` through `MP0_SMN_C2PMSG_103`: each has `__CONTENT__SHIFT` set to `0x0` and `__CONTENT_MASK` set to `0xFFFFFFFFL`.
- `MP1_SMN_C2PMSG_32` through `MP1_SMN_C2PMSG_103`: same full-width `CONTENT` field pattern for the MP1 SMN block.
- `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT`: define `CREDIT_VALUE` in bits 1:0 (`0x00000003L`) and `CLIENT_ID` at shift `0x10` with mask `0x00FF0000L`.
- `MP0_SMN_IH_SW_INT` and `MP1_SMN_IH_SW_INT`: define an 8-bit software interrupt `ID` at shift `0x0` and a `VALID` bit at shift `0x8`.
- Public CRU interrupt macros `MP0_IH_CREDIT`, `MP0_IH_SW_INT`, `MP0_IH_SW_INT_CTRL`, `MP1_IH_CREDIT`, `MP1_IH_SW_INT`, and `MP1_IH_SW_INT_CTRL`: mirror credit/software-interrupt layouts and add control fields `INT_MASK` bit 0 and `INT_ACK` bit 8.
- `MP1_SMN_FPS_CNT` and `MP1_FPS_CNT`: expose a full-width `COUNT` field.
- `MP1_FIRMWARE_FLAGS`: defines `INTERRUPTS_ENABLED` in bit 0 and the remaining bits as `RESERVED`.
- `MP1_C2PMSG_0` through `MP1_C2PMSG_103`, plus `MP1_P2CMSG_0` through `MP1_P2CMSG_3`: public MP1 message registers with full-width `CONTENT`.
- `MP1_P2CMSG_INTEN` and `MP1_P2CMSG_INTSTS`: expose four low interrupt enable/status bits.

## Control Flow

There is no executable control flow. The only compile-time flow is the include guard `_mp_12_0_0_SH_MASK_HEADER`, which prevents duplicate macro definitions within one translation unit.

Operational control flow is supplied by AMDGPU/SMU code that includes this header. Typical use is:

1. Read or construct a 32-bit register value.
2. Use a field `MASK` and `SHIFT` macro to isolate or position a value.
3. Write the value through the driver register access path for the matching MP 12.0.0 register offset.

## State And Persistence Behavior

The header owns no runtime state and performs no persistence. It describes hardware-backed register state: mailbox registers can carry host-to-firmware (`C2PMSG`) and firmware-to-host (`P2CMSG`) payloads, interrupt registers carry pending/valid/ack bits, and firmware flags expose interrupt enable state. Any persistence or volatility is entirely in the device registers and firmware protocol, not in this file.

## Dependencies And Integration Points

The file depends only on the C preprocessor. Its integration contract is naming consistency with AMD register access code and the matching MP 12.0.0 offset definitions. It is consumed by AMDGPU power-management, SMU, interrupt, and firmware message paths that need stable field encodings for MP registers.

Important integration points include:

- Register offset headers in the same `asic_reg/mp/` family.
- AMDGPU SMN/MMIO helpers that combine offset, base index, mask, and shift macros.
- Firmware mailbox protocols that assign semantic meanings to individual `C2PMSG` and `P2CMSG` registers.
- Interrupt handling code that uses `IH_SW_INT`, `IH_SW_INT_CTRL`, and credit fields.

## Risks And Maintenance Notes

The highest risk is ASIC-generation mismatch. MP 12.0.0 field macros should not be mixed with MP 13.x offsets unless the consuming code deliberately proves layout compatibility. Full-width `CONTENT` masks are easy to use, but interrupt control and firmware flag fields are small and can corrupt adjacent bits if a caller shifts or masks incorrectly.

The `L` suffix on masks means the literal type can vary with C data model; driver code should continue to use fixed-width register value types when combining these constants. Generated formatting also makes broad manual edits risky: a single off-by-one register name or copied mask can silently direct firmware traffic to the wrong mailbox.

## Test Signals

Useful validation is mostly compile-time and hardware/driver level:

- Build coverage for AMDGPU code paths that include MP 12.0.0 register headers.
- Preprocessor or static checks that each `__SHIFT` has the expected companion `_MASK`.
- Driver tests or bring-up logs showing SMU mailbox commands complete on MP 12.0.0 hardware.
- Interrupt-path tests that verify software interrupt `VALID`, `INT_ACK`, and credit handling still works.
- Register-dump comparisons against AMD-generated reference headers or ASIC documentation.
