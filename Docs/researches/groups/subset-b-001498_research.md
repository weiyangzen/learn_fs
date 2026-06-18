# Research: subset-b-001498

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_offset.h

## Purpose

`clk_10_0_2_offset.h` is a generated AMDGPU CLK register address header for the `clk_clk1_0_SmuClkDec` address block at base address `0x5b800`. It exposes symbolic MMIO register offsets for a CLK1 block used by display clock management. The header does not implement clock policy; it gives driver code stable names for registers used to inspect and control PLL programming, clock bypass selection, deep-sleep enablement, and live clock counters.

The file is small and guarded by `_clk_10_0_2_OFFSET_HEADER`. Every register macro has a paired `*_BASE_IDX` macro. The base index is consistently `1`, so consumers must preserve that instance index when building register tables.

## Important APIs, Types, And Macros

There are no functions, structs, or C types. The exported API is a set of preprocessor constants:

- `mmCLK1_CLK_PLL_REQ` and `mmCLK1_CLK_PLL_REQ_BASE_IDX`: PLL request register for feedback multiplier and spine divider fields described in the matching shift/mask header.
- `mmCLK1_CLK0_BYPASS_CNTL`, `mmCLK1_CLK1_BYPASS_CNTL`, `mmCLK1_CLK2_BYPASS_CNTL`, and `mmCLK1_CLK3_BYPASS_CNTL`: bypass source and divisor control registers for the CLK0 through CLK3 outputs.
- `mmCLK1_CLK2_STATUS`: status register for CLK2. This file provides the address even though the paired `clk_10_0_2_sh_mask.h` does not define fields for it.
- `mmCLK1_CLK3_DFS_CNTL`, `mmCLK1_CLK3_DS_CNTL`, and `mmCLK1_CLK3_ALLOW_DS`: dynamic frequency/deep-sleep controls for CLK3, typically associated with DCFCLK-style low-power behavior in the display clock manager.
- `mmCLK1_CLK0_CURRENT_CNT` through `mmCLK1_CLK3_CURRENT_CNT`: live clock counter registers used to measure or report current clock rates.

## Control Flow

The only control flow is compile-time include-guard behavior. At runtime, AMD display clock-manager code maps these constants into register tables and then uses helpers such as `REG_READ`, `REG_GET`, or lower-level MMIO helpers to read and write hardware registers. Typical consumer flow is: select the ASIC-specific register table, read the current counter or bypass register by symbolic name, and decode any fields with the matching shift/mask macros.

## State And Persistence Behavior

This header stores no runtime state. The state affected by the constants lives in GPU hardware registers. Writes to the PLL request, bypass, DFS, or deep-sleep registers can persist until later driver writes, firmware/SMU action, power-state changes, or reset. Current-count and status registers are observational state and should be treated as hardware readback values rather than software-owned persistence.

## Dependencies

The file has no include dependencies. It depends operationally on the AMDGPU register-access layer, ASIC selection code that chooses the CLK 10.0.2 layout only for compatible hardware, and `clk_10_0_2_sh_mask.h` for field positions. The `mm` prefix and `BASE_IDX` convention match AMDGPU generated register headers and are consumed by display clock-manager register-table macros.

## Integration Points

The main integration point is the AMD display core clock-manager path under `drivers/gpu/drm/amd/display/dc/clk_mgr`. Related local code defines clock-manager register structs with fields such as `CLK1_CLK0_CURRENT_CNT`, `CLK1_CLK3_ALLOW_DS`, and `CLK1_CLK*_BYPASS_CNTL`. Those structs are populated from generated register headers and used for display clock reporting, bypass-source decoding, SMU logging, and PLL-derived frequency calculations.

## Risks And Edge Cases

The primary risk is using the right register name with the wrong base index or ASIC generation. These constants are small integer offsets, so an incorrect include or table macro can compile cleanly while targeting a different clock block. `CLK2_STATUS` and `CLK3_DFS_CNTL` have address definitions here without corresponding field masks in the paired file, so consumers must either use another field source or treat them as raw values. Registers that modify PLLs, bypasses, or deep-sleep control should be handled with hardware sequencing and reserved-bit preservation; this file does not document ordering, lock, or side-effect requirements.

## Test Signals

Useful validation includes building AMDGPU display configurations that include this header, regenerating CLK 10.0.2 register headers from the authoritative AMD register database, and comparing offsets. Runtime tests should read back current-count registers for DISPCLK/DPPCLK/DPREFCLK/DCFCLK-style clocks, verify bypass register decoding against expected sources, and exercise display suspend/resume or deep-sleep transitions while checking that CLK3 low-power state is reported correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_sh_mask.h

## Purpose

`clk_10_0_2_sh_mask.h` is the generated field-layout companion for `clk_10_0_2_offset.h`. It defines `*_SHIFT` and `*_MASK` macros for CLK1 PLL request, bypass control, deep-sleep control, and current-count registers in the `clk_clk1_0_SmuClkDec` block. It contains no executable logic; its purpose is to let AMDGPU code compose and decode 32-bit register values without embedding bit positions at call sites.

## Important APIs, Types, And Macros

There are no functions or types. The public surface is the macro convention:

- `CLK1_CLK_PLL_REQ__FbMult_int`, `PllSpineDiv`, and `FbMult_frac` fields define a 9-bit integer feedback multiplier, 4-bit spine divider at bit 12, and 16-bit fractional feedback multiplier at bit 16.
- `CLK1_CLK0_BYPASS_CNTL` through `CLK1_CLK3_BYPASS_CNTL` each provide `CLKx_BYPASS_SEL` in bits 0..2 and `CLKx_BYPASS_DIV` in bits 16..19.
- `CLK1_CLK3_DS_CNTL__CLK3_DS_DIV_ID` provides a 3-bit deep-sleep divider ID.
- `CLK1_CLK3_ALLOW_DS__CLK3_ALLOW_DS` exposes the deep-sleep allow bit at bit 0.
- `CLK1_CLK0_CURRENT_CNT` through `CLK1_CLK3_CURRENT_CNT` expose a full 32-bit `CURRENT_COUNT` field.

Consumers usually use these macros through AMDGPU field helpers such as `REG_GET`, `REG_SET`, or `get_reg_field_value`, or manually with `mask` and `shift` expressions.

## Control Flow

The header's only control flow is the `_clk_10_0_2_SH_MASK_HEADER` include guard. Runtime flow is entirely in consumers. A common read path is: read `mmCLK1_CLK_PLL_REQ`, extract `FbMult_int` and `FbMult_frac`, and derive a reference or display clock rate. Bypass reporting reads a `CLK1_CLKx_BYPASS_CNTL` register and extracts `CLKx_BYPASS_SEL`. Deep-sleep reporting reads `CLK1_CLK3_ALLOW_DS` or `CLK1_CLK3_DS_CNTL` and interprets the allow and divider fields.

## State And Persistence Behavior

The macros themselves are compile-time constants. They describe state stored in hardware registers. PLL fields and bypass/divider fields are configuration state; current-count fields are hardware measurement/readback state; the deep-sleep allow bit controls low-power behavior until hardware reset or subsequent driver/firmware programming. The file does not cache, allocate, or persist anything in software.

## Dependencies

This file depends on the matching CLK 10.0.2 offset header for register addresses and on AMDGPU register-field helpers that expect the `REGISTER__FIELD_MASK` and `REGISTER__FIELD__SHIFT` naming convention. It also depends on correct ASIC dispatch: the bit layout is only valid for hardware matching this generated CLK version.

## Integration Points

Display clock-manager code uses equivalent PLL request fields in multiple DCN generations to compute or report clock values. Local integration searches show clock-manager headers and C files use current-count, bypass-control, and deep-sleep fields to populate debug structures and logs. This header is therefore part of the low-level contract between generated ASIC register metadata and display clock observability/power management.

## Risks And Edge Cases

Incorrect masks silently mis-decode clocks or write adjacent fields. PLL fields are especially sensitive because frequency calculations depend on the exact fractional and integer multiplier widths. Bypass registers use repeated field names with only the clock number changing, which is a copy/paste risk in register tables. `CURRENT_COUNT_MASK` uses `0xFFFFFFFFL`; consumers should store values in unsigned fixed-width types to avoid signed-long surprises on 32-bit builds. For writable registers, callers should preserve reserved bits with read-modify-write because this header only describes known fields.

## Test Signals

Validation should build the display driver paths that include this header and compare generated masks against AMD's register database. Runtime checks include reading PLL fields and verifying derived frequencies, reading current-count registers under known clock states, toggling or observing deep-sleep allowance during display idle transitions, and checking bypass-source debug output for each CLK0..CLK3 register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_10_0_2_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_offset.h

## Purpose

`clk_11_0_0_offset.h` is a generated AMDGPU register address header for a compact CLK 11.0.0 block. It names two registers in the `clk_clk3_0_SmuClkDec` address block at base address `0x5c800`: a CLK3 PLL request register and a CLK2 DFS divider-control register. The header gives display clock-manager code symbolic offsets for ASIC-specific clock programming and readback.

## Important APIs, Types, And Macros

The file defines no functions or C types. Its exported constants are:

- `mmCLK3_0_CLK3_CLK_PLL_REQ` with `BASE_IDX` `3`, offset `0x000e`.
- `mmCLK3_0_CLK3_CLK2_DFS_CNTL` with `BASE_IDX` `3`, offset `0x0054`.

The prefix encodes both the clock block instance (`CLK3_0`) and register family (`CLK3`). Consumers use the matching `clk_11_0_0_sh_mask.h` macros to decode feedback multiplier and divider fields.

## Control Flow

Only the `_clk_11_0_0_OFFSET_HEADER` include guard executes at compile time. Runtime code selects this header's register table for compatible ASICs, reads the PLL request register to derive the PLL-programmed clock source, and reads or writes the CLK2 DFS control register to inspect or program the divider. The file itself does not sequence clock changes.

## State And Persistence Behavior

The header contributes compile-time constants only. Hardware state is stored in the PLL request and DFS control registers. PLL and divider values are persistent hardware configuration across normal software reads, but can change through SMU/firmware interaction, display clock-manager updates, power transitions, or reset.

## Dependencies

The file depends on AMDGPU's generated-register naming conventions, the matching shift/mask header, and display clock-manager infrastructure that turns `mm*` names plus `BASE_IDX` into register-table entries. It also depends on correct ASIC matching because the offsets and base index are not self-validating.

## Integration Points

Local display code references CLK3 PLL request fields through `CLK_SRI` and `CLK_SF`-style macros in clock-manager internal headers. These constants support DCN clock-manager paths that need PLL feedback multiplier values or DFS divider values for derived clock reporting and programming.

## Risks And Edge Cases

This header is sparse: it exposes only two registers. Consumers must not assume it covers the full CLK block. The `BASE_IDX` value is `3`, unlike many newer register headers that use base index `0`, so table-generation macros must retain the correct base index. Confusing `CLK3_0_CLK3_CLK2_DFS_CNTL` with similarly named CLK0/CLK1/CLK4 blocks can result in reading the wrong clock domain.

## Test Signals

Build coverage should include the DCN clock-manager variant that uses CLK 11.0.0 metadata. Hardware validation should verify PLL-derived frequency calculations from `CLK3_0_CLK3_CLK_PLL_REQ` and divider extraction from `CLK3_0_CLK3_CLK2_DFS_CNTL`. A generated-header comparison against AMD register metadata is the strongest unit-level signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_sh_mask.h

## Purpose

`clk_11_0_0_sh_mask.h` defines the field positions and masks for the two registers named by `clk_11_0_0_offset.h`. It is generated hardware metadata for the `clk_clk3_0_SmuClkDec` block and supports safe decoding of CLK3 PLL request fields and CLK2 DFS divider control.

## Important APIs, Types, And Macros

There are no runtime APIs or types. The macro surface is:

- `CLK3_0_CLK3_CLK_PLL_REQ__FbMult_int__SHIFT`/`MASK`: 9-bit integer PLL feedback multiplier at bit 0.
- `CLK3_0_CLK3_CLK_PLL_REQ__PllSpineDiv__SHIFT`/`MASK`: 4-bit spine-divider field at bit 12.
- `CLK3_0_CLK3_CLK_PLL_REQ__FbMult_frac__SHIFT`/`MASK`: 16-bit fractional PLL feedback multiplier at bit 16.
- `CLK3_0_CLK3_CLK2_DFS_CNTL__CLK2_DIVIDER__SHIFT`/`MASK`: 7-bit CLK2 divider field at bit 0.

The field names match AMDGPU's `REG_GET`/`REG_SET` macro expectations.

## Control Flow

The only direct flow is the include guard. Consumer flow is generally read-only for diagnostics and clock calculation: read the PLL request register, extract multiplier fields, optionally combine them with reference-clock information, and read the DFS divider to determine the final clock. If a path programs the divider, it should use the mask to update only the divider field.

## State And Persistence Behavior

The file itself has no mutable state. It describes persistent hardware configuration fields. PLL multiplier and spine divider values influence the source clock. The DFS divider influences the clock output derived from that source. Changes made through these fields affect hardware behavior until changed by driver, firmware, power management, or reset.

## Dependencies

This header depends on the matching offsets, AMDGPU field-helper macro conventions, and unsigned 32-bit register access. Its values are ASIC-specific and must be synchronized with generated CLK 11.0.0 hardware definitions.

## Integration Points

Display clock-manager internal headers contain table macros for `CLK3_CLK_PLL_REQ` and `CLK3_CLK2_DFS_CNTL` and field macros for `FbMult_int`/`FbMult_frac`. Those table entries are consumed by clock-manager code when calculating display-related clock rates or reporting hardware clock state.

## Risks And Edge Cases

The `CLK2_DIVIDER` field is 7 bits wide, which differs from the 3-bit bypass selectors and 4-bit deep-sleep dividers found in other CLK generations. Consumers should not share field widths across generations by assumption. PLL calculations can be wrong if `PllSpineDiv` is ignored on hardware that requires it. Mask literals use `L` suffixes, so unsigned storage is preferred.

## Test Signals

Test signals include compile coverage for clock-manager macros, generated-header comparison, and readback tests that validate PLL multiplier and divider-derived clock frequencies. Edge testing should cover divider boundary values and confirm that field extraction does not include adjacent bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_1_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_1_offset.h

## Purpose

`clk_11_0_1_offset.h` is a generated AMDGPU CLK register address header for a CLK4 block. It provides two MMIO register addresses: one for the CLK4 PLL request register and one for the CLK4 CLK2 current-count register. The header supports display clock-manager code that needs PLL source information and live clock readback on ASICs matching CLK 11.0.1.

## Important APIs, Types, And Macros

No functions or C types are defined. The exported register constants are:

- `mmCLK4_0_CLK4_CLK_PLL_REQ` at `0x460e`, `BASE_IDX` `0`.
- `mmCLK4_0_CLK4_CLK2_CURRENT_CNT` at `0x467f`, `BASE_IDX` `0`.

The matching shift/mask header provides PLL feedback multiplier, spine divider, fractional multiplier, and full-width current-count fields.

## Control Flow

Compile-time flow is limited to the `_clk_11_0_1_OFFSET_HEADER` include guard. Runtime consumers select this register layout for compatible hardware and typically read the PLL request register to calculate a clock source and read the current-count register to observe the effective CLK2 rate. This header does not define any sequencing, polling, or timeout behavior.

## State And Persistence Behavior

The constants are immutable at compile time. Hardware state behind the constants includes PLL configuration and live counter/readback state. PLL configuration persists until driver/firmware changes, power events, or reset. The current-count register is a hardware measurement endpoint and should not be treated as software-owned state.

## Dependencies

This file depends on AMDGPU generated-register infrastructure, `clk_11_0_1_sh_mask.h`, and clock-manager register-table macros that accept `mm*` names and base indices. Correct ASIC dispatch is required because the absolute-style offsets and base index differ from the CLK 11.0.0 and CLK 11.5.0 layouts.

## Integration Points

The display clock-manager internal header has register-table macros for `CLK4_CLK_PLL_REQ` and `CLK4_CLK2_CURRENT_CNT`. Those integrate with clock calculation and debug reporting paths, especially for clock domains where an FCLK or related fabric/display clock is represented by a CLK4 current counter.

## Risks And Edge Cases

The file is intentionally narrow and should not be used as a complete CLK4 register map. It uses `BASE_IDX` `0` and larger offsets (`0x46xx`), unlike CLK 11.0.0's small offsets with `BASE_IDX` `3`. Mixing these layouts will compile but target wrong registers. Consumers must also handle that only a CLK2 current count is exposed; other CLK4 counters are absent from this generation's header.

## Test Signals

Build tests should compile the DCN paths that instantiate the CLK4 register table. Runtime checks should validate PLL field extraction from `mmCLK4_0_CLK4_CLK_PLL_REQ` and current-count readback from `mmCLK4_0_CLK4_CLK2_CURRENT_CNT` under known clock conditions. Regenerated metadata comparison is the best static check.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_1_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_1_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_1_sh_mask.h

## Purpose

`clk_11_0_1_sh_mask.h` is the generated field-layout header for the CLK 11.0.1 CLK4 register subset. It defines field masks for the CLK4 PLL request register and the CLK4 CLK2 current-count register. It enables AMDGPU display code to decode PLL settings and live counter values with the standard register-field helper convention.

## Important APIs, Types, And Macros

There are no functions or structs. The exported field macros are:

- `CLK4_0_CLK4_CLK_PLL_REQ__FbMult_int`: 9-bit integer feedback multiplier at bit 0.
- `CLK4_0_CLK4_CLK_PLL_REQ__PllSpineDiv`: 4-bit PLL spine divider at bit 12.
- `CLK4_0_CLK4_CLK_PLL_REQ__FbMult_frac`: 16-bit fractional feedback multiplier at bit 16.
- `CLK4_0_CLK4_CLK2_CURRENT_CNT__CURRENT_COUNT`: full 32-bit current-count readback field.

Consumers use the `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` pairs through `REG_GET`/`REG_SET`-style helpers or direct bit operations.

## Control Flow

The only control flow is the `_clk_11_0_1_SH_MASK_HEADER` include guard. Runtime flow is consumer-driven: read the PLL request value, extract feedback fields, calculate a source clock, and read the current-count register when reporting or validating the resulting clock. The header does not enforce read ordering or lock behavior.

## State And Persistence Behavior

All symbols are compile-time constants. PLL fields describe persistent hardware configuration; the current-count field describes live measurement state. The driver may observe these fields repeatedly for diagnostics, but no software state is stored in the header.

## Dependencies

This header depends on the matching offset header, the AMDGPU field-helper naming convention, and correct ASIC-specific inclusion. It also relies on consumers using unsigned 32-bit arithmetic for masks such as `0xFFFF0000L` and `0xFFFFFFFFL`.

## Integration Points

Display clock-manager register macros reference CLK4 PLL and current-count fields for clock source and live-rate reporting. The file is part of the generated include tree under `asic_reg/clk`, so it can be selected by ASIC-specific display resource and clock-manager code without hand-coded offsets.

## Risks And Edge Cases

The paired offset header exposes only one current-count register, so code must not expect a full CLK0..CLK4 counter family. PLL fields share names and widths with other generations, but the register prefix differs; copying generic CLK1 or CLK3 code without updating prefixes can break table generation. Signed interpretation of full-width masks should be avoided.

## Test Signals

Static validation should compare the generated field list against AMD's source register database and build all users. Runtime validation should compare current-count readback to expected clock rates and verify PLL-derived calculations, including fractional multiplier handling and spine divider treatment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_0_1_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_offset.h

## Purpose

`clk_11_5_0_offset.h` is a generated AMDGPU CLK register address header for `clk_clk1_0_SmuClkDec` at base address `0x5c000`. It names CLK1 PLL, bypass, deep-sleep, and current-count registers for a four-clock block. It is structurally close to the CLK 10.0.2 CLK1 map but uses `CLK1_0_CLK1_*` register names, different offsets, and `BASE_IDX` `0`.

## Important APIs, Types, And Macros

There are no functions or types. The exported register constants are:

- `mmCLK1_0_CLK1_CLK_PLL_REQ` for PLL feedback multiplier control.
- `mmCLK1_0_CLK1_CLK0_BYPASS_CNTL` through `mmCLK1_0_CLK1_CLK3_BYPASS_CNTL` for per-clock bypass source/divider selection.
- `mmCLK1_0_CLK1_CLK3_DS_CNTL` and `mmCLK1_0_CLK1_CLK3_ALLOW_DS` for CLK3 deep-sleep divider and allow behavior.
- `mmCLK1_0_CLK1_CLK0_CURRENT_CNT` through `mmCLK1_0_CLK1_CLK3_CURRENT_CNT` for live clock counters.

Every register has `BASE_IDX` `0`, which is part of the register-table contract.

## Control Flow

The header only uses an include guard. Runtime flow is external: AMD display code selects ASIC-specific register tables, reads counters and bypass registers for diagnostics, and may use PLL/deep-sleep registers for clock calculation or low-power control. No polling loops or state transitions are implemented in this file.

## State And Persistence Behavior

The file holds no state. It identifies hardware state in PLL, bypass, deep-sleep, and current-count registers. PLL and bypass fields can affect the active display clock topology until driver/SMU changes or reset. Current counters are readback state, and deep-sleep registers affect whether and how CLK3 can enter lower-power operation.

## Dependencies

Operational dependencies include `clk_11_5_0_sh_mask.h`, AMDGPU MMIO/register-table helpers, and ASIC dispatch that selects CLK 11.5.0 only for matching hardware. Because this is generated metadata, it also depends on consistency with AMD's register database.

## Integration Points

The constants integrate with display clock-manager register structs containing `CLK1_CLK*_CURRENT_CNT`, `CLK1_CLK3_ALLOW_DS`, and `CLK1_CLK*_BYPASS_CNTL` fields. These paths populate debug and SMU log data for display clocks such as DISPCLK, DPPCLK, DPREFCLK, and DCFCLK, and help compute or verify clock sources from PLL and bypass state.

## Risks And Edge Cases

The name pattern is easy to confuse with `clk_10_0_2` because both represent a CLK1 block with four current counters. Offsets and base index differ, so sharing tables across generations is unsafe. `CLK3` is the only deep-sleep-controlled clock in this header; code must not assume CLK0/CLK1/CLK2 have matching allow registers. Hardware sequencing for PLL and bypass updates is not documented here and must come from clock-manager logic or hardware specs.

## Test Signals

Static tests should compare the generated offset table against the register database and build display clock-manager users. Runtime signals include current-count readbacks for each clock, bypass-source decoding, and display idle/suspend tests that confirm CLK3 deep-sleep allowance and counters behave as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_sh_mask.h

## Purpose

`clk_11_5_0_sh_mask.h` is the generated field-mask companion for `clk_11_5_0_offset.h`. It describes the bit layout of CLK1 PLL request, bypass-control, deep-sleep-control, and current-count registers in the CLK 11.5.0 generation. The header enables field extraction and read-modify-write operations in AMDGPU display clock code without hard-coded bit positions.

## Important APIs, Types, And Macros

There are no functions, structs, or enums. The field macros cover:

- `CLK1_0_CLK1_CLK_PLL_REQ__FbMult_int` at bits 0..8 and `FbMult_frac` at bits 16..31. Unlike CLK 10.0.2 and CLK 11.0.x PLL masks, this file does not define a `PllSpineDiv` field.
- `CLK1_0_CLK1_CLK0_BYPASS_CNTL` through `CLK1_0_CLK1_CLK3_BYPASS_CNTL`, each with a 3-bit `CLKx_BYPASS_SEL` and 4-bit `CLKx_BYPASS_DIV`.
- `CLK1_0_CLK1_CLK3_DS_CNTL__CLK3_DS_DIV_ID`, a 3-bit deep-sleep divider ID.
- `CLK1_0_CLK1_CLK3_ALLOW_DS__CLK3_ALLOW_DS`, a 1-bit deep-sleep allow flag.
- `CLK1_0_CLK1_CLK0_CURRENT_CNT` through `CLK1_0_CLK1_CLK3_CURRENT_CNT`, each exposing all 32 bits as `CURRENT_COUNT`.

## Control Flow

The header's only flow is its include guard. Runtime consumers read register values and pass them through field helpers. Typical paths extract PLL feedback values for frequency calculations, decode bypass selectors for diagnostics, read current-count registers for current clock rates, and inspect or program CLK3 deep-sleep bits.

## State And Persistence Behavior

The macros describe hardware state but do not store software state. PLL feedback and bypass/divider settings are persistent hardware configuration. Current-count fields are hardware readback. Deep-sleep allow and divider fields influence low-power entry and remain active until changed by driver, firmware, power transition, or reset.

## Dependencies

This file depends on matching offsets, AMDGPU field-helper conventions, and correct ASIC selection. It also depends on consumers noticing the missing `PllSpineDiv` field relative to nearby generations; generic PLL code must not unconditionally request that field for CLK 11.5.0.

## Integration Points

Display clock-manager code uses these field definitions through generated `CLK_SF`/`REG_GET` tables and clock debugging paths. The PLL fields feed clock derivation, bypass fields feed source reporting, current-count fields feed live frequency debug, and deep-sleep fields feed DCFCLK-style low-power state reporting.

## Risks And Edge Cases

The missing `PllSpineDiv` is the most important generation-specific difference. Code that assumes a spine divider exists because it is present in CLK 10.0.2 or CLK 11.0.x will fail to build or calculate incorrectly. Full-width current-count masks should be handled with unsigned values. Repeated bypass macros can be miswired across CLK0..CLK3 in register tables. As with all generated hardware metadata, manual edits can introduce silent hardware misprogramming.

## Test Signals

Validation should include build coverage of clock-manager tables for CLK 11.5.0, generated-header comparison, and runtime clock debug checks. Specific tests should confirm PLL frequency derivation without a spine-divider field, bypass decoding for all four clocks, and deep-sleep behavior for CLK3 during display idle transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_11_5_0_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_15_0_0_offset.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_15_0_0_offset.h

## Purpose

`clk_15_0_0_offset.h` is a generated AMDGPU CLK register address header for the `clk_clk8_0_SmuClkDec` address block at base address `0x6e000`. It uses the newer `regCLK8_*` naming style and exposes register offsets for five clock lanes, a tick-count configuration/status pair, bypass controls, deep-sleep controls, and current counters. It supports newer display clock-manager code, including DCN42-style CLK8 readback and debug paths.

## Important APIs, Types, And Macros

There are no functions or types. The register constants are:

- `regCLK8_CLK0_DS_CNTL` through `regCLK8_CLK4_DS_CNTL`: per-clock deep-sleep divider and allow-control registers.
- `regCLK8_CLK0_BYPASS_CNTL` through `regCLK8_CLK4_BYPASS_CNTL`: per-clock bypass source-selection registers.
- `regCLK8_CLK_TICK_CNT_CONFIG_REG` and `regCLK8_CLK_TICK_CNT_STATUS`: tick-count configuration and status registers for counter timing.
- `regCLK8_CLK0_CURRENT_CNT` through `regCLK8_CLK4_CURRENT_CNT`: live current-count registers for five clocks.

All entries use `BASE_IDX` `0`.

## Control Flow

Only the `_clk_15_0_0_OFFSET_HEADER` include guard is present. Runtime flow is implemented by consumers: configure or rely on the tick-count window, read current-count registers, read bypass controls, and inspect deep-sleep control bits for each clock. Local DCN42 clock-manager code reads `CLK8_CLK0_CURRENT_CNT` through `CLK8_CLK4_CURRENT_CNT`, reads bypass registers, and stores results in debug structures.

## State And Persistence Behavior

This file contains compile-time constants only. Hardware state includes per-clock deep-sleep configuration, bypass source selection, tick-count measurement configuration/status, and live current-count values. Deep-sleep and bypass settings are hardware configuration; current counts and tick status are readback/measurement state.

## Dependencies

The header depends on `clk_15_0_0_sh_mask.h`, generated AMDGPU register-table conventions that handle `reg*` names, and ASIC-specific code that maps CLK8 registers to display clock domains such as DISPCLK, DPPCLK, DPREFCLK, DCFCLK, and DTBCLK. It also depends on consumers retaining `BASE_IDX` `0`.

## Integration Points

Local display code shows direct integration with `dcn42_clk_mgr.c`: it reads CLK8 current counters, bypass registers, and deep-sleep state into clock debug/reporting structures, divides current counts for MHz-style presentation, and logs SMU clock state. `dc/inc/hw/clk_mgr.h` also defines CLK8 fields for clock-manager state snapshots.

## Risks And Edge Cases

This generation differs from older CLK1 headers by providing deep-sleep controls for all five clocks and by omitting PLL request registers entirely. Code ported from CLK1 generations must not assume PLL fields exist. The `reg` prefix may require different register-table macros than `mm`-prefixed headers. Current-count interpretation may depend on tick-count configuration, and the header does not define measurement timing semantics.

## Test Signals

Static validation should build DCN42/CLK8 register tables and compare generated offsets with AMD metadata. Runtime validation should read all five current counters, confirm bypass-source decoding, verify per-clock deep-sleep allow bits, and check that tick-count configuration/status behavior produces stable frequency readbacks across idle, active display, and suspend/resume paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_15_0_0_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_15_0_0_sh_mask.h -->
# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_15_0_0_sh_mask.h

## Purpose

`clk_15_0_0_sh_mask.h` is the generated bitfield header for the CLK 15.0.0 CLK8 block. It defines field masks for tick-count configuration, five bypass-control registers, and five deep-sleep-control registers. Unlike earlier CLK headers in this work item, it does not define PLL request fields or current-count fields, even though the offset header names current-count registers.

## Important APIs, Types, And Macros

There are no functions or C types. The exported field macros are:

- `CLK8_CLK_TICK_CNT_CONFIG_REG__TIMER_THRESHOLD`: a 16-bit threshold field at bit 0.
- `CLK8_CLK0_BYPASS_CNTL__CLK0_BYPASS_SEL` through `CLK8_CLK4_BYPASS_CNTL__CLK4_BYPASS_SEL`: 3-bit bypass source selectors for each of five clocks.
- `CLK8_CLK0_DS_CNTL` through `CLK8_CLK4_DS_CNTL`: each has a 4-bit `CLKx_DS_DIV_ID` at bits 0..3 and a `CLKx_ALLOW_DS` bit at bit 4.

These macros are used with standard AMDGPU field helpers or direct `get_reg_field_value`-style decoding.

## Control Flow

The header has only an include guard. Runtime consumers read or write CLK8 registers and use these masks to decode timer thresholds, bypass selectors, deep-sleep divider IDs, and deep-sleep allow bits. Local DCN42 code reads current-count and bypass registers, then decodes bypass fields with these masks; it also checks deep-sleep state using the allow bit position.

## State And Persistence Behavior

The macros are compile-time constants. The represented hardware state includes timer threshold configuration for clock-count measurement, bypass source configuration, and per-clock deep-sleep enable/divider settings. These settings persist in hardware until changed by driver, firmware, power transition, or reset. Current counters exist in the paired offset header, but this mask header does not define a `CURRENT_COUNT` field, implying consumers may read those registers as raw values.

## Dependencies

This file depends on `clk_15_0_0_offset.h`, AMDGPU field-helper conventions, and correct DCN/ASIC register selection. It also depends on consumers understanding the generation-specific CLK8 layout: five clocks, per-clock deep-sleep controls, and no PLL request masks in this file.

## Integration Points

The display clock-manager path for DCN42 uses CLK8 bypass and deep-sleep state to populate debug snapshots and log SMU clock information. Bypass fields map to displayed clock-source state for DISPCLK, DPPCLK, DPREFCLK, DCFCLK, and DTBCLK. Deep-sleep fields map to per-clock low-power eligibility and divider state. The timer threshold supports stable current-count measurement windows.

## Risks And Edge Cases

The paired offset file lists `CLK8_CLK_TICK_CNT_STATUS` and five `CURRENT_CNT` registers, but this mask file defines no status or current-count fields. Consumers should treat those as raw registers unless another generated source provides fields. `CLKx_ALLOW_DS` is bit 4 for every clock, but local comments in consumers may use legacy wording; tests should verify the clock index and bit meaning. Older CLK code that expects bypass divider fields at bits 16..19 will not apply here because CLK8 bypass masks only expose the selector.

## Test Signals

Validation should include compiling DCN42 clock-manager code, comparing masks with AMD register metadata, and runtime tests that read bypass selectors and deep-sleep fields for all five clocks. Frequency readback tests should verify that raw current-count values and tick threshold settings produce expected reported rates, and suspend/idle tests should ensure allow bits match actual low-power transitions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/clk/clk_15_0_0_sh_mask.h -->
