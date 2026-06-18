# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h

Chunk: `subset-b-001475`
Covered source range: lines 1-3812 of `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_sh_mask.h`

## Purpose

This chunk is the front portion of AMD's generated BIF 3.0 register field mask header. It does not implement executable logic; it provides C preprocessor constants that describe bit masks and bit shifts for fields in the BIF/NBIF register block used by older AMD GPU ASIC support code.

The header pairs with `bif_3_0_d.h`, which provides register addresses such as `mmBACO_CNTL`, `ixPB0_PIF_CNTL`, and `ixPB0_TX_LANE*_CTRL_REG0`. This file supplies the field-level constants used to compose, extract, and poll values inside those registers.

The covered range includes:

- top-level BIF/BACO control and status fields;
- bus number, device/function, framebuffer aperture, config aperture, MM index/data, interrupt, debug, reset, scratch, SSA, XDMA, and BIOS scratch field definitions;
- PB0 physical bus interface, PLL, RX, TX, lane, override, power, sequence, and debug fields for lanes 0-15;
- the beginning of equivalent PB1 global/debug/override/status field definitions.

The source range ends at line 3812 in the middle of the PB1 global SCI status override block. Later chunks must complete the PB1 family and the rest of the header before producing a final file-level report.

## Important APIs, Types, And Macros

There are no C functions, structs, enums, or exported symbols in this chunk. The API surface is entirely macro constants.

The naming convention is consistent:

- `<REGISTER>__<FIELD>_MASK` is the bit mask to isolate or update the field in a 32-bit register.
- `<REGISTER>__<FIELD>__SHIFT` is the right-shift count for the field.
- Register names are shared with address macros in `bif_3_0_d.h` and related generation-specific `*_d.h` files.

The chunk contains 3,788 `#define` lines in the assigned range. Excluding the include guard, almost all constants are field masks or shifts. There is one incomplete mask/shift pair at the range boundary: `PB1_GLB_SCI_STAT_OVRD_REG4__FREQDIV_14_MASK` appears at line 3812 and its matching shift is outside this work item.

Important register families in this range include:

- `BACO_CNTL`, `BF_ANA_ISO_CNTL`, `BIF_BACO_DEBUG`, and `BIF_BACO_DEBUG_LATCH`: BACO power-state entry/exit, isolation, reset, power-good, and debug latch fields.
- `BIF_BUSNUM_*` and `BIF_DEVFUNCNUM_*`: bus/device/function capture, list, mask, and autoupdate fields used when BIF filters or tracks host PCI identity.
- `BIF_RESET_EN`: enables and timing fields for soft reset, PHY/PIF/reset-to-config, hot reset, link-disable/down reset, driver reset, strap-valid reset, BIF core reset, and FLR for functions 0-2.
- `BUS_CNTL`, `CONFIG_*`, `MM_INDEX`, `MM_DATA`, `MM_CFGREGS_CNTL`: host aperture, VGA, BIOS ROM, posted/nonposted behavior, config space, and indirect MM register access controls.
- `BIF_FB_EN`, `BIF_XDMA_*`, `BIF_SSA_*`, `HDP_*_COHERENCY_FLUSH_CNTL`: fields around framebuffer access, XDMA apertures, system static aperture windows, and coherency flush controls.
- `INTERRUPT_CNTL` and `INTERRUPT_CNTL2`: interrupt-handler dummy reads, interrupt delay, non-snoop requests, and GPIO/IH interrupt routing.
- `BIF_PERFMON_CNTL` and `BIF_PERFCOUNTER*_RESULT`: performance counter enable, reset, selector, and result fields.
- `PB0_*`: a large generated block for physical bus interface instance 0, including global controls, SCI status overrides, PIF controls, lane pairing, lane power overrides, sequence status, PLL control/override/status, RX/TX global and per-lane controls, TX coefficient accept tables, and TX/RX lane status fields.
- `PB1_*`: the start of a matching physical bus interface instance 1 block, covering DFT, jitter injection, global controls, overrides, and initial SCI status override fields.

## Control Flow

The header has no runtime control flow. Its only compile-time control structure is the include guard:

- `#ifndef BIF_3_0_SH_MASK_H`
- `#define BIF_3_0_SH_MASK_H`

At runtime, these constants participate in control flow in code that reads, modifies, writes, or polls hardware registers. For example, the power-management BACO code uses `BACO_CNTL__BACO_EN_MASK`, `BACO_CNTL__BACO_POWER_OFF_MASK`, `BACO_CNTL__BACO_MODE_MASK`, and related shift constants in command tables that sequence BACO entry and exit. The macros become part of operations such as:

- read a register;
- clear the field mask;
- shift a field value into position;
- OR it into the register value;
- write the register back;
- poll until `(register & mask)` matches an expected value.

The PB0/PB1 PIF, PLL, RX, and TX fields are similarly intended for low-level link bring-up, lane power management, training/debug overrides, electrical idle detection, PLL power/frequency mode reporting, transmitter coefficient handling, and per-lane status inspection.

## State And Persistence Behavior

The header itself has no mutable state and no persistence behavior. It defines numeric constants compiled into whichever translation units include it.

The state affected by these constants is hardware state in memory-mapped or indexed BIF registers. Writes using these masks can persist in device registers until changed by the driver, firmware, reset, BACO transition, PCIe link event, or power-management flow. Scratch-register masks such as `BIF_SCRATCH*`, `BIOS_SCRATCH_*`, and `PB0_PIF_SCRATCH` expose fields whose values may intentionally survive across parts of driver/firmware handoff or diagnostic flows, depending on register retention rules outside this header.

Because the constants are generated from hardware register descriptions, correctness depends on exact mask and shift values matching the ASIC's register specification. A wrong constant does not fail locally; it can silently set the wrong bit in persistent hardware state.

## Dependencies And Integration Points

The direct dependency is the C preprocessor. The header is consumed alongside BIF address headers, especially:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/bif/bif_3_0_d.h`
- other generation-specific BIF/NBIF `*_d.h` and `*_sh_mask.h` headers

Known integration points visible in the tree include:

- `drivers/gpu/drm/amd/pm/legacy-dpm/si_dpm.c`, which includes `bif/bif_3_0_sh_mask.h`;
- BACO power-management flows such as `ci_baco.c`, `fiji_baco.c`, `smu7_baco.c`, and newer generation variants that use same-named BACO field masks for command-table read/modify/write and wait operations;
- register helper macros and accessors in AMDGPU/PowerPlay code that expect the `<REG>__<FIELD>_MASK` and `<REG>__<FIELD>__SHIFT` naming style.

The header is architecture-specific. It should be included only in code paths that operate on hardware matching BIF 3.0 register layouts or compatibility layers that deliberately reuse these definitions. Adjacent ASIC generations may share names while changing fields, masks, or register addresses.

## Risks And Edge Cases

The main risk is silent hardware misprogramming. Since these are plain numeric macros, the compiler cannot validate that a mask belongs to the register being accessed or that the matching shift is used.

Mask/shift pairs must remain synchronized. A copy/paste or generator error in either half can make field extraction and updates incorrect. This matters especially for multi-bit fields such as reset delay selectors, lane pairing, PLL divider/frequency modes, RX/TX power states, and TX coefficient fields.

The chunk boundary is in the middle of a generated field family. Line 3812 includes `PB1_GLB_SCI_STAT_OVRD_REG4__FREQDIV_14_MASK` without its matching shift in this range, so any analysis of PB1 is incomplete until later chunks are merged.

Many PB0 definitions are repeated per lane and per lane group. Off-by-one lane numbering, lexicographic ordering (`10` before `1` in some generated blocks), or accidental use of `PB0` fields against `PB1` registers can be hard to detect in review.

Several fields control destructive or disruptive hardware behavior: BACO power-off/isolation/reset, BIF reset enables, PIF power overrides, PLL override controls, RX/TX frontend power, lane reset, and debug/test modes. Incorrect writes can hang the PCIe link, break device resume, or require a full GPU reset.

The file relies on `L`-suffixed hexadecimal constants. They are intended for 32-bit register values, but callers should avoid signed arithmetic surprises and should use the driver's normal unsigned register types when combining masks.

Generated headers are usually not unit-tested directly. Regression risk is highest when regenerating from a new register database, manually editing a field, or mixing headers from different ASIC generations.

## Test Signals

Useful validation is mostly build, register-access, and hardware behavior coverage:

- Compile coverage for translation units that include `bif_3_0_sh_mask.h`, especially legacy DPM and PowerPlay paths.
- Static checks that every `_MASK` in the generated header has a matching `__SHIFT` and that no duplicate macro names have conflicting values. The assigned range intentionally has one incomplete pair at the boundary.
- Consistency checks against `bif_3_0_d.h`: field macro register prefixes should map to address macros with the same register names.
- BACO enter/exit tests on supported ASICs, validating `BACO_CNTL` mode transitions, power-good fields, isolation controls, reset enable behavior, and recovery after resume.
- PCIe link bring-up, link speed change, ASPM/L0s/L1 transitions, FLR, hot reset, link-down reset, and driver reset tests that exercise `BIF_RESET_EN`, `PB0_PIF_*`, `PB0_PLL_*`, `PB0_RX_*`, and `PB0_TX_*` fields.
- Runtime register readback tests for representative single-bit and multi-bit fields to confirm mask/shift extraction returns expected values after controlled writes.
- Suspend/resume and low-power tests that verify scratch, BACO, PIF power, PLL power, and RX/TX lane state do not regress.
- Hardware debug or lab validation for per-lane PB0/PB1 fields, because lane-indexed constants can compile cleanly while targeting the wrong physical lane.
