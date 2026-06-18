# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_12_0_0_offset.h

## Purpose

`mp_12_0_0_offset.h` is the generated register-address map for MP/SMU generation 12.0.0. It defines MP0 and MP1 SMN `mm...` offsets and `_BASE_IDX` values used by Renoir-era SMU and display code to access mailbox, interrupt, and firmware-status registers.

Like other AMD ASIC register offset headers, it contains no field definitions. It must be used with `mp_12_0_0_sh_mask.h` or equivalent matching field headers for bit extraction and masked writes.

## Important APIs, Types, and Macros

The header exports 303 `#define` entries. For every register offset macro there is a matching `_BASE_IDX`, with all observed base indexes set to `0`.

Major ranges:

- `mmMP0_SMN_C2PMSG_32` through `mmMP0_SMN_C2PMSG_103`, mapped from `0x0060` through `0x00a7`.
- `mmMP0_SMN_IH_CREDIT`, `mmMP0_SMN_IH_SW_INT`, and `mmMP0_SMN_IH_SW_INT_CTRL`, mapped at `0x00c1` through `0x00c3`.
- `mmMP1_SMN_C2PMSG_32` through `mmMP1_SMN_C2PMSG_103`, mapped from `0x0260` through `0x02a7`.
- `mmMP1_SMN_IH_CREDIT`, `mmMP1_SMN_IH_SW_INT`, `mmMP1_SMN_IH_SW_INT_CTRL`, and `mmMP1_SMN_FPS_CNT`, mapped at `0x02c1` through `0x02c4`.

Unlike `mp_11_5_0_offset.h`, this header does not define `mmMP1_SMN_C2PMSG_104` through `mmMP1_SMN_C2PMSG_127` or MP1 external scratch offsets.

## Control Flow and Runtime Behavior

The header has no executable control flow. Consumers define the runtime behavior.

Observed integrations:

- `pm/swsmu/smu12/smu_v12_0.c` includes this header with `mp_12_0_0_sh_mask.h`, reads MP1 firmware flags through a PCIE/SMN path, and uses the matching mask header to test `INTERRUPTS_ENABLED`.
- `display/dc/clk_mgr/dcn21/rn_clk_mgr_vbios_smu.c` includes this header and uses a `REG(reg_name)` macro that expands `MP0_BASE.instance[0].segment[mm ## reg_name ## _BASE_IDX] + mm ## reg_name`. Its SMU mailbox transaction polls `MP1_SMN_C2PMSG_91`, writes a parameter to `MP1_SMN_C2PMSG_83`, and triggers the message through `MP1_SMN_C2PMSG_67`.
- `amdgpu/psp_v12_0.c` includes this header for PSP generation 12 register addressing.

## State and Persistence Behavior

The header does not store state. It names hardware registers that contain:

- MP0 and MP1 C2P mailbox payloads;
- MP1 firmware/SMU command parameters, command IDs, and responses;
- interrupt credit, software interrupt, interrupt mask, and interrupt acknowledge registers;
- MP1 FPS counter state.

Mailbox and interrupt register contents are persistent hardware state until firmware, the driver, or reset changes them. The constants in this header are therefore part of the driver-firmware communication contract.

## Dependencies and Integration Points

This file depends on matching use with:

- `mp_12_0_0_sh_mask.h` for fields such as `MP1_FIRMWARE_FLAGS__INTERRUPTS_ENABLED_MASK` and SMN C2P message `CONTENT`.
- ASIC base-offset headers such as `renoir_ip_offset.h`, which define `MP0_BASE`.
- Register helpers such as `REG_READ`, `REG_WRITE`, `RREG32_PCIE`, and `RREG32_SOC15`.
- SMU common helpers in `smu_cmn` and display VBIOS SMC message protocols.

The header uses the older `mm` naming convention. Later MP 13 headers may use `reg...` names, so cross-generation code must respect the expected helper macro family.

## Risks and Edge Cases

- The MP1 mailbox range stops at C2PMSG 103. Reusing 11.5.0 code that expects C2PMSG 104-127 would fail at compile time or require a different offset header.
- All base indexes are `0`; if an ASIC base table changes, this generated map must change with it.
- Display mailbox code relies on hard-coded semantic indices, especially response `91`, parameter `83`, and trigger `67`. Any offset error can create silent SMU command loss or long busy waits.
- Offset headers do not encode access width, read/write side effects, or firmware protocol restrictions. Call sites must know whether a register is safe to poll, write, clear, or acknowledge.
- Mixing this MP 12.0.0 offset header with MP 11.x or 13.x field headers can compile in limited cases but target incorrect hardware semantics.

## Test Signals

Useful validation signals include:

- Build `smu_v12_0.o`, `psp_v12_0.o`, and `rn_clk_mgr_vbios_smu.o`.
- Exercise Renoir display clock programming paths that call the VBIOS SMU message helpers.
- Confirm firmware-status checks in `smu_v12_0_check_fw_status()` return success when MP1 firmware has enabled interrupts.
- Runtime signs of bad offsets include `-EIO` from firmware-status checks, failed PSP initialization, repeated SMU busy responses, display clock failures, and rejected or unknown VBIOS SMC messages.
