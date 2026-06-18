# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mp/mp_13_0_2_offset.h

## Purpose

`mp_13_0_2_offset.h` defines register offsets and `_BASE_IDX` selectors for MP 13.0.2. It is an address map for AMDGPU MP/SMU code and is intended to be paired with generation-compatible field mask headers.

The file covers MP0 SMN mailboxes and interrupts, MP1 public firmware flags, MP1 SMN mailboxes and interrupts, MP1 FPS count, and a small MP1 extended scratch range.

## Important APIs, Types, And Macros

This file exports only preprocessor constants.

Important macro families:

- `regMP0_SMN_C2PMSG_32` through `regMP0_SMN_C2PMSG_127`: contiguous MP0 SMN mailbox offsets from `0x0060` through `0x00bf`.
- `regMP0_SMN_IH_CREDIT`, `regMP0_SMN_IH_SW_INT`, and `regMP0_SMN_IH_SW_INT_CTRL`: MP0 SMN interrupt helper offsets at `0x00c1` through `0x00c3`.
- `regMP1_FIRMWARE_FLAGS`: public MP1 firmware flag register at `0xbee009`.
- `regMP1_SMN_C2PMSG_32` through `regMP1_SMN_C2PMSG_103`: MP1 SMN mailbox offsets from `0x0260` through `0x02a7`.
- `regMP1_SMN_IH_CREDIT`, `regMP1_SMN_IH_SW_INT`, `regMP1_SMN_IH_SW_INT_CTRL`, and `regMP1_SMN_FPS_CNT`: MP1 SMN interrupt/count offsets from `0x02c1` through `0x02c4`.
- `regMP1_SMN_EXT_SCRATCH0` through `regMP1_SMN_EXT_SCRATCH7`: eight MP1 scratch offsets from `0x0340` through `0x0347`.
- Every register offset has a matching `_BASE_IDX` macro set to `0`.

Compared with `mp_13_0_0_offset.h`, MP 13.0.2 has a wider MP0 mailbox range through `C2PMSG_127`, a narrower MP1 mailbox range through `C2PMSG_103`, only scratch registers 0-7, no `regMP1_SMN_PUB_CTRL`, and no `regMPIO_FIRMWARE_FLAGS`.

## Control Flow

There is no runtime control flow. The include guard `_mp_13_0_2_OFFSET_HEADER` only prevents duplicate inclusion. Runtime behavior is controlled by callers that use these constants in register read/write operations.

## State And Persistence Behavior

The header is stateless and persistent only as source code. It names hardware registers whose contents are volatile or firmware-owned. Mailbox offsets identify command/status payload registers, interrupt offsets identify hardware interrupt coordination state, and scratch offsets identify firmware/driver communication storage. This file does not cache or synchronize any of that state.

## Dependencies And Integration Points

The file has no include dependencies. It integrates with:

- MP 13.0.2-compatible field mask headers and AMDGPU register access helpers.
- SMU command submission paths that choose MP0 or MP1 `C2PMSG` registers.
- Interrupt handling paths using `IH_CREDIT`, `IH_SW_INT`, and `IH_SW_INT_CTRL`.
- Firmware status code reading `regMP1_FIRMWARE_FLAGS`.
- Firmware/diagnostic code using the limited `EXT_SCRATCH0` to `EXT_SCRATCH7` range.

The register block comments are part of the integration contract: `regMP1_FIRMWARE_FLAGS` uses a public CRU block address, while `regMP1_SMN_*` names use SMN-decoded offsets.

## Risks And Maintenance Notes

The largest risk is copying assumptions from MP 13.0.0. Code using `regMP1_SMN_PUB_CTRL`, `regMPIO_FIRMWARE_FLAGS`, MP1 `C2PMSG_104`-`127`, or scratch registers above 7 must not be enabled merely because a GPU is MP 13.x. Conversely, MP0 mailboxes extend to `C2PMSG_127` in this file, unlike the MP0 range in `mp_13_0_0_offset.h`.

All `_BASE_IDX` values are currently zero, so consumers may have implicit single-base assumptions. If generated data changes, those paths need explicit review. As with all register maps, mistakes are high impact because bad offsets can hit unrelated hardware registers.

## Test Signals

Useful validation includes:

- Compile coverage for MP 13.0.2 ASIC support.
- Static comparison against AMD-generated MP 13.0.2 register references.
- Runtime SMU mailbox tests that cover the MP0 `C2PMSG_127` upper range and the MP1 `C2PMSG_103` boundary.
- Firmware flag reads from the MP1 public CRU block.
- Negative or guarded tests ensuring unavailable MP 13.0.0-only registers are not referenced for MP 13.0.2.
