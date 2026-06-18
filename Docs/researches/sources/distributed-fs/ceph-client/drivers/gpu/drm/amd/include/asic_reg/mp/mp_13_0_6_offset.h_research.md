# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_6_offset.h

## Purpose

`mp_13_0_6_offset.h` declares register offset macros for the MP block on SMU/MP ASIC version 13.0.6. It is an address map, not an implementation unit. Consumers include it to form MMIO/SMN addresses for MP0 and MP1 command/message mailboxes, interrupt handoff registers, MP1 scratch registers, and an MP1 public firmware-flags register.

The header uses `_mp_13_0_6_OFFSET_HEADER` as an include guard and carries AMD's permissive license block. Address comments identify three generated register blocks: `aid_mp_SmuMp0_SmnDec`, `aid_mp_SmuMp1_SmnDec`, and `aid_mp_SmuMp1Pub_CruDec`, all with base address `0x0`.

## Important APIs, Types, And Macros

There are no C types or functions. The exported API is the macro namespace:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_103`, with offsets `0x0060` through `0x00a7`, plus matching `_BASE_IDX` macros set to `0`.
- `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL` at offsets `0x00c1` through `0x00c3`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_127`, with offsets `0x0260` through `0x02bf`, plus matching `_BASE_IDX` macros set to `0`.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, `regMP1_SMN_FPS_CNT`, and `regMP1_SMN_PUB_CTRL` at offsets `0x02c1` through `0x02c5`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31` at `0x0340` through `0x035f`, except scratch9 is absent.
- `regMP1_FIRMWARE_FLAGS` at `0xbee00a`.

Every listed register has a companion `reg..._BASE_IDX` macro, currently `0`. Consumer-side helpers such as `SOC15_REG_OFFSET()` or local `REG(reg_name)` macros combine the base index with an IP base table to compute the final address.

## Control Flow

The file has no runtime control flow. Build-time control flow is limited to include-guard selection. Runtime behavior is induced by consumers that use these constants to read or write PMFW/SMU mailbox registers. Typical flows include writing a message ID to a `C2PMSG` register, passing arguments through other mailbox registers, polling a response mailbox, and checking firmware interrupt readiness through `regMP1_FIRMWARE_FLAGS` or its hand-written SMN alias in PPT code.

## State And Persistence

The header itself stores no state. The macros name persistent hardware-visible registers. `C2PMSG` registers are command, argument, response, or scratch mailboxes depending on the SMU protocol used by a caller. `EXT_SCRATCH` registers provide firmware/driver scratch state across transactions and possibly across some reset scopes. `MP1_FIRMWARE_FLAGS` exposes firmware status, including the interrupt-enabled bit described in the paired sh/mask header.

Because the values are hard-coded ABI constants, any mismatch with ASIC register programming guides persists as incorrect hardware access until the header or consumer override is fixed.

## Dependencies And Integration Points

This header pairs with `mp_13_0_6_sh_mask.h`, which defines fields for the registers named here. `smu13/smu_v13_0_6_ppt.c` includes both files, undefines generic `MP1_Public` and `smnMP1_FIRMWARE_FLAGS`, and supplies local TODO-tagged final offsets before checking `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`. RAS/MCA code such as `umc_v12_0.c` includes the 13.0.6 mask for MCA field decoding.

The register names match the broader AMDGPU register macro pattern used by display and power-management code: a `reg...` offset macro, a `reg..._BASE_IDX`, and field macros in the companion mask header. Integration depends on the correct IP base table and on callers selecting the ASIC-specific header that matches the device.

## Risks

The main risk is silent hardware misaddressing. The file's `regMP1_FIRMWARE_FLAGS` value is `0xbee00a`, while the 13.0.6 PPT code overrides firmware flags with `0x3010028` and notes that final register offsets need checking. That is a strong signal that public-register addressing may require special handling outside the generated offset namespace.

Another risk is assuming the 13.0.6 layout matches nearby 13.0.x variants. Compared with 13.0.8, 13.0.6 exposes more MP1 scratch registers and `regMP1_SMN_PUB_CTRL`; its firmware flag offset also differs. Consumers that reuse 13.0.8 constants on 13.0.6 could address the wrong firmware flag or omit required scratch/control registers.

## Test Signals

Useful validation signals are successful compilation of consumers including this header, SMU firmware boot/status checks returning success, mailbox message transactions completing without timeout, and interrupt enable checks through `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK`. Runtime tests should exercise SMU command paths, display clock-manager interactions where applicable, suspend/resume, reset, and RAS/MCA error collection on ASICs that use 13.0.6.
