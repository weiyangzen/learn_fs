# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_offset.h lines 9632-11973

## Purpose

This chunk is a generated AMD DPCS 4.2.0 register-offset header slice. It contains no executable C logic; it publishes preprocessor constants for DisplayPort PCS / PHY control registers used by AMDGPU display code.

The requested range contains 2,330 `#define` entries. It starts at the tail of the `DPCSSYS_CR3` indirect CR address space, covers the full `addressBlock: dpcssys_cr4_rdpcstxcrind`, and ends with a small `RDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` shift/mask and register-offset shim. The CR4 block provides indirect-register offsets for supervisor/common PLL state, per-lane digital and analog PHY controls, raw always-on lane registers, raw common registers, raw memory windows, and raw lane PCS/PMA/FSM/IRQ/TX/RX controls.

Although this file is under a local `ceph-client` source tree, this chunk is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, allocations, locks, or direct MMIO operations in this chunk. The exported interface is macro metadata:

- `ixDPCSSYS_CR3_*`: indirect DPCS CR3 register offsets. This chunk only contains the CR3 tail, ending CR3 lane analog TX/RX offsets, raw memory windows, and raw lane PCS/PMA/FSM/IRQ/TX/RX offsets.
- `ixDPCSSYS_CR4_*`: indirect DPCS CR4 register offsets. This is the dominant block in the range and covers the complete CR4 generated namespace.
- `RDPCSPIPE0_RDPCSPIPE_PHY_CNTL6__*` and `RDPCSPIPE1_RDPCSPIPE_PHY_CNTL6__*`: local shift/mask definitions for `RDPCS_PHY_DPALT_DP4`, `RDPCS_PHY_DPALT_DISABLE`, and `RDPCS_PHY_DPALT_DISABLE_ACK` bits.
- `regRDPCSPIPE[0-4]_RDPCSPIPE_PHY_CNTL6` plus `_BASE_IDX`: direct MMIO offsets for the two real RDPCSPIPE instances, aliased across five logical transmitters.

The main CR4 offset families are:

- `SUP_DIG` and `SUP_ANA`: supervisor/common control offsets for ID code, reference-clock overrides, MPLLA/MPLLB dividers, HDMI clocking, SSC peak/stepsize programming, charge-pump controls, prescalers, bandgap/level controls, RTUNE, MPLL analog readback/override, and common output/status registers.
- `SUPX_DIG` and `SUPX_ANA`: extended supervisor offsets for alternate-bus, ATB, PLL calibration, PFD, DCC, PLL miscellaneous, reserved, and LC tank controls.
- `RAWCMN_DIG_*`: raw common digital offsets for MPLL loop observation/control, fast FSM state/status, ATE override and status, PLL status, clock observation, and common/raw memory access helpers.
- `RAWAONLANE[0-3]` and `RAWAONLANEX`: always-on per-lane offsets for PCS/PMA boundary controls, reset/power-state request and acknowledge IRQs, DCC on-demand IRQs, PMA lane override/status, raw TX/RX control, RX PWRUP controls, and rate controls.
- `LANE[0-3]` and `LANEX`: per-lane digital and analog offsets for PCS/PMA transfer signals, FSM controls/status, IRQ controls, TX/RX override paths, equalization/adaptation, DCC status, PMA lane/supervisor interfaces, TX FSM/clocking/DCC, RX FSM/LOS/data/adaptation status, ATE controls, and analog TX/RX calibration, termination, ATB, CDR, squelch, and power controls.
- `RAWLANE[0-3]` and `RAWLANEX`: raw per-lane offsets for the same PCS/PMA/FSM/IRQ/TX/RX/ATE surfaces, generally used through indirect CR addressing.
- `RAWMEM_DIG_ROM_CMN0_B0_R0` and `RAWMEM_DIG_RAM_CMN0_B0_R0`: raw ROM/RAM memory windows.

The `LANEX`, `RAWLANEX`, and `RAWAONLANEX` forms are generic lane-X aliases alongside explicit lane 0-3 instances. In this chunk, CR4 has 1,189 lane-family defines, 625 raw-lane defines, 278 supervisor defines, 52 raw-common defines, and 2 raw-memory defines.

## Control Flow

This header has no runtime control flow. Its constants are consumed by register-table construction and by register-helper macros in the AMD display driver:

1. `dcn31_resource.c` includes `dpcs_4_2_0_offset.h` and the matching `dpcs_4_2_0_sh_mask.h`.
2. DCN31 resource initialization expands `DPCS_DCN31_REG_LIST(id)` into per-link encoder register tables, including `RDPCSTX_PHY_CNTL*`, `RDPCSPIPE_PHY_CNTL6`, `RDPCS_TX_CR_ADDR`, and `RDPCS_TX_CR_DATA`.
3. Runtime link encoder paths use shared `REG_GET`, `REG_UPDATE`, and related helpers against those tables.
4. DPCS indirect accesses use the direct CR address/data registers from earlier chunks of this same file together with `ixDPCSSYS_CR*_*` offsets from this and adjacent chunks.
5. USB-C DP-alt-mode legacy detection reads `RDPCS_PHY_DPALT_DISABLE` and `RDPCS_PHY_DPALT_DP4` from either `RDPCSTX_PHY_CNTL6` or `RDPCSPIPE_PHY_CNTL6`, depending on ASIC revision and transmitter routing.

The macros do not encode sequencing. PHY power-up/down, MPLL setup, lane rate/width programming, DP alt-mode query order, reset acknowledgement, training, suspend/resume restore, and interrupt acknowledgement are all controlled by consumer code and hardware rules outside this header.

## State And Persistence Behavior

The chunk stores no software state and persists nothing itself. It names hardware-visible DPCS state:

- Supervisor/common state for reference clocks, MPLLA/MPLLB programming, SSC, PLL calibration, prescalers, bandgap, RTUNE, and analog test/readback buses.
- Per-lane PCS/PMA state for TX/RX override paths, lane number, data enable, rate/width, equalization/adaptation, termination, PMA interfaces, and loopback/test controls.
- FSM and calibration state for RX startup, RX adaptation, AFE/DFE/reflvl/IQ calibration, VCO wait/calibration, continuous calibration/adaptation, DCC flags/status, and common calibration status.
- IRQ state for RX/TX reset/request/rate/pstate/adaptation events, lane transceiver mode changes, RX phase-2 calibration, RX-to-TX serial loopback, and DCC on-demand events.
- Analog TX/RX state for DCC DACs, power overrides, termination code, clocks, CDR, squelch, calibration, ATB measurement/force registers, and reserved silicon fields.
- DP-alt-mode state in `RDPCSPIPE_PHY_CNTL6` for whether DP alt mode is disabled, whether 4-lane DP-alt operation is present, and the disable acknowledgement bit.

Persistence is hardware-defined. Configuration fields generally remain until the driver reprograms the link, the PHY is reset or power-gated, suspend/resume restores state, or a GPU/ASIC reset occurs. Status and IRQ fields may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while relevant DPCS clocks and power domains are active. The offset header does not describe those access semantics.

## Dependencies And Integration Points

This generated offset header must stay synchronized with the matching generated shift/mask header and AMD's DPCS 4.2.0 register database:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_0_sh_mask.h` supplies field shifts and masks for the offsets named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` directly includes this file and builds DCN31 link encoder and HPO DP link encoder register/shift/mask tables.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.h` defines `DPCS_DCN31_REG_LIST()` and `DPCS_DCN31_MASK_SH_LIST()`, which expect the `RDPCSTX*`, `RDPCSPIPE*`, and DPCS CR register names from this generated header family.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dio/dcn31/dcn31_dio_link_encoder.c` uses `RDPCSTX_PHY_CNTL6` and `RDPCSPIPE_PHY_CNTL6` fields to detect USB-C DP-alt-mode disablement and 2-lane versus 4-lane DP-alt capability on legacy paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/hpo/dcn31/dcn31_hpo_dp_link_encoder.h` and `.c` include `RDPCSTX_PHY_CNTL6[5]` in HPO DP link encoder state and read `RDPCS_PHY_DPALT_DISABLE`.

The behavioral integration point for this chunk is display link bring-up, especially DCN31 DisplayPort/USB-C PHY handling. The CR4 indirect offsets describe low-level PHY and lane state, while the RDPCSPIPE tail directly supports DP-alt-mode decisions that can cap link lane count or decide whether a USB-C DP path is usable.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset, base index, shift, or mask can compile cleanly while reading or writing the wrong hardware register or bit.
- The file is generated metadata. Manual edits can diverge from the authoritative AMD register database, the matching `dpcs_4_2_0_sh_mask.h`, firmware expectations, or silicon documentation.
- The chunk boundary is artificial. It starts in the CR3 tail and then covers CR4; the CR3 address block starts in earlier chunks, and whole-file conclusions require merge-lane reconciliation.
- `LANEX` and `RAWLANEX` aliases sit beside explicit lane 0-3 offsets. Consumers must select the correct generic or per-lane symbol; mixing them can silently target the wrong indirect lane context.
- The `RDPCSPIPE only has 2 instances` note is important. Logical instances 2 and 4 alias instance 0, and logical instance 3 aliases instance 1. Code that assumes five independent RDPCSPIPE register banks can misread DP-alt-mode state or mask a per-transmitter issue.
- The DP-alt-mode fields affect link capability. A bad `RDPCS_PHY_DPALT_DP4` or `RDPCS_PHY_DPALT_DISABLE` definition can incorrectly permit four lanes on a two-lane USB-C alt-mode path, cap a valid four-lane path to two lanes, or report the connector as unavailable.
- Low-level PHY controls are timing and power sensitive. Wrong MPLL, DCC, RX adaptation, CDR, termination, power, or calibration offsets can cause link training failures, intermittent high-rate failures, hotplug-only failures, or resume-only regressions.
- IRQ and status offsets are side-effect-sensitive. Confusing request, acknowledge, clear, mask, or status registers can produce missed PHY events, stuck reset handshakes, or interrupt storms.
- Analog/test-bus and ATE registers should not be treated as ordinary runtime controls. Accidental writes can disturb calibration, lane measurement, or production-test state.

## Test Signals

Useful validation combines generated-header consistency checks with display link behavior:

- Build AMDGPU display support for DCN31. Missing or renamed macros should surface in `dcn31_resource.c`, `dcn31_dio_link_encoder.h`, and `dcn31_hpo_dp_link_encoder.h`.
- Mechanically compare lines 9632-11973 against AMD's authoritative DPCS 4.2.0 register database and the adjacent DPCS 4.2.x generated headers where the CR4 layout is expected to match.
- Cross-check every `ixDPCSSYS_CR4_*` register used by the matching shift/mask header has a corresponding offset here, and verify the `RDPCSPIPE*_RDPCSPIPE_PHY_CNTL6` shift/mask definitions match the field layout used by `DPCS_DCN31_MASK_SH_LIST()`.
- Add or run static checks for lane-family consistency across `LANE0-3`, `LANEX`, `RAWLANE0-3`, `RAWLANEX`, `RAWAONLANE0-3`, and `RAWAONLANEX`, while allowing intentional per-lane address differences.
- Exercise DisplayPort and USB-C DP-alt-mode links on DCN31-class hardware across all transmitters, including 2-lane and 4-lane alt-mode docks/cables. Expected signals are correct max lane-count selection, successful link training, and no false unavailable-link reports.
- Test ASIC revision paths that choose `RDPCSTX_PHY_CNTL6` versus `RDPCSPIPE_PHY_CNTL6`, especially Yellow Carp B0 handling in `dcn31_dio_link_encoder.c`.
- Exercise hotplug, unplug, suspend/resume, link retraining, low-power entry/exit, high bit-rate modes, and HPO DP paths while watching for DPCS register timeouts, stuck reset acknowledgements, failed calibration/adaptation, DP-alt-mode misdetection, and training instability.
- Use register dumps around `RDPCS_TX_CR_ADDR`/`RDPCS_TX_CR_DATA` indirect accesses to confirm CR4 offsets address the intended supervisor, lane, raw lane, raw common, and raw memory windows.

## Cross-Chunk Notes

The previous chunk owns most of the `DPCSSYS_CR3` address block. This chunk begins at the final CR3 lane and raw-lane offsets, then owns the full `DPCSSYS_CR4` indirect address block and the RDPCSPIPE compatibility tail before the file's `#endif`. The final per-file research document should merge this with earlier chunks before making whole-file claims about all DPCS 4.2.0 instances, all direct MMIO offsets, or all indirect CR address spaces.
