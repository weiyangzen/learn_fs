# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h - chunk subset-b-002334

Chunk scope: lines 4857-7242 of `dpcs_4_2_2_offset.h`, chunk 3 of 5 for this generated AMD DPCS 4.2.2 register-offset header. This chunk contains 2,382 preprocessor constants and two local address-block comments; it does not define C types, functions, executable control flow, or storage.

## Purpose

This chunk exports symbolic offsets for DPCS/DPCSSYS indirect register addresses used by AMD display/link-encoder code for DCN315-era hardware. The constants map hardware register names to 16-bit-style indirect offsets such as `0x4300`, `0x804a`, or `0xe0c8`. Driver code can use these names instead of hard-coded numeric offsets when programming DisplayPort/PHY/link-lane control, PLL/supervisor, receiver adaptation, lane interrupt, raw-lane, and raw-AON-lane registers.

The source file as a whole is guarded by `_dpcs_4_2_2_OFFSET_HEADER`, carries AMD MIT licensing, and is paired with `dpcs_4_2_2_sh_mask.h`, which provides bitfield shift/mask definitions for the same register names. `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both headers and uses register-list macros such as `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)` to bind DPCS offsets and field metadata into DCN315 link encoder resource tables.

## Register Families Covered

The chunk begins in the tail of the `dpcssys_cr1` indirect map and switches at lines 5493-5494 into `addressBlock: dpcssys_cr2_rdpcstxcrind` with base address `0x0`. The visible families are:

- `CR1_RAWAONLANE2/3/X`: raw always-on lane offsets for lane 2 tail, lane 3, and lane-X aliases. These cover AFE/CTLE/DFE offsets, receiver phase adjustment, MPLL coarse tune, adaptation status, RX slicer controls, signal-detect calibration, firmware config, and TX DCC config.
- `CR1_SUPX`: supervisor lane-X digital and analog PLL/support offsets around `0x8000-0x8096`, including IDCODE, refclk/MPLL override inputs, SSC peak/step registers, ASIC feedback inputs, bandgap, PLL charge-pump, prescaler, RTUNE, bandgap, MPLL analog, ATB, and PMIX override/status registers.
- `CR1_LANEX` and `CR1_RAWLANEX`: lane-X register templates for digital/analog lane control and raw-lane PCS/PMA/FSM/IRQ/TX/RX control, including TX/RX power control, RX adaptation, RX statistics, analog override/status, raw memory probe entries, PMA transfer signals, interrupt status/clear/mask registers, and PCS transfer overrides.
- `CR2_SUP`, `CR2_LANE0-3`, `CR2_RAWCMN`, `CR2_RAWLANE0-3`, `CR2_RAWAONLANE0-3/X`, and partial `CR2_SUPX`: the same style of indirect map for DPCSSYS CR2. The chunk contains complete CR2 supervisor, lane, raw-common, raw-lane, and raw-AON-lane sections, then stops at `ixDPCSSYS_CR2_SUPX_ANA_MPLLA_ATB2`.

Observed macro-family counts in this chunk include complete 82-entry raw-AON-lane blocks, 125-entry raw-lane blocks, 203-entry full lane blocks for CR2 lanes 1 and 2, shorter 85-entry CR2 lane 0 and 3 spans visible in this chunk, 139-entry CR1/CR2 supervisor blocks, and a partial 71-entry `CR2_SUPX` tail section.

## Important APIs, Types, and Macros

There are no callable APIs or C data types. The exported interface is the macro namespace:

- `ixDPCSSYS_CRn_*`: indirect DPCSSYS register offsets for channel/register-bank `CRn`; this chunk covers `CR1` and `CR2`.
- `*_LANE0` through `*_LANE3`: per-physical-lane offsets.
- `*_LANEX` and `*_RAW...LANEX`: template/aggregate lane-X offsets, useful when hardware or macro layers address a lane-independent alias.
- `*_SUP` and `*_SUPX`: common supervisor and supervisor-X PLL/support register spaces.
- `*_DIG_*` vs `*_ANA_*`: digital control/status registers versus analog PHY/PLL/control registers.

Examples of semantic groups visible in the names are `TX_PWRCTL`, `RX_ADPTCTL`, `RX_STAT`, `ANA_TX`, `ANA_RX`, `RAWCMN`, `FSM`, `IRQ_CTL`, `PMA_XF`, `PCS_XF`, `MPLL`, `SSC`, `RTUNE`, `BG`, `ATB`, `SIGDET`, `DCC`, and firmware calibration/configuration.

## Control Flow

This header contributes no runtime branches or sequencing by itself. Its values are consumed at compile time by preprocessor token-pasting and register helper macros in the AMD display stack. In DCN315 resource setup, `dcn315_resource.c` includes the offset and shift/mask headers, defines DPCS/DCN base segment constants, and expands register-list macros into static register tables. Runtime read/write flow is then handled by the display core register helpers and link encoder code, which use those tables to perform MMIO or indirect register access.

For the `ixDPCSSYS_*` constants specifically, the expected hardware flow is indirect addressing through DPCSSYS/RDPCS CR address/data windows defined elsewhere in the same header, for example `DPCSSYS_CRn_DPCSSYS_CR_ADDR` and `DPCSSYS_CRn_DPCSSYS_CR_DATA`. The constants in this chunk are the indirect addresses placed into those windows, not the final MMIO addresses themselves.

## State and Persistence Behavior

The chunk contains immutable compile-time constants only. It has no memory ownership, no persistent on-disk state, no locks, no counters, and no initialization or teardown behavior. Hardware state changes occur only when other driver code uses these offsets to read or write the corresponding PHY/link registers.

Because the offsets identify real hardware registers, their values are persistent interface contract data for the ASIC generation. Any edit can silently retarget PHY, PLL, signal-detect, DFE/adaptation, interrupt, or lane-control operations to a different hardware register.

## Dependencies and Integration Points

Primary dependencies are structural rather than linked code:

- `dpcs_4_2_2_sh_mask.h` must stay aligned with these offset names so field-level helpers can apply masks to the correct registers. Matching shift/mask entries exist for representative names such as `DPCSSYS_CR2_SUP_DIG_IDCODE_LO`, `DPCSSYS_CR2_LANE2_DIG_RX_ADPTCTL_DFE_TAP3_STATUS`, and `DPCSSYS_CR2_SUPX_ANA_MPLLA_ATB2`.
- `dcn315_resource.c` includes this header, defines DPCS base segments, and builds link encoder register/mask tables using DPCS macros.
- The broader display register-helper stack depends on generated offset naming conventions (`reg...`, `ix...`, base-index macros, and token-pasted names) remaining stable.
- Adjacent DPCS headers such as `dpcs_4_2_0_offset.h`, `dpcs_4_2_3_offset.h`, and `dpcs_3_1_4_offset.h` share many names and values; diffs against those files are useful for spotting intended ASIC-generation changes versus generator drift.

## Risks

- Offset corruption is high impact: a single wrong numeric value can direct link-training, PLL, DCC, RX adaptation, or interrupt handling to the wrong indirect register.
- The chunk crosses a source-file boundary from CR1 into CR2 and ends mid-`CR2_SUPX`; merge logic must preserve chunk order or the final per-file report will lose register-map context.
- The values are dense and repetitive, making manual review error-prone. Lane blocks often differ only by lane number and offset page (`0x1100`, `0x1200`, `0x1300`, etc.).
- Several constants are lane-X aliases or raw/register-bank views rather than ordinary per-lane MMIO names; using them as direct MMIO offsets would be incorrect.
- Generated-header alignment with `dpcs_4_2_2_sh_mask.h` is essential. A name present only in one header can break field access macros or leave an offset without bitfield metadata.

## Test and Validation Signals

Useful validation signals for this chunk are mostly build-time and hardware-facing:

- Compile DCN315 display code that includes `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h`; missing or renamed macros should fail during resource-table initialization.
- Run static checks comparing this offset header against `dpcs_4_2_2_sh_mask.h` for matching register-name coverage.
- Diff against neighboring generated versions (`dpcs_4_2_0_offset.h` and `dpcs_4_2_3_offset.h`) to confirm repeated offsets remain intentionally identical and generation-specific deltas are expected.
- Exercise display link initialization, HPD/connect/disconnect, DisplayPort link training, HDMI/TMDS paths, power-state transitions, and suspend/resume on DCN315 hardware.
- Watch for runtime symptoms tied to this address region: failed link training, unstable clocks/PLL lock, RX adaptation failures, signal-detect issues, unexpected lane IRQs, or DCC calibration failures.

## Cross-Chunk Notes

Chunk 2 ends immediately before this one in the CR1 register map. This chunk starts at the final visible `CR1_RAWAONLANE2` TX DCC config entry, completes several CR1 lane-X/raw-lane groups, includes the `dpcssys_cr2_rdpcstxcrind` marker, and covers CR2 through a partial `SUPX` analog block. Chunk 4 should continue at `CR2_SUPX_ANA_MPLLA_ATB3` or the next generated constant after line 7242 and complete the remaining CR2/CR3-style register-map material.
