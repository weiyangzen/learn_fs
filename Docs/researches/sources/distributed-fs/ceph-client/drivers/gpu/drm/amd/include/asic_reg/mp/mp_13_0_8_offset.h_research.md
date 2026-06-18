# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_8_offset.h

## Purpose

`mp_13_0_8_offset.h` declares MP register offsets for SMU/MP ASIC version 13.0.8. Like other files in this directory, it is generated register metadata used by AMDGPU code to produce final MMIO/SMN addresses through local base-index helpers.

The header covers MP0 and MP1 SMN decoder mailboxes and a small MP1 public block. It uses `_mp_13_0_8_OFFSET_HEADER` as an include guard.

## Important APIs, Types, And Macros

The exported macro groups are:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_103`, at offsets `0x0060` through `0x00a7`.
- MP0 interrupt handoff registers `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL`, at `0x00c1` through `0x00c3`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_127`, at offsets `0x0260` through `0x02bf`.
- MP1 interrupt handoff registers at `0x02c1` through `0x02c3`, plus `regMP1_SMN_FPS_CNT` at `0x02c4`.
- MP1 extended scratch registers `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH7`, at `0x0340` through `0x0347`.
- `regMP1_FIRMWARE_FLAGS` at `0xbee009`.

Every register macro has a `_BASE_IDX` macro set to `0`. There are no C functions or data types.

## Control Flow

There is no runtime control flow in the header. Consumers use these constants to implement PMFW mailbox transactions and display-clock SMU requests. For example, `display/dc/clk_mgr/dcn316/dcn316_smu.c` includes this header, builds a local `MP0_BASE` table, and defines `REG(reg_name)` as `MP0_BASE.instance[0].segment[reg..._BASE_IDX] + reg...` before issuing VBIOSSMC messages.

## State And Persistence

The macros name hardware state. `C2PMSG` registers carry command, response, and argument data for host-to-firmware communication. `IH_*` registers represent interrupt-credit and software-interrupt state. `EXT_SCRATCH0-7` provide MP1 scratch storage exposed by this ASIC variant. `MP1_FIRMWARE_FLAGS` is a firmware status register whose field layout is defined in `mp_13_0_8_sh_mask.h`.

The header itself is stateless, but changes to its constants directly affect persistent driver behavior across boots because they alter the addresses used for all related transactions.

## Dependencies And Integration Points

This file is paired with `mp_13_0_8_sh_mask.h`. The direct consumer found in this tree is `dcn316_smu.c`, where the offset macros are integrated with display clock-manager register helpers and SMU message definitions. The same macro style is compatible with AMDGPU's broader `SOC15_REG_OFFSET()` and register-helper conventions.

Compared with 13.0.6, this variant uses address-block comments without the `aid_` prefix, lacks `regMP1_SMN_PUB_CTRL`, exposes only scratch0-7, and uses firmware flag offset `0xbee009` rather than `0xbee00a`.

## Risks

Variant drift is the central risk. The 13.0.8 file is close to 13.0.6 but not identical, so mechanical reuse of offsets across ASIC revisions can produce subtle PMFW failures. The reduced scratch-register set is another risk for code that assumes scratch8 or scratch10-31 are available.

Because base indices are all zero, consumers with incorrect local base tables may still compile and produce bad final addresses. The address comments say base `0x0`, so final addressing depends entirely on the external IP base map used by the caller.

## Test Signals

Compile-time validation should ensure `dcn316_smu.c` and other 13.0.8 consumers resolve all `REG()` and `FN()` macros. Runtime validation should cover display clock SMU messages such as PMFW version, display clock, DPP clock, DCF clock, table transfer, and DTB clock requests. Healthy signals are non-timeout SMU replies, correct PMFW version reads, and no display clock programming regressions on DCN316-class hardware.
