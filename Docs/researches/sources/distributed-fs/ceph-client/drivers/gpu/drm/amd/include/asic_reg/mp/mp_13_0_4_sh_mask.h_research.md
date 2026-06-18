# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_4_sh_mask.h

## Purpose

This generated header defines bit shifts and masks for MP 13.0.4 register fields. It pairs with `mp_13_0_4_offset.h`: the offset header tells consumers where each register is, while this header tells them how to interpret or compose values inside those registers. It is part of AMDGPU's ASIC register-definition layer and contains no executable implementation.

The file is organized into `mp_SmuMp0_SmnDec` and `mp_SmuMp1_SmnDec`. MP0 field macros cover C2PMSG 32-103 and MP0 interrupt helper registers. MP1 field macros cover C2PMSG 32-127, MP1 interrupt helper registers, FPS count, and MP1 external scratch registers 0-7.

## Important APIs, Types, And Macros

The public API is a set of macros guarded by `_mp_13_0_4_SH_MASK_HEADER`. There are no C types or functions. Most `C2PMSG` registers are represented as a single full-width `CONTENT` field at shift `0x0` with mask `0xFFFFFFFFL`. This matches their mailbox role: command IDs, parameters, responses, ring addresses, and firmware-defined payloads are usually treated as opaque 32-bit words by the PSP or SMU firmware protocol.

The interrupt helper fields mirror the MP 13.0.2 shape. `MP0_SMN_IH_CREDIT` and `MP1_SMN_IH_CREDIT` expose `CREDIT_VALUE` and `CLIENT_ID`. `*_IH_SW_INT` exposes `ID` and `VALID`; `*_IH_SW_INT_CTRL` exposes `INT_MASK` and `INT_ACK`. `MP1_SMN_FPS_CNT__COUNT` and `MP1_SMN_EXT_SCRATCH0..7__DATA` are full-width fields.

Compared with MP 13.0.2, this header lacks the specialized MP0 `C2PMSG_126` boot/error subfields and lacks `MP1_FIRMWARE_FLAGS`. Compared with MP 13.0.5, it has only scratch registers 0-7 and no MP1 public firmware-flags block.

Inventory signal: the header contains 189 shift definitions and 191 mask definitions.

## Control Flow

There is no runtime control flow. The include guard prevents multiple definition. Runtime control flow belongs to consumers such as `amdgpu/psp_v13_0_4.c`. That code uses the matching offset header heavily for mailbox polling and writes. It includes this mask header to keep version-specific field definitions available for any field-based register operations and to match the standard PSP include pattern used by other PSP versions.

The relevant consumer control pattern is mailbox-oriented: wait for a bootloader-ready bit in an MP0 C2PMSG register, write a firmware memory address to another C2PMSG register, write a command value, delay or poll, then read a response or sign-of-life register. The field macros here are the symbolic bridge if code needs to mask or shift one of those response values.

## State And Persistence Behavior

This file has no internal state. The state it describes is hardware state inside MP0/MP1 mailbox and interrupt registers. Consumers may observe command responses, interrupt state, scratch data, and firmware counters. Writes are hardware side effects, not software persistence. Since most C2PMSG fields are full-width content, consumers are responsible for protocol-specific interpretation outside this header.

## Dependencies

The file depends only on the preprocessor but should be used with `mp_13_0_4_offset.h` and AMDGPU register access helpers. Consumers often use offsets with `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and PSP wait helpers. If field helper macros such as `FD`/`FN` are used, they depend on the naming convention provided here.

## Integration Points

The direct exact include site is `amdgpu/psp_v13_0_4.c`, which implements PSP 13.0.4 microcode loading and ring command handling. Although the visible register operations in that file primarily use register offsets and broader PSP response masks, this header supplies the version-matched field view for MP0/MP1 mailbox and interrupt registers. It is also part of the larger generated MP register header family, so tooling or driver additions can include it when adding field-based access for 13.0.4.

## Risks

The main risk is version skew with the offset header or hardware specification. Since the masks are mostly full-width, many mistakes would not be caught by build tests. Missing specialized fields are also a risk for maintainers: code ported from MP 13.0.2 must not assume `MP0_SMN_C2PMSG_126__GPU_ERR_*` definitions exist here. Code ported from MP 13.0.5 must not assume `MP1_FIRMWARE_FLAGS` or scratch registers beyond 7 exist here. Incorrect interrupt masks could cause lost, stuck, or falsely acknowledged firmware interrupts.

## Test Signals

Build coverage confirms macro availability and include compatibility. Runtime PSP 13.0.4 smoke tests should show firmware load, bootloader wait, SOS sign-of-life, and ring operations succeeding without C2PMSG timeouts. Static tests should compare the generated field list against the MP 13.0.4 register database, especially the absence of `MP1_FIRMWARE_FLAGS`, the MP1 scratch range, and the interrupt helper bit definitions.
