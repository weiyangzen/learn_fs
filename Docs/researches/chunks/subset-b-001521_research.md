# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_d.h lines 9069-10084

## Scope And Purpose

This chunk is the closing section of AMDGPU's generated DCE 11.2 register address header. It contains no executable C logic; it publishes compile-time MMIO register address constants for display PHY, PLL, display PLL, and DisplayPort/clock-source transmitter blocks on ASICs using the DCE 11.2 register map.

The range starts in the middle of the COMBOPHY TX-lane table, beginning with `CMD_BUS_TX_CONTROL_LANE2` instance aliases, then covers:

- Per-lane COMBOPHY transmitter controls for lanes 0-3 across COMBOPHY TX register instances 0-7.
- Repeated `TX_DISP_RFU*` transmitter reserved/display-specific registers for RFU slots 0-12 across lanes 0-3 and instances 0-7.
- COMBOPHY common-register addresses for margin/de-emphasis nominal settings, lane power management, transmitter control, TMDS/DisplayPort support, lane resets, impedance/calibration code control, and common display RFU registers.
- COMBOPHY PLL register addresses for frequency, bandwidth, calibration, loop, debug, regulator, observe, DFT, and PLL wrapper control registers across PLL instances 0-7.
- Display PPLL register addresses for three display PLL instances.
- DPCSTX transmitter register addresses for eight DisplayPort clock-source transmitter instances.

The file path lives under a local `ceph-client` source mirror, but this chunk is AMDGPU Linux kernel display-driver hardware metadata. It does not describe Ceph filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, storage objects, or preprocessor conditionals in this chunk except the closing include guard. The macro namespace is the API:

- `mm<REGISTER>` names the base address for the first/default instance of a register family.
- `mmDC_COMBOPHYTXREGS<n>_<REGISTER>` names the same TX-lane register for COMBOPHY TX instance `n`, where `n` runs from 0 to 7 in this chunk.
- `mmDC_COMBOPHYCMREGS<n>_<REGISTER>` names the common COMBOPHY register for common instance `n`.
- `mmDC_COMBOPHYPLLREGS<n>_<REGISTER>` names the COMBOPHY PLL register for PLL instance `n`.
- `mmDC_DISPLAYPLLREGS<n>_<REGISTER>` names the display PLL register for display PLL instance `n`, where this table covers instances 0-2.
- `mmDPCSTX<n>_<REGISTER>` names the DPCSTX transmitter register for transmitter instance `n`, where `n` runs from 0 to 7.

The per-lane COMBOPHY TX address families include `CMD_BUS_TX_CONTROL_LANE2`, `CMD_BUS_TX_CONTROL_LANE3`, `MARGIN_DEEMPH_LANE0` through `MARGIN_DEEMPH_LANE3`, `CMD_BUS_GLOBAL_FOR_TX_LANE0` through `CMD_BUS_GLOBAL_FOR_TX_LANE3`, and `TX_DISP_RFU0_LANE0` through `TX_DISP_RFU12_LANE3`. These addresses are arranged in a regular pattern: lanes are offset by 0x10, RFU/common register slots advance by 1, and COMBOPHY instances occupy repeated address windows such as `0x48xx`, `0x49xx`, and `0x9axx` through `0x9dxx`.

The common COMBOPHY families include `COMMON_MAR_DEEMPH_NOM`, `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, `COMMON_ZCALCODE_CTRL`, and `COMMON_DISP_RFU1` through `COMMON_DISP_RFU7`. These are per-PHY common controls rather than per-lane registers.

The COMBOPHY PLL families include `FREQ_CTRL0` through `FREQ_CTRL3`, `BW_CTRL_COARSE`, `BW_CTRL_FINE`, `CAL_CTRL`, `LOOP_CTRL`, `DEBUG0`, `VREG_CFG`, `OBSERVE0`, `OBSERVE1`, `DFT_OUT`, `PLL_WRAP_CNTRL1`, and `PLL_WRAP_CNTRL`. The display PPLL families include `PPLL_VREG_CFG`, `PPLL_MODE_CNTL`, `PPLL_FREQ_CTRL0` through `PPLL_FREQ_CTRL3`, `PPLL_BW_CTRL_COARSE`, `PPLL_BW_CTRL_FINE`, `PPLL_CAL_CTRL`, `PPLL_LOOP_CTRL`, `PPLL_REFCLK_CNTL`, `PPLL_CLKOUT_CNTL`, `PPLL_DFT_CNTL`, `PPLL_ANALOG_CNTL`, `PPLL_POSTDIV`, `PPLL_DEBUG0`, `PPLL_OBSERVE0`, `PPLL_OBSERVE1`, `PPLL_UPDATE_CNTL`, `PPLL_OBSERVE0_OUT`, `PPLL_STATUS_DEBUG1`, `PPLL_DEBUG_MUX_CNTL`, `PPLL_DIV_UPDATE_DEBUG`, and `PPLL_STATUS_DEBUG0`.

The DPCSTX families include `DPCSTX_PHY_CNTL`, `DPCSTX_TX_CLOCK_CNTL`, `DPCSTX_TX_CNTL`, `DPCSTX_CBUS_CNTL`, `DPCSTX_REG_ERROR_STATUS`, `DPCSTX_TX_ERROR_STATUS`, `DPCSTX_PLL_UPDATE_ADDR`, `DPCSTX_PLL_UPDATE_DATA`, `DPCSTX_INDEX_MODE_ADDR`, `DPCSTX_INDEX_MODE_DATA`, `DPCSTX_DEBUG_CONFIG`, and `DPCSTX_TEST_DEBUG_DATA`.

## Control Flow

This chunk has no runtime control flow. Every line is a preprocessor `#define` that maps a symbolic register name to a numeric MMIO address.

Runtime control flow appears in consumer code that includes `dce_11_2_d.h`, selects an address macro for a particular PHY/PLL/transmitter instance, and performs a register read, write, or read-modify-write through AMD display register helpers. A typical flow is:

1. Select the correct instance-specific address, for example a `mmDC_COMBOPHYPLLREGS<n>_FREQ_CTRL*`, `mmDC_DISPLAYPLLREGS<n>_PPLL_*`, or `mmDPCSTX<n>_DPCSTX_*` macro.
2. Use the matching DCE 11.2 field mask/shift definitions from the companion generated mask header when only part of the register is being updated.
3. Write PHY/PLL/transmitter programming values in the order required by display bring-up, link training, clock switching, power transitions, or diagnostics.
4. Poll status/debug registers such as `OBSERVE*`, `DFT_OUT`, `PPLL_STATUS_DEBUG*`, `DPCSTX_REG_ERROR_STATUS`, or `DPCSTX_TX_ERROR_STATUS` when the hardware sequence requires confirmation.

Because this header only supplies addresses, it does not enforce safe sequencing. Ordering constraints such as disabling a transmitter before changing PLL parameters, waiting for PLL lock/update completion, resetting lanes before reprogramming PHY state, or clearing sticky DPCSTX status are owned by display-driver and firmware-facing code outside this file.

## State And Persistence Behavior

The header stores no software state and has no persistence mechanism. It describes hardware-backed state in display PHY, PLL, and DPCSTX MMIO registers.

The hardware state represented by this chunk includes COMBOPHY per-lane transmitter setup, margin/de-emphasis values, lane-global TX command state, common lane power management, common lane resets, impedance/calibration control, COMBOPHY PLL frequency/bandwidth/calibration/loop parameters, display PPLL mode/frequency/post-divider/update/debug state, and DisplayPort transmitter PHY/clock/control/error/debug/indexed-access state.

Persistence is register-specific. Some values are control settings that remain programmed until a later driver or firmware write, display link reset, PHY reset, PLL update, suspend/resume transition, power-gating transition, or full GPU reset. Other values are status or debug outputs that reflect current hardware state, and error/status registers may be sticky or clear-on-write depending on the matching hardware specification. This address header does not encode read-only, write-one-to-clear, self-clearing, reserved, or power-domain access semantics.

## Dependencies And Integration Points

This chunk depends on the generated AMD ASIC register-header contract. It is normally paired with the matching DCE 11.2 mask/shift header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_11_2_sh_mask.h`, so consumers can combine address macros from this file with field masks and shifts from the companion file.

Direct include points in this source tree are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/clk_mgr/dce112/dce112_clk_mgr.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce112/dce112_compressor.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hwss/dce112/dce112_hwseq.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dce112/dce112_resource.c`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/smumgr/vegam_smumgr.c`

The practical integration surface is the AMD display core and power-management stack for DCE 11.2/Vega-era hardware. These address constants support display clock programming, PHY/transmitter setup, DisplayPort/HDMI link enablement, lane power/reset sequencing, PLL programming and observation, and debug/error paths. Firmware tables, BIOS/ATOM-derived transmitter settings, and hardware resource discovery can influence which instance macros are used for a particular connector and signal type.

## Risks And Edge Cases

The primary risk is silent MMIO misaddressing. A wrong address macro can compile cleanly while directing a register write to the wrong PHY, PLL, lane, transmitter, or reserved address. In display bring-up this can appear as missing output, unstable link training, wrong pixel clock, incorrect lane voltage swing/de-emphasis, spurious DPCSTX errors, or a hang during power/clock transitions.

Instance and lane repetition is the main source of human and generator-review risk. The chunk contains many near-identical definitions where only the instance number, lane number, RFU slot, or low address nibble changes. Copy or generation errors can be hard to detect by inspection and may only affect one connector mapping, one transmitter instance, or one lane width configuration.

Clock and PLL registers are high impact. Misprogramming `FREQ_CTRL*`, `BW_CTRL_*`, `CAL_CTRL`, `LOOP_CTRL`, `PPLL_FREQ_CTRL*`, `PPLL_POSTDIV`, or update/control registers can produce incorrect display clocks, failed PLL lock, jitter, or broken mode-set behavior. Some PLL fields are likely safe only under strict sequencing with disabled outputs or quiesced links.

PHY and transmitter controls are also sensitive. `MARGIN_DEEMPH_*`, `COMMON_LANE_PWRMGMT`, `COMMON_TXCNTRL`, `COMMON_TMDP`, `COMMON_LANE_RESETS`, `DPCSTX_PHY_CNTL`, `DPCSTX_TX_CLOCK_CNTL`, and `DPCSTX_TX_CNTL` touch the physical signal path. Incorrect values can break DisplayPort link training, HDMI/TMDS output, lane powerdown, HPD-driven reconfiguration, or resume from low-power states.

Reserved/RFU and debug/DFT registers should be treated conservatively. The `TX_DISP_RFU*`, `COMMON_DISP_RFU*`, `DEBUG*`, `OBSERVE*`, `DFT_OUT`, `DPCSTX_DEBUG_CONFIG`, and `DPCSTX_TEST_DEBUG_DATA` names indicate vendor-reserved, test, or observation surfaces. Production code should avoid writing undocumented debug or RFU locations unless the ASIC programming guide or existing AMD sequence requires it.

The requested range begins mid-family, after earlier lines have already defined lane 0/1 `CMD_BUS_TX_CONTROL` entries, and it ends with the header's include guard close. The merge lane should treat the beginning split as a chunk boundary artifact rather than a real omission in the source file.

## Test Signals

Useful validation signals are mostly build-time plus display hardware behavior:

- AMDGPU builds for DCE 11.2 paths should compile with all included address macros and no missing/renamed register definitions.
- Static register-map checks can compare every address in this generated header against AMD's source register database and the companion mask/shift header.
- Display mode-set tests should validate that pixel clocks, PPLL post-dividers, and link clocks are correct across common resolutions, refresh rates, and connector types.
- DisplayPort link-training tests should cover one-, two-, and four-lane configurations, multiple transmitter instances, hotplug, retraining, suspend/resume, and low-power transitions.
- HDMI/TMDS output tests should exercise `COMMON_TMDP`, common TX controls, and PHY power/reset sequencing through real connector bring-up.
- PLL status/debug checks should confirm lock/update/status behavior through `PPLL_STATUS_DEBUG*`, `PPLL_DIV_UPDATE_DEBUG`, `OBSERVE*`, and related debug registers when available.
- DPCSTX error-path diagnostics should watch `DPCSTX_REG_ERROR_STATUS` and `DPCSTX_TX_ERROR_STATUS` during link bring-up, retraining, and forced fault scenarios.
- Multi-display tests should be included because the instance tables cover eight COMBOPHY/DPCSTX blocks and three display PLLs; errors can be instance-local and invisible on a single default connector.

Regression symptoms from bad constants include blank displays, failed hotplug recovery, modes rejected or programmed with the wrong clock, link training loops, intermittent flicker, reduced lane count or link rate, failures after suspend/resume, unexpected DPCSTX error status, or debug reads returning values from the wrong transmitter/PLL instance.

## Cross-Chunk Notes

Earlier chunks of `dce_11_2_d.h` define the beginning and middle of the DCE 11.2 display register address namespace, including preceding display controller, PHY, and lane-register families. This chunk closes the COMBOPHY TX/common/PLL, display PPLL, and DPCSTX address tables and then terminates the include guard with `#endif /* DCE_11_2_D_H */`. The final per-file research document should present the whole file as generated AMDGPU register-address metadata rather than algorithmic driver code.
