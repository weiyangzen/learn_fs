# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 39244-41604

## Scope And Purpose

This chunk is a generated AMD NBIO 6.1 shift/mask header slice. It defines bit positions and bit masks for 206 NBIO/PCIe/PHY registers, exporting 2150 preprocessor constants of the form `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. There is no executable C logic here; the purpose is to give AMDGPU code exact field encodings for read-modify-write operations against NBIO PCIe, reset, SMU-facing, clock/power, and DesignWare E12MP PHY registers.

The slice starts in the PCIe performance-counter area, covers PRBS link-test fields, software-reset command/control registers, CPM/RSMU/LNCNT/SMU sideband controls, and then enters the `nbio_pipe_pcs_dwc_e12mp_phy_x4_ns0...` address block. The PHY block dominates the chunk and describes reference-clock override, MPLLA/MPLLB PLL control/status, spread-spectrum clocking, analog override/test controls, resistor tuning, and lane-0 digital TX/RX override, power, VCO, CDR, and adaptation fields. The final line in this chunk is the `DWC_E12MP_PHY_X4_NS_X4_0_LANE0_DIG_RX_ADPTCTL_ADPT_CFG_7` register comment; its fields continue in the next chunk.

## Register Families Covered

The opening PCIe performance block provides field definitions for counter/control registers in several clock domains. `PCIE_PERF_CNTL_SLV_NS_C_CLK` and `PCIE_PERF_CNTL_TXCLK2` expose `EVENT0_SEL`, `EVENT1_SEL`, and upper counter byte fields, while `PCIE_PERF_COUNT0_*` and `PCIE_PERF_COUNT1_*` expose full 32-bit counter fields. `PCIE_PERF_CNTL_EVENT0_PORT_SEL` and `PCIE_PERF_CNTL_EVENT1_PORT_SEL` select which TX, master, slave, and second TX clock-domain ports feed performance events.

The PCIe PRBS block defines link-test control and observation fields. `PCIE_PRBS_CLR`, `PCIE_PRBS_STATUS1`, `PCIE_PRBS_STATUS2`, `PCIE_PRBS_FREERUN`, `PCIE_PRBS_MISC`, `PCIE_PRBS_USER_PATTERN`, `PCIE_PRBS_LO_BITCNT`, `PCIE_PRBS_HI_BITCNT`, and `PCIE_PRBS_ERRCNT_0` through `_15` describe per-lane clear, polarity, lock, bit-count completion, free-run, test-mode, data-rate, checker-mask, user-pattern, total-bit-count, and per-lane error-count fields.

The software-reset block is a dense set of reset orchestration fields. `SWRST_COMMAND_STATUS` reports or commands reconfigure, atomic reset, reset-complete, wait-state, upstream/downstream link reset, config-only reset, PHY calibration reset, and reset type selection. `SWRST_GENERAL_CONTROL` gates reset behavior such as reconfigure/atomic enable, reset period, wait-for-link-up, idle behavior, config transfer mode, PCS bypass, CrossFire lockdown, and SDP reset handling. `SWRST_COMMAND_0` and `_1` encode write-side reset requests for port config, global/calib/core/register/PHY/sticky/config reset categories, PCS lane resets 0-15, AXI and monitor resets, CPM reset, PHY0 reset, and strap-valid. `SWRST_CONTROL_0` through `_6` provide the corresponding auto-trigger enables, write enables, and hold-training controls. `SWRST_EP_COMMAND_0` and `SWRST_EP_CONTROL_0` cover endpoint-specific config-only, hot-reset, link-down, and link-disable reset paths.

The NBIO control and SMU-facing block includes `CPM_CONTROL` for LCLK/TXCLK/refclk clock gating and latency behavior, `SMN_APERTURE_ID_A/B` for SMU/PCS/IOHUB/NBIF aperture identifiers, `RSMU_*` controls for message send, invalid-read/write behavior, power-gating hysteresis, and BIOS timer command/rate fields, plus `LNCNT_*` latency/noise-counter controls, window sizing, quantization thresholds, weights, and accumulated counters. `SMU_INT_PIN_SHARING_PORT_INDICATOR` maps link-management, LTR, and DPC interrupt status by port, while `SMU_PCIE_FENCED1_REG` exposes MP0 PCIe CrossFire lockdown.

The DWC E12MP PHY supervisor digital section starts with IDCODE and reference-clock override fields, then defines MPLLA/MPLLB override and ASIC-input fields. These cover PLL enable bits, refclk dividers, divider clock enables and multipliers, SSC enable/range/fractional controls, bandwidth, lane selection, output enables, and override-enable controls. Supervisor digital status/override-output registers expose analog override selections for MPLLA/MPLLB, resistor tuning, RX termination, MPLL power-control finite-state status, calibration readiness, pclk/output/fbclk state, reset/analog enable state, timing thresholds, coarse tune, skip-cal tune, and SSC phase/frequency programming.

The DWC E12MP PHY supervisor analog section provides low-level analog and test-bus fields for MPLLA/MPLLB, RTUNE, switch power/misc measurement, and bandgap. It includes override bits for enable/calibration/fbclk/reset, vreg measurement selections, ATB selectors, analog power measurement selectors, resistor-tune control and status, RX/TXDN/TXUP tune set values, and matching status fields.

The DWC E12MP lane-0 digital ASIC section maps override and ASIC-driven TX/RX inputs and outputs. It covers lane-level TX/RX enable, reset, rate, power-present, request/ack, electrical idle, beacon, detect RX request/result, PIPE transmit detection, loopback, LFPS, TX deemphasis/swing/margin/common-mode, RX equalization evaluation/control/status, CDR/VCO controls, and corresponding output fields. The repeated `*_OVRD_IN_*` and `*_ASIC_IN_*` groups make it possible to distinguish hardware-driven state from forced override state.

The lane-0 TX/RX power and signal-integrity block defines P-state programming for TX and RX. `TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, and `P2` contain per-state width, divider, swing, deemphasis, PLL selector, elastic-buffer mode, termination, vboost, VREG, and related transmitter power fields. `TX_PWRUP_TIME_*` registers describe power-up, power-down, rate-change, TX receiver-detect, PCLK, termination, reset, and differential-clock timing. RX P-state registers similarly encode LOS threshold, CDR tracking, VCO low-frequency settings, EQ/term behavior, adapt-mode, DFE bypass, VREG, VGA/CTLE/DFE, and continuous-adaptation settings; RX power-up time and control registers set sequencing thresholds and fast lock behavior.

The lane-0 RX calibration and adaptation tail covers VCO calibration control, timing, and status; XAUI comma alignment mask; RX LBERT mode/sync/error count; CDR controls and SSC on/off gain counters; DPLL frequency and bounds; and RX adaptation configuration. The adaptation fields visible in this chunk include ASM iteration counts and waits, CTLE pole override, DFE T1 analog disable, training pattern configuration, CTLE/VGA/ATT/DFE/EYE/TGG enables, DFE thresholds, threshold offset, and CTLE/VGA/ATT adaptation step-size or saturation thresholds.

## APIs, Types, And Functions

This chunk defines no functions, structs, unions, enums, or runtime APIs. Its exported interface is purely preprocessor constants:

- `*_SHIFT` values used to place or extract a field within a register value.
- `*_MASK` values used to preserve, clear, or test the field bits.
- Register and field naming that must match the corresponding NBIO 6.1 offset header and AMDGPU access code.

Consumers normally combine these definitions with AMDGPU register helpers and common field macros, such as read-modify-write helpers, `REG_SET_FIELD`-style packing, or explicit `(value & MASK) >> SHIFT` extraction. The matching offset header supplies register addresses; this header supplies bit semantics.

## Control Flow

There is no direct control flow in the header. It affects runtime behavior only through compile-time substitution of field constants into consuming driver code.

The implied hardware control flows are sequencing-sensitive. A PCIe PRBS flow would program `PCIE_PRBS_MISC`, optionally set `PCIE_PRBS_USER_PATTERN` and bit-count registers, enable/free-run testing, poll lock and bit-count status, then read per-lane error counters and clear state. A software-reset flow would configure `SWRST_GENERAL_CONTROL`, assert specific command bits in `SWRST_COMMAND_*` or endpoint command registers, poll `RESET_COMPLETE`/`WAIT_STATE`, and use `SWRST_CONTROL_*` write-enable/auto-enable bits to constrain which reset domains are affected. A PHY bring-up or power-state flow would program supervisor clocks and MPLL controls, observe MPLL status/calibration fields, apply TX/RX P-state and power-up timers, then validate RX VCO/CDR/adaptation status.

## State And Persistence Behavior

The header itself stores no software state and has no persistence behavior. The state represented by these constants is persistent hardware register state until reset, power-gating, firmware ownership changes, or subsequent driver writes.

Important state categories include performance counter configuration and counts, PRBS test configuration and per-lane error counters, PCIe reset command/status, per-domain reset write-enable and auto-enable state, clock-gating policy and latency, SMN aperture identifiers, RSMU invalid-access and power-gating controls, latency/noise counter windows and accumulators, SMU interrupt-sharing port indicators, PLL and SSC programming, analog override/test-bus selections, resistor-tuning values, lane TX/RX override and ASIC state, P-state programming, power-up timing thresholds, RX VCO calibration results, CDR/DPLL frequency tracking, LBERT counters, and RX adaptation configuration.

Several fields are status or counter fields rather than configuration fields. Examples include `PCIE_PRBS_STATUS*`, `PCIE_PRBS_ERRCNT_*`, `SWRST_COMMAND_STATUS`, MPLL power-control `STAT` registers, RTUNE `*_STAT`, lane ASIC output registers, RX VCO status, RX LBERT error count, CDR status, and DPLL frequency. Consumers should avoid read-modify-writing status-only or reserved fields unless the hardware spec explicitly permits it.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 6.1 register package around it:

- The matching `nbio_6_1_offset.h` constants for register addresses and base indexes.
- Earlier and later chunks of `nbio_6_1_sh_mask.h`; this slice begins mid-register-family and ends at the start of `RX_ADPTCTL_ADPT_CFG_7`.
- AMDGPU SOC15/NBIO register access infrastructure that translates offsets and base indexes into MMIO or indirect register operations.
- Common AMDGPU bitfield helpers used to pack and extract shift/mask-defined fields.
- Hardware/firmware ownership rules for PCIe, SMU, RSMU, and PHY registers.

Integration points are hardware-facing. PCIe diagnostics and bring-up can use the performance and PRBS fields. NBIO reset and link recovery code can use the `SWRST_*` groups. Power-management and clock-gating paths can use `CPM_CONTROL`, RSMU power-gating, BIOS timer, and PLL power-control fields. SMU or management-controller integration can use SMN aperture, interrupt-pin-sharing, and fenced-control fields. PHY initialization, link training, signal-integrity tuning, and low-level debug can use the DWC E12MP supervisor, analog, lane TX/RX, CDR, VCO, LBERT, and adaptation groups.

## Risks And Edge Cases

The main risk is that these constants look mechanically simple while representing destructive hardware controls. A wrong mask, shift, or register pairing can reset the wrong PCIe/PHY domain, hold link training indefinitely, misprogram clock or PLL state, corrupt link signal integrity, or produce misleading diagnostics.

Reserved fields are frequent, especially in 16-bit DWC PHY registers. Driver code should preserve reserved bits during read-modify-write sequences unless the hardware documentation requires a fixed value. This matters in supervisor analog/test-bus registers and lane RX/TX controls, where adjacent bits can control analog enables, calibration overrides, or measurement muxes.

The reset groups have several layers of gating: command bits, auto-trigger enable bits, write-enable bits, endpoint-only controls, reset type bits, and hold-training bits. Consumers must distinguish command/status fields from enable/write-enable fields; setting a command without the expected enable or clearing write-enable state can lead to partial resets or timeout-prone flows.

The PHY block uses both override and ASIC-driven inputs. Forcing an override without later restoring ASIC ownership can leave TX/RX lanes in nonstandard power, rate, equalization, or reset states. Conversely, reading an override-output or ASIC-output field as if it were the effective lane state can hide which source currently owns the signal.

The PRBS and LBERT fields are diagnostic/test-oriented. Enabling them on a live link or with the wrong data-rate/test-mode/polarity/user-pattern settings can disrupt normal traffic or create false error signals. Error counters span 16 lanes and 32-bit counters, while some status fields are 16-bit masks; code must handle lane indexing and counter lifetime consistently.

The chunk boundary cuts off immediately after the `RX_ADPTCTL_ADPT_CFG_7` comment. Any merged analysis or consumer lookup must include the following chunk for that register's fields and for the rest of the lane RX adaptation/analog section.

## Test Signals

The header is validated mostly through build coverage plus hardware, emulator, or lab validation:

- Compile coverage for AMDGPU NBIO 6.1 code that includes `nbio_6_1_sh_mask.h` and references these field names.
- Static or generated-header checks that each `_MASK` aligns with its paired `_SHIFT` and expected field width, especially for repeated `SWRST_*`, `PCIE_PRBS_ERRCNT_*`, MPLLA/MPLLB, and lane P-state groups.
- PCIe performance-counter tests that select event ports, read counter low/upper fields, and confirm monotonic or expected event counts.
- PRBS/LBERT diagnostics that enable a controlled test mode, observe lock/sync, verify bit-count completion, and confirm lane error counters increment or stay zero as expected.
- Reset and link-recovery tests that exercise hot-reset, link-down, link-disable, config-only, PHY calibration, and full reset flows while polling `RESET_COMPLETE` and checking link retraining.
- Clock/power tests that verify CPM clock-gating latency controls, RSMU power-gating hysteresis, BIOS timer behavior, and LNCNT accumulation.
- PHY bring-up logs or hardware tests that confirm MPLLA/MPLLB calibration readiness, PLL status, SSC programming, RTUNE results, TX/RX P-state transitions, RX VCO calibration, CDR/DPLL tracking, and adaptation convergence.

Merged per-file research should connect this bitfield slice with the adjacent offset-header chunk and the following shift/mask chunk so consumers see both register addresses and complete field definitions.
