# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_sh_mask.h lines 61666-64082

## Scope

This chunk is a generated AMD NBIO 6.1 register shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, enums, variables, branches, loops, allocations, locks, direct MMIO reads, or direct MMIO writes in this line range.

The assigned range starts with the final mask line for `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANEX_DIG_AON_RX_IQ_PHASE_ADJUST`, then covers raw-lane always-on PHY fields, IRQ control bits, PMA transfer/control fields, PCS/KPX/KPNP reset and lane-map fields, PCIe x16 PCS global/lane/equalization controls, and finally begins the next DWC E12MP PHY X4 instance (`X4_1`) through `DWC_E12MP_PHY_X4_NS_X4_1_SUP_DIG_ANA_RX_TERM_OVRD_OUT`. The chunk boundary is artificial: the first register started in the previous chunk, and the final register continues after line 64082.

Although this file lives below `distributed-fs/ceph-client`, it is AMDGPU hardware register metadata, not Ceph or filesystem logic.

## Purpose

`nbio_6_1_sh_mask.h` publishes the bit positions and masks used to compose, preserve, clear, and decode NBIO 6.1 hardware register fields. This chunk focuses on low-level PCIe PHY/PCS programming: lane adaptation, DFE/CTLE values, PHY/PMA reset handshakes, link/lane mapping, PCS capabilities and indirect apertures, per-lane FIFO/KP fabric controls, PRBS/BERT diagnostics, PCIe x16 lane controls, equalization coefficients for lanes 0-15 at multiple generations, and PLL/reference-clock controls for the next PHY X4 slice.

Each field normally appears as:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the bit mask for that field.

Consumers pair these definitions with register offsets from `nbio_6_1_offset.h`, reset/default values from `nbio_6_1_default.h`, and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15`.

## Important Macro Families

The opening `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANEX_DIG_AON_*` family describes always-on raw-lane PHY state for X4 slice 0. It includes MPLLA/MPLLB coarse tune fields, RX/TX resistor tuning readbacks, initial power-up done, RX adaptation values for attenuation, VGA, CTLE boost/pole, DFE taps 1-5, adaptation done, fast startup/adaptation/calibration flags, even/odd slicer controls, lane common-calibration status, and eight generic `ADPT_CTL_n` 16-bit values. These are analog/PHY calibration and adaptation fields rather than ordinary PCI config fields.

The `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANEX_DIG_IRQ_CTL_*` family defines one-bit request/status/clear/mask fields for reset return, RX reset, RX request, RX rate, RX P-state, RX adaptation request, and RX adaptation disable events. `IRQ_MASK` contains independent mask bits for the same event classes. These fields are hardware protocol state; the macros do not encode whether a status bit is sticky, write-one-to-clear, or level-triggered.

The `DWC_E12MP_PHY_X4_NS_X4_0_RAWLANEX_DIG_PMA_XF_*`, `TX_CTL_*`, and `RX_CTL_*` groups bridge between digital raw-lane logic and PMA/PHY signals. They define lane-request, PMA reset, P-state, rate, RX/TX request, lane power-present, TX common-mode, TX Vboost, RX termination, CDR tracking, signal-detect, TX/RX FSM control, TX clock control, LOS mask control, RX data enable override, offset-cancellation status, and adaptation-control status fields.

The `addressBlock: nbio_pipe_pcs_lcu_pcie_pcs_prime_phyx4_pcs_prime_dir` section defines prime PCS/LCU metadata and control. `DXIO_HWDID` reports instance and hardware version identifiers; `DXIO_LINKAGE_*` fields identify associated lane groups, muxes, FIFOs, and protocol/native PHY links; `PCS_LANEGRP0_MAPPING` through `PCS_LANEGRP7_MAPPING` describe lane shifts, target mux positions, and lane connection masks; `MAC_CAPABILITIES*` and `PCS_CAPABILITIES` expose lane/engine counts; `PCS_EXTENDED_CAP` and `PCS_APERTURE*_LOC/IDX` describe PCS capability chaining and indirect aperture layout.

The PCS/KPX reset and power section includes `DXIO_CFG_SOFT_RESET`, `KPX_LANE_DATA_SOFT_RESET`, `KPX_LANE_DATA_SOFT_RESET1`, `KPX_PMA_INFO_SOFT_RESET`, `PCS_PRIME_PHYX4_PCS_PMA_SOFT_RESET`, `PCS_SOFT_RESET`, `PCS_LCU_CNTL`, and `PCS_PIPE_PER_LANE_SOFT_RESET`. These macros provide per-debug-channel reset bits, per-lane serdes reset bits for lanes 0-37, per-PMA reset bits, per-PHY soft reset bits, global PCS reset, PCS LCU clock/power gating and SMU IDs, and per-pipe-lane reset bits for lanes 0-15.

The `addressBlock: nbio_lcu_kpfifo_kpfifo0_kpfifo_dir` section exposes KPFIFO0 primary TX FIFO metadata and controls. `KPFIFO0_PRI_TX_FIFO_HSCID` provides hardware revision/version fields. `KPFIFO0_PRI_TX_FIFO_CONTROL_LANE_0` through `_LANE_3` define link ID, FIFO read-pointer offset, FIFO depth, FIFO bypass, FIFO init mode, standalone mode, and hardware-debug flags. `KPFIFO0_PCS_PMA_SOFT_RESET` provides one-bit PCS/PMA reset control.

The `addressBlock: nbio_lcu_kpnp_kpnp0_kpnp_dir` section covers KPNP SNPS0 PHY interface state. It includes hardware schema version, PHY/lane counts and flags, lane ID, lane-request control/status handshakes, PMA control words, PHY/lane soft reset fields, and reset-control state. These fields are another integration layer between PCS/KP fabric and the PHY.

The `addressBlock: nbio_pipe_pcs_pcs_core0_dir` section defines PCIe x16 PCS core controls. `PCS_PCIEX16_GLOBAL_CONTROL0` through `GLOBAL_CONTROL17` include mode/rate selection, symbol alignment, elastic FIFO thresholds, low-frequency and coarse-frequency checks, PRBS generation/checking controls and status, user PRBS pattern and bit/error counters, BERT controls, 8b/10b error accumulation settings, and related diagnostic/status fields. `PCS_PCIEX16_LANE0_CONTROL` through `LANE15_CONTROL` repeat logical link number, master PLL mask, PCLK gating, and LFPS polarity fields per lane.

The `addressBlock: nbio_pipe_pcs_pcs_pciex16_gaskt_pcs_pciex16_gaskt_dir` section defines a gasket layer around the PCIe x16 PCS. `PCS_GLOBAL_CONTROL17` through `GLOBAL_CONTROL30` cover reference-clock ranges and dividers, MPLLA/MPLLB multipliers, bandwidth, div8/div10/refclk-div2/force-enable settings, TX boost and CDR/termination settings, RX adaptation controls, SKP/symbol behavior, TX common-mode and reset controls, and PCIe/USB-oriented tuning fields. `PCS_STATUS1` reports status bits including rate, PLL, and RX activity signals.

The `PCS_LANE0_CNTRL1` through `PCS_LANE15_CNTRL1` families define per-lane control bits. The `PCS_LANE0_COEFF1` through `PCS_LANE15_COEFF3` families then define per-lane equalization coefficient fields for Gen1, Gen2, and Gen3: TX precursor, main cursor, postcursor, RX CTLE boost, and RX CTLE pole. The repetition is significant because each lane and generation has a distinct macro namespace even though the field positions are consistent.

The final `addressBlock: nbio_pipe_pcs_dwc_e12mp_phy_x4_ns1...` section starts PHY X4 slice 1. It covers ID code low/high, reference-clock override inputs, MPLLA/MPLLB override inputs, supervisor override inputs/outputs, level override inputs, ASIC-input controls for PLL/refclk/reset/rtune/res handshakes, analog MPLLA/MPLLB override outputs, and analog RTUNE override output. The last visible block, `DWC_E12MP_PHY_X4_NS_X4_1_SUP_DIG_ANA_RX_TERM_OVRD_OUT`, begins at line 64080 and continues outside this chunk.

## APIs, Types, And Functions

There are no C APIs, types, or functions in this chunk. The exported interface is the preprocessor macro namespace for generated NBIO 6.1 register fields.

The visible in-tree direct include for this header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`. That file uses the generated NBIO register model through SOC15 accessors and field helpers for revision ID, memory size, doorbells, HDP flush registers, interrupts, and PCIe/NBIO setup. The exact low-level PHY/PCS field names in this chunk are not obviously referenced by normal C call sites in the scanned tree; they are still part of the generated ASIC register ABI and may be used by firmware-facing paths, debug tools, future code, or out-of-tree bring-up logic.

## Control Flow

This header has no executable control flow. Runtime behavior is supplied by including driver code and by the hardware state machines described by the fields:

1. Driver, firmware, or debug code selects a register offset from the matching NBIO 6.1 offset header.
2. It reads a register value from the NBIO/PCS/PHY aperture or writes a composed value through SOC15/MMIO/SMN accessors.
3. It uses the `__SHIFT` and `_MASK` constants directly or indirectly through field helper macros to isolate or set a field.
4. Hardware state machines then handle PHY calibration, reset handshakes, PRBS/BERT diagnostics, lane mapping, equalization, PLL/reference-clock state, lane power/rate transitions, or interrupt/status updates.

For this chunk, the implicit workflows are PHY initialization and calibration, RX adaptation, link/lane reset and power sequencing, PCIe x16 PCS setup, per-lane equalization programming, PHY/PCS diagnostic test modes, and interrupt/status clear or mask operations.

## State And Persistence Behavior

The header itself stores no software state and persists nothing. It describes hardware-backed state in NBIO, PCS, KPFIFO/KPNP, and DWC E12MP PHY blocks.

The represented state includes calibration readbacks, tuning controls, power-up done bits, adaptation done bits, DFE/CTLE/slicer values, fast-calibration bypass flags, lane/PMA/PHY reset bits, IRQ status/clear/mask bits, PMA transfer override inputs and outputs, PCS capability and aperture metadata, lane-group mappings, FIFO depth/mode settings, KPNP lane request/status, PCIe x16 PCS PRBS/BERT counters and lock/error status, global PCS frequency/error/FIFO thresholds, per-lane control state, per-generation equalization coefficients, and supervisor/ASIC/analog PLL/refclk/RTUNE controls for PHY X4 slice 1.

Some fields are static capabilities or hardware revision IDs. Others are software-programmed controls, hardware-updated status, clear-on-write event state, or analog calibration values that only make sense while the PHY is in a particular power/rate/training phase. Reset defaults are not encoded here; the companion `nbio_6_1_default.h` carries defaults for many of the same register names, including nonzero defaults for selected RX IQ/slicer/DFE values, PCIe x16 global controls, and lane coefficient registers.

## Dependencies And Integration Points

The immediate dependencies are the C preprocessor and AMD's generated register naming convention. Correct use also depends on:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_offset.h` for matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h` for reset/default values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_smn.h` and the wider SOC15 register-access layer for address translation and access paths.
- AMDGPU field and MMIO helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and `WREG32_FIELD15`.

Functional integration points are PCIe link bring-up, ASIC initialization, firmware-assisted PHY programming, runtime power management, suspend/resume, reset recovery, lane training/equalization, SR-IOV or multi-function PCIe behavior when lane state is virtualized or partitioned, diagnostic PRBS/BERT tests, and low-level debug or manufacturing validation paths. Because these are generated low-level PHY/PCS fields, the normal driver may rely on firmware defaults for many values and only touch a small subset directly.

## Risks And Edge Cases

- Chunk boundaries are partial. The first line completes a register started earlier, and the last block begins `ANA_RX_TERM_OVRD_OUT` without showing its masks.
- The macros are untyped integer constants. A wrong shift or mask can compile cleanly while programming the wrong analog, reset, lane, or diagnostic bit.
- This range has dense repetition across lanes 0-15, DFE taps, FIFO lanes, lane reset bits, and coefficient generations. Generation drift or off-by-one suffix errors are easy to miss by visual review.
- PHY and PCS fields are timing-sensitive. Changing reset, PLL, refclk, rate, P-state, CDR, termination, TX boost, or RX adaptation fields in the wrong order can break link training or leave hardware stuck until a broader reset.
- IRQ status, clear, and mask fields may have side effects not visible in the macro names. Generic read/modify/write can lose latched diagnostic state or fail to clear an asserted condition if the hardware uses write-one-to-clear semantics.
- Equalization coefficients and CTLE/DFE fields directly influence signal integrity. Bad values may only appear as intermittent link errors, retraining, bandwidth drops, or platform-specific failures.
- PRBS and BERT fields are diagnostic controls. Leaving generators/checkers enabled or selecting the wrong lane/rate can disturb normal traffic or produce misleading error counters.
- PCS aperture and lane-group mapping fields define access and muxing topology. Mismatched offsets, lane groups, or target mux positions can make later register access or lane association wrong even when bit arithmetic is correct.
- The slice naming (`X4_0`, `X4_1`) matters. Applying macros from one PHY slice to another slice's offset family can target plausible but incorrect hardware state.

## Test Signals

Useful validation is mostly generated-header consistency plus hardware or simulation testing:

- Build AMDGPU configurations that include NBIO 6.1 headers to catch missing, renamed, or malformed macros.
- Compare this chunk against `nbio_6_1_offset.h` and `nbio_6_1_default.h` to confirm register names, address-block transitions, defaults, and field widths remain synchronized.
- On matching hardware or emulation, exercise PCIe link bring-up, retraining, suspend/resume, and reset recovery while watching link speed/width, lane training, RX adaptation done, power-up done, and IRQ status/clear behavior.
- Run PRBS/BERT or PHY diagnostic procedures, where available, to validate lane selection, lock/error counters, user patterns, bit-count completion, and clear/mask fields.
- Validate per-lane equalization and coefficient programming across lanes 0-15 and Gen1/Gen2/Gen3 against expected link stability and error counters.
- Exercise PHY/PCS reset paths, including per-lane serdes reset, per-PMA reset, per-PHY soft reset, PCS soft reset, pipe-lane reset, and PMA/PCS reset handshake fields.
- Check lane mapping and PCS aperture metadata with any low-level debug tools that traverse PCS indirect apertures or lane group muxing.
- For any code that touches these fields, add readback checks around masks and shifts so programmed values are observed in the expected bit positions without altering reserved bits.

## Chunk Notes

- Lines 61666-62019 finish raw-lane X4_0 AON, IRQ, PMA transfer, TX/RX control, and adaptation status fields.
- Lines 62020-62366 cover PCS prime, lane-group mapping, PCS apertures, KPX/PMA/PCS resets, PCS LCU control, and pipe-lane reset fields.
- Lines 62367-62585 cover KPFIFO0 and KPNP0 lane/FIFO/PHY request and reset controls.
- Lines 62586-62967 cover PCIe x16 PCS core global controls, PRBS/BERT diagnostics, and per-lane control fields.
- Lines 62968-63771 cover PCIe x16 gasket controls, status, per-lane controls, and per-lane Gen1/Gen2/Gen3 coefficient fields.
- Lines 63772-64082 begin the next DWC E12MP PHY X4 slice (`X4_1`) supervisor, PLL/refclk, ASIC input, and analog override fields.
