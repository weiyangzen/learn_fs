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
