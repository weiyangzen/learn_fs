# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 4871-7256

## Scope

This chunk is a generated AMD DPCS 4.2.3 offset-header segment. It contains C preprocessor constants only: no functions, structs, enums, storage, or executable logic. The visible range starts in the middle of the `ixDPCSSYS_CR1_RAWAONLANE2_*` always-on raw-lane block at `DIG_RX_DCC_CAL_ICM_CODE_0` and ends in the middle of the `ixDPCSSYS_CR2_SUPX_*` supervisor-X block at `DIG_MPLLB_HDMI_CLK_ASIC_IN`.

The constants are DPCS indexed-control-register addresses. Earlier in the same header, each DPCS CR instance has display MMIO address/data ports such as `regDPCSSYS_CR1_DPCSSYS_CR_ADDR`, `regDPCSSYS_CR1_DPCSSYS_CR_DATA`, `regDPCSSYS_CR2_DPCSSYS_CR_ADDR`, and `regDPCSSYS_CR2_DPCSSYS_CR_DATA`. The `ixDPCSSYS_*` values in this chunk are the 16-bit-style indirect addresses written to those address ports before reading or writing the corresponding data port.

## Purpose

The header provides compile-time register-index metadata for AMDGPU display PHY code on the DCN 3.1.6 / DPCS 4.2.3 path. Driver code pairs these offset macros with companion shift/mask macros from `dpcs_4_2_3_sh_mask.h` and with DC register access helpers to configure DisplayPort/HDMI PHY lanes, power states, PLLs, receiver adaptation, signal detection, calibration, and debug/test paths.

Within this chunk, the main hardware areas are:

- CR1 always-on raw lane 2 tail and lane 3 full blocks, covering RX DCC calibration readback, TX DCC bank access/control, MPLL bandgap control, signal-detect override/readback, firmware mode/adaptation/calibration configuration, lane transceiver-mode inputs, and RX signal-detect/TX DCC configuration.
- CR1 `RAWAONLANEX`, the lane-generic always-on raw-lane template at the `0x7000` index range.
- CR1 `SUPX`, the extended supervisor block at `0x8000` through `0x8096`, covering ID, reference-clock overrides, MPLLA/MPLLB override and spread-spectrum registers, charge-pump controls, ASIC inputs, prescaler/bandgap/level controls, analog PLL controls, RTUNE controls/status, and digital analog override/status outputs.
- CR1 `LANEX`, the lane-generic main lane template at `0x9000` through `0x90ff`, covering ASIC override/input/output interfaces, TX/RX power controls, RX VCO/CDR/DPLL, RX adaptation, RX statistics, MPHY, digital analog override/status, and raw analog TX/RX controls.
- CR1 `RAWLANEX`, the lane-generic raw PCS/PMA/FSM/IRQ/control template at `0xe000` through `0xe0c8`.
- CR2 supervisor, lane, raw common, raw lane, always-on raw lane, lane-generic always-on, and early supervisor-X blocks. CR2 coverage begins at the full `SUP` block and continues through lane 0, lane 1, lane 2, lane 3, raw common, raw lanes 0-3, always-on raw lanes 0-3, `RAWAONLANEX`, and the start of `SUPX`.

## Macro Groups

The chunk's generated macro families and line spans are:

- `ixDPCSSYS_CR1_RAWAONLANE2_*` lines 4871-4891: tail of CR1 raw AON lane 2, from RX DCC calibration codes through TX DCC configuration.
- `ixDPCSSYS_CR1_RAWAONLANE3_*` lines 4892-4973: full CR1 raw AON lane 3, `0x4300` through `0x4351`.
- `ixDPCSSYS_CR1_RAWAONLANEX_*` lines 4974-5055: lane-generic CR1 raw AON template, `0x7000` through `0x7051`.
- `ixDPCSSYS_CR1_SUPX_*` lines 5056-5194: CR1 extended supervisor, `0x8000` through `0x8096`.
- `ixDPCSSYS_CR1_LANEX_*` lines 5195-5397: CR1 lane-generic main lane template, `0x9000` through `0x90ff`.
- `ixDPCSSYS_CR1_RAWLANEX_*` lines 5398-5522: CR1 lane-generic raw lane template, `0xe000` through `0xe0c8`.
- `ixDPCSSYS_CR2_SUP_*` lines 5527-5665: CR2 supervisor, `0x0000` through `0x0096`.
- `ixDPCSSYS_CR2_LANE0_*` lines 5666-5750: partial CR2 lane 0 set, `0x1000` through `0x10ef`; this lane has ASIC/TX-power/statistic/analog-TX coverage in this chunk but not the full RX/control breadth visible for lanes 1 and 2.
- `ixDPCSSYS_CR2_LANE1_*` lines 5751-5953: full CR2 lane 1, `0x1100` through `0x11ff`.
- `ixDPCSSYS_CR2_LANE2_*` lines 5954-6156: full CR2 lane 2, `0x1200` through `0x12ff`.
- `ixDPCSSYS_CR2_LANE3_*` lines 6157-6241: partial CR2 lane 3 set, `0x1300` through `0x13ef`.
- `ixDPCSSYS_CR2_RAWCMN_*` lines 6242-6293: CR2 raw common controls, `0x2000` through `0x2040`.
- `ixDPCSSYS_CR2_RAWLANE0_*` through `ixDPCSSYS_CR2_RAWLANE3_*` lines 6294-6793: four CR2 raw lane PCS/PMA/FSM/IRQ/control blocks at `0x3000`, `0x3100`, `0x3200`, and `0x3300` bases.
- `ixDPCSSYS_CR2_RAWAONLANE0_*` through `ixDPCSSYS_CR2_RAWAONLANE3_*` lines 6794-7121: four CR2 always-on raw-lane blocks at `0x4000`, `0x4100`, `0x4200`, and `0x4300` bases.
- `ixDPCSSYS_CR2_RAWAONLANEX_*` lines 7122-7203: CR2 lane-generic always-on raw-lane template, `0x7000` through `0x7051`.
- `ixDPCSSYS_CR2_SUPX_*` lines 7204-7256: beginning of CR2 extended supervisor, `0x8000` through `0x8035`; the following source lines continue this block.

## Important APIs, Types, And Functions

There are no callable APIs in this chunk. The public interface is the generated macro naming contract:

- `ixDPCSSYS_CRn_SUP_*` and `ixDPCSSYS_CRn_SUPX_*` name supervisor indexed-register addresses.
- `ixDPCSSYS_CRn_LANE0_*` through `ixDPCSSYS_CRn_LANE3_*` name concrete per-lane indexed-register addresses.
- `ixDPCSSYS_CRn_LANEX_*`, `ixDPCSSYS_CRn_RAWLANEX_*`, and `ixDPCSSYS_CRn_RAWAONLANEX_*` name lane-generic template addresses.
- `ixDPCSSYS_CRn_RAWLANE*_*` names raw PCS/PMA/FSM/IRQ/control indexed-register addresses for specific lanes.
- `ixDPCSSYS_CRn_RAWAONLANE*_*` names always-on raw-lane indexed-register addresses for calibration/adaptation/signal-detect/DCC state.

The companion shift/mask header supplies bitfield names for these register groups. This offset header supplies only the register-index side of the address plus field pair.

## Control Flow

This header contributes no runtime control flow. Runtime code includes the header, expands selected macros into register tables, and uses those tables during link encoder and PHY operations.

The implied hardware flows are sequencing-sensitive even though they are not implemented here:

- Supervisor PLL and clock programming through `SUP`/`SUPX` reference-clock, MPLLA/MPLLB, SSC, charge-pump, prescaler, bandgap, and RTUNE indices.
- Lane TX power and DCC setup through `LANE*`/`LANEX` TX power-control, DCC CR-bank, DAC, clock-alignment, and LBERT indices.
- Lane RX power, VCO/CDR/DPLL, adaptation, statistics, and analog status through the `LANE*`/`LANEX` RX control families.
- PCS/PMA handshakes, IRQ masks/status/clear paths, FSM shortcuts, OCLA debug controls, and ATE/test overrides through `RAWLANE*`/`RAWLANEX`.
- Always-on calibration and status readback through `RAWAONLANE*`/`RAWAONLANEX`, including DFE/AFE offsets, IQ phase adjustment, common calibration status, DCC calibration codes, signal detection, firmware configuration, and lane transceiver mode.

## State And Persistence

The macros themselves are stateless compile-time constants. The state they address lives in volatile DPCS PHY hardware behind indirect CR address/data ports. That state is affected by modesets, link training, hotplug handling, PHY power transitions, suspend/resume, reset recovery, diagnostics, and any debug path that writes raw DPCS CR registers.

Several addressed registers are status or latched readback locations: ID registers, calibration-done/status registers, adaptation results, FOM/statistic counters, DCC acknowledgements, signal-detect state, PLL/RTUNE status, ASIC input/output handshakes, and analog status registers. Others are override controls, timing controls, calibration configuration, or raw analog controls. Override state can outlive a single debug operation until explicitly cleared or until hardware reset, so consumers must restore normal ASIC ownership after special sequences.

Because this is an offset header, persistence correctness mostly means preserving the address map. A wrong numeric macro value can send an otherwise valid field write to the wrong DPCS CR register and silently corrupt unrelated PHY state.

## Dependencies

This chunk depends on the AMD ASIC register-generation pipeline and the DPCS 4.2.3 hardware specification staying synchronized. It is normally consumed with:

- `dpcs_4_2_3_sh_mask.h`, which provides the field masks and shifts for these indexed registers.
- The top-level DPCS address/data port definitions in the same file, such as `regDPCSSYS_CR1_DPCSSYS_CR_ADDR`/`DATA` and `regDPCSSYS_CR2_DPCSSYS_CR_ADDR`/`DATA`.
- AMD display register-list macros such as `DPCS_DCN31_REG_LIST` and `DCN3_1_RDPCSTX_REG_LIST`, which build link encoder register tables from generated offsets.
- DCN 3.1.6 resource construction in `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, which includes both `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`.
- Link encoder, HPO DP link encoder, PHY power, link training, and diagnostics code that ultimately uses these DPCS indexed registers through AMDGPU display register helpers.

The file is part of an imported AMDGPU display driver subtree in this repository. It has no direct dependency on Ceph filesystem logic despite the repository path containing `ceph-client`.

## Integration Points

In `dcn316_resource.c`, DPCS 4.2.3 offsets are included with DCN 3.1.6 offsets and masks to populate link encoder and HPO DP link encoder register tables. `DPCS_DCN31_REG_LIST(id)` includes the indexed DPCS CR address/data access registers (`RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA`) along with RDPCSTX PHY controls; HPO DP resource construction also includes `DCN3_1_RDPCSTX_REG_LIST` entries. These tables are the bridge between the generated address constants and runtime link encoder objects.

The chunk's concrete CR1 and CR2 prefixes matter. The same suffix, for example `RAWAONLANE2_DIG_TX_DCC_CONFIG`, can appear under different CR instances with the same index value but a different CR address/data port. Consumers must pair `ixDPCSSYS_CR1_*` indices with CR1 access paths and `ixDPCSSYS_CR2_*` indices with CR2 access paths.

The `LANEX`, `RAWLANEX`, and `RAWAONLANEX` blocks are lane-generic templates. They are useful for generated table patterns and structural validation, but direct programming paths still need to resolve the intended physical lane and CR instance. Concrete lane blocks (`LANE0`-`LANE3`, `RAWLANE0`-`RAWLANE3`, `RAWAONLANE0`-`RAWAONLANE3`) encode the per-lane base increments.

## Risks

- The chunk starts in the middle of `ixDPCSSYS_CR1_RAWAONLANE2_*`; the previous chunk owns the beginning of that always-on lane 2 block.
- The chunk ends in the middle of `ixDPCSSYS_CR2_SUPX_*`; the next chunk owns the remaining CR2 supervisor-X analog and RTUNE/override/status indices.
- Generated address drift compiles cleanly. A wrong `ixDPCSSYS_*` value will not be caught by C type checking and can route a valid field write to the wrong indirect register.
- CR instance mixups are easy because CR1 and CR2 blocks reuse many suffixes and many numeric index ranges. The CR access port and index macro must be kept together.
- Lane mixups are easy because lane blocks are repetitive and often differ only by the `0x100` base increment or by a lane-template `X` prefix.
- Partial lane coverage is asymmetric in this chunk: CR2 lane 0 and lane 3 blocks are shorter than lane 1 and lane 2 in the visible range. Per-file reconciliation should not infer missing lane support solely from this chunk.
- Supervisor PLL, RTUNE, bandgap, power-state, VCO/CDR/DPLL, adaptation, DCC, and raw analog registers are hardware-sequencing sensitive. Incorrect writes can cause failed link training, display blanking, unstable high-rate links, bad signal-detect behavior, or misleading diagnostics.
- Reserved analog registers and undocumented template locations should be treated as hardware-owned unless a validated sequence explicitly writes them.

## Test Signals

Useful validation signals for changes touching this header or its consumers include:

- Kernel build coverage for AMDGPU display code that includes `dpcs_4_2_3_offset.h`, especially DCN 3.1.6 resource and link encoder paths.
- Generated-header consistency checks that compare repeated CR1/CR2 and lane 0-3 blocks for expected base increments and suffix preservation.
- Diff checks against neighboring generated DPCS versions such as `dpcs_4_2_2_offset.h` and `dpcs_4_2_0_offset.h` to distinguish intentional ASIC-version changes from generator drift.
- Static checks that each offset macro used by a field mask has a matching register group in `dpcs_4_2_3_sh_mask.h`.
- Hardware bring-up on DCN 3.1.6/DPCS 4.2.3 devices: boot display, hotplug, modesets, suspend/resume, GPU reset recovery, and multi-monitor operation.
- DisplayPort and HDMI link-training stress across lane counts, link rates, UHBR/HBR modes where applicable, and power-state transitions.
- PHY diagnostics that exercise CR1/CR2 supervisor PLL/RTUNE status, TX DCC programming, RX adaptation/statistic readback, signal-detect calibration, raw PCS/PMA IRQ handling, OCLA/debug controls, and analog status readback.

## Boundary Notes For Merge

The final per-file report should reconcile this chunk with adjacent chunks before making whole-file claims. The first visible CR1 raw AON lane 2 register is `ixDPCSSYS_CR1_RAWAONLANE2_DIG_RX_DCC_CAL_ICM_CODE_0` at `0x423d`, not the start of lane 2. The final visible CR2 `SUPX` register is `ixDPCSSYS_CR2_SUPX_DIG_MPLLB_HDMI_CLK_ASIC_IN` at `0x8035`; immediately following source lines continue `SUPX` with additional ASIC input, analog, RTUNE, and override/status offsets.
