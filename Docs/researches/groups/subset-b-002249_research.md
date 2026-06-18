# Research: subset-b-002249

Grouped research for AMD DPCS register headers under `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_offset.h

## Purpose

`dpcs_2_0_3_offset.h` is a generated AMD display PHY control/status register offset header for the DPCS 2.0.3 register block used by the DCN 2.0.1 resource path. It defines symbolic MMIO register offsets and `_BASE_IDX` selectors for two transmitter instances, `DPCSTX0`/`RDPCSTX0` and `DPCSTX1`/`RDPCSTX1`. The direct `DPCSTX` block covers transmit-side clock, FIFO/control, CBUS, interrupt, and PLL update registers. The `RDPCSTX` block covers reduced/display PHY control, clocking, interrupt status, PLL update data, CR address/data access, scratch, and `RDPCSTX_PHY_CNTL0` through `RDPCSTX_PHY_CNTL14`.

The header carries no executable logic. Its purpose is to provide a stable hardware-address contract to the AMD display driver. `dcn201_resource.c` includes this file together with `dpcs_2_0_3_sh_mask.h`, then expands link encoder register tables from these macros.

## Important APIs, Types, and Macros

The public surface is entirely preprocessor definitions:

- `mmDPCSTX0_DPCSTX_TX_CLOCK_CNTL` through `mmDPCSTX0_DPCSTX_PLL_UPDATE_DATA`, and equivalent `DPCSTX1` names, map transmit control registers to offsets `0x2928` through `0x292d` for instance 0 and `0x2a00` through `0x2a05` for instance 1.
- `mmRDPCSTX0_RDPCSTX_CNTL` through `mmRDPCSTX0_RDPCSTX_PHY_CNTL14`, and equivalent `RDPCSTX1` names, map reduced PHY control/status registers to offsets `0x2930` through `0x294e` and `0x2a08` through `0x2a26`.
- Every register has a companion `..._BASE_IDX` macro set to `2`. Resource macros use this index with segment macros such as `BASE(mm..._BASE_IDX)` before adding the register offset.
- The include guard `_dpcs_2_0_3_OFFSET_HEADER` prevents duplicate macro definition inside a single translation unit.

There are no C functions, structs, enums, or inline helpers in this file. The effective API is the macro naming scheme expected by resource and link encoder headers.

## Control Flow

The control flow is compile-time macro expansion:

1. `dcn201_resource.c` includes `dpcs_2_0_3_offset.h` and `dpcs_2_0_3_sh_mask.h`.
2. Link encoder register lists expand names such as `RDPCSTX0_RDPCSTX_PHY_CNTL3` into `BASE(mmRDPCSTX0_RDPCSTX_PHY_CNTL3_BASE_IDX) + mmRDPCSTX0_RDPCSTX_PHY_CNTL3`.
3. The resulting numeric addresses populate `struct dcn10_link_enc_registers` arrays for two link encoder instances.
4. Runtime encoder code later uses those populated register structs through AMD display register helper paths, not through this header directly.

The file itself has no branches or runtime entry points. A bad macro value changes the compiled register table silently, which is why generated-header correctness is critical.

## State and Persistence Behavior

No software state is stored by this header. The defined offsets point at persistent hardware MMIO state in the display PHY and transmitter blocks. Registers named by this file can affect live link behavior, including PHY reset, lane enablement, FIFO state, clock gating, PLL programming, interrupt clearing/masking, and scratch/debug state. Persistence is hardware-defined: values may survive until reset, power-gate transitions, or explicit driver writes, depending on the register.

## Dependencies and Integration Points

This header depends on the AMD ASIC register generation convention:

- `mm...` prefixes are consumed by resource macros using token pasting.
- `_BASE_IDX` values must match the DCN base segment definitions included by the resource file.
- Field definitions from `dpcs_2_0_3_sh_mask.h` must correspond to these offsets.
- `dcn201_resource.c` is the direct integration point for DCN 2.0.1, where only two link encoder instances are created.
- `dcn20_link_encoder.h` provides many DPCS mask/shift list macros that expect `RDPCSTX0` field names.

Because all names are plain preprocessor macros, any consumer that includes multiple ASIC generations in one translation unit risks name collisions unless the build isolates generation-specific resource files.

## Risks and Edge Cases

- Offset and mask mismatches can compile cleanly but write the wrong hardware register or field.
- All `_BASE_IDX` values are `2`; if a future ASIC routes these blocks through a different segment, resource tables would target the wrong MMIO aperture.
- The 2.0.3 offset surface covers only two DPCS/RDPCS instances. Reusing it for a design with more transmitters would create missing macro failures or, worse, incorrect copy/paste substitutions.
- `dpcs_2_0_3_sh_mask.h` contains some debug field definitions for registers such as `DPCSTX0_DPCSTX_DEBUG_CONFIG`, but this offset header does not define matching `mmDPCSTX*_DPCSTX_DEBUG_CONFIG` offsets. That is safe only while no 2.0.3 register-list macro instantiates those debug registers.
- These register names encode hardware behavior but not access semantics. Clear-on-write, read-only status, and sequence requirements must be enforced in the higher-level link encoder code or hardware programming tables.

## Test Signals

Useful validation signals include:

- A build of the DCN 2.0.1 display resource path, especially `dcn201_resource.c`, to catch missing or renamed macros.
- Static comparison against AMD register XML/source-generation output for DPCS 2.0.3.
- Link encoder bring-up tests on matching hardware, including DP link training, lane enable/disable, PLL programming, hotplug, suspend/resume, and interrupt handling.
- Register readback traces confirming that addresses in the constructed `link_enc_regs` table resolve to the intended DPCS and RDPCS instance offsets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_offset.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_sh_mask.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_sh_mask.h

## Purpose

`dpcs_2_0_3_sh_mask.h` is the generated shift/mask companion for the DPCS 2.0.3 register block. It defines the bit positions and bit masks for fields inside the registers addressed by `dpcs_2_0_3_offset.h`, covering `DPCSTX0`/`RDPCSTX0` and `DPCSTX1`/`RDPCSTX1`. It gives higher-level AMD display code the field metadata needed to pack and extract register values without hardcoding bit arithmetic at each use site.

The file is especially important for link encoder programming. Field groups cover transmitter symbol-clock enables, FIFO controls, PLL update request/pending bits, CBUS reset/delay, interrupt error/mask bits, RDPCS lane FIFO enablement, SRAM and symbol-clock controls, PHY power and reset control, DP Alt mode status/control, four-lane DP TX lane handshakes, termination and inversion controls, MPLL/SSC programming, CR address/data access, scratch registers, fuse/equalization fields, and RX load values.

## Important APIs, Types, and Macros

The API is a large set of `#define` values following the convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the low bit position.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask as a 32-bit literal, usually with an `L` suffix.

Important register groups include:

- `DPCSTX*_DPCSTX_TX_CLOCK_CNTL` fields for `DPCS_SYMCLK_GATE_DIS`, `DPCS_SYMCLK_EN`, and clock-on status.
- `DPCSTX*_DPCSTX_TX_CNTL` fields for PLL update request/pending, data swap/order inversion, FIFO enable/start/delay, and soft reset.
- `DPCSTX*_DPCSTX_INTERRUPT_CNTL` fields for register FIFO overflow, TX lane FIFO errors, clear bits, and interrupt masks.
- `RDPCSTX*_RDPCSTX_CNTL` and `RDPCSTX*_RDPCSTX_CLOCK_CNTL` fields for CBUS/SRAM resets, lane FIFO enables, SRAM clock controls, external reference clock, and symclk-div2 controls.
- `RDPCSTX*_RDPCSTX_PHY_CNTL0` through `PHY_CNTL14` fields for PHY reset, power stability, DP Alt mode, lane reset/disable/ack, lane data enable, term controls, pstate/rate/width, MPLL fractional and SSC programming, and calibration force.
- `RDPCSTX*_RDPCSTX_PHY_FUSE0` through `PHY_FUSE3` and `PHY_RX_LD_VAL` fields for lane EQ/fuse calibration and load values.
- `DPCSSYS_CR0`/`DPCSSYS_CR1` field aliases for CR address/data paths.

There are no C functions or types. The macros are consumed by helper macros such as `LE_SF(..., __SHIFT)` and `LE_SF(..., _MASK)` to initialize field metadata structs.

## Control Flow

The header participates in compile-time field-table construction:

1. `dcn201_resource.c` includes this file after the matching offset header.
2. Link encoder macro lists in `dcn20_link_encoder.h` reference fields such as `RDPCS_PHY_DP_TX0_CLK_RDY`, `RDPCS_PHY_DP_TX0_DATA_EN`, `RDPCS_PHY_DP_MPLLB_MULTIPLIER`, and `RDPCS_TX_FIFO_LANE0_EN`.
3. `LE_SF`/`SF`-style macros append `__SHIFT` or `_MASK` to the register-field names, creating initializer values for `struct dcn10_link_enc_shift` and `struct dcn10_link_enc_mask`.
4. Runtime register helpers use those shifts and masks to read or update individual MMIO fields.

No runtime control flow lives in this file. Its behavior is visible only through code generated by preprocessor expansion and later hardware register operations.

## State and Persistence Behavior

The file stores no software state. It describes bit layout for stateful hardware registers. Fields represent hardware controls and status bits for clocks, resets, FIFOs, interrupts, PHY power, lane training, DP/HDMI mode behavior, PLL configuration, and fuse-derived calibration. Some fields are likely read-only status bits, some are write controls, and some are write-one-to-clear or handshake bits, but those semantics are not encoded here. The driver must preserve unrelated bits during updates by using masks and read-modify-write helpers correctly.

## Dependencies and Integration Points

Primary dependencies are:

- Register offsets from `dpcs_2_0_3_offset.h`.
- The AMD display register helper convention that builds field metadata from `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK`.
- `dcn201_resource.c`, which includes the 2.0.3 pair for the DCN 2.0.1 resource implementation.
- `dcn20_link_encoder.h`, which lists many DPCS fields used by DCN 2.x link encoders.
- Runtime link encoder code that calls register helpers through pre-built register, shift, and mask structs.

The file is not self-sufficient: a field mask is useful only when a consumer also has the correct register offset for the same ASIC generation.

## Risks and Edge Cases

- A wrong shift or mask can corrupt neighboring fields while still compiling cleanly.
- The duplicate-sounding names ending in `_MASK_MASK`, such as interrupt-mask field masks, are generated from field names that themselves include `MASK`. They are intentional but easy for humans to misread.
- Field availability must match the register list. This file defines debug fields for `DPCSTX*_DPCSTX_DEBUG_CONFIG` and `DPCSTX0_DPCSTX_TEST_DEBUG_DATA`, while the 2.0.3 offset header does not define matching offsets for those registers. Consumers must avoid instantiating fields that lack an address in this ASIC header pair.
- Access semantics are absent. Higher-level code must know which fields are read-only status, write-one-to-clear, poll-until-ack, or require sequencing around resets and clocks.
- Because the file is generated, manual edits risk diverging from hardware documentation and from neighboring DPCS generations.

## Test Signals

Useful validation signals include:

- Compile coverage of `dcn201_resource.c` and link encoder headers to catch missing field macros.
- Static generation-diff checks against the DPCS 2.0.3 source register specification.
- Bitfield unit checks, where possible, that verify `(mask >> shift)` widths for common fields such as FIFO delay, MPLL multiplier, lane rate, and term control.
- Hardware DP link training and mode-set tests that exercise lane enable, PLL setup, data enable, and interrupt clear/mask paths.
- Suspend/resume and power-gating tests that exercise SRAM/clock/reset fields and catch missing preserve-mask behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_0_3_sh_mask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_offset.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_offset.h

## Purpose

`dpcs_2_1_0_offset.h` is the generated offset header for the DPCS 2.1.0 hardware block used by the DCN 2.1 resource path. Compared with DPCS 2.0.3, it expands the register surface substantially: it defines five DPCS/RDPCS transmitter instances, numbered 0 through 4, and adds register offsets for debug, SRAM power control, spare/cntl2, DP Alt mode control, DMCU DPALT override/block registers, PHY fuse registers, RX load values, `PHY_CNTL15` through `PHY_CNTL17`, `DEBUG_CONFIG2`, and DPCSSYS CR aliases for each instance.

The direct user in this tree is `dcn21_resource.c`, which includes `dpcs_2_1_0_offset.h` with the matching `dpcs_2_1_0_sh_mask.h` and builds five link encoder register entries for Renoir/DCN 2.1 style hardware.

## Important APIs, Types, and Macros

The header exports preprocessor constants only:

- `mmDPCSTX{0..4}_DPCSTX_TX_CLOCK_CNTL`, `TX_CNTL`, `CBUS_CNTL`, `INTERRUPT_CNTL`, `PLL_UPDATE_ADDR`, `PLL_UPDATE_DATA`, and `DEBUG_CONFIG`.
- `mmRDPCSTX{0..4}_RDPCSTX_CNTL`, `CLOCK_CNTL`, `INTERRUPT_CONTROL`, `PLL_UPDATE_DATA`, `RDPCS_TX_CR_ADDR`, `RDPCS_TX_CR_DATA`, `RDPCS_TX_SRAM_CNTL`, `SCRATCH`, `SPARE`, `CNTL2`, `DMCU_DPALT_DIS_BLOCK_REG`, `DEBUG_CONFIG`, `PHY_CNTL0` through `PHY_CNTL17`, `PHY_FUSE0` through `PHY_FUSE3`, `PHY_RX_LD_VAL`, `DMCU_DPALT_PHY_CNTL3`, `DMCU_DPALT_PHY_CNTL6`, `DPALT_CONTROL_REG`, and `DEBUG_CONFIG2`.
- `mmDPCSSYS_CR{0..4}_DPCSSYS_CR_ADDR` and `mmDPCSSYS_CR{0..4}_DPCSSYS_CR_DATA` aliases, which map to the same CR address/data offsets as the matching `RDPCSTX` instance.
- Every defined register has a companion `..._BASE_IDX` with value `2`.

The instance offsets follow a regular stride by address block base: instance 0 starts around `0x2928`, instance 1 around `0x2a00`, instance 2 around `0x2ad8`, instance 3 around `0x2bb0`, and instance 4 around `0x2c88`. The corresponding RDPCS and DPCSSYS CR aliases sit inside each instance block.

## Control Flow

Like the other ASIC register headers, the only control flow is build-time expansion:

1. `dcn21_resource.c` includes this header and defines `BASE(seg)` against the DCN 2.1 MMIO segment macros.
2. `link_regs(id, phyid)` expands `DPCS_DCN21_REG_LIST(id)` for each of five encoder instances.
3. Register-list macros paste tokens such as `mmRDPCSTX2_RDPCSTX_PHY_CNTL7_BASE_IDX` and `mmRDPCSTX2_RDPCSTX_PHY_CNTL7` into address initializers.
4. The populated `link_enc_regs[]` table is passed into `dcn21_link_encoder_construct`, after transmitter IDs are mapped to physical instances.
5. Runtime link encoder code accesses the registers indirectly through the populated table and matching shift/mask metadata.

This file does not enforce sequencing. It only makes the hardware addresses available.

## State and Persistence Behavior

The header stores no software state. It names hardware state that controls and reports DPCS/RDPCS behavior. The expanded 2.1.0 register surface includes additional state for SRAM power, debug control, DP Alt mode coordination with DMCU, fuse-calibrated PHY settings, and per-lane/PLL programming. Persistence and reset behavior are hardware-defined. Driver code must assume that fields can be affected by ASIC reset, display power gating, firmware/DMCU access, hotplug/link training flows, and suspend/resume transitions.

## Dependencies and Integration Points

Important dependencies and integration points include:

- `dpcs_2_1_0_sh_mask.h`, which supplies field positions and masks for the offsets in this file.
- `dcn21_resource.c`, the direct resource-file consumer for DCN 2.1.
- `dcn20_link_encoder.h` and DCN 2.1 link encoder code, which expect DPCS register names to exist for the selected ASIC generation.
- Base segment macros such as `DMU_BASE__INST0_SEG2`; every `_BASE_IDX` here is `2`.
- DPCSSYS CR aliases that intentionally share offsets with per-instance `RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA`.

Because this file defines generic macro names used by token-pasting helpers, it should be included only in translation units that are intentionally building for DPCS 2.1.0.

## Risks and Edge Cases

- The header exposes five instances; consumers must map logical transmitter IDs to valid array indexes. `dcn21_resource.c` has a dedicated transmitter-to-phy mapping path, so off-by-one or unsupported transmitter IDs would be a runtime risk outside this header.
- DPCSSYS CR aliases duplicate address values already exposed through `RDPCSTX*_RDPCS_TX_CR_*`. This is likely intentional, but mixed use can hide aliasing bugs if code assumes they are independent registers.
- Wrong `_BASE_IDX` or offset values would affect every register access constructed from these macros and may not be caught by the compiler.
- Expanded debug, fuse, SRAM, and DP Alt mode registers often have sequencing or ownership constraints. The offset header cannot express whether the display driver, firmware, or hardware owns a field at a given time.
- The regular instance stride makes copy/paste or generator bugs easy to miss in review; register specification diffs are more reliable than visual inspection.

## Test Signals

Useful validation signals include:

- Build coverage of `dcn21_resource.c` and the DCN 2.1 link encoder path to verify all token-pasted register names resolve.
- Static comparison against the DPCS 2.1.0 generated register specification, including the aliasing between `RDPCS_TX_CR_*` and `DPCSSYS_CR*`.
- Hardware smoke tests on DCN 2.1 systems with multiple active outputs, exercising all five possible link encoder entries where hardware supports them.
- DP and HDMI mode-set/link-training tests that program PHY lane control, PLL, FIFO, clock, and reset registers.
- Suspend/resume, hotplug, and USB-C/DP Alt mode scenarios that exercise the added SRAM power and DPALT/DMCU-related register ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_2_1_0_offset.h -->
