# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_4_1_0_offset.h

## Purpose
This generated AMDGPU register-offset header defines the ATHUB 4.1.0 SOC15 register offsets used by the driver for XPB and RPB register access. It covers the ATHUB XPB decoder block annotated with base address `0x3000` and the ATHUB RPB decoder block annotated with base address `0x31d0`.

The file is a hardware register map, not algorithmic code. It exports symbolic `reg...` offsets and paired `..._BASE_IDX` constants so AMDGPU code can access ATHUB 4.1.0 registers through SOC15 helper macros without embedding raw numeric offsets.

## Important APIs, types, and functions
There are no C functions, structs, enums, or data objects. The interface is the macro set guarded by `_athub_4_1_0_OFFSET_HEADER`.

Important macro groups include:

- `regXPB_RTR_SRC_APRTR0` through `regXPB_RTR_SRC_APRTR13` and `regXPB_RTR_DEST_MAP0` through `regXPB_RTR_DEST_MAP13` for XPB source aperture and destination routing tables.
- `regXPB_CLG_CFG0` through `regXPB_CLG_CFG7`, `regXPB_CLG_EXTRA0`, `regXPB_CLG_EXTRA1`, `regXPB_CLG_EXTRA_MSK`, readback registers, match/mask/valid registers, and GFX/MM unit-ID mapping registers for client grouping and request matching.
- `regXPB_P2P_BAR_CFG`, `regXPB_P2P_BAR0` through `regXPB_P2P_BAR7`, setup and delta registers, plus `regXPB_PEER_SYS_BAR0` through `regXPB_PEER_SYS_BAR13` for peer and P2P BAR configuration.
- `regXPB_CLK_GAT`, `regXPB_INTF_CFG`, `regXPB_INTF_STS`, `regXPB_PIPE_STS`, `regXPB_WCB_STS`, `regXPB_MAP_INVERT_FLUSH_NUM_LSB`, `regXPB_STICKY`, `regXPB_STICKY_W1C`, `regXPB_SUB_CTRL`, `regXPB_PERF_KNOBS`, `regXPB_MISC_CFG`, and related status/control registers.
- `regATHUB_SHARED_VIRT_RESET_REQ`, which is present in ATHUB 4.1.0 before the RPB control range and is not present in the ATHUB 3.0.0 offset header.
- `regATHUB_MEM_POWER_LS` and `regATHUB_MISC_CNTL`, which support ATHUB clock and light-sleep control.
- `regRPB_*` registers for pass-through, block-level, tag, arbitration, BIF, SDP/DF port, VC switch, ATS, and performance-counter controls.

The file defines 126 unique register names, each paired with `*_BASE_IDX`. Every base index is `0`.

## Control flow
The header has no runtime control flow. Its only compile-time control is the include guard.

Runtime control flow is represented by consumers such as `amdgpu/athub_v4_1_0.c`. That file includes this offset header and the matching `athub_4_1_0_sh_mask.h`, reads `regATHUB_MISC_CNTL` for IP version 4.1.0, conditionally sets or clears clock-gating and memory light-sleep masks, and writes the register back only when changed. Unsupported ATHUB versions return zero or skip writes in that implementation.

The normal access pattern is: select an ATHUB 4.1.0 device path, pass `reg...` names to `RREG32_SOC15()` or `WREG32_SOC15()` with `ATHUB` instance `0`, and use the matching mask header to isolate fields.

## State and persistence behavior
This header persists no software state. It names volatile hardware register locations.

State reachable through these offsets includes XPB routing and aperture tables, P2P and peer BAR setup, client grouping/matching and unit-ID mappings, WCB/interface/pipe status, sticky W1C status, subsystem stall/reset controls, ATHUB shared virtualization reset request state, ATHUB clock/power control, RPB arbitration and BIF policy, ATS controls, SDP/DF port credits, virtual-channel switching, and RPB performance-counter state.

Those hardware values can be reset or changed by GPU reset, suspend/resume, runtime power management, firmware, virtualization transitions, and driver initialization. Durable behavior depends on AMDGPU reprogramming sequences.

## Dependencies
This header depends only on the C preprocessor. Correct integration depends on:

- `athub_4_1_0_sh_mask.h` for the bitfield definitions matching these offsets.
- AMDGPU SOC15 register helpers and ATHUB base-address tables.
- IP discovery selecting ATHUB hardware version 4.1.0 before using these offsets.
- `athub_v4_1_0.c` and related power-management code for the direct `regATHUB_MISC_CNTL` use case.
- `gmc_v12_0.c` and other GFX12 memory-management code that includes the ATHUB 4.1.0 register vocabulary.

## Integration points
Direct include sites in this tree are `drivers/gpu/drm/amd/amdgpu/athub_v4_1_0.c` and `drivers/gpu/drm/amd/amdgpu/gmc_v12_0.c`.

`athub_v4_1_0.c` uses `regATHUB_MISC_CNTL` for ATHUB medium-grain clock-gating and memory light-sleep control on IP version 4.1.0. It skips clock-gating writes for SR-IOV VFs, mirroring the safety behavior in earlier ATHUB generations.

`gmc_v12_0.c` includes the header as part of the GFX12 memory-controller register environment. The header provides the ATHUB XPB/RPB layout needed by code that works with address translation, routing, peer BAR behavior, and memory-management integration on ATHUB 4.1.0 hardware.

The header sits beside the ATHUB 4.1.0 shift/mask header and older ATHUB generation maps. It is not interchangeable with ATHUB 3.0.0: several offsets are moved, split, added, or reordered.

## Risks and edge cases
The highest risk is using this header with the wrong IP generation. ATHUB 4.1.0 differs from ATHUB 3.0.0: `regXPB_CLG_EXTRA` is split into `regXPB_CLG_EXTRA0` and `regXPB_CLG_EXTRA1`; match validity registers and GFX/MM unit-ID mapping registers are added; `regATHUB_SHARED_VIRT_RESET_REQ` appears; the RPB base is `0x31d0`; and performance-counter result/control offsets are ordered differently.

As with all generated register maps, incorrect offsets can silently write the wrong hardware register. Potential damage includes broken clock/power state, bad peer BAR routing, request-path stalls, lost sticky status, bad virtualization reset behavior, or invalid ATS/RPB arbitration state.

All base indices are `0`. Code that passes these macros through SOC15 helpers is aligned with the generated data; code that open-codes addresses or assumes another base segment is fragile.

W1C and sticky registers such as `regXPB_STICKY_W1C` should not be handled with generic read/modify/write patterns. Control registers such as `regXPB_SUB_CTRL` and virtualization reset registers also require hardware-aware sequencing.

The contiguous-looking indexed register groups have fixed hardware bounds. Consumers should not infer `SRC_APRTR14`, `DEST_MAP14`, `P2P_BAR8`, or `PEER_SYS_BAR14` from the repeated naming pattern.

## Test signals
Useful validation signals include:

- Compile coverage for `athub_v4_1_0.c` and `gmc_v12_0.c` with `athub_4_1_0_offset.h` and the matching mask header.
- Runtime register traces on ATHUB 4.1.0 hardware confirming `regATHUB_MISC_CNTL` maps to the expected hardware address and clock-gating/light-sleep writes modify only intended bits.
- SR-IOV tests verifying ATHUB v4.1 clock-gating programming is skipped for virtual functions.
- GPU reset and suspend/resume testing confirming ATHUB 4.1 XPB/RPB and power-management state is restored by higher-level driver code.
- Bring-up comparison against AMD generated register data for the new 4.1.0-only offsets, especially shared virtualization reset, CLG extra splitting, match-valid registers, unit-ID mappings, and reordered RPB performance-counter registers.
- Negative testing around sticky/W1C status and subsystem reset/stall registers to catch unsafe generic register-update helpers.
