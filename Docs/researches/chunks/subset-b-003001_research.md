# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_6_1_default.h lines 17080-19894

## Scope

This chunk is part of AMDGPU's generated NBIO 6.1 default-register header. The selected range contains `#define ..._DEFAULT` constants for the DesignWare Controller E12MP x4 PCIe PHY (`DWC_E12MP_PHY_X4`) exposed through the NBIO SMN register namespace. It does not define executable code, C types, or callable APIs; its API surface is the macro namespace consumed by NBIO/powerplay code together with the matching `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` register descriptions.

The range starts in the middle of `smnDWC_E12MP_PHY_X4_NS_X4_2_RAWCMNX_DIG_MEM_CMN5` and ends in the lane-1 AON adaptation controls for `smnDWC_E12MP_PHY_X4_NS_X4_3_RAWLANE1`. It should be merged later with adjacent chunks for the full generated file-level view.

## Purpose

These macros encode hardware reset/default values for NBIO 6.1 PCIe PHY common and lane registers. The values are used as authoritative constants for register programming, validation, diagnostics, or generated include completeness in the Vega10/NBIO v6.1 driver stack. They preserve ASIC-specific strap/PHY tuning data in source form rather than deriving it at runtime.

The relevant register families in this chunk are:

- `NS_X4_2_RAWCMNX_DIG_MEM_CMN5` and `CMN6`: 16-bit `DATA` defaults for common-side PHY micro/register memory banks, arranged as bank/register pairs (`B0_R8` through `B6_R31` in this chunk).
- `NS_X4_2_RAWLANEX` and `NS_X4_3_LANE0..LANE3`: per-lane digital and analog defaults for override paths, power-state timing, RX adaptation, TX/RX controls, status counters, PLL calibration, and analog tuning.
- `NS_X4_3_RAWCMN_DIG_MEM_CMN2..CMN6`: common-memory bank defaults for the next x4 PHY instance.
- `NS_X4_3_RAWCMN_DIG_*`: common digital controls for MPLLA/MPLLB bandwidth and spread-spectrum override inputs.
- `NS_X4_3_RAWLANE0` and `RAWLANE1`: raw per-lane PCS/FSM/AON/IRQ/PMA/TX/RX defaults, ending partway through lane 1 AON adaptation controls.

## Important Macro Groups

The common-memory register groups are mostly opaque generated names with a single `DATA` field in `nbio_6_1_sh_mask.h` (`DATA_MASK` is `0xFFFFL`). Their ordering and values matter more than semantic field names in this header. Patterns such as repeated address-like values (`0x00180`, `0x001af`, `0x0078d`) followed by data-like values indicate packed PHY initialization table material for common memory banks.

The named raw common/lane groups have clearer semantics via the corresponding shift/mask header:

- `RAWCMN_DIG_CMN_CTL` and `RAWCMN_DIG_MPLLA/MPLLB_*`: common PHY controls for PLL bandwidth and SSC override inputs. Defaults keep most override enable paths disabled, while bandwidth/SSC control defaults (`0x43`, `0x5000`) encode the reset tuning for both PLLs.
- `RAWLANE*_DIG_PCS_XF_TX_*` and `RAWLANE*_DIG_PCS_XF_RX_*`: PCS cross-function override and PCS input/output registers. RX PCS input masks include rate, width, power state, low-power detect, CDR/VCO, AFE/DFE adaptation enable/request/continuous bits, off-cancel continuous state, and reset. RX equalization fields include attenuation, VGA gain, CTLE boost/pole, DFE tap, adaptation acknowledge, figure-of-merit, and TX preset direction feedback.
- `RAWLANE*_DIG_FSM_*`: fast-path FSM and calibration status defaults for RX startup calibration, AFE/DFE calibration/adaptation, bypass/reference-level/IQ calibration, TX common-mode, RX detect, RX power-up, VCO wait/calibration, and common calibration status.
- `RAWLANE*_DIG_AON_*`: always-on calibration and adaptation storage, including AFE/DFE offset defaults (`0x80` neutral midpoint in many fields), phase adjust, MPLL coarse tune, resistor tune values, initial power-up done, RX adaptation result/status fields, slicer controls, and AON adaptation control registers.
- `RAWLANE0_DIG_IRQ_CTL_*`: reset, RX reset/request/rate/pstate/adaptation IRQ status/clear/mask defaults. The reset return request default is asserted (`0x1`); interrupt status, clear, and mask defaults are otherwise zero in this slice.
- `RAWLANE0_DIG_PMA_XF_*`: PMA lane/support/TX/RX override and input defaults. Lane override in/out defaults are `0x3`, while PMA TX/RX override paths are mostly disabled/zero.
- `RAWLANE0_DIG_TX_CTL_*` and `RAWLANE0_DIG_RX_CTL_*`: TX FSM/clock and RX FSM/LOS/data-enable controls. The TX FSM default `0xDE` enables selected RX-detect allowances and encodes MPLL-off wait timing; TX clock default enables the TX clock. RX LOS mask and RX data-enable override defaults are nonzero tuning constants.

## Control Flow

There is no runtime control flow in this range. At compile time the preprocessor makes these default values available to code that includes `nbio_6_1_default.h`. The observed direct includes are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c`, which also includes the offset, shift/mask, and SMN headers and uses NBIO register macros with `RREG32_*`, `WREG32_*`, and `REG_SET_FIELD` helpers.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/vega10_inc.h`, an aggregate Vega10 include that exposes NBIO default/offset/mask constants to powerplay code.

In normal driver flow, NBIO v6.1 code reads and writes hardware registers through SOC15/SMN access helpers. This chunk supplies constants only; any sequencing, polling, and side effects live in the consumers that use the matching offset/mask/SMN definitions.

## State and Persistence

The macros are immutable compile-time constants. They do not allocate memory, cache state, persist user data, or directly touch hardware. The state they describe is hardware reset/default state for NBIO/PCIe PHY registers. When consumers write these values to hardware, the persisted state is in device registers and is lost or reset according to GPU reset, power management, suspend/resume, or PCIe link reinitialization behavior.

Because many values tune analog/PHY behavior, the source file acts as persistent source-of-truth metadata for ASIC-specific defaults. Any change to a constant can alter link training, PLL behavior, receiver adaptation, power-state transition timing, interrupt masking, or calibration defaults even though this header itself has no executable path.

## Dependencies and Integration Points

This chunk depends on register naming consistency across the NBIO 6.1 generated headers:

- `nbio_6_1_offset.h` and `nbio_6_1_smn.h` provide register addresses/SMN identifiers for the same symbolic register names.
- `nbio_6_1_sh_mask.h` provides field masks and shifts. For the memory-bank registers in this chunk, the common field is typically a 16-bit `DATA` mask. For PCS/FSM/AON/IRQ/PMA/TX/RX controls, the shift/mask header exposes meaningful fields used by register access helpers.
- `nbio_v6_1.c` integrates the header into the AMDGPU NBIO block implementation alongside runtime register access macros.
- `vega10_inc.h` makes the generated defaults available to Vega10 powerplay/hardware-manager code.

The names also overlap conceptually with Display Core PHY/DPCS raw-lane register families (`RAWLANE*_DIG_PCS_XF_*` appears in display encoder headers), but this file's namespace is NBIO/PCIe PHY, not DC link encoder programming.

## Risks

- Generated-header drift: default, offset, SMN, and shift/mask headers must remain synchronized. A renamed or reordered default macro without matching address/mask changes can silently break consumers or diagnostics.
- Opaque memory-bank values: `RAWCMN*_DIG_MEM_CMN*` macros expose only `DATA`; reviewers cannot infer safety from field names. Changes require hardware table provenance or comparison against generated register specs.
- PHY tuning sensitivity: defaults around MPLL bandwidth/SSC, RX adaptation, DFE/CTLE offsets, slicer control, LOS masking, and TX/RX power-state timing can affect PCIe link stability across speeds, lanes, boards, and suspend/resume paths.
- Partial-lane coverage in this chunk: the selected line range ends inside `RAWLANE1_DIG_AON_*`. Per-file analysis must merge adjacent chunks before drawing conclusions about all lanes or the full x4 instance.
- Include bloat/compile coupling: the header is very large and included by low-level driver and powerplay aggregate headers. Macro name collisions or accidental edits can have broad compile impact even when no C code changes.

## Test Signals

Useful validation signals for changes touching this region include:

- Build coverage for AMDGPU with NBIO 6.1/Vega10 paths enabled, catching missing macro names or inconsistent generated headers.
- Static comparison against regenerated `nbio_6_1_default.h`, `nbio_6_1_offset.h`, `nbio_6_1_sh_mask.h`, and `nbio_6_1_smn.h` from the same register database.
- Boot/probe logs on Vega10-class hardware confirming AMDGPU initialization, NBIO setup, and powerplay initialization complete without register access faults.
- PCIe link training and stability checks: negotiated generation/width, retrain events, AER errors, link down/up events, and suspend/resume or GPU reset behavior.
- Stress tests that exercise PCIe traffic and power transitions, including runtime power management, clock gating/light sleep, interrupt delivery, doorbell usage, and high-throughput DMA.
- Hardware diagnostics for PHY calibration/adaptation status where available, especially RX adaptation done/FOM/status fields and IRQ status bits for reset/rate/pstate/adaptation events.
