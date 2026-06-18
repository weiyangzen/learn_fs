# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 54035-56403

## Scope And Purpose

This chunk is a generated AMD NBIO 6.1 shift/mask header slice for the `DWC_E12MP_PHY_X4_NS_X4_0` PCIe PHY register space. It does not implement executable logic. Its purpose is to expose compile-time bitfield contracts for driver code that reads, writes, or packs fields in Synopsys DWC E12MP PHY lane, supervisor, PLL, termination, power, calibration, and CDR registers.

The chunk contains 2,115 `#define` macros under 254 register-comment blocks. Each field is represented by a `__SHIFT` macro and a matching `_MASK` macro, using 16-bit register masks such as `0x0001L`, `0x03FFL`, or `0x8000L`. The requested range begins with the tail of `RAWLANE2` RX adaptation status, covers the full `RAWLANE3` lane-facing register block, then transitions through shared `SUPX` supervisor/PLL/RTUNE registers and into generic `LANEX` lane-template registers. The final requested line stops at the shift definitions for `LANEX_DIG_RX_DPLL_FREQ_BOUND_0`; its mask definitions continue just after this chunk.

## Register Families Covered

The first visible entry is `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANE2_DIG_RX_CTL_ADAPT_CONT_STATUS`, a one-bit `ENABLE` status field for lane 2 continuous RX adaptation. The rest of the lane-specific portion focuses on `RAWLANE3`.

`RAWLANE3_DIG_PCS_XF_*` fields describe PCS-facing TX/RX handshakes and overrides. TX registers expose `PSTATE`, low-power detect (`LPD`), width, rate, MPLL select/enable, master MPLL state, override enables, reset/request/detect-RX/vboost/iboost controls, and ACK/status outputs. RX registers similarly expose rate, width, power state, request/reset, AFE/DFE adaptation enables, CDR VCO load and low-frequency override values, LOS threshold override, REF load value, adaptation request/continuous/off-cancel controls, PCS input fields, RX ACK/RESET/LOS output status, adaptation ACK/FOM, and TX pre/main/post direction fields used by link equalization.

`RAWLANE3_DIG_FSM_*` fields describe the lane micro-FSM and fast-path calibration controls. They include global FSM override, memory-address and status monitors, fast RX startup/adaptation/AFE/DFE/bypass/reference-level/IQ calibration fields, fast AFE/DFE adaptation enables, supervisor fast-path signaling, fast TX common-mode and RX-detect paths, fast RX power-up, RX VCO wait/calibration controls, and common-calibration status.

`RAWLANE3_DIG_AON_*` fields are always-on lane state, trim, and adaptation registers. The chunk covers AFE and DFE offset DAC/IDAC controls for ATT, CTLE, VGA, summer, phase, data, bypass, and error slicers; phase adjust linear/map values; MPLLA/MPLLB coarse tune snapshots; RTUNE RX/TX pull-down/TX pull-up values; init power-up completion; RX adaptation ATT/VGA/CTLE/DFE tap values; adaptation done and fast flags; slicer controls; lane common-calibration status; and adaptation-control registers `ADPT_CTL_0` through `ADPT_CTL_7`.

`RAWLANE3_DIG_IRQ_CTL_*` fields describe lane interrupt status, clear, mask, and reset-return request bits for RX reset, RX request, RX rate change, RX power-state change, RX adaptation request, and RX adaptation disable events.

`RAWLANE3_DIG_PMA_XF_*`, `RAWLANE3_DIG_TX_CTL_*`, and `RAWLANE3_DIG_RX_CTL_*` fields bridge the lane PCS/digital logic to PMA and lane control. They include lane/supervisor/TX/RX override inputs and PMA inputs, ACK/REQ/RESET override outputs, lane RTUNE request, TX wait and RX-detect allowance bits by power state, TX clock enable/select, RX control FSM enable, rate-change-in-P1 control, RX LOS mask count, RX data-enable override count, internal reference tracking count, and continuous off-cancel/adaptation status.

`SUPX_DIG_*` and `SUPX_ANA_*` fields cover the shared supervisor and analog side. This includes IDCODE high/low, reference-clock override, MPLLA/MPLLB override and ASIC input registers, supervisor/lane-level override and ASIC input fields, analog MPLL/RTUNE/RX termination override outputs, analog status, MPLLA/MPLLB power-control calibration, override, status, timing thresholds, coarse tune, skip-cal coarse tune, spread-spectrum phase/frequency registers, analog MPLL miscellaneous/override/ATB registers, RTUNE control/status/set/stat registers for RX/TXDN/TXUP, switch power/misc measurement registers, and bandgap control.

`LANEX_DIG_*` fields are lane-template equivalents used for ASIC override/ASIC IO, TX and RX power control, loopback/error test, RX VCO calibration, CDR, and DPLL frequency handling. The chunk covers lane/TX/RX ASIC override and ASIC input/output fields, EQ override inputs and outputs, TX P-state and power-up timing fields, TX LBERT mode, RX P-state and power-up timing fields, RX analog adaptation enable, VCO calibration control/time/status, XAUI comma mask, RX LBERT mode/error count, CDR control/status, DPLL frequency value, and the start of DPLL upper-frequency-bound fields.

## APIs, Types, And Functions

There are no C functions, structs, enums, or runtime APIs in this chunk. The exported interface is entirely preprocessor metadata:

- `DWC_E12MP_PHY_X4_NS_X4_0_*__FIELD__SHIFT` macros for field bit positions.
- `DWC_E12MP_PHY_X4_NS_X4_0_*__FIELD_MASK` macros for field bit masks.
- Reserved-field masks such as `RESERVED_15_13_MASK`, which document unused or reserved bits and help generated tooling preserve the full register layout.

Consumers normally combine these macros with AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD*`, or lower-level read/modify/write paths. The matching address and default-value contracts live in companion headers: `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, and `nbio_6_1_default.h`. In this source tree, `nbio_6_1_sh_mask.h` is included by NBIO runtime code (`amdgpu/nbio_v6_1.c`), SR-IOV mailbox code (`amdgpu/mxgpu_ai.c`), and Vega power-management include aggregators (`pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`).

## Control Flow

This header has no runtime control flow. Its control effect is indirect: register-field helpers expand these constants at compile time to produce masks and shifts for hardware register transactions.

The runtime sequences implied by these fields are hardware protocol sequences. PCS/PMA transfer registers carry request/ack/reset handshakes between digital PCS, PMA, and lane logic. Override fields select whether software/test logic or ASIC/PCS state drives a signal, while paired output/status fields expose acknowledgements or observed analog/digital state. IRQ status/clear/mask fields imply an interrupt sequence of detect, mask or service, clear, and verify. PLL, VCO, CDR, adaptation, and RTUNE fields imply ordered bring-up or tuning flows where control bits are written, status/done bits are polled, and tuning values are retained or observed.

Because the chunk is only a bitfield map, it does not encode ordering, delays, polling timeouts, lock ownership, or access width. Those must be supplied by the consuming NBIO/PCIe PHY initialization, power-management, diagnostics, or virtualization paths.

## State And Persistence Behavior

The persistent state represented here is hardware register state inside the NBIO PCIe PHY. The header itself stores no software state and performs no persistence.

Important state categories include lane power state and rate/width settings, request/reset/ACK handshakes, TX/RX low-power and RX-detect policy, MPLL selection and state, TX boost/current settings, RX AFE/DFE enable and adaptation state, LOS and CDR/VCO calibration state, FOM/equalization direction feedback, lane FSM fast-calibration settings, always-on trim and DFE/AFE calibration values, RTUNE measured/set values, PLL power and spread-spectrum settings, analog status, interrupt pending/clear/mask bits, TX/RX P-state timing tables, LBERT error counts, CDR gain/frequency controls, and DPLL bounds.

Many fields are not merely informational. Override-enable bits and reset/request bits can force PHY behavior away from normal ASIC-driven state. Calibration and tuning values can affect link stability across speed changes and low-power transitions. Status fields such as calibration done, RX VCO up/correct, CDR status, ACK, LOS, and adaptation done are state signals that consumers may poll before progressing.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 6.1 register package remaining internally consistent:

- `nbio_6_1_offset.h` or `nbio_6_1_smn.h` must provide the addresses for these named registers.
- `nbio_6_1_default.h` provides reset/default values for the same register names, including this range's `RAWLANE3`, `SUPX`, and `LANEX` defaults.
- AMDGPU register helper macros must agree with the generated naming scheme: register name, field name, `__SHIFT`, and `_MASK`.
- Consuming code must know whether the target is lane-specific (`RAWLANE3`), shared supervisor (`SUPX`), or generic lane-template (`LANEX`) register space.

Integration points are hardware-facing. The `RAWLANE3` block integrates with PCIe lane initialization, link-speed/rate changes, equalization, RX adaptation, PMA/PCS handshakes, RX-detect behavior, lane interrupts, and debug or bring-up override flows. The `SUPX` block integrates with shared PLL/reference-clock, supervisor, RTUNE, analog measurement, bandgap, and spread-spectrum controls. The `LANEX` block integrates with lane-template power-management tables, VCO/CDR/DPLL calibration, ASIC interface overrides, and LBERT-style test/error monitoring.

## Risks And Edge Cases

Generated shift/mask files are mechanically simple but high risk. A wrong shift or mask can corrupt unrelated hardware fields during read/modify/write, especially because many registers pack independent one-bit enables, multi-bit tuning values, and reserved fields into the same 16-bit register.

The lane naming is easy to misuse. This chunk starts at a `RAWLANE2` tail entry, then defines `RAWLANE3`, later `SUPX`, and finally `LANEX` generic registers. Copying a `RAWLANE3` field into a lane-agnostic path, or confusing `LANEX` template fields with a concrete raw lane, can send software to the wrong register address when combined with companion offset/SMN macros.

Override fields deserve special care. Registers with `OVRD_EN`, `*_OVRD_VAL`, `RESET_OVRD_*`, `REQ_OVRD_*`, VCO/REF load overrides, analog override outputs, and ASIC override inputs can bypass normal hardware sequencing. Writing them during a live link, power transition, or SR-IOV context can cause link retraining failures, lost interrupts, failed ACK handshakes, or unstable calibration.

The requested range ends mid-register at `DWC_E12MP_PHY_X4_NS_X4_0_LANEX_DIG_RX_DPLL_FREQ_BOUND_0`: it includes the `FREQ_BOUND_EN`, `UPPER_FREQ_BOUND`, and `RESERVED_15_11` shift definitions but not the corresponding masks, which appear immediately after line 56403. Any merged per-file research should stitch this boundary to the next chunk before treating DPLL bounds as fully documented.

Reserved masks document bits that should generally be preserved or written according to hardware guidance. Consumer code should avoid constructing full-register literals from only known fields unless defaults and reserved-bit behavior are understood.

## Test Signals

The primary validation signal is build coverage for AMDGPU NBIO 6.1 consumers that include this header and use these generated names with register-field helpers. Because this is a hardware register contract, runtime validation normally comes from hardware, simulator, or bring-up tests rather than unit tests.

Useful test and debug signals include successful PCIe link bring-up and retraining across supported rates and widths, stable low-power P-state transitions, clean TX/RX request/ACK handshakes, expected RX-detect behavior, RX adaptation completion with plausible FOM/equalization values, IRQ status/clear/mask behavior for lane reset/request/rate/pstate/adaptation events, stable MPLLA/MPLLB lock and spread-spectrum behavior, valid RTUNE readings, VCO calibration done/up/correct status, CDR convergence, LBERT error-count behavior, and no regressions in SR-IOV or power-management paths that share NBIO register access.

For static validation, compare this chunk against the matching default and address headers for name coverage, verify that every field has a coherent shift/mask pair except for the intentional chunk boundary at `LANEX_DIG_RX_DPLL_FREQ_BOUND_0`, and run compile checks that exercise generated `REG_SET_FIELD`/`REG_GET_FIELD` expansions for representative PCS/PMA, SUPX, and LANEX fields.
