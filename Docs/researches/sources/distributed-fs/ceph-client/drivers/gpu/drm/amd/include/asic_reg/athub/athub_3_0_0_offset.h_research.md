# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_3_0_0_offset.h

## Purpose
This generated AMDGPU register-offset header defines the symbolic SOC15 register offsets for ATHUB hardware version 3.0.0. The covered address space is the ATHUB XPB decoder block, annotated with base address `0x3000`, and the ATHUB RPB decoder block, annotated with base address `0x31b0`.

The file is not executable code. Its job is to give C driver code stable `reg...` constants and matching `..._BASE_IDX` constants for register address calculation through AMDGPU helpers such as `RREG32_SOC15()` and `WREG32_SOC15()`. The paired `athub_3_0_0_sh_mask.h` file supplies the bit layouts for the same register names.

## Important APIs, types, and functions
There are no functions, structs, enums, or variables. The public interface is the macro namespace guarded by `_athub_3_0_0_OFFSET_HEADER`.

Important exported groups are:

- `regXPB_RTR_SRC_APRTR0` through `regXPB_RTR_SRC_APRTR13`, which name source aperture registers for XPB routing.
- `regXPB_RTR_DEST_MAP0` through `regXPB_RTR_DEST_MAP13`, which name the matching destination map registers.
- `regXPB_CLG_CFG0` through `regXPB_CLG_CFG7`, `regXPB_CLG_EXTRA`, `regXPB_CLG_EXTRA_MSK`, readback variants, and GFX/MM/GUS match/mask registers, which describe client grouping and request matching.
- `regXPB_P2P_BAR_CFG`, `regXPB_P2P_BAR0` through `regXPB_P2P_BAR7`, `regXPB_P2P_BAR_SETUP`, and delta registers for peer-to-peer BAR routing.
- `regXPB_PEER_SYS_BAR0` through `regXPB_PEER_SYS_BAR13` for peer system BAR state.
- `regXPB_CLK_GAT`, `regXPB_INTF_CFG`, `regXPB_INTF_STS`, `regXPB_PIPE_STS`, `regXPB_SUB_CTRL`, `regXPB_STICKY`, `regXPB_STICKY_W1C`, `regXPB_MISC_CFG`, and performance-tuning/status registers.
- `regATHUB_MISC_CNTL` and `regATHUB_MEM_POWER_LS`, which are the main ATHUB power-management registers used by ATHUB v3 code.
- `regRPB_*` registers for pass-through behavior, block level, tag configuration, arbitration, BIF controls, SDP/DF port controls, virtual-channel switching, ATS controls, and RPB performance counters.

The file defines 112 unique register names, each with a matching `*_BASE_IDX`. Every base index in this header is `0`.

## Control flow
This header has no runtime control flow. Its only compile-time control flow is the include guard.

Runtime behavior appears in consumers. `amdgpu/athub_v3_0.c` includes this header and uses `regATHUB_MISC_CNTL` as the default ATHUB miscellaneous-control register for IP versions such as 3.0.0 and 3.0.2. It reads the register, toggles bit masks from `athub_3_0_0_sh_mask.h`, and writes it back only when the value changes. For IP versions 3.0.1 and 3.3.0 that file overrides the miscellaneous-control offset with local `regATHUB_MISC_CNTL_V3_0_1` and `regATHUB_MISC_CNTL_V3_3_0` macros, which is an important signal that similar ATHUB v3 revisions can move registers even when the bit layout remains compatible enough for the same mask header.

The general access pattern is: include the offset header, include the matching shift/mask header, choose an ATHUB IP version, compute or pass the symbolic offset to SOC15 register helpers, then modify hardware register contents with masks from the companion header.

## State and persistence behavior
The header persists no software state. Its constants address volatile GPU hardware registers whose contents are affected by reset defaults, firmware initialization, driver bring-up, runtime power management, SR-IOV mode, and active workloads.

State reachable through these offsets includes ATHUB clock-gating and memory light-sleep state, XPB routing tables, source/destination aperture configuration, P2P and peer BAR mappings, client grouping and matching state, interface credits and pipe status, sticky write-one-to-clear event bits, RPB arbitration and virtual-channel policy, ATS routing controls, SDP/DF port credit state, and RPB performance counters. Any persistence across suspend/resume or GPU reset must be provided by higher-level AMDGPU reinitialization paths, not by this header.

## Dependencies
The header itself depends only on the C preprocessor. Meaningful use depends on:

- `athub_3_0_0_sh_mask.h` for field shifts and masks matching these offsets.
- AMDGPU SOC15 register helpers from `soc15_common.h` and related AMDGPU infrastructure.
- ASIC/IP discovery selecting an ATHUB v3 register layout before compiling or executing code paths that use these names.
- ATHUB base-address tables supplied by ASIC-specific IP offset files through `adev->reg_offset`.
- Power-management and memory-routing code that understands the hardware contract behind XPB and RPB registers.

## Integration points
Direct include sites in this tree are `drivers/gpu/drm/amd/amdgpu/athub_v3_0.c` and `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`.

`athub_v3_0.c` uses `regATHUB_MISC_CNTL` with `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` to report and control ATHUB medium-grain clock gating and memory light sleep. It skips programming for SR-IOV VFs.

`gmc_v11_0.c` includes the header as part of the GFX11 memory-controller register environment. Even if a given macro is not referenced directly in the visible source, the header makes the ATHUB XPB/RPB register namespace available to memory-management code that may be conditionalized by ASIC family or build configuration.

## Risks and edge cases
The main risk is register drift. These offsets are a hardware ABI: an incorrect value can redirect a read or write to a different ATHUB register and affect address routing, peer BAR setup, clock/power behavior, or status clearing.

The `regATHUB_MISC_CNTL` exception in `athub_v3_0.c` for IP versions 3.0.1 and 3.3.0 is a concrete edge case. Code must not assume all ATHUB v3 revisions use the same miscellaneous-control offset just because the macro name exists in this header.

All `*_BASE_IDX` values are `0`. Consumers that ignore base indices are currently compatible with this file, but future generated headers could use a different base segment. Accessors should continue to use the SOC15 helpers rather than open-coding addresses.

Several XPB status registers have sticky or write-one-to-clear semantics by name, especially `regXPB_STICKY_W1C`. Generic read/modify/write operations against W1C registers can acknowledge events unexpectedly.

The repeated indexed groups are intentionally contiguous in many places, but code should not infer unlisted registers. For example, the aperture and destination-map ranges stop at 13 and P2P BARs stop at 7 in this header.

## Test signals
Useful validation signals are mostly build-time and hardware integration oriented:

- Compile coverage for `athub_v3_0.c` and `gmc_v11_0.c` with both `athub_3_0_0_offset.h` and `athub_3_0_0_sh_mask.h` included, checking for missing or conflicting macros.
- Runtime register traces on ATHUB 3.0.0/3.0.2 ASICs showing `RREG32_SOC15(ATHUB, 0, regATHUB_MISC_CNTL)` reads the expected miscellaneous-control register.
- Clock-gating tests verifying `athub_v3_0_set_clockgating()` toggles only the intended `CG_ENABLE` and `CG_MEM_LS_ENABLE` bits and is a no-op for SR-IOV VFs.
- GPU reset and suspend/resume tests verifying ATHUB clock/power and routing-related state is restored by the owning AMDGPU paths.
- Bring-up comparison against AMD generated register databases for the XPB base `0x3000`, RPB base `0x31b0`, the documented gaps such as the missing `0x0033`, and the final RPB ATS offsets.
