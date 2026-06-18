# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_offset.h lines 9643-11969

## Scope

This chunk is the final segment of the generated AMD DPCS 4.2.3 register-offset header. It covers lines 9643-11969, contains 2,320 `#define` entries, and ends at the file's closing `#endif`. The selected range exports numeric indirect-register offsets only; it has no C functions, structs, enums, typedefs, runtime variables, branches, locking, allocation, direct MMIO access, or persistence logic.

The chunk starts in the tail of the `DPCSSYS_CR3` lane-broadcast region at `ixDPCSSYS_CR3_LANEX_DIG_ANA_RX_AFE_ATT_VGA` and completes the CR3 `LANEX` analog tail plus the CR3 `RAWLANEX` raw lane-broadcast block. It then starts the explicit `// addressBlock: dpcssys_cr4_rdpcstxcrind` section at lines 9821-9822 and covers the CR4 indexed register map through `ixDPCSSYS_CR4_RAWLANEX_DIG_PCS_XF_TX_OVRD_IN_2`.

Observed macro counts in this range are 176 `CR3` symbols and 2,144 `CR4` symbols. The CR4 block includes `SUP` and `SUPX` support regions, lane regions, raw common, raw lane, raw always-on lane, and lane-broadcast aliases.

## Purpose

`dpcs_4_2_3_offset.h` publishes symbolic offsets for AMD DPCS 4.2.3 display/link PHY registers. These `ixDPCSSYS_*` constants are the indirect register numbers used with DPCSSYS CR address/data windows defined earlier in the same header, not host virtual addresses or ordinary direct MMIO offsets.

This chunk's purpose is to finish the CR3 lane-broadcast map and provide the complete final CR4 indexed-register block for DCN316-era DPCS hardware. Runtime display code can combine these offsets with the companion `dpcs_4_2_3_sh_mask.h` field definitions to program DisplayPort/PHY link state, PLLs, TX/RX lane power, receiver adaptation, signal detection, calibration, raw PCS/PMA handoff, IRQ status/clear/mask registers, diagnostics, and manufacturing/test override paths without hard-coded numeric register addresses.

## Important Macros and Address Families

The exported API surface is the generated preprocessor namespace:

- `ixDPCSSYS_CR3_LANEX_*`: the final visible CR3 lane-broadcast analog RX/TX tail around `0x90b2-0x90ff`, including RX AFE/CTLE/slicer/IQ/signal-detect override outputs, analog TX measurement/power/ATB/DCC/termination/misc registers, and analog RX clock/CDR/slicer/power/squelch/calibration/ATB registers.
- `ixDPCSSYS_CR3_RAWLANEX_*`: CR3 raw lane-broadcast offsets around `0xe000-0xe0c8`, covering PCS TX/RX override/input/output mirrors, RX adaptation acknowledgement and figure-of-merit values, FSM status and fast-calibration controls, lane IRQ status/clear/masks, PMA crossbar inputs/outputs, TX/RX controller status, OCLA/UPCS observability, ATE overrides, and master MPLL loop controls.
- `ixDPCSSYS_CR4_SUP_*`: CR4 supervisor/common offsets for IDCODE, refclk and MPLL override inputs, MPLLA/MPLLB SSC parameters, charge-pump controls, ASIC feedback inputs, prescaler, RTUNE, bandgap/reference controls, analog MPLL controls, power-control timers/status, clock/reset timing, and digital-to-analog override/status outputs.
- `ixDPCSSYS_CR4_LANE0` through `ixDPCSSYS_CR4_LANE3`: concrete lane register offsets. Lanes 1 and 2 expose the larger repeated lane surface with TX/RX power, VCO, CDR, DPLL, adaptation, statistics, MPHY, analog override, and analog TX/RX controls. Lanes 0 and 3 expose smaller generated subsets in this range and are paired with their separate raw always-on and raw-lane blocks.
- `ixDPCSSYS_CR4_RAWAONLANE0` through `ixDPCSSYS_CR4_RAWAONLANE3` and `ixDPCSSYS_CR4_RAWAONLANEX`: always-on lane offsets for AFE/CTLE/DFE adaptation values, slicer and phase controls, MPHY/RTUNE/DCC state, signal-detect calibration, firmware calibration/adaptation configuration, lane transceiver mode, and TX DCC configuration.
- `ixDPCSSYS_CR4_RAWCMN_*`: raw common always-on offsets for SRAM boot/load state, power gating and reset overrides, supply/reference/MPLL request and acknowledgement routing, firmware ID, VREF state, reference-range override, and MPLL powerdown timing.
- `ixDPCSSYS_CR4_SUPX_*`, `ixDPCSSYS_CR4_LANEX_*`, and `ixDPCSSYS_CR4_RAWLANEX_*`: broadcast or lane-indexed alias views of the CR4 support, lane, and raw-lane register layouts.

The address ranges convey hardware grouping: low offsets cover supervisor/common and concrete lane spaces, `0x4000`-class offsets cover raw always-on lane blocks, `0x8000` and `0x9000` are support/lane alias windows, and `0xe000`-class offsets cover raw lane PCS/PMA/FSM/IRQ/control windows.

## Control Flow

There is no executable control flow in this header chunk. The runtime flow is supplied by AMDGPU display code and the DPCS hardware:

1. DC resource code includes this generated offset header with `dpcs_4_2_3_sh_mask.h`.
2. Register-list macros expand selected `ixDPCSSYS_*` offsets and matching shift/mask constants into static register tables.
3. Link encoder and PHY code use AMD display register helpers to read, write, update, and poll the addressed DPCS indirect registers.
4. The hardware performs the actual sequencing for reference-clock enablement, PLL and MPLL setup, lane TX/RX power states, VCO/CDR/DPLL calibration, receiver adaptation, DCC, signal detect, IRQ generation/clearing, PCS/PMA handoff, and diagnostic capture.

For this source tree, `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c` includes `dpcs/dpcs_4_2_3_offset.h` and `dpcs/dpcs_4_2_3_sh_mask.h`, then uses `DPCS_DCN31_REG_LIST(id)` and `DPCS_DCN31_MASK_SH_LIST(...)` to populate DCN316 link encoder/resource register metadata.

## State and Persistence Behavior

The file itself is stateless. All values are immutable compile-time constants generated from an ASIC register database. It owns no memory, stores no driver state, opens no files, and has no initialization or teardown behavior.

The represented hardware registers do carry state when other code accesses them. State domains include PLL and clock state, SRAM boot/load state, TX/RX lane power states, CDR/DPLL/VCO calibration results, RX adaptation and DFE/CTLE/AFE tuning, DCC calibration, signal-detect calibration, IRQ status and masks, PCS/PMA request/acknowledgement paths, raw FSM status, OCLA/UPCS diagnostic selection, ATE overrides, and analog test-bus readback. Hardware contents persist only according to the relevant reset and power domains, so higher-level code must reprogram or revalidate them after GPU reset, DPCS reset, power gating, suspend/resume, hotplug retraining, link-rate changes, or firmware-driven reinitialization.

## Dependencies and Integration Points

The direct dependency is the C preprocessor. The semantic dependencies are stronger:

- The companion `dpcs_4_2_3_sh_mask.h` must stay aligned with these register names so field helpers apply shifts and masks to the correct offsets.
- `dcn316_resource.c` is the main in-tree consumer for DPCS 4.2.3, binding the offset and shift/mask headers into DCN316 display resource tables.
- DIO/link encoder and DC register-helper code rely on stable generated naming conventions such as `ixDPCSSYS_CR4_LANE2_DIG_RX_CDR_CDR_CTL_0` and token-pasted register-list macros.
- The DPCSSYS CR address/data windows and base-index constants defined earlier in this header provide the indirect access path for these `ix...` offsets.
- Firmware and hardware controllers may own raw FSM, raw common, AON lane, calibration, and PCS/PMA control surfaces during parts of link bring-up; software must coordinate rather than treating every offset as a free direct-control register.
- Adjacent generated DPCS versions such as `dpcs_4_2_0_offset.h` and `dpcs_4_2_2_offset.h` provide useful diff references for detecting unintended generated-header drift versus expected ASIC-version changes.

## Risks

- A wrong numeric offset can compile cleanly while directing a read or write to the wrong PHY register, causing link-training failure, PLL instability, broken signal detect, bad receiver adaptation, failed DCC calibration, or power-state hangs.
- This chunk begins mid-CR3 and then switches to CR4. Merge or review logic must preserve the earlier chunks for the full CR3 context and must not treat the CR3 tail here as an independent complete address block.
- CR4 contains many repeated lane and alias layouts. Prefix mistakes between `LANE*`, `LANEX`, `RAWLANE*`, `RAWLANEX`, `RAWAONLANE*`, and `RAWAONLANEX` can target an unintended concrete lane or broadcast/indexed view.
- IRQ status, clear, and mask registers have similar names but different side effects. The offset header does not encode write-one-to-clear behavior, clear ordering, or mask polarity.
- Raw PCS/PMA, ATE, OCLA, firmware config, and override registers can force hardware away from normal state-machine ownership. Incorrect writes can disrupt calibration, link recovery, or manufacturing/debug paths.
- Reserved analog/digital offsets are still named in the generated map. Consumers must not assume reserved registers are safe scratch space or safe to modify without matching field guidance.
- Manual edits to this generated header can desynchronize the offset map from `dpcs_4_2_3_sh_mask.h`, DCN316 resource tables, and the underlying silicon register database.

## Test and Validation Signals

Useful validation signals are build-time, generated-data, and hardware-integration oriented:

- Build or preprocess AMDGPU display code for DCN316 with `dpcs_4_2_3_offset.h` and `dpcs_4_2_3_sh_mask.h`; missing or renamed macros should fail where resource tables expand DPCS register lists.
- Static checks should confirm this chunk remains offset-only, contains the expected 2,320 `#define` entries in the selected range, and ends with the header guard footer.
- Cross-check consumed `ixDPCSSYS_CR3_*` and `ixDPCSSYS_CR4_*` register names against `dpcs_4_2_3_sh_mask.h` for matching bitfield definitions where field access is expected.
- Diff repeated CR4 lane, raw-lane, raw always-on, `SUPX`, `LANEX`, and `RAWLANEX` families against neighboring generated versions to catch accidental missing entries or address shifts.
- Exercise DCN316 display paths on hardware: DisplayPort and HDMI modeset, hotplug, link retraining, lane-count and link-rate changes, suspend/resume, GPU reset, power-gating recovery, and error recovery after failed training.
- Hardware bring-up should show expected readback for reference-clock enable, MPLL lock and calibration, bandgap/reference timing, TX/RX pstate acknowledgements, RX VCO/CDR/DPLL calibration, receiver adaptation completion, DCC acknowledgement, signal detect, IRQ status/clear/mask behavior, raw FSM status, and analog/ATE override cleanup.

## Chunk Notes

This is a source-tree-aligned chunk report only for `subset-b-002385`. It intentionally does not create a final per-file synthesis for `dpcs_4_2_3_offset.h`; that belongs to the later merge/reconciliation lane after all chunks for this generated header are available.
