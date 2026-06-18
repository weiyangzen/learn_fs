# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/umc/umc_8_14_0_offset.h

## Purpose

`umc_8_14_0_offset.h` is a compact generated UMC 8.14.0 register-offset header. It exposes only the GECC error-counter selector and GECC error-counter registers for channel 0, using the `regUMCCH0_*` naming style and base index `0`.

## Important APIs, Types, And Macros

The exported macros are `regUMCCH0_GeccErrCntSel`, `regUMCCH0_GeccErrCnt`, and their `_BASE_IDX` values. The offsets match the familiar `0x0328` and `0x0329` GECC selector/counter locations, but the symbol names no longer include the `CH0_0` instance spelling used by UMC 8.10.0 and 8.7.0. There are no MCA status/address offsets in this generation-specific file.

## Control Flow And Data Flow

No control flow is implemented here. Consumers use the selector offset to choose GECC or poison counting behavior and read the counter offset to retrieve corrected and uncorrected counts. Decoding requires the matching `umc_8_14_0_sh_mask.h` masks.

## State And Persistence Behavior

The header has no mutable state. It names persistent hardware counter configuration and count registers. The state is hardware-owned and may be affected by RAS configuration, error events, resets, or power transitions.

## Dependencies And Integration Points

This file depends only on preprocessing and integrates with ASIC-specific AMDGPU UMC/RAS code. It should be used with `umc_8_14_0_sh_mask.h`, not with older UMC masks whose symbol names include `UMCCH0_0` or whose base indexes differ.

## Risks And Test Signals

The narrowed surface is itself a risk: code ported from UMC 8.10.0 or 8.7.0 must not expect MCA `STATUST0` or `ADDRT0` macros from this header. Tests should build the UMC 8.14.0 path, verify GECC count reads on matching hardware, and compare generated names/offsets against the AMD register database.
