# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_11_5_0_offset.h

## Purpose

`mp_11_5_0_offset.h` is the generated register-address map for MP/SMU generation 11.5.0. It defines `mm...` register offsets and matching `..._BASE_IDX` values for MP0 and MP1 SMN register blocks. The display clock-manager path for DCN 3.01 includes it to calculate addresses for Vangogh SMU mailbox communication.

The file is address-only. Field semantics come from `mp_11_5_0_sh_mask.h`; code combines both headers through register helper macros.

## Important APIs, Types, and Macros

This header exports 367 preprocessor defines. For each `mm...` register offset there is a `..._BASE_IDX`, all observed as `0`.

Major register ranges:

- `mmMP0_SMN_C2PMSG_32` through `mmMP0_SMN_C2PMSG_103`, mapped contiguously from `0x0060` through `0x00a7`.
- `mmMP0_SMN_IH_CREDIT`, `mmMP0_SMN_IH_SW_INT`, and `mmMP0_SMN_IH_SW_INT_CTRL`, mapped at `0x00c1`, `0x00c2`, and `0x00c3`.
- `mmMP1_SMN_C2PMSG_32` through `mmMP1_SMN_C2PMSG_127`, mapped contiguously from `0x0260` through `0x02bf`.
- `mmMP1_SMN_IH_CREDIT`, `mmMP1_SMN_IH_SW_INT`, `mmMP1_SMN_IH_SW_INT_CTRL`, and `mmMP1_SMN_FPS_CNT`, mapped at `0x02c1` through `0x02c4`.
- `mmMP1_SMN_EXT_SCRATCH0` through `mmMP1_SMN_EXT_SCRATCH7`, mapped from `0x03c0` through `0x03c7`.

The consumer-facing API is the macro naming convention. Display code defines:

```c
#define REG(reg_name) (MP0_BASE.instance[0].segment[mm ## reg_name ## _BASE_IDX] + mm ## reg_name)
```

That makes `REG_READ(MP1_SMN_C2PMSG_91)` resolve through `mmMP1_SMN_C2PMSG_91` and `mmMP1_SMN_C2PMSG_91_BASE_IDX`.

## Control Flow and Runtime Behavior

There is no executable control flow in this header. Runtime behavior appears in consumers that use these offsets for SMU command mailboxes.

The direct observed consumer is `display/dc/clk_mgr/dcn301/dcn301_smu.c`, which:

- Polls `MP1_SMN_C2PMSG_91` until the SMU response is no longer busy.
- Writes `MP1_SMN_C2PMSG_91` to clear the response register.
- Writes a parameter to `MP1_SMN_C2PMSG_83`.
- Writes a VBIOS SMC message ID to `MP1_SMN_C2PMSG_67`.

The address constants in this file therefore define the physical mailbox endpoints for display clock, DCFCLK, DPPCLK, FCLK, watermarks, and display-idle-optimization messages on the supported ASIC.

## State and Persistence Behavior

The header stores no software state. The offsets point at hardware registers whose contents persist according to SMU/firmware and hardware reset rules.

Stateful hardware concepts described by the map include:

- MP0 and MP1 command-to-processor mailboxes.
- MP1 response/parameter/message registers used by display SMU command sequences.
- MP1 interrupt and credit registers.
- MP1 external scratch registers, which can be used as firmware-driver scratch communication state.

Because all `_BASE_IDX` values are `0`, callers expect the MP0 base segment array entry `0` to be valid for these registers.

## Dependencies and Integration Points

Integration depends on:

- `mp_11_5_0_sh_mask.h` for fields inside the same registers.
- ASIC IP offset headers such as `vangogh_ip_offset.h`, which define `MP0_BASE` segment layout.
- Display register helpers in `reg_helper.h`, including `REG_READ` and `REG_WRITE`.
- SMU/VBIOS message protocol constants local to `dcn301_smu.c`.

The offsets are not self-validating. If the map is used with a mismatched ASIC base table or with MP 11.0/12.0 field headers, the code can compile while targeting the wrong registers.

## Risks and Edge Cases

- `MP1_SMN_C2PMSG_104` through `MP1_SMN_C2PMSG_127` exist in 11.5.0 but not in the 12.0.0 offset header researched in this work item. Cross-generation reuse must not assume identical mailbox depth.
- The file has no active-function-ID or public-control offsets; those fields exist in other MP generations or mask files, so consumers must not infer address availability from similarly named mask macros elsewhere.
- Register offsets are small `mm` offsets, not full SMN absolute addresses. They must be combined with the correct base segment.
- Mailbox register mistakes are high impact: polling the wrong response register can look like a permanent SMU busy timeout, while writing the wrong trigger register can send no command or a malformed command.

## Test Signals

Useful signals include:

- Build `display/dc/clk_mgr/dcn301/dcn301_smu.o` with this header and `mp_11_5_0_sh_mask.h`.
- Exercise Vangogh/DCN301 display clock changes and inspect SMU logs for response values other than busy.
- Check that `REG_READ(MP1_SMN_C2PMSG_91)`, `REG_WRITE(MP1_SMN_C2PMSG_83, ...)`, and `REG_WRITE(MP1_SMN_C2PMSG_67, ...)` access the expected addresses in register traces.
- Hardware symptoms of bad offsets include display clock programming failure, repeated `SMU Response was not OK` messages, hangs in wait loops, or failed watermark/table transfer messages.
