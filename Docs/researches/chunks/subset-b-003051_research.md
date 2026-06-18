# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 113663-116035

## Scope

This chunk is part of AMDGPU's generated NBIO 6.1 register bitfield mask header. It contains only C preprocessor constants for register-field shifts and masks; there are no functions, structs, runtime branches, or storage objects in this range.

The covered lines finish part of the `DWC_E12MP_PHY_X4_NS_X4_3_LANE2` PCIe PHY register definitions and then move into a large `LANE3` block. The source names indicate Synopsys/DWC E12MP x4 PHY lane registers for NBIO/PCIe. The chunk begins at lane 2 RX adaptation/status and analog override/status fields, crosses into lane 3 ASIC-side TX/RX override and normal input/output fields, then covers lane 3 TX/RX power control, RX VCO calibration, CDR/DPLL, RX adaptation/statistics, digital-to-analog override/status fields, and the start of lane 3 analog TX override/tuning fields.

## Purpose

The purpose of this section is to provide exact bit encodings for low-level PCIe PHY lane registers so AMDGPU code can read, set, clear, and poll individual hardware fields without embedding numeric bit positions in driver logic. The definitions are paired with address/default headers in the same generated NBIO family; this file supplies `__SHIFT` and `_MASK` macros for fields in those registers.

The macros describe hardware surfaces used for link bring-up, lane power sequencing, RX/TX analog enablement, VCO calibration, CDR/DPLL setup, RX adaptation and equalization, link BERT/test support, ASIC-to-PHY handshakes, and analog test/override controls. The values are static compile-time metadata, while the actual state lives in NBIO/PCIe PHY registers on the GPU.

## Important Definitions

The generated naming convention is consistent throughout the chunk:

- `DWC_E12MP_PHY_X4_NS_X4_3_<lane>_<block>_<register>__<field>__SHIFT` gives the field's least significant bit.
- `DWC_E12MP_PHY_X4_NS_X4_3_<lane>_<block>_<register>__<field>_MASK` gives the pre-shifted bit mask.
- Most registers are 16-bit field layouts, with masks commonly ending in `L` and using low-halfword ranges such as `0xFFFFL`, `0x00FFL`, or `0xF000L`.
- `RESERVED_*` fields are generated alongside functional fields, which lets comparisons and full-register descriptions remain complete but also highlights bits driver code should generally not modify.

Major register groups visible in this chunk:

- Lane 2 RX adaptation tail: `DIG_RX_ADPTCTL_RX_SLICER_CTRL_ODD`, DFE error/bypass VDAC offsets, error slicer levels, RX statistic load/data/match/control/counter registers, and analog TX/RX override/status blocks.
- Lane 2 digital analog output/status: `DIG_ANA_TX_OVRD_OUT`, TX termination/equalization override outputs, RX control/power/VCO override outputs, RX calibration/DAC/AFE/scope/slicer/IQ/calibration signal controls, and `DIG_ANA_STATUS_0/1`.
- Lane 2 analog controls: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_VBOOST`, TX termination code up/down, TX iboost/clock/misc, plus RX ATB/DCC/power/CDR/calibration/termination/slicer/VREG controls.
- Lane 3 ASIC handoff: `DIG_ASIC_LANE_OVRD_IN`, TX/RX override input/output registers, ASIC input/output registers, RX EQ and RX CDR/VCO ASIC inputs. These fields model reset, clock, rate, pstate, PLL, data-enable, adaptation, margining, and figure-of-merit handshakes between the GPU ASIC logic and the PHY lane.
- Lane 3 TX power control: `DIG_TX_PWRCTL_TX_PSTATE_P0`, `P0S`, `P1`, `P2`, and TX power-up timing registers. Fields include TX analog enable bits, serial/data/clock enable bits, boost, driver and IB boost settings, common-mode and VREG controls, and per-state timing.
- Lane 3 RX power control: `DIG_RX_PWRCTL_RX_PSTATE_P0`, `P0S`, `P1`, `P2`, RX power-up timing registers, and `RX_PWRUP_CTL_0`. Fields include LOS, AFE, clock regulator, DCC, deserializer, CDR, VCO reset/calibration, continuous calibration, and digital clock enables.
- Lane 3 VCO/CDR/DPLL: `DIG_RX_VCOCAL_RX_VCO_CAL_CTRL_0/1/2`, calibration timing/status registers, `DIG_RX_CDR_CDR_CTL_0..4`, `DIG_RX_CDR_STAT`, `DIG_RX_DPLL_FREQ`, and DPLL frequency bounds. These expose calibration method, FSM behavior, calibration delay/count fields, status flags, CDR enable/track/lock controls, and DPLL frequency limits.
- Lane 3 adaptation and statistics: `DIG_RX_ADPTCTL_ADPT_CFG_0..9`, reset adaptation config, ATT/VGA/CTLE/DFE tap status registers, slicer and VDAC offsets, pattern matching controls, statistic counter enables, sample counters, and match/mask controls.
- Lane 3 digital analog override/status: `DIG_ANA_TX_OVRD_OUT`, TX termination/equalization outputs, RX control/power/VCO override outputs, RX calibration/DAC/AFE/scope/slicer/IQ controls, analog status bits, and VCO counter status.
- Lane 3 analog TX start: `ANA_TX_OVRD_MEAS`, `ANA_TX_PWR_OVRD`, `ANA_TX_ALT_BUS`, `ANA_TX_ATB1/2`, `ANA_TX_VBOOST`, TX termination code up/down, `ANA_TX_IBOOST_CODE`, and the start of `ANA_TX_OVRD_CLK`.

Representative field semantics include:

- Enable and reset bits: `*_ANA_*_EN`, `*_DIG_CLK_EN`, `*_VCO_FREQ_RST`, `*_VCO_CAL_RST`, `RX_PWRUP_CTL`, `PHY_RESET`, `RESET_N`, and `RESET_ACK`.
- Calibration/status bits: `VCO_CAL_DONE`, `VCO_CAL_FAIL`, `VCO_CAL_CODE`, `VCO_CNTR`, `ASM1_DONE`, adaptation tap status, sample counter done flags, and analog status fields such as LOS/calibration/loopback indicators.
- Link/power-state fields: `PSTATE`, `RATE`, `WIDTH`, `POWER_STATE`, `TX_PSTATE_*`, `RX_PSTATE_*`, and per-state RX/TX power-up timing values.
- Adaptation/equalization fields: ATT, VGA, CTLE, DFE tap values, DFE error/bypass/data VDAC offsets, slicer controls, RX adaptation enable/configuration, and TX pre/main/post cursor controls.
- Test and diagnostic controls: LBERT controls/errors, RX statistic pattern matching, data masks, sample/stat counters, ATB measurement controls, JTAG/alternate bus fields, and analog measurement mux/override fields.

## Control Flow

There is no executable control flow in this header chunk. The control behavior is indirect and occurs wherever AMDGPU code includes `nbio_6_1_sh_mask.h` and uses these masks with register access helpers.

The typical use pattern is:

1. Driver code selects a register address from the generated NBIO register address headers.
2. It reads the current register value through an MMIO/SMN/PCIe register accessor.
3. It extracts a field by applying the generated `_MASK` and `__SHIFT`, or clears and sets a field when programming hardware.
4. It writes the new value back or polls status fields until a hardware condition changes.

For this chunk, likely flows include programming lane 3 RX/TX power states during PCIe link bring-up or low-power transitions, sequencing RX VCO calibration and CDR/DPLL lock behavior, collecting RX adaptation/statistical diagnostics, and applying temporary PHY override paths for debug, reset, or calibration sequences. The lane 2 definitions in this range are mostly the tail of similar RX/analog diagnostics and override surfaces.

## State And Persistence

The macros themselves have no runtime state, persistence, allocation, locking, or error handling. They are compile-time constants emitted into any object that includes the header.

The state represented by these constants is hardware state:

- Per-lane transient state in lane 2 and lane 3 PHY registers, including RX adaptation results, status counters, VCO/CDR status, IRQ/handshake-style bits, analog enablement, and power-state controls.
- Configuration state that may be initialized by hardware straps, firmware, PSP/SMU setup, BIOS tables, or earlier driver sequences before these fields are read or overridden.
- Reset-sensitive state that may be lost across GPU reset, BACO, suspend/resume, PCIe retraining, or PHY power-gating events unless higher-level AMDGPU code restores it.

Persistence semantics therefore depend on the hardware power/reset domain and the AMDGPU NBIO/PCIe resume/reset paths. This header only describes where fields are located.

## Dependencies And Integration Points

Direct dependency is the C preprocessor. Functional integration depends on the rest of the AMDGPU generated register stack:

- Register address headers such as `nbio_6_1_offset.h` or related `smn*`/`mm*` address definitions identify the register locations.
- Default-value headers such as `nbio_6_1_default.h` provide reset/default values for some of the same registers.
- AMDGPU NBIO and virtualization code includes this header directly; source search shows inclusion from `amdgpu/nbio_v6_1.c`, `amdgpu/mxgpu_ai.c`, and PowerPlay Vega include aggregators.
- Register helper macros in AMDGPU conventionally combine register names, field names, `__SHIFT`, and `_MASK` definitions for `REG_GET_FIELD`, `REG_SET_FIELD`, and read-modify-write flows.
- The definitions are part of the Linux DRM AMDGPU driver surface under a Ceph client source snapshot; they are not Ceph filesystem logic despite the repository path prefix.

This chunk should be reconciled with adjacent chunks for the same generated file. The line interval starts mid-lane-2 and ends mid-lane-3 analog TX clock definitions, so the final per-file report needs neighboring chunks to describe the complete lane 2 and lane 3 register families.

## Risks

- Any mismatch between a generated mask/shift and the ASIC register specification can cause silent misprogramming of PCIe PHY hardware. In this region that could affect link training, power-state transitions, RX adaptation, CDR lock, VCO calibration, or analog test paths.
- Repeated lane definitions are vulnerable to copy/generation drift. Lane 3 should usually mirror lane 2 and other lanes for equivalent register groups, but hardware-specific exceptions must come from the register database rather than manual edits.
- Reserved fields are exposed as masks. Driver code should avoid writing arbitrary values into `RESERVED_*` fields because read-modify-write mistakes may toggle undocumented hardware behavior.
- Override fields are high risk. Bits named `OVRD`, `override`, `*_reg`, `PHY_RESET`, clock enable, VCO reset, DCC enable, and analog test bus controls can bypass normal link-training ownership and leave the PHY in an unusable state if written out of sequence.
- Status/clear semantics are not visible from the names alone. Fields used as done/fail/latch/clear bits may require write-one-to-clear, pulse, or polling behavior that generic helper use cannot infer.
- Generated headers can produce large, review-hostile diffs. Manual editing of this file should be avoided; validation should compare regenerated output against the authoritative ASIC register source.

## Test Signals

Useful validation signals for changes touching this chunk:

- Build AMDGPU with NBIO 6.1/Vega-era support enabled to catch missing, renamed, or malformed macros.
- Compare the generated header against the authoritative AMD register database for NBIO 6.1, especially lane 2/lane 3 symmetry and reserved-bit layouts.
- Search for field-helper use of touched names to ensure any renamed field still matches `REG_GET_FIELD`/`REG_SET_FIELD` expectations.
- Hardware smoke test on affected ASICs should cover PCIe link bring-up, link speed/width changes, ASPM or power-management transitions, suspend/resume, GPU reset, and virtualization paths if SR-IOV/MxGPU uses the same NBIO definitions.
- Watch kernel logs for PCIe AER errors, link retraining loops, AMDGPU timeout/reset messages, CDR/VCO calibration failures, or unexpected link width/speed downgrades.
- Diagnostic validation can poll representative status fields such as VCO calibration done/fail, CDR lock/status, RX adaptation tap status, RX statistic sample-done bits, and analog LOS/calibration status after normal link initialization.
