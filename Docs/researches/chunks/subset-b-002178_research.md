# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 66982-69371

## Scope

This chunk is a generated AMD DCN 4.1.0 register field shift/mask slice for DPCSSYS CR0 PHY control and status registers. It contains preprocessor constants only; there are no C functions, structs, enums, or local executable branches. The requested range starts in the middle of `DPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`, covers the tail of lane 0 analog TX fields, covers most of lane 1 digital/analog PHY fields, and ends in the first fields of `DPCSSYS_CR0_LANE1_ANA_RX_SQ`.

Within the requested lines I counted 2,181 `#define` entries across 210 unique register names: 1,089 `__SHIFT` constants, 1,092 `_MASK` constants, and 209 register comment headers. The small shift/mask imbalance is from artificial chunk boundaries: the chunk begins after some lane 0 shift definitions and ends before the lane 1 RX squelch masks.

The visible register families are:

- Lane 0 tail fields for TX DCC DAC override, TX fast-start/loopback/ACJTAG, analog TX measurement, power, alternate bus, ATB, DCC, termination-code, clock, VREG, and reserved/NC controls.
- Lane 1 digital ASIC override and ASIC-view fields for TX, RX, lane loopback, data rate, width, pstate, CDR/VCO load values, equalization, link power, and acknowledge/status paths.
- Lane 1 TX power-control state tables for P0, P0S, P1, and P2, plus TX power-up timing, DCC CR-bank/DAC access, clock alignment, and LBERT control.
- Lane 1 RX power-control state tables, VCO calibration, CDR/DPLL configuration and status, RX adaptation controls/status, DAC selection, pattern/stat counters, MPHY PWM/termination controls, and LBERT error reporting.
- Lane 1 digital-to-analog override outputs for TX power/clock/equalization, RX power/CDR/VCO/calibration/slicer/IQ/status/termination/MPHY/signaldetect/DCC paths.
- Lane 1 analog TX and RX register fields for measurement, power override, VREG, DCC/termination, clock, CDR/deserializer, slicer, AFE/DFE/deserializer power, loopback, and the beginning of squelch response control.

## Purpose

`dcn_4_1_0_sh_mask.h` is the bitfield half of the DCN 4.1.0 generated register contract. Each macro gives the bit position or bit mask for a hardware field. Driver code combines these constants with register offsets from the matching generated offset headers and the display register helper macros (`REG_SET`, `REG_UPDATE`, `REG_GET`, `REG_WAIT`, and related token-pasting helpers) to perform MMIO operations without embedding raw bit positions in handwritten logic.

This chunk specifically documents low-level DPCSSYS CR lane controls. These fields describe the internal PHY-control register map behind DPCSSYS CR address/data access, including per-lane link transmitter and receiver controls. The field names cover areas used by PHY bring-up, link training diagnostics, power sequencing, calibration, loopback, and manufacturing/debug paths rather than the main display pipe programming surface.

## Important APIs And Data Shapes

There are no callable APIs in this header slice. The important data shape is the generated field naming convention:

- `DPCSSYS_CR0_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_DATA_EN__SHIFT`
- `DPCSSYS_CR0_LANE1_DIG_TX_PWRCTL_TX_PSTATE_P0__TX_P0_DATA_EN_MASK`

The register name appears before `__`; the field name appears between `__` and the `__SHIFT` or `_MASK` suffix. Most fields are 16-bit CR-register fields, with masks such as `0x0001L`, `0x00FFL`, `0x7FFFL`, or `0xFFFFL`. Reserved and non-connected fields are also generated as masks, for example `RESERVED_*` and `NC*`, which lets mechanical table generation preserve the full hardware word layout.

The DCN 4.1.0 source tree includes this file from DCN401 resource, clock manager, IRQ, GPIO, and DMUB support files. `dcn401_resource.c` uses token-pasting register construction macros such as `SR`, `SRI`, `SRI_ARR`, `SRII`, and `REG` with `dcn_4_1_0_offset.h` and this shift/mask header. `dmub_dcn401.c` builds `dmub_srv_dcn401_regs` by expanding `DMUB_DCN401_REGS()` into offsets and `DMUB_DCN401_FIELDS()` into mask/shift arrays with `FD_MASK()` and `FD_SHIFT()`. `irq_service_dcn401.c` similarly token-pastes register names and `_MASK` constants into IRQ source descriptors.

The requested DPCSSYS lane fields are not typical display-pipe fields such as HUBP, DPP, MPC, OTG, or HPD. In `dcn_4_1_0_offset.h`, the directly visible DPCSSYS CR0 entries are the indirect access registers `DPCSSYS_CR0_DPCSSYS_CR_ADDR` and `DPCSSYS_CR0_DPCSSYS_CR_DATA`; closely related `dpcs_*_offset.h` headers expose matching internal `ixDPCSSYS_CR0_LANE*` indices for other DCN/DPCS variants. This makes the names in this chunk part of an indirect PHY register map rather than ordinary memory-mapped display block registers.

## Runtime Control Flow

This header has no local control flow. Runtime behavior is produced by consumers that include generated headers, assemble register tables, and call register helpers.

A typical use pattern for generated field constants is:

1. Resource or service construction selects DCN 4.1.0 offsets and shift/mask tables.
2. A feature implementation calls a register helper such as `REG_UPDATE` or `REG_GET`.
3. The helper reads or writes the register offset, applies the generated `_MASK` and `__SHIFT`, and updates the field value.
4. For status fields, the driver may poll or compare generated masks until hardware reports a transition.

For this chunk's DPCSSYS CR fields, the implied hardware flows are lane-level and PHY-level:

- TX request, pstate, rate, width, data enable, MPLL select, HDMI mode, reset, RX detect, transmitter EQ, and DCC controls describe how lane 1's transmitter can be overridden or observed.
- RX request, pstate, rate, width, termination, data enable, CDR tracking, SSC, alignment, clock shift, AFE/DFE adaptation, loopback, VCO load, and DPLL frequency fields describe receiver bring-up and training.
- Power-control PSTATE registers encode which analog/digital enables are asserted for TX and RX low-power/active states; power-up time registers encode sequencing delays and skip/fast-path bits.
- Calibration/status blocks expose VCO calibration codes, RX adaptation values, DFE taps, slicer levels, pattern-match/stat counters, and LBERT error counts for hardware diagnostics.

Because the chunk is generated data, the final per-file report should avoid assigning a specific handwritten call path to every field unless a consumer of the indirect DPCSSYS CR address/data mechanism is also identified.

## State And Persistence

The state represented here persists in hardware registers, not in software storage:

- Override input registers persist forced software values and corresponding `*_OVRD_EN` enable bits until rewritten, reset, or superseded by hardware power/reset behavior.
- ASIC input/output and status registers expose hardware-observed state such as TX acknowledge, RX valid/adaptation status, DCC DAC acknowledge, VCO calibration status, LBERT errors, and stat-counter sample completion.
- PSTATE and power-up timing fields persist the lane power sequencing model used by hardware when changing PHY states.
- Calibration, adaptation, DCC DAC, VREG, termination, EQ, CDR, DPLL, slicer, and signaldetect fields persist analog PHY tuning and measurement values.

The software-visible persistence is the compiled-in constant table: if these constants are wrong, every runtime user built against the generated table will address the wrong bit positions until the driver is rebuilt with corrected generated headers.

## Dependencies And Integration Points

Primary dependencies and integration points:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies DCN 4.1.0 MMIO offsets and base-index constants. For DPCSSYS CR0, it exposes the indirect CR address/data registers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn401/dcn401_resource.c` includes this header and builds DCN401 register/mask/shift tables used by the display resource pool.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn401.c` includes this header and stores selected masks/shifts in `dmub_srv_dcn401_regs` for DMUB service operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn401/irq_service_dcn401.c`, `dc/clk_mgr/dcn401/dcn401_clk_mgr.c`, and `dc/gpio/dcn401/*` include this same generated file for their DCN401 register field tables.
- Neighboring generated DPCS headers such as `include/asic_reg/dpcs/dpcs_3_1_4_offset.h`, `dpcs_4_2_0_offset.h`, and `dpcs_4_2_2_offset.h` show matching `ixDPCSSYS_CR0_LANE*` internal register indices for many names in this chunk. Those are useful cross-checks, but they are not interchangeable with the DCN 4.1.0 generated header set.

The broader integration point is link PHY operation: display link encoders, HPO/DP link encoders, link training, and diagnostics depend on correct PHY state and register tables even when they access higher-level RDPCS/DPCSTX abstractions rather than these exact generated names.

## Risks

- Bitfield drift is high impact. A wrong mask or shift in PHY power, reset, CDR, DPLL, EQ, or pstate fields can produce link-training failures, unstable clocks, no display output, excessive power draw, or broken low-power transitions.
- The requested range starts and ends inside register families. The first register lacks its opening field definitions in this chunk, and `DPCSSYS_CR0_LANE1_ANA_RX_SQ` lacks its masks here. Whole-register completeness must be reconciled with adjacent chunks.
- Many fields are paired value/override-enable bits. Setting a value without the matching `*_OVRD_EN`, or corrupting the enable bit's mask, can make debug writes ineffective or leave forced PHY state active.
- The PSTATE and timing registers encode hardware sequencing. Incorrect fields for `TX_P*_ANA_*`, `RX_P*_ANA_*`, `*_PWRUP_TIME_*`, or skip/fast bits can change ordering around clocks, resets, VCM hold, DCC calibration, deserializer enable, and RX detect.
- RX adaptation and calibration fields are compact and status-heavy. Wrong masks for DFE taps, CTLE/VGA/ATT status, VCO calibration, DPLL bounds, or stat counters can hide real PHY failures or make debug tooling report misleading values.
- Reserved and `NC` fields should generally be preserved unless hardware documentation explicitly says otherwise. Generated constants expose them, but writing them casually can create compatibility problems across steppings.
- The same-looking DPCSSYS names appear in multiple generated DCN/DPCS versions. Mixing `dcn_4_1_0_sh_mask.h` with offsets or enums from another generation may compile in some token-paste paths but produce incorrect hardware accesses.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for DCN401 with `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` included by resource, IRQ, GPIO, clock manager, and DMUB code. Token-paste mismatches should fail compilation.
- Generated-header consistency checks that every complete field in this range has a matching `__SHIFT` and `_MASK`, allowing for the chunk's partial first and last registers.
- Mechanical diffing against AMD's authoritative generated register database and nearby DPCS/DCN generated headers for the same `DPCSSYS_CR0_LANE*` register names.
- Hardware smoke tests on DCN401 systems covering DisplayPort and HDMI link bring-up, link-rate changes, lane-count changes, HPD unplug/replug, suspend/resume, and display power transitions.
- Link-training diagnostics showing stable CDR/DPLL lock behavior, no unexpected LBERT errors, and sane RX adaptation/status values after rate changes.
- Register dumps around DPCSSYS CR address/data access, if available in debug firmware or diagnostics, verifying that pstate, DCC, CDR, RX adaptation, and status fields decode according to these masks.

## Chunk Boundary Notes

This chunk begins at line 66982, after the first six fields of `DPCSSYS_CR0_LANE0_DIG_ANA_TX_DCC_DAC_OVRD_OUT`. The previous chunk should contain that register's comment header and early shift definitions. This chunk ends at line 69371 after `DPCSSYS_CR0_LANE1_ANA_RX_SQ__NC4_3__SHIFT`; the masks and any remaining squelch fields continue in the next chunk. The final per-file research document should merge these neighboring chunks before making whole-file completeness claims about DPCSSYS CR0 lane coverage.
