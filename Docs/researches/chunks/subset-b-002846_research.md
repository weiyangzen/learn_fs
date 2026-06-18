# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/mmhub/mmhub_9_4_1_sh_mask.h lines 11823-14186

## Purpose

This chunk is part of the generated AMDGPU MMHUB 9.4.1 shift/mask register header. It does not define executable logic, functions, or C types. Instead, it publishes preprocessor constants that describe 32-bit bitfield layouts for MMEA1 registers in the second MMHUB/MMEA instance: GMI arbitration, address normalization and address decoding, IO arbitration, SDP request/credit handling, misc arbitration behavior, latency sampling, and the beginning of MMEA1 performance counter configuration.

Each register field appears as a pair of macros:

- `REG__FIELD__SHIFT`, the low bit position.
- `REG__FIELD_MASK`, the bit mask to isolate or set the field.

The companion files provide the other parts of the contract: `mmhub_9_4_1_offset.h` maps these symbolic register names to MMIO offsets and base indices, while `mmhub_9_4_1_default.h` supplies reset/default values. `amdgpu/mmhub_v9_4.c` includes all three headers for MMHUB v9.4 support.

## Important Register Groups

The opening lines complete the MMEA1 DRAM write priority quantum definitions, then the chunk switches to GMI fields. The GMI client-to-group maps (`MMEA1_GMI_RD_CLI2GRP_MAP0/1`, `MMEA1_GMI_WR_CLI2GRP_MAP0/1`) pack 32 client IDs into two registers using 2-bit group fields. The group-to-virtual-channel maps (`MMEA1_GMI_RD_GRP2VC_MAP`, `MMEA1_GMI_WR_GRP2VC_MAP`) assign four arbitration groups to 3-bit virtual channel values.

GMI throttling and arbitration fields include lazy-delay registers, CAM controls, page burst limits, and read/write priority coefficient sets for age, queuing, fixed priority, urgency, urgency masking, and three quantum threshold registers. The pattern is mirrored for read and write paths. Urgency masking uses one bit per client ID across all 32 IDs, while coefficient registers use compact 3-bit per-group fields and quantum registers use 8-bit thresholds for four groups.

The address normalization section describes `MMEA1_ADDRNORM_BASE_ADDR0..5`, matching limit registers, and high-address offset registers for selected ranges. These fields define range validity, legacy MMIO hole enable, channel/die/socket interleave geometry, interleave address selection, base address, destination fabric ID, limit address, and optional high address offsets. Hole control and NP2 channel config fields appear for both DRAM and GMI paths.

Address decoder definitions cover bank and misc config, DRAM/GMI hash controls, harvest controls, and repeated decoder blocks `MMEA1_ADDRDEC0`, `MMEA1_ADDRDEC1`, and `MMEA1_ADDRDEC2`. Each decoder block contains base-address registers for primary CS0-CS3 and secondary CS0-CS3, address masks for CS pairs, address geometry config fields, bank/row selectors, extended bank selectors, column low/high selectors, and RM/channel row-selection controls. These macros encode how physical addresses are split into memory-controller dimensions.

The IO section mirrors the GMI arbitration structure for IO clients: read/write client-to-group maps, combine flush timers, group burst limits, age/queuing/fixed/urgency coefficients, urgency masks, and quantum thresholds. IO default values in the companion default header differ from GMI, so code must pair these masks with the correct `MMEA1_IO_*` register names rather than assuming identical policy values.

The SDP section defines arbitration and credit fields for traffic leaving the MMHUB path. `MMEA1_SDP_ARB_DRAM`, `MMEA1_SDP_ARB_GMI`, and `MMEA1_SDP_ARB_FINAL` expose burst-limit and switching behavior. Priority fields distinguish DRAM, GMI, and IO priority control. Credit and reserve registers define tag limits, read/write response credits, per-VC tag reserves, and VCC/VCD credit reserves, including `DISTRIBUTE_POOL` bits. `MMEA1_SDP_REQ_CNTL` controls request pass/chain overrides and inner-domain mode.

The tail contains global knobs and observability definitions. `MMEA1_MISC` includes relative-priority toggles for DRAM/GMI/IO read/write arbiters, early write return enable bits per VC, link manager mode/threshold/delay fields, and chip-select arbitration preferences. `MMEA1_LATENCY_SAMPLING` selects two samplers across DRAM/GMI/IO, read/write/atomic classes, and VC fields. `MMEA1_PERFCOUNTER_LO`, `MMEA1_PERFCOUNTER_HI`, and the start of `MMEA1_PERFCOUNTER0_CFG`/`1_CFG` define performance counter data, compare, event select, mode, enable, and clear fields.

## Control Flow and State

There is no runtime control flow in this chunk. The state represented here is hardware state in MMIO registers, accessed elsewhere through AMDGPU register read/write helpers such as `RREG32_SOC15`, `WREG32_SOC15`, and related macros. The header only supplies compile-time constants used to build masks, shifts, and register field values.

Persistence is hardware-defined. Register contents persist according to GPU reset, power-gating, suspend/resume, firmware, and driver initialization behavior, not according to this header. The default reset contract is externalized in `mmhub_9_4_1_default.h`; for example, this chunk's address decoder and SDP fields have matching `mmMMEA1_*_DEFAULT` constants there.

## Dependencies and Integration Points

This file depends only on the C preprocessor. It is guarded by `_mmhub_9_4_1_SH_MASK_HEADER` at file scope and is included by MMHUB v9.4 driver code along with:

- `mmhub/mmhub_9_4_1_offset.h` for register addresses and base indices.
- `mmhub/mmhub_9_4_1_default.h` for reset/default register values.
- SOC15 register access infrastructure in the AMDGPU driver.

The macros in this chunk are useful only when paired with the matching MMHUB 9.4.1 register offsets. The `MMEA1_*` offsets in `mmhub_9_4_1_offset.h` use base index `1` for this instance, so consumers must preserve instance/base-index selection when reading or writing fields.

## Risks

The main risk is silent hardware misprogramming from stale or mismatched generated constants. Adjacent MMHUB generations expose similarly named fields with different bit positions or masks; for example, address normalization interleave fields and SDP request control fields differ across sibling headers. Accidentally mixing `mmhub_9_4_1_sh_mask.h` with a different generation's offset/default header can compile cleanly but write the wrong bits.

Because most fields are dense packed bitfields, incorrect shift/mask use can corrupt neighboring fields in the same register. This is especially risky for address decoder and address normalization registers because bad base, limit, mask, hash, or selector fields can redirect or alias memory traffic. Arbitration and credit fields can also create performance regressions, starvation, deadlock-like stalls, or incorrect QoS behavior if programmed outside hardware expectations.

The chunk is generated-looking and repetitive, so hand edits are risky. Any manual change should be treated as a hardware contract change and checked against the ASIC register source, the offset header, default header, and any firmware programming tables.

## Test Signals

Useful validation is mostly integration and hardware-facing:

- Build coverage for `amdgpu/mmhub_v9_4.c` and any MMHUB 9.4.1 users verifies that macro names remain available and do not collide.
- Register read/write smoke tests on MMHUB 9.4.1 hardware can confirm that fields are programmed through the expected offsets and base index.
- Suspend/resume, GPU reset, GART setup, VM context setup, and multi-MMHUB instance tests are relevant because they exercise MMHUB register programming around persisted hardware state.
- Memory stress, page fault handling, peer/GMI traffic, IO traffic, and performance counter sampling are behavioral signals for the address normalization, decoder, arbitration, SDP, latency, and perf-counter fields defined here.
- Static comparison against generated ASIC register sources, plus consistency checks between `_offset.h`, `_sh_mask.h`, and `_default.h`, is the best low-level guard against drift.

## Chunk Boundary Notes

This chunk starts mid-register at the final mask entries for `MMEA1_DRAM_WR_PRI_QUANT_PRI1` and ends after `MMEA1_PERFCOUNTER1_CFG__ENABLE__SHIFT`, before the remaining fields for `MMEA1_PERFCOUNTER1_CFG` and subsequent MMEA1 registers. Whole-file reconciliation should merge this with neighboring chunks to describe the complete MMHUB 9.4.1 register surface.
