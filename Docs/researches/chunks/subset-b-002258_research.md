# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_offset.h lines 4792-7215

## Purpose

This chunk is the final slice of AMD's generated DPCS 3.1.4 register-offset header. It contains no executable driver logic; it publishes C preprocessor constants that map symbolic Display Core PHY/PCS/DCIO register names to numeric offsets and, for MMIO-style `reg...` entries, companion `_BASE_IDX` selectors. Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU display hardware metadata, not distributed filesystem code.

The range starts in the tail of the `DPCSSYS_CR2_LANE3` internal-index register list, then covers the `DPCSSYS_CR2_RAWCMN` common block and raw lanes 0 through 7. It then switches to direct display decoder register aliases for DCIO, GPIO/DDC/HPD/AUX pads, UNIPHY macro reserved spaces, RDPCSTX transmit PHY instances, CR address/data windows, RDPCSPIPE controls, and two panel/backlight power sequencer blocks. The chunk ends with the file's closing `#endif`.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, local includes, allocation paths, or locking primitives in this chunk. The public interface is the generated macro namespace:

- `ixDPCSSYS_CR2_*`: indirect DPCS CR2 register indices. These are used through CR address/data access paths rather than as plain MMIO offsets.
- `reg<block>_<register>`: direct register offset aliases for DCIO, RDPCSTX, RDPCSPIPE, DPCSSYS CR windows, and PWRSEQ blocks.
- `reg<block>_<register>_BASE_IDX`: base-address segment selector paired with each direct `reg...` offset. All visible `_BASE_IDX` values in this chunk are `2`.

The requested range contains 2,354 `#define` statements: 1,434 `ix...` internal-index constants and 920 `reg...` direct-offset/base-index constants. Major register families in this slice are:

- `ixDPCSSYS_CR2_LANE3_*`: the end of lane 3 receive statistic counters, match/stat controls, digital-to-analog TX override outputs, analog TX power/termination/equalization/DCC registers, and reserved analog TX slots.
- `ixDPCSSYS_CR2_RAWCMN_*`: common DPCS raw controls for MPLL A/B overrides, spread-spectrum controls, lane FSM extension, MPLL state, TX calibration code, SRAM init status, OCLA/debug visibility, PCS/FW ID codes, AON RTUNE values for lanes 0 through 7, power-gate overrides, VREF stats, resistance overrides, and reference-range/misc configuration.
- `ixDPCSSYS_CR2_RAWLANE0` through `ixDPCSSYS_CR2_RAWLANE7`: repeated per-lane PCS/PMA/FSM/IRQ/TX/RX control blocks. Each lane has PCS transfer override/input/output registers, RX adaptation and figure-of-merit registers, per-lane FSM fast-path and status registers, RX/TX interrupt and clear registers, PMA transfer controls, TX/RX control/status registers, ATE override hooks, and master MPLL loop controls.
- `regDC_*`, `regDCIO_*`, `regUNIPHY*_*`, `regDC_GPIO_*`, `regPHY_AUX_CNTL`, and `regAUXI2C_PAD_ALL_PWR_OK`: DCIO clock/reference/mux state, UNIPHY link and channel crossbar controls, pinstraps/intercept/soft-reset controls, backlight frame-start selection, genlock/swaplock pads, DDC/HPD/generic GPIO masks/data/enables/readbacks, pad strength, AUX controls, RX/pull-up enables, and AUX/I2C pad power-good status.
- `regDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `...RESERVED57`, and equivalent ranges for UNIPHY2, UNIPHY3, and UNIPHY4: contiguous reserved macro-control address spaces for PHY instances at base addresses `0x360`, `0x6c0`, `0xa20`, and `0xd80`; the UNIPHY0 address block is present but empty in this chunk.
- `regRDPCSTX0`, `regRDPCSTX1`, and `regRDPCSTX2`: repeated RDPCS transmitter control, clock, interrupt, PLL update, CR address/data, SRAM, scratch/spare, PHY control 0-17, PHY fuse 0-3, RX load value, DPALT control, and PLL override registers.
- `regDPCSSYS_CR0`, `regDPCSSYS_CR1`, and `regDPCSSYS_CR2`: direct aliases for each instance's CR address/data window; these overlap the corresponding RDPCSTX CR address/data offsets.
- `regRDPCSPIPE0_RDPCSPIPE_PHY_CNTL6` and `regRDPCSPIPE1_RDPCSPIPE_PHY_CNTL6`: pipe-level PHY control aliases.
- `regPWRSEQ0_*` and `regPWRSEQ1_*`: panel power GPIO enable/control/mask/readback, panel sequence control/state/delay/reference-divider registers, backlight PWM control/period/register-lock registers, and spare power-sequencer state.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMD display driver code that includes this generated offset header with matching shift/mask headers and register-access helper macros. The typical flow is:

1. Resource, GPIO, DIO/PHY, link-training, backlight, or firmware-facing display code selects an ASIC-specific register set.
2. Token-pasting helper macros resolve names such as `regRDPCSTX2_RDPCSTX_PHY_CNTL0`, `regPWRSEQ0_BL_PWM_CNTL`, or `ixDPCSSYS_CR2_RAWLANE3_DIG_FSM_STATUS_MON`.
3. For direct `reg...` entries, access helpers combine `BASE(reg..._BASE_IDX)` with the offset before issuing MMIO reads/writes.
4. For `ixDPCSSYS_CR2_*` entries, code programs a CR address register and transfers data through the paired CR data register for the relevant DPCS/RDPCS instance.
5. Higher-level display code sequences resets, clocks, PLL programming, link enablement, lane training, GPIO/AUX/DDC access, panel power, backlight PWM, interrupt handling, and suspend/resume restore using these constants.

The macro data does not encode ordering, access width, polling requirements, write-one-to-clear behavior, or read-only/write-only status. Those semantics come from the companion mask/enum headers and the code that consumes this file.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It describes hardware-backed state:

- CR2 raw common and lane registers hold PHY/PCS configuration and live status for PLLs, RTUNE calibration, SRAM initialization, lane FSMs, RX adaptation, TX/RX power and reset paths, PMA/PCS override paths, ATE/debug paths, and interrupt latches/clears.
- DCIO and GPIO registers hold display IO routing, clock/reference selection, UNIPHY link/crossbar configuration, GPIO output/input/mask/enable state, DDC/HPD/generic pin state, pad strengths, AUX pad controls, pull-up/RX enablement, and soft-reset state.
- RDPCSTX registers hold transmitter reset/clock/FIFO state, PHY DP/HDMI rate and width controls, PLL update state, CR bridge state, SRAM controls, DPALT controls, PHY fuses, and scratch/spare registers.
- PWRSEQ registers hold panel target/state sequencing, delay and reference divider values, backlight PWM configuration, PWM register lock state, and power-sequencer GPIO state.

Persistence is hardware-defined. Configuration registers may survive until the next modeset, link reconfiguration, power gate, suspend/resume, or ASIC reset. Status, interrupt, clear, counter, debug, and calibration registers may be volatile, sticky, self-clearing, write-one-to-clear, or sequencing-sensitive. The offset header intentionally does not model those behaviors.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus AMD's generated ASIC register-header convention. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_3_1_4_sh_mask.h`, which provides shifts and masks for the register names defined here.
- SOC/DCN base-address tables and helper macros that interpret `_BASE_IDX == 2`.
- Related generated enum headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h` and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc24_enum.h`, which define field values for PWRSEQ and RDPCSTX concepts.
- ATOM firmware structures in `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/atomfirmware.h`, whose transmitter parameter comments map values such as TX equalization and voltage boost to RDPCSTX PHY fuse/control fields.

Integration points are display-hardware focused: DC link encoder/PHY setup, DisplayPort and HDMI PHY programming, AUX/DDC/HPD GPIO translation, panel power sequencing, backlight PWM control, DMU/firmware-assisted PHY programming, debug/OCLA inspection, and low-power or reset flows. The `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` and `reg..._CR_DATA` aliases are especially important because they are the bridge between direct MMIO access and the many `ixDPCSSYS_CR2_*` internal register indices in this chunk.

## Risks And Edge Cases

- Offset or base-index drift is the central risk. These constants are untyped macros, so a wrong offset or `_BASE_IDX` can compile cleanly while targeting the wrong MMIO address.
- `ix...` and `reg...` constants are not interchangeable. Treating an internal CR index such as `ixDPCSSYS_CR2_RAWLANE0_DIG_FSM_STATUS_MON` as a direct MMIO offset, or bypassing the CR address/data window, would access the wrong hardware path.
- The range begins mid-block at the tail of `DPCSSYS_CR2_LANE3`; adjacent chunks are needed for the complete lane 3 CR2 map and complete file-level interpretation.
- Repeated lane and instance families are copy-sensitive. RAWLANE0-7, UNIPHY1-4, RDPCSTX0-2, CR0-2, and PWRSEQ0-1 have similar names but different offsets and base addresses; off-by-one instance selection can create connector-specific, lane-count-specific, or panel-specific failures.
- Some apparent overlaps are intentional aliases. For example, RDPCSTX CR address/data offsets are also exposed through `regDPCSSYS_CR*`; validation must distinguish generated aliases from collisions.
- The UNIPHY reserved ranges are named `RESERVED`, but they still occupy concrete addresses. New code should not infer field semantics from those names without the matching hardware database or mask definitions.
- RDPCSTX, PLL, CR, SRAM, and lane FSM registers are sequencing-sensitive. Misordered reset, clock, SRAM init, PLL update, or lane training accesses can produce blank displays, link-training failures, FIFO errors, or intermittent failures after resume.
- GPIO/DDC/HPD/AUX and PWRSEQ registers affect external pins and panel power. Incorrect mask/enable/polarity/delay/PWM programming can break EDID reads, hotplug detection, backlight control, panel sequencing, or low-power wake.

## Test Signals

Useful validation signals are mostly integration or hardware tests rather than unit tests:

- Build coverage that includes ASIC paths using `dpcs_3_1_4_offset.h` and `dpcs_3_1_4_sh_mask.h`; macro spelling or missing companion definitions should fail at compile time.
- Register-header consistency checks that every direct `reg...` offset has a matching `_BASE_IDX`, and that alias pairs such as `regRDPCSTX*_RDPCS_TX_CR_ADDR` and `regDPCSSYS_CR*_DPCSSYS_CR_ADDR` intentionally match.
- Display bring-up tests across connectors mapped to different RDPCSTX/UNIPHY instances, including link training at multiple DP rates and lane counts, HDMI/DP mode changes, hotplug, AUX DPCD reads, and DDC EDID reads.
- Suspend/resume and power-gating tests that exercise RDPCSTX SRAM/PLL/clock restore, CR register access, GPIO state restoration, panel power sequencing, and backlight PWM restoration.
- Panel-specific tests for PWRSEQ0 and PWRSEQ1: power on/off timing, backlight enable/disable, PWM period and brightness changes, register lock behavior, and GPIO polarity.
- Debug/fault tests using interrupt/status paths for RDPCSTX FIFO errors, DPALT toggles, RAWLANE IRQ status/clear registers, and OCLA/debug visibility where hardware support is available.
