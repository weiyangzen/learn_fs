# subset-b-001473

Grouped research for ATHUB generated register headers. Each section preserves the source path in its title and is delimited for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_3_0_0_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_3_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_3_0_0_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_3_0_0_sh_mask.h

## Purpose
This generated AMDGPU shift/mask header defines the bitfield layout for ATHUB 3.0.0 XPB and RPB registers. It is the companion to `athub_3_0_0_offset.h`: the offset header names register locations, while this file names the shift amount and bit mask for each field inside those registers.

The file is not executable code. It provides compile-time constants for safe register composition, extraction, and read/modify/write operations in the ATHUB, GMC, and power-management paths.

## Important APIs, types, and functions
There are no functions, structs, enums, or storage. The exported API is the macro convention guarded by `_athub_3_0_0_SH_MASK_HEADER`.

For each field the header defines a `REGISTER__FIELD__SHIFT` macro and a `REGISTER__FIELD_MASK` macro. Key field groups include:

- XPB routing fields: `XPB_RTR_SRC_APRTR*__BASE_ADDR`, and `XPB_RTR_DEST_MAP*` fields such as `NMR`, `DEST_OFFSET`, `DEST_SEL`, `DEST_SEL_RPB`, `SIDE_OK`, and `APRTR_SIZE`.
- XPB client grouping fields: `XPB_CLG_CFG0` through `XPB_CLG_CFG7` fields for WCB number, LB type, P2P BAR, host flush, and side flush; `XPB_CLG_EXTRA*` compare/mask/valid fields; and GFX/MM/GUS match/mask registers.
- XPB BAR and peer routing fields: `XPB_P2P_BAR_CFG`, `XPB_P2P_BAR0` through `XPB_P2P_BAR7`, `XPB_P2P_BAR_SETUP`, delta registers, and `XPB_PEER_SYS_BAR0` through `XPB_PEER_SYS_BAR13`.
- XPB status/control fields: clock-gating delays and enable bits in `XPB_CLK_GAT`, interface credits/status, pipe fullness and busy bits, subsystem stall/reset bits in `XPB_SUB_CTRL`, sticky status fields, miscellaneous fields, and performance knobs.
- ATHUB power/control fields: `ATHUB_MISC_CNTL__CG_ENABLE_MASK`, `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK`, power-gating status/busy fields, light-sleep delay controls, and `ATHUB_MEM_POWER_LS` setup/hold fields.
- RPB policy and routing fields: pass-through override bits, block-level override fields, tag fields, arbitration controls, BIF controls, SDP/DF port credits, virtual-channel switching, ATS controls, and performance-counter configuration/result fields.

The naming convention is the important contract. Callers typically OR a mask into a register, clear a mask out of a register, or shift a prepared field value by the corresponding `__SHIFT` before masking.

## Control flow
This header has no runtime control flow. Its only branch-like behavior is the include guard.

The runtime control flow using these masks is visible in `amdgpu/athub_v3_0.c`. That file reads ATHUB miscellaneous control, sets or clears `ATHUB_MISC_CNTL__CG_ENABLE_MASK` when medium-grain clock gating is requested and supported, sets or clears `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` for light sleep, then writes the register back only if the value changed. `athub_v3_0_get_clockgating()` reads the same register and reports enabled feature flags when these masks are set.

Most other masks in this file are register-schema data rather than direct call-site logic in the inspected tree. They become active when future or conditional code programs XPB routing, BAR setup, RPB arbitration, ATS, or performance counters.

## State and persistence behavior
The header contains no mutable state. The masks describe fields in mutable hardware registers.

The most stateful hardware areas represented here are:

- `ATHUB_MISC_CNTL` clock-gating, power-gating, busy/status, and light-sleep control bits.
- XPB routing and aperture maps that determine how source address windows map to destination paths.
- P2P and peer system BAR fields that mark BAR validity, address fields, compression/send behavior, and system BAR relationships.
- XPB sticky and write-one-to-clear status fields, where writes can acknowledge hardware events.
- XPB subsystem stall and reset fields, which can intentionally stop or reset internal sub-blocks.
- RPB arbitration, virtual-channel switching, pass-through, block-level, ATS, and port credit fields, which affect request ordering and data flow.
- RPB performance counters, where clear, enable, selection, compare, and result fields are hardware-maintained.

Persistence depends on GPU reset, power transitions, firmware, and AMDGPU reprogramming. The macros themselves do not preserve or restore register contents.

## Dependencies
This header depends only on the preprocessor, but correct use depends on:

- `athub_3_0_0_offset.h` or an IP-revision-compatible offset source naming the registers being accessed.
- AMDGPU register helpers and common bitfield idioms used by the driver.
- ATHUB IP version selection so the bit layout matches the actual silicon.
- Power-management feature flags such as `AMD_CG_SUPPORT_ATHUB_MGCG` and `AMD_CG_SUPPORT_ATHUB_LS` in the direct ATHUB v3 consumer.
- Hardware documentation or generated-register tooling that defines reserved, W1C, sticky, busy, and performance-counter semantics beyond the bit positions visible here.

## Integration points
Direct include sites in this tree are `drivers/gpu/drm/amd/amdgpu/athub_v3_0.c` and `drivers/gpu/drm/amd/amdgpu/gmc_v11_0.c`.

`athub_v3_0.c` directly consumes `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` for clock-gating and memory light-sleep control. It uses the same masks when reporting active clock-gating flags.

`gmc_v11_0.c` includes this header alongside the offset header for GFX11 memory-controller support. ATHUB is part of the address-translation and memory-routing path, so the bitfield definitions are part of the register vocabulary available to GMC code even when individual masks are not referenced by the visible grep results.

The file also integrates with generated ATHUB register families. Similar register names appear across 1.x, 2.x, 3.x, and 4.x headers, but field presence and register offsets vary by generation. Consumers must include the matching generation rather than relying on a same-named field from another IP.

## Risks and edge cases
Incorrect masks are as dangerous as incorrect offsets. A wrong mask can preserve the target register address but alter the wrong field, leave stale bits behind, or write reserved bits with undefined hardware effects.

Read/modify/write code must use masks carefully around W1C and sticky registers such as `XPB_STICKY_W1C`. Writing back a value read from a status register can clear events.

Shift and mask pairs need to be kept together. Using a shift from one ATHUB generation with a mask or offset from another generation can produce plausible-looking values that program the wrong field.

Several fields are control-plane hazards: `XPB_SUB_CTRL` stall/reset bits can stop internal request paths; `RPB_BIF_CNTL*` and `RPB_ARB_CNTL*` can change request arbitration; ATS fields can affect translation behavior; and BAR validity/address fields can change peer routing. These should not be toggled by generic debug code without hardware-specific sequencing.

Some field names are generic or generated, such as `XPB_MISC_CFG__FIELDNAME*`. The names alone do not explain semantics, so code using those fields should cite the hardware specification or a known programming sequence.

The direct ATHUB v3 power-management consumer also has IP-version-specific offset overrides for `ATHUB_MISC_CNTL`. That means a matching bit mask does not imply the register sits at the same offset across all ATHUB v3 variants.

## Test signals
Useful validation signals include:

- Build coverage for `athub_v3_0.c` and `gmc_v11_0.c`, proving all referenced masks compile with the v3 offset header.
- Clock-gating tests on ATHUB v3 hardware confirming writes using `ATHUB_MISC_CNTL__CG_ENABLE_MASK` and `ATHUB_MISC_CNTL__CG_MEM_LS_ENABLE_MASK` change only those intended bits.
- Register readback tests around `athub_v3_0_get_clockgating()` showing reported `AMD_CG_SUPPORT_ATHUB_MGCG` and `AMD_CG_SUPPORT_ATHUB_LS` flags match hardware register state.
- Hardware bring-up validation comparing generated masks against AMD's register database for XPB/RPB fields, especially BAR address/valid fields, W1C status fields, and RPB ATS/arbitration controls.
- Stress tests across suspend/resume, runtime power management, and GPU reset ensuring higher-level code restores ATHUB state and does not rely on reset-preserved values.
- Negative testing for status-clearing paths to ensure code never performs unsafe read/modify/write cycles on W1C fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_3_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_4_1_0_offset.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/athub/athub_4_1_0_offset.h -->
