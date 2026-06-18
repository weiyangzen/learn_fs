# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h lines 5192-7664

## Scope

- Chunk id: `subset-b-002114`
- Source file: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_offset.h`
- Source lines: 5192-7664
- Observed content: 2,473 generated header lines containing 2,405 `#define` entries. All entries are `reg*` register-offset macros; 1,202 of them are `_BASE_IDX` companions.

This chunk is a generated AMD DCN 3.6.0 register-offset slice. It has no executable C logic. The range begins with the final two `DC_PERFMON14` counter-value registers, then covers MPC compositor, MPCC routing, MPCC output gamma, MPCC multi-color-management, output CSC, ABM0, and most of ABM1. The final line is `regABM1_DC_ABM1_BL_MASTER_LOCK`; the matching `_BASE_IDX` appears after this chunk.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The chunk publishes compile-time MMIO offsets and base-index selectors for DCN 3.6 display composition and panel/backlight blocks. Driver code combines these values with `dcn_3_6_0_sh_mask.h` field masks so register-list macros can build per-ASIC register tables for the Display Core resource pool, hardware sequencer, DMUB service, IRQ service, MPC color/composition code, and ABM/backlight code.

The covered hardware surface is display-pipeline stateful hardware:

- `DC_PERFMON14` tail and complete `DC_PERFMON15` offsets for display performance counters.
- `MPCC0` through `MPCC3` compositor instances for top/bottom plane selection, OPP routing, blending gains, update-lock selection, background color, memory power, and status.
- Global `MPC` configuration registers for clock/reset, CRC, perfmon event selection, background bypass, host reads, pending status, vupdate-lock groups, CRC results, and DWB mux selection.
- `MPCC_OGAM0` through `MPCC_OGAM3` output gamma and gamut-remap register sets.
- `MPCC_MCM0` through `MPCC_MCM3` multi-color-management register sets, including shaper LUTs, 3D LUTs, 1D LUTs, gamut remap matrices, and memory-power control.
- `MPC_OUT0` through `MPC_OUT3` output mux, denormalization, output CSC coefficient, and coefficient-format registers.
- `ABM0` complete and `ABM1` nearly complete adaptive backlight modulation blocks for PWM input/output, ambient-light/user levels, ACE controls, luma statistics, histogram programming/readback, sample rates, and master locks.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported API surface is the generated macro namespace:

- `reg<REGISTER>`: numeric MMIO register offset within the selected DCN register segment.
- `reg<REGISTER>_BASE_IDX`: segment selector consumed by AMD display register helpers before adding the offset.
- `// addressBlock: ...` and `// base address: ...`: generated block comments that identify repeated hardware instances and their hardware database bases.

Important macro families in this range include:

- `regMPCC{0..3}_MPCC_*`: MPCC routing, blending, update lock, background color, memory power, and status offsets.
- `regMPC_*`, `regADR_*_VUPDATE_LOCK_SET*`, `regCFG_VUPDATE_LOCK_SET*`, and `regCUR_VUPDATE_LOCK_SET*`: global MPC control/status, CRC, pending state, writeback muxing, and vupdate-lock routing.
- `regDC_PERFMON15_*`: per-block performance counter control, state, counter value, and monitor high/low offsets.
- `regMPCC_OGAM{0..3}_*`: MPCC output-gamma LUT access, RAMA/RAMB piecewise-linear curve programming, offsets, region descriptors, LUT control, and gamut remap coefficient registers.
- `regMPCC_MCM{0..3}_*`: MCM shaper control and LUT windows, 3D LUT index/data/control, 1D LUT control and RAMA/RAMB piecewise-linear tables, gamut-remap matrix controls, and memory-power controls.
- `regMPC_OUT{0..3}_*`: output muxing, denormalization clamps, CSC mode and matrix coefficients for coefficient banks A/B, plus `regMPC_OUT_CSC_COEF_FORMAT`.
- `regABM0_*` and `regABM1_*`: backlight PWM levels, ambient/user/target/current/final/minimum duty cycle controls, ABM algorithm control, ACE slopes/thresholds, luma-statistic registers, histogram bin/result registers, sample rates, and master-lock registers.

The repeated families are part of the ABI between generated ASIC headers and token-pasting register-list macros. For example, DCN36 resource setup reuses shared DCN3.2-style MPC register lists such as `MPC_REG_LIST_DCN3_2_RI(inst)` and `MPC_OUT_MUX_REG_LIST_DCN3_0_RI(inst)`, which expand names like `regMPCC2_MPCC_TOP_SEL`, `regMPCC_MCM2_MPCC_MCM_SHAPER_CONTROL`, and `regMPC_OUT2_CSC_MODE`.

## Control Flow

This header chunk has no local control flow. Runtime behavior comes from AMDGPU Display Core:

1. DCN36-specific code includes `dcn/dcn_3_6_0_offset.h` and `dcn/dcn_3_6_0_sh_mask.h`.
2. Resource and service code expands register-list macros, token-pasting symbolic register names into offset-table initializers.
3. Helpers compute addresses as `BASE(reg..._BASE_IDX) + reg...` and store them in per-block tables.
4. Runtime display code uses those tables through `REG_READ`, `REG_WRITE`, `REG_SET`, `REG_UPDATE`, indexed LUT helpers, and block-specific wrappers.
5. Hardware performs the actual work: MPCC composition, gamma/LUT access, MCM color transforms, output CSC, update-lock synchronization, CRC/perfmon capture, and ABM backlight decisions.

Concrete integration observed in this tree includes `dmub_srv_dcn36_regs_init()` in `display/dmub/src/dmub_dcn36.c`, which initializes DCN36 DMUB register offsets from this generated header, and `display/dc/resource/dcn36/dcn36_resource.c`, which includes the same header and builds DCN36 resource/hardware-sequencer tables. The MPC/MPCC/MCM/output-CSC names in this chunk are also consumed through shared DCN3.x register-list macros in `display/dc/resource/dcn32/dcn32_resource.h`.

The header does not encode sequencing. Consumers must still obey hardware ordering for update locks, LUT index/data writes, RAM bank selection, color-transform enablement, MPCC tree updates, clock/memory power control, CRC/perfmon start/stop, and ABM lock/update flows.

## State And Persistence Behavior

The macros are stateless constants. State exists in the hardware registers they name:

- MPCC registers hold current compositor topology, top/bottom plane inputs, OPP selection, blending gains, background color, update-lock routing, stall/status, and MPCC memory-power state.
- MPC global registers hold clock/reset state, CRC configuration/results, perfmon event selection, DPP pending-status observations, vupdate-lock group routing, and DWB mux state.
- MPCC OGAM registers expose indexed LUT windows and RAMA/RAMB piecewise-linear curve memory. Writes mutate hardware color RAM and related mode/configuration state.
- MPCC MCM registers expose shaper LUT memory, 3D LUT memory, 1D LUT memory, gamut-remap matrix state, and memory-power controls for per-MPCC color management.
- MPC OCSC registers hold output mux, denormalization, and output CSC coefficients for each output path.
- ABM registers hold panel/backlight control state, ambient-light and user-level inputs, duty-cycle targets/current values, ACE thresholds/slopes, luma-statistic observations, histogram readbacks, and master-lock state.
- Perfmon registers hold counter controls, latched values, and monitor state.

Persistence is hardware-defined. Configuration values may survive until a modeset, block reset, power-gating event, suspend/resume transition, GPU reset, or ASIC reset. Status, CRC, histogram, perfmon, pending, and current backlight values may be volatile, latched, sticky, or valid only while the corresponding display pipe, OPP, MPC, or ABM power/clock domain is active. The offset header carries no access-type metadata; consumers must rely on the companion shift/mask header, register specs, and block-specific programming sequences.

## Dependencies And Integration Points

Direct dependencies and consumers include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_6_0_sh_mask.h`, which supplies the matching field shifts and masks for the offsets in this file.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn36.c`, which includes this header and initializes DCN36 DMUB register offsets with `REG_OFFSET_EXP(reg_name)`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn36/dcn36_resource.c` and `dcn36_resource.h`, which include this header and build DCN36 resource, hardware-sequencer, hub, clock, interrupt, MPC, and output register tables.
- Shared DCN3.x MPC register-list definitions in `display/dc/resource/dcn32/dcn32_resource.h`, including MPCC, MPCC OGAM, MPCC MCM, MPC output mux, output CSC, and ABM helper lists.
- AMD display color-management interfaces in `display/dc/dc.h` and hardware-type enums in `display/dc/dc_hw_types.h`, which expose concepts corresponding to MPCC OGAM, MPCC MCM, RMCM, and output CSC programming.
- ASIC enum headers such as `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/soc21_enum.h`, which define symbolic field values for MPC/MPCC OGAM/MCM/OCSC modes selected through these offsets.

Integration points visible to users include multi-plane composition, HDR/output gamma, 3D LUT and color-space conversion paths, CRC diagnostics, display performance monitoring, writeback muxing, panel brightness and adaptive backlight behavior, suspend/resume restore, and display power-management transitions.

## Risks And Edge Cases

- Numeric drift is the primary risk. A wrong offset or `_BASE_IDX` can compile cleanly while causing a register helper to read or write the wrong MMIO address.
- This range has artificial chunk boundaries. It starts after the beginning of `DC_PERFMON14` and ends one line before `regABM1_DC_ABM1_BL_MASTER_LOCK_BASE_IDX`, so the merge lane must combine adjacent chunks before making complete-file claims.
- Repeated instance parity matters. `MPCC0` through `MPCC3`, `MPCC_OGAM0` through `MPCC_OGAM3`, `MPCC_MCM0` through `MPCC_MCM3`, `MPC_OUT0` through `MPC_OUT3`, and `ABM0/ABM1` are structurally parallel with shifted offsets. A generation error can break one pipe/output/backlight instance while adjacent instances still work.
- Base-index mistakes are as damaging as offset mistakes. Nearly all registers in the main display blocks use base index `3`, while the leading `DC_PERFMON14` tail uses base index `2`; helpers must not treat raw offsets as absolute addresses.
- LUT and RAM access registers are stateful index/data windows. Wrong sequencing or wrong offsets can corrupt color tables even if individual writes look valid.
- MPCC routing and update-lock registers affect atomic modeset behavior. Incorrect offsets can cause tearing, stale plane composition, wrong OPP routing, or deadlocks waiting for update/status bits.
- Color-management registers are visually sensitive. Errors in OGAM/MCM/OCSC offsets may show up only on HDR, color-managed, wide-gamut, 3D LUT, or multi-plane blending paths.
- ABM registers combine control, locks, live sensor/statistic state, and algorithm results. Bad offsets can cause incorrect brightness, flicker, stuck backlight levels, resume-only panel brightness failures, or misleading luma/histogram diagnostics.
- Perfmon, CRC, pending-status, and histogram values can be transient or latched. Tests must account for timing and power state rather than assuming stable readback.

## Test Signals

Useful validation combines generated-header checks with DCN36 hardware behavior:

- Build AMDGPU display support with DCN36 enabled. Missing or renamed macros should fail in `dmub_dcn36.c`, `dcn36_resource.c`, IRQ setup, and shared MPC/ABM register-list expansions.
- Mechanical header checks: every non-boundary `reg*` offset in this chunk should have a matching `_BASE_IDX`, repeated instance layouts should match expected deltas, and all names should have matching shift/mask entries in `dcn_3_6_0_sh_mask.h`.
- Cross-generation diff checks against nearby DCN3.x offset headers where DCN36 intentionally reuses shared MPC, MPCC, MCM, OCSC, ABM, and perfmon layouts.
- Modeset and composition testing on DCN36 hardware with one through four active pipes, multi-plane blending, MPCC top/bottom paths, OPP routing, update-lock behavior, and DWB mux use.
- Color-path tests covering degamma/gamma, MPCC OGAM LUT programming, MCM shaper/3D LUT/1D LUT use, gamut remap, output CSC banks A/B, HDR metadata workflows, and suspend/resume color-state restore.
- CRC/perfmon diagnostics that start/stop counters, read high/low values, select MPC events, and confirm counter values are coherent across power and modeset transitions.
- ABM/backlight tests covering enable/disable, ambient-light/user-level inputs, min/current/target/final duty cycle transitions, histogram/luma-stat readbacks, master-lock handling, panel blank/unblank, and suspend/resume brightness restore.
- Power-management tests for MPCC/MCM memory-power controls, clock/reset state, repeated modesets, runtime power gating, GPU reset recovery, and static-screen/idle transitions.

## Chunk Boundary Notes

Lines 5192-5197 are the tail of the preceding `DC_PERFMON14` block. Lines 5198-7543 cover complete MPCC0-3, MPC config, DC_PERFMON15, MPCC_OGAM0-3, MPCC_MCM0-3, MPC OCSC, and ABM0 groups. Lines 7544-7664 cover ABM1 through `regABM1_DC_ABM1_BL_MASTER_LOCK`; the companion `_BASE_IDX` and any following ABM blocks must be read from the next chunk before final per-file synthesis.
