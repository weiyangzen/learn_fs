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
