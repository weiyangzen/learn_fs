# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_5_offset.h

## Purpose

This generated header provides MP 13.0.5 register offsets and base-index selectors for AMDGPU MP0/MP1 register access. It is an address map, not executable code. Consumers use `reg...` constants and `reg..._BASE_IDX` selectors with AMDGPU register-access helpers to talk to PSP/SMU firmware through mailbox registers and related MP1 status/scratch registers.

The header covers `mp_SmuMp0_SmnDec`, `mp_SmuMp1_SmnDec`, and `mp_SmuMp1Pub_CruDec`. MP0 includes C2PMSG 32-103 and MP0 interrupt helper registers. MP1 includes C2PMSG 32-127, MP1 interrupt helper registers, `MP1_SMN_FPS_CNT`, an extended scratch range, and `MP1_FIRMWARE_FLAGS`.

## Important APIs, Types, And Macros

The public surface is a set of preprocessor macros guarded by `_mp_13_0_5_OFFSET_HEADER`. Every register macro has an offset and base-index macro. There are no functions, structs, enums, or stateful definitions.

MP0 offsets start at `regMP0_SMN_C2PMSG_32` `0x0060` and continue sequentially through `regMP0_SMN_C2PMSG_103` `0x00a7`, followed by `regMP0_SMN_IH_CREDIT` `0x00c1`, `regMP0_SMN_IH_SW_INT` `0x00c2`, and `regMP0_SMN_IH_SW_INT_CTRL` `0x00c3`. MP1 offsets start at `regMP1_SMN_C2PMSG_32` `0x0260` and continue through `regMP1_SMN_C2PMSG_127` `0x02bf`; MP1 interrupt helpers are at `0x02c1` through `0x02c3`; `regMP1_SMN_FPS_CNT` is `0x02c4`.

The scratch range is larger than MP 13.0.4: it includes `regMP1_SMN_EXT_SCRATCH0` through `8`, skips `9`, then includes `10` through `31`, with offsets `0x0340` through `0x035f` except the missing `0x0349` entry. `regMP1_FIRMWARE_FLAGS` is in the MP1 public block at `0xbee009`.

All base indices in this file are `0`. This is a critical distinction from MP 13.0.4, where analogous offsets use base index `1`.

Inventory signal: the header contains 414 register/base-index macro definitions.

## Control Flow

There is no runtime control flow. Runtime behavior appears in display/SMU consumers that include this file. `display/dc/clk_mgr/dcn314/dcn314_smu.c` includes it and defines local MP1 base segment constants with a `REG(reg_name)` macro that selects `BASE(reg..._BASE_IDX) + reg...`. It uses MP1 C2PMSG registers 67, 83, and 91 to send VBIOS SMU messages and poll responses. `display/dc/clk_mgr/dcn315/dcn315_smu.c` also includes it and uses a local `MP0_BASE` segment table, then performs a different mailbox flow through MP1 C2PMSG 37 and 38 plus an indexed write to `mmMP1_C2PMSG_3`.

## State And Persistence Behavior

The file itself is stateless. The described registers are hardware/firmware state: command mailboxes, response mailboxes, interrupt helper state, scratch registers, firmware flags, and counters. Consumer writes change hardware register contents and can trigger firmware actions. Consumer reads observe firmware state that may change asynchronously. Persistence is limited to the active device/firmware session.

## Dependencies

This header depends on the preprocessor and on consumer-side AMDGPU register access infrastructure. Direct consumers provide base tables or SOC15 helpers that understand `reg..._BASE_IDX`. It is conventionally paired with `mp_13_0_5_sh_mask.h`, although current direct display consumers found in this tree include only the offset header and mostly treat mailbox values as full-width protocol words.

## Integration Points

Direct include sites are `display/dc/clk_mgr/dcn314/dcn314_smu.c` and `display/dc/clk_mgr/dcn315/dcn315_smu.c`. These files use MP 13.0.5 mailbox offsets for display clock and power-management communication with PMFW/SMU. The command flows include SMU version queries, display clock and DPP clock frequency changes, DCFCLK limits, deep-sleep clock settings, watermark table transfers, display idle optimizations, and DP reference clock queries. The larger scratch and firmware-flags coverage aligns MP 13.0.5 with other 13.0.x generated headers that expose firmware diagnostics/status registers.

## Risks

The primary risk is wrong base-index interpretation. Because every base index is `0`, a consumer that assumes MP 13.0.4's base index `1` will compute a different physical address even when the register offset number is identical. Another risk is the non-contiguous scratch register list: there is no `regMP1_SMN_EXT_SCRATCH9`, so generated-code or loop-based assumptions over 0-31 can fail at compile time or accidentally target an undefined register. Header mismatch can cause display SMU mailbox timeouts, wrong returned clock values, or firmware commands going to the wrong register.

## Test Signals

Compile-time tests should cover DCN 3.1.4 and DCN 3.1.5 display SMU translation units. Runtime tests should verify SMU message response polling exits busy state, `GetSmuVersion`/`GetPmfwVersion` returns sane data, display clock changes return expected MHz values, and watermark/table transfer paths do not trigger SMU timeouts. Static checks should compare offset sequences, base index `0`, the missing scratch 9, and `MP1_FIRMWARE_FLAGS` address `0xbee009` against the authoritative register database.
