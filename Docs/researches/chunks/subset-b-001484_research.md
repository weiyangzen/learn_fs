# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_5_0_sh_mask.h lines 4614-8563

## Purpose

This chunk is part of the generated AMD BIF 5.0 register bitfield mask header. It does not implement executable logic; it defines C preprocessor constants that describe the bit masks and shift positions for BIF/PCIe PHY registers used by AMDGPU and power-management code on VI-era ASICs.

The assigned range covers the end of the PB0 PHY register field definitions and the beginning/middle of the PB1 PHY definitions. Most of the fields are for PCIe physical-layer control: PLL power/frequency overrides, RX adaptation and equalization tuning, per-lane RX/TX status override fields, TX coefficient/preset acceptance tables, lane grouping/skew control, debug/DFT controls, strap-derived defaults, and per-lane power/data overrides.

The header is paired with the matching register-offset header, `bif_5_0_d.h`, and with helper macros such as `REG_GET_FIELD()` and `REG_SET_FIELD()`. A driver source file includes both the offset and mask headers, reads or writes a 32-bit MMIO/indirect register, and uses these constants to isolate or set a named bitfield without hardcoding numeric bit positions at the call site.

## Important APIs, Types, And Constants

There are no functions, structs, or runtime APIs in this range. The important interface is the naming convention and the generated constants:

- `<REGISTER>__<FIELD>_MASK`: a 32-bit mask for a field inside a hardware register.
- `<REGISTER>__<FIELD>__SHIFT`: the bit offset used to shift field values into or out of the masked position.
- `PB0_*` and `PB1_*`: two parallel PHY/BIF register namespaces. PB0 definitions begin before this chunk and finish in this chunk; PB1 starts in this chunk and continues after it.
- `PB*_RX_GLB_CTRL_REG0` through `PB*_RX_GLB_CTRL_REG8`: RX global configuration fields for Gen1/Gen2/Gen3 adaptation, CDR frequency/phase gains, DFE/FOM/LEQ/OC timing, loop gains, DLL lock/reset behavior, L0/L0s/L1 transition behavior, and frontend/auxiliary power lookup behavior.
- `PB*_RX_GLB_SCI_STAT_OVRD_REG0` and `PB*_RX_GLB_OVRD_REG0/1`: RX SCI status update masks and explicit override value/enable pairs for adaptation hold/reset/tracking, clocks, PLL selection, DLL/front-end/idledet/aux power, and FOM behavior.
- `PB*_RX_LANE[0-15]_CTRL_REG0` and `PB*_RX_LANE[0-15]_SCI_STAT_OVRD_REG0`: per-lane RX backup/debug/test/termination fields and lane status fields such as `RXPWR`, `ELECIDLEDETEN`, `REQUESTTRK`, `ENABLEFOM`, `REQUESTFOM`, `RESPONSEMODE`, and `RXEYEFOM`.
- `PB*_TX_GLB_CTRL_REG0`, `PB*_TX_GLB_LANE_SKEW_CTRL`, `PB*_TX_GLB_SCI_STAT_OVRD_REG0`, `PB*_TX_GLB_COEFF_ACCEPT_TABLE_REG[0-3]`, and `PB*_TX_GLB_OVRD_REG[0-4]`: TX global timing, lane grouping, SCI status override, Gen1/Gen2/Gen3 driver tap override, coefficient acceptance, and clock/reset/data/power override fields.
- `PB*_TX_LANE[0-15]_CTRL_REG0`, `PB*_TX_LANE[0-15]_OVRD_REG0`, and `PB*_TX_LANE[0-15]_SCI_STAT_OVRD_REG0`: per-lane TX display-clock, data inversion, swing boost, PRBS, data-clock/driver/frontend power overrides, and TX status fields such as `TXPWR`, `TXMARG`, `DEEMPH`, `COEFFICIENTID`, and `COEFFICIENT`.
- `PB1_GLB_CTRL_REG[0-5]`, `PB1_GLB_SCI_STAT_OVRD_REG[0-4]`, and `PB1_GLB_OVRD_REG[0-2]`: PB1-level debug, bypass, bandgap/reference, DLL, power-good, termination, link-speed/frequency, and SCI update override fields.
- `PB1_STRAP_*`: strap/default fields for global, TX, RX, PLL, and pin behavior. These encode reset-time hardware configuration inputs such as adaptation modes, equalization defaults, PLL controls, terminations, startup timers, and debug defaults.
- `PB1_DFT_*` and `PB1_HW_DEBUG`: design-for-test jitter injection, PHY debug enable/mode, DFT status, lane enables, and a 32-bit hardware debug bitmap.
- `PB1_PLL_RO*` and `PB1_PLL_LC*`: ring-oscillator and LC PLL control/override/status fields, including clock enables, power lookup entries, reset/debug controls, refdiv/fbdiv/core clock/divider overrides, PLL power, and PLL frequency status.

## Control Flow

This header has no control flow. It contributes compile-time constants that are consumed by C expressions in other AMDGPU and powerplay source files. The practical read/modify/write flow is:

1. Include `bif_5_0_sh_mask.h` and the matching register-address definitions.
2. Read a register with an AMDGPU MMIO helper, or prepare a literal value for a write.
3. Use a mask/shift pair, usually through helper macros, to extract or update one field.
4. Write the resulting 32-bit register value back through an MMIO or indirect-register helper.

The range itself is ordered by register block rather than by runtime use. PB0 RX global fields are followed by PB0 RX lanes, PB0 TX global fields, PB0 TX lanes, then PB1 global/strap/DFT/PLL/RX/TX definitions. Repeated lane records are intentionally expanded for each lane number rather than represented by arrays or functions.

The requested range ends at line 8563 in the middle of `PB1_TX_LANE14_OVRD_REG0`: it includes `TX_DCLK_EN_OVRD_VAL_14`, `TX_DCLK_EN_OVRD_EN_14`, and the mask for `TX_DRV_DATA_EN_OVRD_VAL_14`, while the corresponding shift and later lane-14 override/status fields continue after this chunk. That is a chunk boundary artifact, not a semantic stop in the header.

## State And Persistence Behavior

The file stores no software state and performs no persistence. The constants describe hardware register layout. State changes happen only in consumers that use these masks to write device registers.

The hardware state represented by these fields is persistent at device-register granularity until reset, power transition, firmware action, or another driver write changes it. The affected domains include PCIe PHY lane power state, equalization/adaptation parameters, TX coefficients, PLL clocks, debug/test controls, strap-derived defaults, and SCI/status override behavior.

Because these macros are compile-time definitions, a wrong mask or shift becomes baked into every consumer at build time. There is no runtime validation that a mask matches the underlying ASIC register layout.

## Dependencies

This chunk depends on AMD's generated register naming scheme and on the corresponding address header for BIF 5.0. The `_MASK` and `__SHIFT` constants are meaningful only when used with the matching register offset, such as `ixPB1_TX_GLB_COEFF_ACCEPT_TABLE_REG0` from `bif_5_0_d.h`.

Repository consumers include AMDGPU and power-management files that include `bif/bif_5_0_sh_mask.h`, such as `amdgpu/vi.c`, `amdgpu/mxgpu_vi.c`, `amdgpu/gmc_v8_0.c`, `amdgpu/gfx_v8_0.c`, `amdgpu/sdma_v2_4.c`, `amdgpu/sdma_v3_0.c`, and several `pm/powerplay` SMU/BACO managers. Those consumers rely on AMDGPU register access helpers (`RREG32*`, `WREG32*`) and field helpers (`REG_GET_FIELD`, `REG_SET_FIELD`, plus powerplay `CGS_*` variants) to use the generated bit definitions safely.

The definitions also depend on hardware documentation for the BIF 5.0 PHY. Many names expose implementation-specific concepts such as CBI updates, SCI status overrides, RX APU/debug paths, RX FOM measurement, Gen1/2/3 tuning, LC and RO PLLs, and lane grouping. These are not self-describing enough to change by intuition; updates must come from the authoritative ASIC register generator or hardware spec.

## Integration Points

The direct integration point is compile-time inclusion by AMDGPU and powerplay code for VI-generation ASIC setup, suspend/resume, BACO, GPU reset, SDMA/GFX/GMC initialization, and SMU interactions. This header provides field-level constants; source files provide the sequencing and policy.

Key hardware integration surfaces represented by this chunk are:

- PCIe PHY RX adaptation and equalization, including CDR gains, DFE/FOM/LEQ timing, eye/FOM reporting, and lane electrical-idle/tracking status.
- PCIe PHY TX behavior, including driver taps, coefficient acceptance, de-emphasis, margining, PRBS/debug enable, data inversion, swing boost, lane grouping, and per-lane power/data overrides.
- PLL and clock management for LC and RO PLLs, including power, clock enable, reference/frequency/divider overrides, and PLL status override fields.
- Strap/default configuration used to reflect reset-time hardware options into driver-visible register fields.
- Debug and DFT paths for PHY validation, jitter injection, PRBS, analog debug selection, bypass paths, and test status.

The final merged research document should connect this chunk to adjacent ranges. The preceding chunk contains earlier PB0 global, strap, DFT, and PLL definitions; this chunk starts after PB0 PLL LC1 status definitions have already begun. The following chunk completes PB1 TX lane 14, lane 15, and later BIF/PCIe field definitions.

## Risks And Edge Cases

- Incorrect masks or shifts can cause silent hardware misprogramming. A field write can accidentally alter neighboring bits, fail to set the intended field, or read a bogus status value.
- PB0 and PB1 definitions are highly repetitive but not interchangeable. Copying a PB0 constant into PB1 code, or a lane-N constant into another lane without checking the register address, can target the wrong PHY block or lane.
- The repeated lane records invite mechanical drift. Each RX lane should expose the same set of control/status fields, and each TX lane should expose the same control/override/status fields, but line-boundary chunks can make a lane appear incomplete.
- The chunk begins and ends mid-header context. Specifically, it starts with the last field of `PB0_PLL_LC1_SCI_STAT_OVRD_REG0` and ends mid-`PB1_TX_LANE14_OVRD_REG0`; research and review should not infer complete register coverage solely from this slice.
- Many fields are override enable/value pairs. Setting an override value without its enable bit, or leaving an enable asserted during normal link training, can interfere with PHY-managed state machines.
- Strap fields often represent reset defaults. Treating them as ordinary mutable configuration can conflict with firmware, board straps, or ASIC-specific bring-up assumptions.
- Debug/DFT fields such as PRBS, jitter injection, analog select, BSCAN, bypass, and forced PLL/reset controls can disrupt normal PCIe link operation if enabled in production paths.
- TX coefficient and RX equalization fields affect link quality. Bad values can produce training failures, link downtraining, replay errors, or intermittent PCIe faults that appear outside the BIF driver code.
- Some fields are status override or "ignore CBI update" controls. Misuse can leave software reading stale or forced status rather than hardware-owned lane/PLL state.

## Test Signals

Useful validation signals are mostly build-time and hardware bring-up signals:

- A kernel or module build that includes AMDGPU should compile cleanly with no missing BIF 5.0 mask/shift symbols.
- Static generation checks should verify that every `_MASK` has the expected `__SHIFT`, that masks are contiguous where required, and that repeated lane records are symmetric across lanes and PB0/PB1 where the hardware layout expects symmetry.
- Register access tests or debugfs register dumps should confirm that `REG_GET_FIELD()` extracts plausible values for RX/TX lane status, PLL power/frequency status, and link-speed/frequency fields.
- PCIe link training should reach the expected width and generation on affected VI ASICs after driver initialization, suspend/resume, BACO entry/exit, and GPU reset.
- Stress testing should show no new PCIe AER/replay/equalization errors, link downtraining, or intermittent GPU hangs when code paths use RX/TX/PLL masks from this header.
- Power-management tests should validate that BACO/SMU paths can still force or observe the intended BIF/PHY fields without leaving debug, DFT, or override bits asserted.
- Hardware diagnostics that intentionally enable PRBS, jitter injection, or PHY debug modes should verify that the requested lane and PB block are affected, and that the fields can be restored to normal afterward.
