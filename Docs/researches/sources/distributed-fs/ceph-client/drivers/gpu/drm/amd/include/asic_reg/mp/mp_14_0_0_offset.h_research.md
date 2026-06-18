# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_14_0_0_offset.h

## Purpose

`mp_14_0_0_offset.h` declares MP1 SMN register offsets for MP/SMU ASIC version 14.0.0. It is narrower than the 13.0.x offset headers in this subset: it only exposes the `mp_SmuMp1_SmnDec` address block and does not define MP0 registers or the MP1 public firmware-flags register in this file.

The header uses `_mp_14_0_0_OFFSET_HEADER` as its include guard. It is generated register metadata used by display and SMU code to address MP1 mailboxes, interrupt handoff, FPS count, and extended scratch registers.

## Important APIs, Types, And Macros

The macro API includes:

- `regMP1_SMN_C2PMSG_0` through `regMP1_SMN_C2PMSG_127`, contiguous from `0x0240` through `0x02bf`. This is broader than the 13.0.x headers in this subset, which start at C2PMSG_32.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, and `regMP1_SMN_FPS_CNT` at `0x0340` through `0x0343`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH31`, contiguous from `0x03c0` through `0x03df`.
- Companion `_BASE_IDX` macros, all set to `0`.

No structs, enums, or functions are defined.

## Control Flow

The file has no runtime control flow. It participates in consumer control flow through generated addresses used for mailbox transactions. `display/dc/clk_mgr/dcn35/dcn35_smu.c` includes this offset header and `mp_14_0_0_sh_mask.h`, defines MP1 base segments locally, and computes addresses through `REG(reg_name)`.

Another SMU consumer pattern appears in `smu14/smu_v14_0_2_ppt.c`, where mailbox control uses `SOC15_REG_OFFSET(MP1, 0, regMP1_SMN_C2PMSG_66)`, `regMP1_SMN_C2PMSG_90`, and `regMP1_SMN_C2PMSG_82` as message, response, and argument registers. That example is for a nearby 14.0.x variant, but it shows how these macro names drive SMU message control.

## State And Persistence

The header itself stores no state. It maps hardware state exposed through MP1 registers. The expanded C2PMSG range includes low mailboxes 0-31 plus 32-127, so consumers can use protocol-specific low or high mailboxes. Interrupt handoff and FPS count registers expose live firmware/interrupt state. Scratch0-31 provide firmware/driver scratch storage.

Because these are ABI-like constants, a wrong value persists as a runtime hardware access bug until fixed in source or hidden by a consumer override.

## Dependencies And Integration Points

This header pairs with `mp_14_0_0_sh_mask.h` for field definitions, although the mask file in this tree notably covers `MP1_CRU1_MP1_FIRMWARE_FLAGS` rather than the C2PMSG fields. `dcn35_smu.c` includes both and contains a TODO stating that real headers should be used when correct, then defines local MP1 base segments. That TODO is an important integration signal: consumers may still compensate for incomplete or imperfect generated base metadata.

The file follows AMDGPU's `reg...` and `_BASE_IDX` convention, so it can be consumed by `REG()` helpers and `SOC15_REG_OFFSET()` style macros. It does not define `regMP1_CRU1_MP1_FIRMWARE_FLAGS`; firmware flag addresses for SMU14 are instead represented elsewhere, such as `smu_v14_0.h` constants and newer MP 14.0.2 offset headers.

## Risks

The main risk is assuming MP 14.0.0 layout matches 13.0.x. Here the C2PMSG range starts at index 0, the interrupt registers move to `0x0340` and later, and scratch registers move to `0x03c0` and later. Using 13.0.x offsets on 14.0.0 would direct mailbox and interrupt traffic to wrong addresses.

Another risk is incomplete public-block coverage. Code needing MP1 firmware flags must not expect this file to provide `regMP1_FIRMWARE_FLAGS` or `regMP1_CRU1_MP1_FIRMWARE_FLAGS`. The TODO in `dcn35_smu.c` also suggests that base segment definitions should be treated carefully during future cleanup.

## Test Signals

Compile-time signals include successful resolution of all `regMP1_SMN_C2PMSG_*` and `_BASE_IDX` macros in DCN35 and SMU14 code. Runtime signals should cover DCN35 SMU messages such as PMFW version, display clock, DPP clock, DCF clock, table transfer, IPS/Z-state messages, and mailbox response polling. Failures usually show up as SMU command timeouts, unknown-command responses, display clock programming failures, or firmware status checks that never report interrupts enabled through the separate SMU14 firmware flag path.
