# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 93608-96300

## Scope

This chunk is a generated AMD NBIO 6.1 register shift/mask header segment for the Synopsys DWC E12MP x4 PHY namespace `DWC_E12MP_PHY_X4_NS_X4_2`. It contains only C preprocessor constants; there are no functions, structs, runtime variables, allocations, locks, branches, loops, or direct MMIO operations in this range.

The slice starts at a boundary fragment: the final three masks for `DWC_E12MP_PHY_X4_NS_X4_2_LANE3_ANA_TX_OVRD_MEAS`. It then defines complete Lane 3 analog TX and RX field layouts through `LANE3_ANA_RX_ATB_VREG`. The rest of the chunk is a large generated run of raw common digital memory entries: complete `RAWCMN_DIG_MEM_CMN2`, `CMN3`, and `CMN4` banks `B0` through `B7`, rows `R0` through `R31`, plus the beginning of `RAWCMN_DIG_MEM_CMN5_B0_R0` through `R12`.

Although this file is located under a local `ceph-client` source mirror, this header is AMDGPU ASIC register metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bitfield positions for NBIO 6.1 PHY registers. Each field follows the generated AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset used when packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate, clear, preserve, or update that field.

The companion address header, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h`, supplies matching register offsets. Runtime AMDGPU code combines offsets from that header with these masks through helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening boundary fragment finishes `LANE3_ANA_TX_OVRD_MEAS` with masks for `pull_up_reg`, `pull_dn_reg`, and the high reserved byte. The corresponding shifts and earlier masks are outside this work item, so adjacent chunks are needed for a complete register-level view of `TX_OVRD_MEAS`.

The complete Lane 3 analog TX sections cover:

- `LANE3_ANA_TX_PWR_OVRD`: override and register bits for loopback, reference generator, clock divider, data path, clock, serial path, and override enable.
- `LANE3_ANA_TX_ALT_BUS`: alternate bus drive source, alternate bus override, oscillator observation fields for `vph`, `vptx`, low-Vt and normal `vp`, plus JTAG data.
- `LANE3_ANA_TX_ATB1` and `LANE3_ANA_TX_ATB2`: analog test bus selectors for ground, DCC rails, TX supply/common-mode nodes, regulator references, RX detect reference, and bias nodes.
- `LANE3_ANA_TX_VBOOST`: VBOOST measurement, reference override, boost enable, and VPTX boost-mode fields.
- `LANE3_ANA_TX_TERM_CODE_DN` and `LANE3_ANA_TX_TERM_CODE_UP`: down/up termination-code override enables and 7-bit termination-code fields.
- `LANE3_ANA_TX_IBOOST_CODE`: LFPS priority, termination-code mirror bits, IBOOST override, and IBOOST code selection.
- `LANE3_ANA_TX_OVRD_CLK`: loopback clock, MPLLA/MPLLB clock, word-clock enable, and associated override fields.
- `LANE3_ANA_TX_MISC`: miscellaneous analog observation bits such as PMOS/NMOS oscillators, ATB bias measurement, and RX-detect reference override.

The complete Lane 3 analog RX sections cover:

- `LANE3_ANA_RX_ATB_IQSKEW`: IQ phase-adjust value, ATB VP/scope measurement enables, and master ATB enable.
- `LANE3_ANA_RX_DCC_OVRD`: data-rate selection, DCC measurement, RX loopback-clock override, DCC/AFE override, and DCC enable fields.
- `LANE3_ANA_RX_PWR_CTRL1` and `LANE3_ANA_RX_PWR_CTRL2`: override/register pairs for ACJT, RX clock, LOS, AFE, DFE, deserializer, and RX loopback enables.
- `LANE3_ANA_RX_ATB_REGREF`, `LANE3_ANA_RX_CDR_AFE`, `LANE3_ANA_RX_CAL_MUXA`, `LANE3_ANA_RX_ATB_MEAS1`, `LANE3_ANA_RX_ATB_MEAS2`, and `LANE3_ANA_RX_CAL_MUXB`: analog test, CDR/AFE phase-detector, calibration mux, DFE tap, and regulator measurement fields.
- `LANE3_ANA_RX_MISC_OVRD`: RX word-clock, LOS/LFPS, short-detect, and override fields.
- `LANE3_ANA_RX_TERM`: RX termination, IQ phase-adjust override, DC/GD termination controls, and reserved low bits.
- `LANE3_ANA_RX_SLC_CTRL` and `LANE3_ANA_RX_ATB_VREG`: slicer control values, slicer-control override, IQC reference override, DFE bypass/regulator measurements, and regulator reference overrides.

The raw common digital memory family is mechanically regular. Every entry in `RAWCMN_DIG_MEM_CMN*_B*_R*` in this chunk defines `DATA__SHIFT` as bit 0 and `DATA_MASK` as `0xFFFFL`, indicating a 16-bit opaque data payload rather than named subfields. Coverage is:

- `RAWCMN_DIG_MEM_CMN2_B0_R0` through `RAWCMN_DIG_MEM_CMN2_B7_R31`: 256 entries.
- `RAWCMN_DIG_MEM_CMN3_B0_R0` through `RAWCMN_DIG_MEM_CMN3_B7_R31`: 256 entries.
- `RAWCMN_DIG_MEM_CMN4_B0_R0` through `RAWCMN_DIG_MEM_CMN4_B7_R31`: 256 entries.
- `RAWCMN_DIG_MEM_CMN5_B0_R0` through `RAWCMN_DIG_MEM_CMN5_B0_R12`: 13 entries before the chunk boundary.

The assigned range contains 24 analog register markers plus 781 raw memory entry markers, with 943 `__SHIFT` definitions and 945 `_MASK` definitions. The two extra masks relative to shifts are explained by the boundary start inside `LANE3_ANA_TX_OVRD_MEAS`.

## Control Flow

There is no executable control flow in this header. Its effect is compile-time: consuming code receives constants for composing or decoding NBIO 6.1 PHY register values.

Typical runtime use follows this pattern:

1. AMDGPU code selects a PHY, NBIO, PCIe, SOC15, or SMN register offset from `nbio_6_1_offset.h`, `nbio_6_1_smn.h`, or related generated headers.
2. The register access layer reads a hardware value or prepares a value to write.
3. Code applies this header's `__SHIFT` and `_MASK` constants directly or through field helpers.
4. The resulting value configures lane analog TX/RX behavior, extracts status/diagnostic fields, sets override bits, selects analog test bus points, or writes opaque raw memory data where supported by the hardware access path.

The Lane 3 analog fields are most relevant to PHY bring-up, PCIe link training and recovery, signal-integrity diagnostics, loopback, calibration, RX detect, termination tuning, clock gating/enablement, and analog test/measurement flows. The raw memory entries represent generated addressable data rows in the common PHY digital memory/register space; this chunk does not define the meaning of individual bits inside those 16-bit payloads.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register fields owned by the GPU PHY, firmware, platform straps, and AMDGPU NBIO/power-management code.

The represented Lane 3 state includes TX loopback and power overrides, data/clock/serial enables, alternate bus and JTAG observation paths, analog test bus selections, VBOOST controls, TX termination and IBOOST tuning, RX DCC/AFE/DFE/deserializer/loopback controls, LOS/LFPS and short-detect behavior, CDR/AFE phase-detector observation, calibration mux selections, RX termination, slicer controls, IQ phase adjustment, and regulator/reference measurement routing. Some fields are software-programmed controls, some are measurement selectors, and some may reflect hardware-owned or firmware-owned calibration state.

The raw common memory state is represented only as 16-bit `DATA` fields. The masks do not specify reset defaults, access permissions, side effects, firmware ownership, row semantics, write ordering, polling rules, or whether entries are persistent across reset, power-gate, suspend/resume, or link retrain events.

## Dependencies And Integration Points

The primary dependency is consistency with the generated NBIO 6.1 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` supplies matching offsets for the `DWC_E12MP_PHY_X4_NS_X4_2` lane and raw memory registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` supplies generated defaults for the same register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` supplies SMN-addressed definitions where applicable.
- AMDGPU register helper macros and SOC15/NBIO accessors consume the generated `__SHIFT`/`_MASK` convention.

Observed direct include sites for this shift/mask header in this source tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/mxgpu_ai.c`, and the Vega powerplay include bundles `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h` and `vega12_inc.h`.

Integration surfaces include NBIO v6.1 initialization, Vega10/Vega12-era power-management policy, PCIe PHY link bring-up, lane-level diagnostics, loopback and RX-detect testing, signal tuning and calibration, suspend/resume or reset recovery, SR-IOV/MxGPU paths that depend on stable PCIe PHY behavior, and hardware debug flows that inspect analog test bus or raw PHY memory rows.

## Risks And Edge Cases

- The chunk boundaries are artificial. The range starts with masks from the tail of `LANE3_ANA_TX_OVRD_MEAS` and ends after `RAWCMN_DIG_MEM_CMN5_B0_R12`, so adjacent chunks are required for complete boundary-register and CMN5 coverage.
- These are untyped preprocessor constants. A stale shift or mask can compile cleanly while programming the wrong PHY bit.
- Lane naming is significant. Applying a `LANE3` mask to a Lane 0/1/2 offset, or applying this `_X4_2` instance's mask to another PHY instance, can create plausible bit operations that affect the wrong physical lane or PHY block.
- Analog override fields can defeat hardware calibration or firmware-controlled sequencing. Incorrect loopback, clock, data, serial, VBOOST, termination, IBOOST, DFE, AFE, deserializer, LOS, or RX termination programming can break link training, degrade signal integrity, hide receive-detect failures, or leave the PHY in a test-only mode.
- Measurement and ATB selectors are diagnostic-facing. Incorrect selector values can produce misleading board or silicon debug readings without causing an obvious software failure.
- Reserved and `NC*` fields appear throughout the analog registers. Generic write patterns should preserve reserved bits unless the hardware specification explicitly allows otherwise.
- The raw memory rows expose opaque 16-bit `DATA` masks. Without the register database semantics, software cannot infer row purpose, side effects, required access order, or whether the data is hardware-, firmware-, or software-owned.
- Generated-header synchronization is critical. Offset/default/mask drift across `nbio_6_1_offset.h`, `nbio_6_1_default.h`, `nbio_6_1_smn.h`, and this file can silently corrupt PHY setup or diagnostics.

## Test Signals

Useful validation is mostly build-time, generated-header, and hardware-integration oriented:

- Build AMDGPU with NBIO 6.1/Vega support enabled; missing, renamed, or duplicated macros should surface in `nbio_v6_1.c`, `mxgpu_ai.c`, `vega10_inc.h`, `vega12_inc.h`, or generated include paths.
- Compare this chunk against `nbio_6_1_offset.h` and `nbio_6_1_default.h` for matching `DWC_E12MP_PHY_X4_NS_X4_2_LANE3_ANA_*` and `RAWCMN_DIG_MEM_CMN*` names, ordering, defaults, and boundaries.
- Verify that all raw memory entries in this range retain the expected `DATA__SHIFT == 0x0` and `DATA_MASK == 0xFFFFL` pattern.
- Boot affected ASICs and run PCIe link bring-up, retraining, reset, suspend/resume, runtime power, and heavy DMA/graphics/compute workloads while monitoring link width/speed stability, correctable/uncorrectable PCIe errors, and recovery from link events.
- Exercise loopback, RX-detect, and PHY diagnostic modes where hardware validation hooks are available; unexpected stuck link states, incorrect LOS/LFPS behavior, or bad RX detect can indicate mask/offset drift.
- Run signal-integrity or lab validation tests that use ATB, calibration mux, VBOOST, termination, IBOOST, DCC/AFE/DFE, slicer, and regulator measurement fields; confirm measurements and tuning responses match the ASIC register database.
- Validate SR-IOV/MxGPU workloads on systems that use this NBIO generation; VF stability under reset and traffic can expose PHY setup mistakes even when the mask header builds cleanly.

## Chunk Notes

- Lines 93608-93610 are a boundary tail for `LANE3_ANA_TX_OVRD_MEAS`.
- Lines 93611-93762 define Lane 3 analog TX override, test bus, VBOOST, termination, IBOOST, clock, and miscellaneous masks.
- Lines 93763-93958 define Lane 3 analog RX IQ skew, DCC, power, ATB/regref, CDR/AFE, calibration, measurement, termination, slicer, and voltage-regulator masks.
- Lines 93959-94724 cover complete `RAWCMN_DIG_MEM_CMN2_B0_R0` through `CMN2_B7_R31` 16-bit data masks.
- Lines 94727-95492 cover complete `RAWCMN_DIG_MEM_CMN3_B0_R0` through `CMN3_B7_R31` 16-bit data masks.
- Lines 95495-96260 cover complete `RAWCMN_DIG_MEM_CMN4_B0_R0` through `CMN4_B7_R31` 16-bit data masks.
- Lines 96263-96300 start `RAWCMN_DIG_MEM_CMN5_B0_R0` through `CMN5_B0_R12`; the remainder of CMN5 continues after this chunk.
