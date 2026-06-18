# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-002332`: lines 1-2470, `Docs/researches/chunks/subset-b-002332_research.md`
- `subset-b-002333`: lines 2471-4856, `Docs/researches/chunks/subset-b-002333_research.md`
- `subset-b-002334`: lines 4857-7242, `Docs/researches/chunks/subset-b-002334_research.md`
- `subset-b-002335`: lines 7243-9628, `Docs/researches/chunks/subset-b-002335_research.md`
- `subset-b-002336`: lines 9629-11957, `Docs/researches/chunks/subset-b-002336_research.md`

## Chunk Research

### subset-b-002332: lines 1-2470

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 1-2470

## Scope

This chunk is the opening 2,470 lines of the generated AMD DPCS 4.2.2 register offset header. It defines preprocessor constants only: direct MMIO register offsets with matching `_BASE_IDX` constants, followed by the beginning of the `DPCSSYS_CR0` indirect control-register address space. There are no C functions, structs, enums, runtime branches, allocation paths, or software persistence logic in this chunk.

The chunk covers:

- Include guard and license header for `dpcs_4_2_2_offset.h`.
- Direct `reg...` offsets for five DPCS CR proxy windows, two panel power sequencers, five RDPCS TX instances, common DCIO controls, chip-level DCIO GPIO/AUX/DDC controls, and UNIPHY reserved macro-control banks.
- The start of `addressBlock: dpcssys_cr0_rdpcstxcrind`, exported as `ixDPCSSYS_CR0_...` indirect offsets from `0x0000` through `ixDPCSSYS_CR0_RAWAONLANE0_DIG_DFE_ODD_REF_LVL` at `0x4008`.

## Purpose

The header gives AMD display driver code stable symbolic names for ASIC-specific DPCS 4.2.2 register offsets. The direct `reg...` macros are MMIO addresses in the display register aperture, while the indirect `ix...` macros are register indices reached through the DPCS control-register address/data proxy. The constants let register tables and helper macros use named hardware registers instead of hard-coded hex values.

Major hardware areas represented here include:

- `DPCSSYS_CR{0..4}_DPCSSYS_CR_ADDR/DATA`: five indirect CR access windows at direct offsets `0x2934/0x2935`, `0x2a0c/0x2a0d`, `0x2ae4/0x2ae5`, `0x2bbc/0x2bbd`, and `0x2c94/0x2c95`.
- `PWRSEQ{0,1}`: panel power sequencing, GPIO power-sequence pins, panel timing delays/dividers, backlight PWM control, period control, register lock, and spare registers.
- `RDPCSTX{0..4}`: repeated RDPCS transmitter blocks containing control, clock, interrupt, PLL update, CR address/data, SRAM, scratch/spare, debug, PHY control, PHY fuse, DP Alt Mode, and PLL override registers.
- `DCIO` and `DCIO_CHIP`: display IO clock/reference/link routing, UNIPHY link and channel crossbar controls, pin straps, soft reset, GPIO banks for DDC/HPD/GENLK/PWRSEQ/AUX, pad strength, AUX/I2C power-good, and related chip-level IO state.
- `DCIO_UNIPHY{1..4}`: reserved UNIPHY macro-control offsets, laid out as repeated 58-register banks at the same base strides as the corresponding PHY/RDPCS instances.
- `DPCSSYS_CR0` indirect map: supervisor PLL/reference/RTUNE/common analog controls, lane 0-3 TX/RX digital and analog controls, raw common always-on controls, raw per-lane PCS/FSM/IRQ/PMA/TX/RX controller controls, and the first always-on lane calibration readbacks.

## Important API Surface

The exported API is the macro namespace. Important direct-offset families are:

- `regDPCSSYS_CR{0..4}_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR{0..4}_DPCSSYS_CR_DATA`, plus `_BASE_IDX`, which name the indirect address/data portals for each CR instance.
- `regPWRSEQ0_*` and `regPWRSEQ1_*`, including `DC_GPIO_PWRSEQ_{EN,CTRL,MASK,A_Y}`, `PANEL_PWRSEQ_{CNTL,STATE,DELAY1,DELAY2,REF_DIV1,REF_DIV2}`, `BL_PWM_{CNTL,CNTL2,PERIOD_CNTL}`, `BL_PWM_GRP1_REG_LOCK`, and `PWRSEQ_SPARE`.
- `regRDPCSTX{0..4}_*`, including `RDPCSTX_CNTL`, `RDPCSTX_CLOCK_CNTL`, `RDPCSTX_INTERRUPT_CONTROL`, `RDPCS_TX_PLL_UPDATE_DATA`, `RDPCS_TX_CR_ADDR`, `RDPCS_TX_CR_DATA`, `RDPCS_TX_SRAM_CNTL`, `RDPCSTX_{SCRATCH,SPARE,CNTL2}`, `RDPCSTX_DMCU_DPALT_*`, `RDPCSTX_DEBUG_CONFIG*`, `RDPCSTX_PHY_CNTL0..17`, `RDPCSTX_PHY_FUSE0..3`, `RDPCSTX_PHY_RX_LD_VAL`, `RDPCS_CNTL3`, and PLL update override registers.
- Common DCIO symbols such as `regDC_GENERICA`, `regDC_GENERICB`, `regDCIO_CLOCK_CNTL`, `regDC_REF_CLK_CNTL`, `regUNIPHY{A..E}_LINK_CNTL`, `regUNIPHY{A..E}_CHANNEL_XBAR_CNTL`, `regDCIO_WRCMD_DELAY`, `regDC_PINSTRAPS`, `regINTERCEPT_STATE`, `regDCIO_BL_PWM_FRAME_START_DISP_SEL`, genlock/swaplock pad controls, and `regDCIO_SOFT_RESET`.
- Chip GPIO/AUX symbols such as `regDC_GPIO_DDC{1..5,VGA}_{MASK,A,EN,Y}`, `regDC_GPIO_HPD_{MASK,A,EN,Y}`, `regDC_GPIO_PWRSEQ{0,1}_EN`, `regPHY_AUX_CNTL`, `regDC_GPIO_AUX_CTRL_0..5`, `regDC_GPIO_RXEN`, `regDC_GPIO_PULLUPEN`, and `regAUXI2C_PAD_ALL_PWR_OK`.
- `regDCIO_UNIPHY{1..4}_UNIPHY_MACRO_CNTL_RESERVED0..57`, which expose reserved but addressable UNIPHY macro-control slots.

The important indirect-offset families in this chunk are all `ixDPCSSYS_CR0_*`:

- `SUP_DIG_*` and `SUP_ANA_*` offsets for ID code, reference-clock overrides, MPLLA/MPLLB dividers and HDMI clocks, spread-spectrum control, PLL override/input/output/status, bandgap, prescaler, RTUNE, power-up timing, and analog PLL control/status.
- `LANE{0..3}` offsets for ASIC lane/TX/RX override and ASIC signal paths, TX power-state and power-up timing, TX DCC controls, TX clock alignment and LBERT, RX power/VCO/CDR/adaptation/statistics, MPHY, analog TX/RX override/status, and analog TX/RX physical controls. Lanes 1 and 2 have fuller RX-side blocks; lanes 0 and 3 are shorter in this line range.
- `RAWCMN_DIG_AON_CMN_*` offsets for always-on common RTUNE values, SRAM blanking, power-gate/supervisor/resource/reference overrides, VREF stats, and common misc configuration.
- `RAWLANE{0..3}` offsets for raw PCS crossbar overrides, lane FSM monitor/fast-calibration registers, per-lane IRQ status/clear/mask registers, PMA interface overrides/status, TX controller status, RX controller status, and ATE PCS interface controls. The chunk includes complete raw-lane banks for lanes 0-3.
- `RAWAONLANE0_DIG_*` begins at the end of the chunk with AFE/DFE/RX adaptation calibration readbacks and offsets.

Each direct register offset in this chunk has `_BASE_IDX 2`, indicating the register base index expected by AMD display register helpers. The `ix...` indirect constants do not have base-index companions because they are indices written through the CR address/data mechanism rather than normal MMIO offsets.

## Control Flow

This header has no executable control flow. The implied register access flow is:

1. Higher-level display code selects a direct `reg...` offset and base index for ordinary MMIO access, or selects a `reg..._CR_ADDR`/`reg..._CR_DATA` pair for an indirect DPCS CR access path.
2. For direct registers, AMD register helpers read or write the MMIO offset using the base index.
3. For indirect CR registers, software writes one `ixDPCSSYS_CR0_*` address to the selected `*_CR_ADDR` register and transfers data through the paired `*_CR_DATA` register.
4. Companion shift/mask headers provide the bit layout used to modify fields safely; this header supplies only the register address/index side of that contract.
5. Hardware state machines in the display PHY, power sequencer, DCIO GPIO/AUX blocks, PLLs, lanes, and raw PCS/PMA blocks perform the actual reset, clocking, training, calibration, IRQ, and status behavior.

The repeated base-address pattern is a key part of the intended flow. RDPCS TX direct blocks and CR proxy windows are repeated at base offsets `0x0`, `0x360`, `0x6c0`, `0xa20`, and `0xd80`, producing register windows for transmitters/CR instances 0-4. UNIPHY reserved banks use the same stride for instances 1-4. Driver code can therefore keep per-instance register tables while relying on generated names to resolve the ASIC-specific addresses.

## State And Persistence

The file itself stores no state. Its constants point at hardware-backed state:

- Panel power sequencer registers hold panel enable sequencing, delay, reference divider, GPIO, and backlight PWM state. Writes can persist in hardware until reset or until later display power-management code reprograms them.
- RDPCSTX control and PHY registers drive transmitter reset, clocking, SRAM access, PLL update, DP Alt Mode behavior, debug hooks, PHY control, fuses, and PLL override paths.
- DCIO/GPIO/AUX registers expose and control connector-facing IO pins, DDC/AUX behavior, HPD state, pad strength, link crossbars, genlock/swaplock pins, and soft resets.
- `ixDPCSSYS_CR0_*` indirect registers represent PHY microarchitectural state for supervisor PLLs, RTUNE, bandgap/reference, per-lane TX/RX power/adaptation/CDR/statistics, raw lane interrupt state, PMA/PCS overrides, FSM calibration monitors, and always-on calibration readbacks.

Durability is hardware-local. The constants do not record values, but incorrect writes through these addresses can leave display PHY lanes, panel power sequencing, or connector GPIO state altered until the driver reinitializes the block or the hardware resets.

## Dependencies And Integration Points

This header depends only on the C preprocessor and its include guard. It is part of the generated AMD ASIC register header set under `include/asic_reg/dpcs/`; it must stay synchronized with the matching DPCS 4.2.2 shift/mask header, generated register tables, and the ASIC programming documentation.

Integration points include:

- AMD display register helpers such as `REG_GET`, `REG_SET`, and indexed register-table patterns that combine offset macros, `_BASE_IDX` macros, and shift/mask macros.
- DC resource and link-encoder code that constructs per-ASIC register lists for DCN/display versions and addresses RDPCS TX, DCIO, HPD/DDC/AUX, panel power sequencing, and PHY controls.
- HPO DisplayPort link encoder paths that read RDPCSTX state, for example `RDPCSTX_PHY_CNTL6` DP Alt Mode state in nearby DCN HPO encoder implementations.
- Atom firmware data structures that refer to RDPCSTX PHY fuse/control semantics for TX EQ and boost programming; the header provides the address names used by code that applies those firmware-derived values.
- Companion generated headers such as `dpcs_4_2_2_sh_mask.h`, which define field masks/shifts for the offset names in this file.

## Risks

- Generated-address drift is the main risk. A wrong offset or base index can make otherwise correct field programming hit the wrong hardware register.
- The direct RDPCSTX and UNIPHY sections are highly repetitive. Instance-copy errors are especially dangerous because a single lane/transmitter can fail while adjacent instances appear correct.
- The indirect CR map mixes supervisor, lane, raw lane, and always-on calibration domains. Confusing direct `reg...` offsets with indirect `ix...` indices can corrupt the wrong access path.
- Many names expose low-level PHY override, PLL, reset, calibration, IRQ clear, and ATE/test controls. Accidental writes can break link training, hold a lane in reset, disable TX/RX data, mask or clear needed interrupts, force test loopback, or disturb panel/backlight sequencing.
- Reserved UNIPHY macro-control offsets are intentionally opaque. Treating them as normal feature registers without matching documentation could program undefined hardware behavior.
- This chunk ends mid-file and mid-`RAWAONLANE0` coverage. File-level analysis must merge this with later chunks before drawing conclusions about the full DPCS 4.2.2 register map.

## Test Signals

Useful validation is mostly compile-time, generated-header consistency, and hardware/display behavior:

- Build coverage should compile every consumer that includes DPCS 4.2.2 offset and shift/mask headers, ensuring macro names and `_BASE_IDX` constants match generated register tables.
- Generated-header checks can compare direct RDPCSTX instances 0-4 for expected stride and register-name parity, and compare UNIPHY reserved banks 1-4 for the expected 58-entry pattern.
- Static checks can confirm direct `reg...` symbols that should be MMIO-visible have `_BASE_IDX 2`, while `ix...` indirect symbols do not.
- Register-table tests should verify that `RDPCSTX_PHY_CNTL*`, `RDPCSTX_PHY_FUSE*`, CR address/data, PWRSEQ, DCIO, HPD/DDC/AUX, and UNIPHY symbols resolve to the intended per-ASIC offsets.
- Hardware or emulator smoke tests should cover panel power-on/off, backlight PWM changes, AUX/DDC/HPD operation, DisplayPort link bring-up and retraining, DP Alt Mode detection, lane reset/request handshakes, PLL programming, RX adaptation, IRQ mask/clear handling, and OCLA/debug reads.
- Failure signatures include compile errors for missing generated symbols, display link training failures, HPD/DDC/AUX timeouts, incorrect backlight or panel sequencing, lane-specific transmitter failures, stuck reset/calibration/status bits, unexpected PHY IRQ storms, or failures limited to one repeated RDPCSTX/UNIPHY instance.

### subset-b-002333: lines 2471-4856

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 2471-4856

## Scope

This chunk is a generated AMD DPCS 4.2.2 register-offset header segment. It covers 2,386 source lines and 2,382 `#define` entries. The content is declarative only: it exports C preprocessor constants for register offsets and contains no functions, structs, enums, runtime branches, allocation, locks, or software persistence.

The slice starts inside the `DPCSSYS_CR0_RAWAONLANE0` always-on lane register group and ends inside `DPCSSYS_CR1_RAWAONLANE2`. Later chunks must provide the trailing `CR1_RAWAONLANE2` entry and subsequent lane/common groups.

## Purpose

`dpcs_4_2_2_offset.h` maps symbolic DPCS 4.2.2 register names to internal register offsets. Driver code pairs these `ix...` address constants with field definitions from `dpcs_4_2_2_sh_mask.h` and AMD display register helpers to program display PHY/DPCS hardware without hard-coded addresses.

This chunk covers low-level DisplayPort/PHY control windows for:

- `CR0_RAWAONLANE0` tail, full `CR0_RAWAONLANE1` through `CR0_RAWAONLANE3`, and `CR0_RAWAONLANEX`.
- `CR0_SUPX`, including supervisor digital registers and analog MPLLA/MPLLB controls.
- `CR0_LANEX`, including generic lane digital/analog TX and RX registers.
- `CR0_RAWMEM` and `CR0_RAWLANEX`.
- `CR1_SUP`, `CR1_LANE0` through `CR1_LANE3`, `CR1_RAWCMN`, and full `CR1_RAWLANE0` through `CR1_RAWLANE3`.
- `CR1_RAWAONLANE0`, `CR1_RAWAONLANE1`, and most of `CR1_RAWAONLANE2`.

## Important API Surface

There are no callable APIs. The exported interface is the generated macro namespace:

- `ixDPCSSYS_CR0_RAWAONLANE{0,1,2,3,X}_DIG_*`: always-on lane offsets for AFE/CTLE offsets, RX adaptation IQ/FOM, DFE ref levels and VDAC/IDAC offsets, RX phase adjust, MPLLA/MPLLB coarse tune, power-up done, adapted ATT/VGA/CTLE/DFE taps, slicer controls, common calibration status, adaptation controls, MPLL disable, signal detect, DCC calibration codes, firmware config, lane transceiver mode, and TX DCC config.
- `ixDPCSSYS_CR0_SUPX_DIG_*` and `ixDPCSSYS_CR1_SUP_DIG_*`: supervisor/common offsets for ID code, reference clock override, MPLL divider and mode override, refgen control, RTUNE control/status, SRAM boot/load, clock selection, supply isolation and power-gate overrides, debug/OCLA controls, reset/power outputs, and analog PMIX override outputs.
- `ixDPCSSYS_CR0_SUPX_ANA_*` and `ixDPCSSYS_CR1_SUP_ANA_*`: analog supervisor offsets for prescaler, RTUNE, bandgap, switch power measurement, MPLLA/MPLLB miscellaneous controls, overrides, ATB entries, control words, and reserved slots.
- `ixDPCSSYS_CR0_LANEX_*` and `ixDPCSSYS_CR1_LANE{0,1,2,3}_*`: lane-scoped ASIC override, TX/RX power control, VCO calibration, CDR/DPLL, RX adaptation controls/status, RX statistics counters, MPHY controls, analog TX/RX override outputs, DCC DAC/term controls, ATB measurement, and reserved analog lane slots.
- `ixDPCSSYS_CR0_RAWLANEX_DIG_*` and `ixDPCSSYS_CR1_RAWLANE{0,1,2,3}_DIG_*`: raw PCS/PMA lane offsets for TX/RX override/input, ATE overrides, master MPLL loop, FSM control and monitor registers, fast RX calibration/adaptation states, IRQ status/clear/mask registers, PMA crossbar override/status, TX/RX controller status, and OCLA/UPCS debug hooks.
- `ixDPCSSYS_CR1_RAWCMN_DIG_*`: raw common-domain offsets for common controls, PMA/PCS power-stable overrides, power-gate override/status, monitor and analog isolation controls, SRAM boot/load, reference clock, MPLL force/ack, VREF status, RTUNE values, reference range override, and miscellaneous always-on common config.

The offsets in repeated lane groups follow regular windows. Examples in this chunk include `CR0_RAWAONLANE1` at `0x4100`-`0x4151`, `CR0_RAWAONLANE2` at `0x4200`-`0x4251`, `CR0_RAWAONLANE3` at `0x4300`-`0x4351`, `CR1_RAWLANE0` at `0x3000`-`0x30c8`, `CR1_RAWLANE1` at `0x3100`-`0x31c8`, `CR1_RAWLANE2` at `0x3200`-`0x32c8`, and `CR1_RAWLANE3` at `0x3300`-`0x33c8`.

## Control Flow

This header has no software control flow. The implied hardware programming flow is:

1. DCN 3.1.5 display resource code includes this offset header and the matching shift/mask header.
2. Resource/link encoder code selects a DPCS block, lane, and symbolic offset.
3. Register helper code performs MMIO or indexed register access using the address constant.
4. Field values from `dpcs_4_2_2_sh_mask.h` are applied during read-modify-write operations.
5. DPCS hardware state machines consume request, reset, power, calibration, adaptation, interrupt, and override writes, while status offsets expose acknowledgements and calibration/debug readback.

The repeated `LANEX` and `RAWLANEX` blocks are generic per-lane templates, while numbered `LANE0`-`LANE3` and `RAWLANE0`-`RAWLANE3` blocks provide concrete lane windows. `RAWAONLANE*` blocks are separate always-on calibration/status windows, not the same layout as raw PCS lane blocks.

## State And Persistence

The file itself stores no runtime state. Its constants address hardware state that persists according to DPCS power domains, resets, and firmware/hardware sequencing.

Important hardware-backed state named in this chunk includes TX/RX pstate and power-up timing, reset/request/ack handshakes, MPLL selection and force/ack controls, RX CDR and VCO calibration state, RX adaptation and DFE status, RTUNE and DCC calibration controls, signal detect filters and readback, IRQ status/clear/mask bits, OCLA/debug monitor registers, ATE/test overrides, and analog TX/RX control or measurement registers.

Because many registers are override or clear/status surfaces, software consumers must preserve reserved bits and respect access semantics from the hardware spec. This offset header only tells callers where registers live; it does not encode write-one-to-clear behavior, read-only status behavior, timing requirements, or reset defaults.

## Dependencies And Integration Points

The syntactic dependency is the C preprocessor and the include guard in the full header. The semantic dependency is AMD's generated DPCS 4.2.2 register database and the companion `dpcs_4_2_2_sh_mask.h` bitfield map.

In this tree, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`, alongside DCN 3.1.5 register headers. The same file defines DPCS base segments after the includes, tying these offsets to DCN 3.1.5 display resource initialization.

Likely consumers are AMD display register tables and link/resource code involved in DisplayPort/PHY bring-up, lane programming, link training, rate/width/pstate changes, hotplug recovery, suspend/resume, power gating, calibration, DCC/RTUNE handling, IRQ handling, and validation/debug flows that read FSM/OCLA/ATE state.

## Risks

- Generated-header drift is the primary risk. A wrong offset can direct a valid field mask to the wrong hardware register, producing silent PHY misconfiguration.
- The chunk is highly repetitive across lanes and controllers. A generation error in one lane window can cause lane-specific link-training or signal-integrity failures that are hard to distinguish from board or cable issues.
- This slice starts and ends mid-group. Merge/reconciliation must not treat `CR0_RAWAONLANE0` or `CR1_RAWAONLANE2` as complete based only on this document.
- `CR0` and `CR1` blocks reuse many offset values under different controller prefixes. Consumers must combine the correct block base, address macro, and field mask rather than assuming a globally unique numeric offset.
- Override registers can bypass normal state-machine control. Leaving ATE, PMA/PCS, reset, MPLL, signal-detect, or data-enable overrides asserted can break normal display operation or power management.
- IRQ status, clear, and mask registers have very similar names. Incorrect access semantics can lose interrupts, create interrupt storms, or clear the wrong event.
- Analog and calibration offsets control MPLL, RTUNE, DCC, CDR, VCO, RX adaptation, and termination behavior. Bad values can produce intermittent failures, not just immediate compile or probe failures.

## Test Signals

Useful validation is mostly build-time, generation-time, and hardware-facing:

- Compile AMDGPU display code that includes `dcn315_resource.c`, verifying `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` remain synchronized.
- Static generated-header checks should confirm expected repeated lane-window structure and matching offset/mask prefixes for complete groups in this range.
- Compare DPCS 4.2.2 offsets against adjacent generated versions, especially `dpcs_4_2_0` and `dpcs_4_2_3`, to catch unintended lane-window or block-offset drift.
- Hardware tests should cover DisplayPort link bring-up, lane-count/rate changes, retraining, hotplug, suspend/resume, low-power entry/exit, RX adaptation, DCC/RTUNE calibration, signal detect, and IRQ clear/mask behavior on DCN 3.1.5-class hardware.
- Debug readback should show sane transitions for reset/request acknowledgements, power-up done, MPLL/RCAL/VREF calibration status, RX adaptation done/FOM, CDR/VCO status, TX DCC status, signal detect outputs, FSM fast-state flags, and OCLA monitor values.

## Chunk Notes For Merge

This document intentionally covers only lines 2471-4856 of `dpcs_4_2_2_offset.h`. The final per-file report should describe the entire file as a generated ASIC register-address map for AMD DPCS 4.2.2, paired with `dpcs_4_2_2_sh_mask.h` and integrated through `dcn315_resource.c`.

### subset-b-002334: lines 4857-7242

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

### subset-b-002335: lines 7243-9628

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 7243-9628

## Scope

This chunk is a generated AMD DPCS 4.2.2 offset-header segment. It covers 2,386 source lines and 2,382 `#define` constants. Every constant in the selected range is an indexed DPCS register offset named with the `ixDPCSSYS_...` convention; there are no `_BASE_IDX` constants, functions, structs, enums, runtime variables, loops, branches, or executable statements in this slice.

The line range starts inside the `DPCSSYS_CR2` indexed-register map, at the tail of the `CR2_SUPX` analog MPLLA group. It continues through the `CR2_SUPX`, `CR2_LANEX`, `CR2_RAWMEM`, and `CR2_RAWLANEX` regions, then crosses the explicit `dpcssys_cr3_rdpcstxcrind` address-block marker and covers most of the corresponding `DPCSSYS_CR3` indexed-register map through `CR3_LANEX_DIG_ANA_SIGDET_OVRD_OUT_2`. The next lines after this chunk continue the `CR3_LANEX` analog tail and the `CR3_RAWMEM`/`CR3_RAWLANEX` aliases, so the CR3 map is not complete in this chunk alone.

## Purpose

`dpcs_4_2_2_offset.h` gives AMDGPU display code symbolic names for DPCS 4.2.2 register offsets. The `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_DATA` registers near the top of the file provide the MMIO address/data windows for CR instances; these `ix...` constants are the indirect offsets written through those windows. Consumer code pairs this offset header with `dpcs_4_2_2_sh_mask.h` to read or update named bitfields without hard-coding internal PHY register numbers.

This chunk specifically maps low-level PHY control, status, calibration, debug, and test registers for CR2 and CR3. It includes common support/MPLL blocks, lane-local digital and analog blocks, raw per-lane PCS/PMA crossbar blocks, raw common always-on control blocks, and lane broadcast forms such as `LANEX`, `RAWAONLANEX`, and `RAWLANEX`.

## Exported API Surface

There are no callable APIs or local C types. The exported surface is the preprocessor macro namespace:

- `ixDPCSSYS_CR2_SUPX_*`: partial CR2 support broadcast region, starting at MPLLA analog ATB/control registers and covering MPLLB analog controls, MPLLA/MPLLB digital power-control registers, clock/reset timing, RTUNE configuration/status, and analog override/status outputs.
- `ixDPCSSYS_CR2_LANEX_*`: CR2 lane-broadcast digital/analog register offsets, including ASIC override/input/output windows, TX/RX power-control and calibration controls, RX CDR/DPLL/adaptation/statistics controls, MPHY controls, digital-to-analog override outputs, and direct analog TX/RX measurement/control registers.
- `ixDPCSSYS_CR2_RAWMEM_*` and `ixDPCSSYS_CR2_RAWLANEX_*`: CR2 raw ROM/RAM and raw lane-broadcast PCS/FSM/IRQ/PMA/TX/RX/ATE offsets in the high indirect range around `0xa000`, `0xc000`, and `0xe000`.
- `ixDPCSSYS_CR3_SUP_*` and `ixDPCSSYS_CR3_SUPX_*`: CR3 support register offsets for IDCODE, refclk, MPLLA/MPLLB override, SSC, charge pump, prescaler, ASIC input/output, bandgap, RTUNE, MPLL power control, clock/reset, and analog override/status.
- `ixDPCSSYS_CR3_LANE{0,1,2,3}_*`: CR3 lane-specific register offsets. Lane 0 and lane 3 are partial in this chunk; lane 1 and lane 2 are more complete and include digital ASIC, TX/RX power, RX CDR/DPLL/adaptation/statistics/MPHY, digital analog-output, and analog TX/RX blocks.
- `ixDPCSSYS_CR3_RAWAONLANE{0,1,2,3,X}_*`: CR3 raw always-on per-lane RX/TX state, power-gating, PCS/PMA request/ack, reset, status, DCC, RTUNE, and analog override/status offsets.
- `ixDPCSSYS_CR3_RAWCMN_*`: CR3 raw common always-on offsets for RTUNE, SRAM boot/load, power-gating override, common reset/supply/reference/MPLL request and acknowledge plumbing, VREF status, reference-range override, and MPLL powerdown timing.
- `ixDPCSSYS_CR3_RAWLANE{0,1,2,3,X}_*`: CR3 raw per-lane PCS/FSM/IRQ/PMA/TX/RX/ATE offsets. These are repeated per physical lane and also exposed through `RAWLANEX` for lane-broadcast or lane-indexed access.

All values in this selected range are 16-bit internal register offsets, not host virtual addresses. The high-order ranges carry block meaning: support/common registers occupy low offsets and `0x8000`-class broadcast support offsets, lane broadcast uses `0x9000`-class offsets, raw ROM/RAM use `0xa000`/`0xc000`, and raw-lane PCS/PMA/control windows use `0xe000`-class offsets.

## Register Areas Covered

The CR2 support-broadcast portion begins midstream at `ixDPCSSYS_CR2_SUPX_ANA_MPLLA_ATB3`. It completes the visible MPLLA analog monitor/control tail, covers MPLLB analog monitor/control and reserved slots, then defines digital MPLL power-control/status/timer/calibration offsets for both MPLLA and MPLLB. The same section exposes clock/reset power-up timers, reference VPHUD, RTUNE configuration and readback registers, and digital analog-override outputs for MPLLA/MPLLB, RTUNE, bandgap, and PMIX.

The CR2 `LANEX` block describes a lane-broadcast view of a single lane register layout. Digital offsets cover ASIC override and ASIC input/output windows, TX power states and power-up timing, TX DCC DAC programming and acknowledgement, TX clock alignment, TX loopback/BERT control, RX power states and timing, RX VCO calibration, RX alignment/LBERT, CDR and DPLL controls, RX adaptation configuration/status/DAC selector/banked access, RX statistics counters and match controls, MPHY low-speed/PWM controls, and digital outputs into analog TX/RX blocks. The following analog offsets expose TX measurement, power override, alternate bus, ATB, DCC DAC, termination, clocks, miscellaneous registers, and RX CDR/slicer/power/squelch/calibration/ATB/reserved registers.

The CR2 raw region includes two memory offsets, `ROM_CMN0_B0_R0` and `RAM_CMN0_B0_R0`, followed by `RAWLANEX` PCS crossbar, FSM, IRQ, PMA crossbar, TX control, RX control, and ATE override windows. This gives software a lower-level lane-broadcast interface to PCS/PMA state-machine inputs and outputs, interrupt status/clear/mask registers, TX/RX request and acknowledgement paths, calibration state, DCC state, OCLA/UPCS observability, and manufacturing/test override controls.

The CR3 block starts cleanly at `// addressBlock: dpcssys_cr3_rdpcstxcrind`. It first maps the normal `SUP` support region from IDCODE and reference-clock overrides through MPLLA/MPLLB overrides, SSC programming, charge pump controls, ASIC inputs, prescaler/bandgap analog controls, MPLL analog controls, MPLL power/timing/calibration, RTUNE, and analog override/status outputs. It then maps lane-specific regions: lane 0 begins at analog RX ATB/reserved registers and continues through raw always-on lane 0; lanes 1 and 2 are complete enough to show the full repeated digital/analog lane layout; lane 3 begins at digital analog outputs and analog TX/RX controls before entering raw always-on lane 3. The CR3 `SUPX` and `LANEX` broadcast regions repeat the same support and lane schemas for broadcast or indexed access across CR3 lanes.

The CR3 raw common and raw lane sections mirror the earlier CR2 raw schema. `RAWCMN` covers common AON RTUNE, SRAM boot/load, power gate and reset override, supply/reference/MPLL request and acknowledge routing, monitor inputs, VREF and reference range state, and MPLL powerdown timing. `RAWLANE0` through `RAWLANE3` plus `RAWLANEX` cover PCS TX/RX override/input/output, FSM status, IRQ status/clear/masks, PMA crossbar input/output, TX/RX controller status, and ATE/loopback/master-MPLL override registers.

## Control Flow And State Behavior

This header chunk has no software control flow. All behavior is supplied by driver code that selects these offsets and by the DPCS hardware reached through the CR address/data windows.

The register names imply several hardware state domains:

- Link and PHY bring-up: support registers drive or observe reference-clock, prescaler, bandgap, MPLL, SSC, RTUNE, clock/reset, SRAM boot/load, and VREF-related state.
- Per-lane power management: TX/RX pstate and power-up timing registers, low-power detect, reset/request/ack fields in the raw PCS/PMA blocks, and supply power-stable controls participate in lane enable, disable, and low-power transitions.
- Clocking and calibration: MPLLA/MPLLB power-control and timing registers, RX VCO calibration, CDR/DPLL controls, DCC DAC programming, RTUNE values, AFE/CTLE/DFE adaptation status, slicer controls, and phase/IQ adjustment offsets represent hardware calibration workflows.
- Status and diagnostics: RX statistics counters, FSM status monitors, OCLA/UPCS windows, LBERT controls/errors, analog ATB/measurement registers, and ATE override windows provide bring-up and validation observability.
- Interrupt lifecycle: raw lane IRQ status, clear, and mask offsets encode a conventional status-clear-mask register pattern for lane reset/request/rate/pstate/adaptation/loopback/DCC/TX events.

No software state is stored in this file. Hardware register contents persist only according to ASIC power domains, resets, and firmware/hardware sequencing. The header itself is stateless and is regenerated from the ASIC register database.

## Dependencies And Integration Points

The direct syntactic dependency is the C preprocessor. The semantic dependency is AMD's generated DPCS 4.2.2 register database and the companion `dpcs_4_2_2_sh_mask.h` bitfield map.

In this tree, `drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` includes both `dpcs/dpcs_4_2_2_offset.h` and `dpcs/dpcs_4_2_2_sh_mask.h`. That ties this generated offset contract to the DCN 3.1.5 resource implementation. The same file defines DPCS base segments and instantiates RDPCSTX register lists for display link encoders, while DIO/HPO link encoder code elsewhere uses RDPCS/RDPCSTX register and field abstractions for DP/HDMI PHY control.

Important integration surfaces include:

- AMD DC resource construction for DCN315, where generated offset and mask headers populate register-address and bitfield tables.
- DisplayPort and HDMI link encoder programming, especially reference-clock enable, DP alt-mode state, lane rate/width/pstate, TX FIFO/clocking, and MPLL programming paths.
- PHY power and suspend/resume flows that need TX/RX pstate, power-up timers, SRAM boot/load, MPLL powerdown timing, and acknowledgement/status readback.
- Hardware bring-up, lab, or manufacturing flows that use ATE, ATB, OCLA, LBERT, raw PCS/PMA, RTUNE, RX adaptation, CDR/DPLL, DCC, and analog override registers.
- Generated-register validation across adjacent DPCS versions. The same offsets appear in nearby `dpcs_4_2_0_offset.h`, `dpcs_4_2_3_offset.h`, and older `dpcs_3_1_4_offset.h` families, so version-to-version diffs are a useful way to detect accidental generated-header drift.

## Risks

- The chunk is all generated numeric register offsets. A single wrong value can route a read or write to the wrong internal PHY register, which may cause display link failures without any C compiler warning.
- The line range starts and ends inside larger logical groups. Merge/reconciliation must not treat the CR2 `SUPX` beginning or the CR3 `LANEX`/`RAWLANEX` ending as complete based only on this chunk.
- CR2 and CR3 blocks are highly repetitive, and lane 0/1/2/3 plus `LANEX`/`RAWLANEX` forms differ mostly by prefix and offset range. Copy-generation drift can create lane-specific or instance-specific failures that are difficult to diagnose.
- Broadcast forms such as `LANEX`, `SUPX`, `RAWAONLANEX`, and `RAWLANEX` can affect more than one lane or can depend on external lane selection. Consumer code must not substitute them blindly for lane-specific offsets.
- Raw and ATE override registers can force hardware away from normal PCS/PMA state-machine control. Leaving override-enable state asserted after debug or manufacturing operations can break link training, calibration, power management, or hotplug recovery.
- IRQ status, clear, and mask registers have similar generated names but different access semantics. The offset header does not encode write-one-to-clear behavior, mask polarity, or ordering requirements.
- Reserved analog and digital slots are named as offsets. They should not be used as scratch registers, and read-modify-write users must preserve reserved bitfields from the companion mask header.

## Test Signals

Useful validation is mainly build-time, generated-data, and hardware integration oriented:

- Compile/preprocess AMDGPU display code for DCN315 with `dpcs_4_2_2_offset.h` and `dpcs_4_2_2_sh_mask.h` included through `dcn315_resource.c`.
- Static generation checks that this slice contains 2,382 non-`BASE_IDX` `ix...` defines and that no callable code or declarations were introduced into the generated header.
- Cross-check each register prefix in this range against the companion `dpcs_4_2_2_sh_mask.h` so offsets and bitfield masks exist for the same generated register names where field definitions are expected.
- Diff DPCS 4.2.2 offsets against adjacent generated versions (`dpcs_4_2_0_offset.h`, `dpcs_4_2_3_offset.h`, and where applicable `dpcs_3_1_4_offset.h`) to catch unintended address movement or missing repeated lane entries.
- Hardware display tests on DCN315-class systems: DP/HDMI link training, lane-count and link-rate changes, hotplug, DP alt-mode transitions, suspend/resume, low-power entry/exit, MST/HPO paths where available, and error recovery after failed training.
- PHY bring-up readback should show expected transitions for reference-clock enable, MPLL lock/power state, SRAM boot/load, RTUNE status, TX/RX pstate acknowledgements, RX VCO/CDR/DPLL calibration, adaptation status, DCC acknowledgement, IRQ status/clear/mask behavior, and analog/ATE override cleanup.

## Chunk Notes For Merge

This document intentionally covers only lines 7243-9628 of `dpcs_4_2_2_offset.h`. Earlier chunks should cover the start of the CR2 indexed-register map, including the missing beginning of `CR2_SUPX`. Later chunks should continue the CR3 `LANEX` analog tail and CR3 raw memory/raw lane-broadcast regions. The final per-file report should describe the whole header as a generated indirect DPCS 4.2.2 offset map for AMDGPU display PHY programming, with `dcn315_resource.c` and the matching shift/mask header as primary in-tree integration anchors.

### subset-b-002336: lines 9629-11957

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_offset.h lines 9629-11957

## Purpose

This chunk is a generated AMD DPCS 4.2.2 register-offset header slice for DCN 3.1.5 display PHY programming. It contains no executable C code. Its interface is a dense set of preprocessor constants that name hardware register indexes and MMIO register offsets used by AMDGPU display code.

The requested range contains 2,318 `#define` entries. It starts near the end of the CR3 indirect DPCS namespace with 162 `ixDPCSSYS_CR3_*` offsets, covers the complete `dpcssys_cr4_rdpcstxcrind` address block with 2,146 `ixDPCSSYS_CR4_*` offsets, then ends with ten `regRDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` direct-register aliases plus their base-index constants. The final comment notes that the RDPCSPIPE aliases are a DCN315-specific hack because RDPCSPIPE has only two physical instances even though higher-level display code exposes more pipe/transmitter ids.

Although this file sits under a local `ceph-client` source mirror, this range is AMDGPU display-controller metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, locks, allocations, includes, or direct register accesses in this chunk. The exported API is the generated macro naming scheme:

- `ixDPCSSYS_CR3_*` and `ixDPCSSYS_CR4_*` name indirect DPCS control-register indexes inside the CR3/CR4 register spaces.
- `regRDPCSPIPE<n>_RDPCSPIPE_PHY_CNTL6` names direct MMIO offsets for the RDPCSPIPE `PHY_CNTL6` register instances.
- `*_BASE_IDX` gives the register base segment index used by AMD display register-table helpers.

The CR3 portion is the tail of the CR3 lane-X/register-X block. It covers analog TX/RX override readbacks and raw lane-X registers: PCS transfer overrides, RX adaptation feedback, lane number, ATE/test overrides, FSM fast-control/status registers, IRQ status/clear/mask registers, PMA transfer registers, TX/RX control registers, and additional PCS ATE overrides.

The CR4 block is the main body of this chunk and begins at `ixDPCSSYS_CR4_SUP_DIG_IDCODE_LO` offset `0x0000`. Major macro families include:

- `SUP_DIG_*`, `SUP_ANA_*`, `SUPX_DIG_*`, and `SUPX_ANA_*`: supervisor/common control, ID, refclk, MPLLA/MPLLB override and ASIC input registers, spread-spectrum clocking, PLL charge-pump and gain settings, bandgap/reference timing, RTUNE configuration/status, analog override outputs, and supervisor analog controls.
- `LANE0` through `LANE3` and `LANEX`: lane-level ASIC, TX power, RX power/VCO/CDR/adaptation, RX statistics, MPHY, digital analog override, analog TX, and analog RX offset namespaces. Lanes 1, 2, and `LANEX` include the larger RX-side set, while lanes 0 and 3 expose a narrower TX/stat-oriented subset in this generated map.
- `RAWCMN_DIG_*`: raw common DPCS controls for MPLLA/MPLLB override and bandwidth/SSC controls, lane FSM extension, common MPLL state, TX calibration, SRAM init, OCLA/debug, PCS/FW ID codes, always-on common RTUNE values, power-gate/supervisor/resource overrides, VREF stats, and reference range/misc configuration.
- `RAWLANE0` through `RAWLANE3` and `RAWLANEX`: repeated raw-lane PCS/FSM/IRQ/PMA/TX/RX/ATE register windows. Each lane has PCS transfer inputs/outputs, RX adaptation ACK/FOM, directed TX coefficient feedback, lane numbering, PH2 calibration, fast RX startup/adaptation/calibration controls, common calibration status, IRQ status/clear/mask registers, PMA lane/supervisor/TX/RX transfer registers, MPHY overrides, TX/RX control/status, and ATE/test override registers.
- `RAWAONLANE0` through `RAWAONLANE3` and `RAWAONLANEX`: always-on lane calibration/status registers. These name AFE/DFE offsets, RX phase and FOM values, MPLL coarse tune, initial power-up/adaptation status, fast flags, slicer and calibration controls, signal-detect and LOS filtering, firmware configuration, DCC calibration/bank access, lane transceiver-mode override/readback, and TX DCC configuration.
- `RAWMEM_DIG_ROM_CMN0_B0_R0` and `RAWMEM_DIG_RAM_CMN0_B0_R0`: raw memory windows in the CR4 indirect space.

The RDPCSPIPE tail maps `RDPCSPIPE0`, `RDPCSPIPE2`, and `RDPCSPIPE4` to offset `0x2d73`, while `RDPCSPIPE1` and `RDPCSPIPE3` map to offset `0x2e4b`; all use base index `2`. This deliberate aliasing is the mechanism described by the local TODO/comment.

## Control Flow

This header has no runtime control flow. It participates in compile-time construction of AMDGPU display register tables:

1. DCN 3.1.5 resource code includes `dpcs/dpcs_4_2_2_offset.h` together with `dpcs/dpcs_4_2_2_sh_mask.h`.
2. Register-list macros and helper macros such as `SR`, `SRI`, `SRI_IX`, `LE_SF`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use token-pasted register names to bind these offsets with matching shift/mask metadata.
3. Runtime display code performs actual sequencing for link encoder setup, DP/HDMI PHY programming, link training, USB-C DP alt-mode queries, lane power transitions, calibration, and debug reads.

The macros in this chunk only say where registers are addressed. They do not encode whether a register is read-only, write-only, clear-on-write, self-clearing, latched, power-domain dependent, or safe to access while firmware owns the PHY.

## State And Persistence Behavior

The file stores no software state and persists nothing. It names hardware-visible state and control surfaces:

- Common/supervisor state for reference clocks, MPLLA/MPLLB programming, spread-spectrum settings, PLL power/calibration timers, bandgap/reference controls, RTUNE results, SRAM init, firmware IDs, and raw common power/resource overrides.
- Lane state for TX and RX request/reset/power-state behavior, data enable, lane width/rate/pstate handshakes, PLL selection, TX DCC, RX VCO/CDR, RX adaptation, DFE/CTLE/VGA/ATT values, signal-detect/LOS filtering, PH2 calibration, and MPHY PWM/termination controls.
- Interrupt and handshake state for RX/TX reset/request/rate/pstate/adaptation events, lane transceiver-mode changes, PH2 calibration request/disable, serial loopback, DCC on-demand events, PMA ACKs, and fast FSM status.
- Debug/test state for ATE overrides, OCLA/UPCS observation controls, LBERT controls and errors, directed TX coefficient feedback, analog test bus controls, and raw ROM/RAM windows.

Persistence is entirely hardware-defined. Configuration registers can survive until rewritten by link training, modeset, PHY reset, power gating, suspend/resume restoration, GPU reset, or ASIC reinitialization. Status, ACK, IRQ, calibration, and statistic registers may be transient, latched, clear-on-write, or valid only while the relevant DPCS common/lane power and clock domains are active.

## Dependencies And Integration Points

This generated offset header must stay synchronized with the matching DPCS 4.2.2 shift/mask header and AMD's authoritative register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_2_sh_mask.h` supplies field shifts and masks for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn315/dcn315_resource.c` directly includes this header and defines the DCN315 DPCS base segments. In that file, DPCS segment bases include `DPCS_BASE__INST0_SEG0` through `DPCS_BASE__INST0_SEG5`, and the DPCS 4.2.2 headers are paired with `dcn_3_1_5` DCN register headers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` lists `RDPCSPIPE_PHY_CNTL6` in `DPCS_DCN31_REG_LIST(id)` and lists its `RDPCS_PHY_DPALT_*` fields in `DPCS_DCN31_MASK_SH_LIST`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` reads `RDPCSPIPE_PHY_CNTL6` in legacy USB-C DP alt-mode paths on Yellow Carp B0-style hardware for transmitters that do not use `RDPCSTX_PHY_CNTL6`.
- Adjacent generated DPCS 4.2.0 and 4.2.3 offset headers expose very similar CR3/CR4 and RDPCSPIPE layouts, making them useful for generator-consistency checks but not substitutes for this ASIC-specific file.

Behaviorally, this chunk integrates with display link bring-up, PHY lane setup, RX adaptation and calibration, DP/HDMI rate and lane-count programming, USB-C DP alt-mode handling, hotplug/modeset flows, suspend/resume restore, firmware handoff, and low-level PHY diagnostics.

## Risks And Edge Cases

- These are untyped preprocessor constants. A wrong offset can compile cleanly and only fail at runtime as a bad register read, corrupt write, stuck poll, or display link failure.
- The file is generated. Manual edits risk divergence from AMD's register database, the companion shift/mask header, firmware expectations, and silicon documentation.
- The chunk starts mid-CR3 namespace. Whole-file consumers must reconcile the preceding CR3 chunks before claiming complete CR3 coverage.
- CR4 contains repeated lane and raw-lane windows with similar register names and regular offset strides. A generator slip in only one lane can break one physical lane while leaving adjacent lanes functional.
- Lane-specific and `LANEX`/`RAWLANEX` macros are not automatically interchangeable. Code that combines a lane-X offset with a concrete-lane mask, or a CR3 offset with a CR4 offset, can silently target the wrong register.
- The RDPCSPIPE aliases intentionally map five logical instances onto two physical offsets. The local TODO says this should be verified for DCN315, so new ASIC support must not assume these aliases are generally correct.
- The RDPCSPIPE registers are used in a legacy DP-alt path that comments about avoiding hangs when querying through DMCUB is unavailable. Incorrect offsets or unsafe access ordering can affect USB-C link capability detection and lane-count limiting.
- Common PLL, spread-spectrum, bandgap, RTUNE, RX CDR/VCO, DCC, PH2 calibration, and DFE/CTLE/VGA/ATT registers are analog-sensitive. Mistakes may reproduce only at certain link rates, lane counts, boards, cables, sinks, voltage/temperature corners, or after suspend/resume.
- IRQ status, clear, and mask registers are side-effect-sensitive. Confusing status offsets with clear offsets can create repeated interrupts, missed events, or link-training timeout paths.
- Raw memory windows and ATE/OCLA/test overrides are high-risk diagnostic surfaces. Production code should access them only through documented sequences and preserve reserved or firmware-owned state.

## Test Signals

Useful validation combines generated-header consistency checks with real display behavior:

- Build AMDGPU display support for DCN315/DPCS 4.2.2. Missing or renamed symbols should surface in resource table, link encoder, and register helper initialization.
- Mechanically compare this offset range against the authoritative DPCS 4.2.2 register source and against `dpcs_4_2_2_sh_mask.h`, ensuring every expected register has matching field definitions where fields exist.
- Compare CR4 repeated `LANE*`, `RAWLANE*`, and `RAWAONLANE*` windows for expected offset stride and intentional asymmetries, especially the narrower lane 0/3 RX surface versus lane 1/2/`LANEX`.
- Cross-check DPCS 4.2.0 and 4.2.3 generated headers for expected CR3/CR4 and RDPCSPIPE alias stability while preserving ASIC-specific differences.
- Exercise DP and HDMI link bring-up across available PHYs, lanes, link rates, and power states. Watch for PLL lock failures, RX adaptation failures, false lane readiness, stuck request/ack bits, and DCC/calibration timeouts.
- Test USB-C DP alt-mode paths on hardware using the RDPCSPIPE aliases. Good signals are correct DP4-vs-two-lane detection, correct `DPALT_DISABLE` handling, and no hangs in the legacy fallback path.
- Run hotplug, modeset, blank/unblank, suspend/resume, runtime power management, and GPU reset tests to catch persistence and restoration issues around CR4 common/lane state.
- Use register dumps on failures to verify that decoded CR4 offsets align with expected supervisor, raw common, raw lane, always-on lane, IRQ, PMA, PCS, CDR/VCO, adaptation, and DCC register values.

## Cross-Chunk Notes

The previous chunk owns the earlier CR3 CR-indirect offset definitions. This chunk resumes at CR3 lane-X analog and raw-lane-X offsets, then contains the full CR4 `dpcssys_cr4_rdpcstxcrind` address block from `0x0000` through `0xe0c8`, followed by the RDPCSPIPE `PHY_CNTL6` direct-register aliases and the header guard close. The final per-file report should merge this with earlier chunks before making complete claims about CR0 through CR3 coverage or about the full DPCS 4.2.2 offset header.
