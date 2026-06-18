# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dpcs/dpcs_4_2_3_sh_mask.h lines 31564-33982

## Scope

This chunk is a partial slice of the generated AMD DPCS 4.2.3 register shift/mask header. It covers line 31564 through line 33982 of `dpcs_4_2_3_sh_mask.h`, inside the `DPCSSYS_CR1` address block. The chunk begins in the middle of the `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_PCS_IN` field list and ends in the middle of the `DPCSSYS_CR1_RAWLANE2_DIG_PCS_XF_TXRX_TERM_CTRL_OVRD_IN` field list; both boundary register blocks continue outside this chunk.

The content is data-only C preprocessor metadata: `#define` constants for register bit shifts and bit masks. It contains no functions, structs, enums, inline helpers, storage, or runtime branches. The substantive behavior comes from consumers combining these `__SHIFT` and `_MASK` constants with the corresponding register addresses from `dpcs_4_2_3_offset.h`.

## Purpose

The chunk defines bitfield layouts for raw DPCS lane registers under controller `CR1`. The names describe hardware sub-blocks used by AMD display PHY/PCS programming:

- `RAWLANE0` and `RAWLANE1`: a broad set of PCS, FSM, IRQ, PMA, TX control, RX control, and ATE/test override fields.
- `RAWLANE2`: the start of the same PCS field family, through RX equalization delta IQ and TX/RX termination override fields.

Each register field is represented by a pair of constants:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset to shift a field value into or out of the register.
- `<REGISTER>__<FIELD>_MASK`: the bit mask for the field in the register word.

The masks in this chunk are mostly 16-bit values such as `0x0001L`, `0x0380L`, `0x8000L`, and `0xFFE0L`, matching the DPCS raw-lane register width visible in the field names and reserved ranges.

## Important API Surface

There are no callable APIs, but the macro namespace is the API. Important macro families in this chunk include:

- PCS TX/RX handshake and override fields: `DPCSSYS_CR1_RAWLANE*_DIG_PCS_XF_TX_PCS_IN`, `TX_OVRD_OUT`, `TX_PCS_OUT`, `RX_OVRD_IN`, `RX_OVRD_IN_1`, `RX_PCS_IN`, `RX_PCS_OUT`, and `RX_OVRD_OUT`.
- RX adaptation and equalization fields: `RX_ADAPT_ACK`, `RX_ADAPT_FOM`, `RX_EQ_DELTA_IQ_OVRD_IN`, `RX_EQ_OVRD_IN_1`, `RX_EQ_OVRD_IN_2`, `RX_PH2_CAL`, and EQ fields in `RX_PCS_IN_3`/`RX_PCS_IN_4`.
- TX equalization direction fields read through RX-side registers: `RX_TXPRE_DIR`, `RX_TXMAIN_DIR`, and `RX_TXPOST_DIR`.
- Lane identity and reserved scratch-style fields: `LANE_NUMBER`, `RESERVED_1`, and `RESERVED_2`.
- ATE and manufacturing/test override fields: `ATE_OVRD_IN`, `PCS_XF_ATE_RX_OVRD_IN*`, `PCS_XF_ATE_TX_OVRD_IN*`, and lane-specific reset/request/data-enable override fields.
- FSM state and fast-sequence observation fields for lanes 0 and 1: `DIG_FSM_FSM_OVRD_CTL`, `MEM_ADDR_MON`, `STATUS_MON`, `FAST_RX_*`, `FAST_TX_*`, `FAST_FLAGS`, `CR_LOCK`, `TX_DCC_FLAGS`, `TX_DCC_STATUS`, `OCLA`, `TX_EQ_UPDATE_FLAG`, `CMNCAL_*_STATUS`, and `RX_IQ_PHASE_OFFSET`.
- IRQ latch, clear, and mask fields for lanes 0 and 1: `RESET_RTN_REQ`, `RX_RESET_IRQ`, `RX_REQ_IRQ`, `RX_RATE_IRQ`, `RX_PSTATE_IRQ`, `RX_ADAPT_REQ_IRQ`, `RX_ADAPT_DIS_IRQ`, their `_CLR` registers, `IRQ_MASK`, `IRQ_MASK_2`, lane transceiver mode IRQs, phase-2 calibration IRQs, loopback IRQs, DCC on-demand IRQs, and TX reset/request IRQs.
- PMA interface fields for lanes 0 and 1: `PMA_XF_LANE_OVRD_IN/OUT`, `PMA_XF_SUP_OVRD_IN`, `PMA_XF_SUP_PMA_IN`, `PMA_XF_TX_OVRD_OUT`, `PMA_XF_TX_PMA_IN`, `PMA_XF_RX_OVRD_OUT`, `PMA_XF_RX_PMA_IN`, `PMA_XF_LANE_RTUNE_CTL`, `PMA_XF_MPHY_OVRD_IN/OUT`, and `PMA_XF_RX_ADAPT_OVRD_OUT`.
- TX/RX local control observation and override fields for lanes 0 and 1: `TX_CTL_TX_FSM_CTL`, `TX_CTL_TX_CLK_CTL`, `TX_CTL_TX_DCC_CONT_STATUS`, `TX_CTL_OCLA`, `TX_CTL_UPCS_OCLA`, `RX_CTL_RX_FSM_CTL`, `RX_CTL_RX_LOS_MASK_CTL`, `RX_CTL_RX_DATA_EN_OVRD_CTL`, `RX_CTL_OFFCAN_CONT_STATUS`, `RX_CTL_ADAPT_CONT_STATUS`, and `RX_CTL_UPCS_OCLA`.

The chunk contains 2,145 `#define` lines across 275 register blocks. The register comments show 122 RAWLANE0 blocks, 125 RAWLANE1 blocks, and 27 RAWLANE2 blocks in this line range.

## Control Flow

This header has no intrinsic control flow. Compile-time inclusion exposes numeric constants to the AMD display driver. Runtime behavior is implemented elsewhere by register access helpers that:

1. Select a register address, typically from `dpcs_4_2_3_offset.h`, such as `ixDPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_PCS_IN`.
2. Use the matching mask and shift macro from this header to extract or update a field.
3. Write the resulting word to memory-mapped hardware or read back a hardware status value.

Because this chunk is generated register metadata, the effective control flow is the hardware sequence encoded by the consumer: lane reset/request handshakes, RX adaptation, PMA/PCS override enablement, IRQ clear/mask operations, and status polling. The header only supplies the bit positions needed for those sequences.

## State and Persistence

The macros themselves are immutable compile-time constants and persist only in compiled objects that include the header. The state they address is external hardware state:

- PCS TX/RX request, reset, rate, width, pstate, low-power, MPLL, detect-RX, and data-enable control bits.
- RX adaptation state, figure-of-merit status, equalizer gain/tap/boost/pole values, phase-2 calibration requests, and IQ offset observations.
- FSM status and fast-sequence status bits for lane startup, calibration, adaptation, DCC, MPLL/RCAL common calibration, and OCLA debug.
- IRQ latch, clear, and mask state for RX/TX lane events.
- PMA override/status state for lane mode, receiver/transmitter enablement, MPLL supervisor inputs, MPHY mode, and RX adaptation outputs.
- ATE and manufacturing-test override state for resets, requests, data enable, equalization, beacon, TX amplitude/de-emphasis, and data rate selections.

Reserved fields are explicitly masked as well, which helps callers preserve or clear full register words consistently. Consumers should avoid writing arbitrary values into reserved fields unless the hardware programming guide requires it.

## Dependencies and Integration Points

The direct dependency is the surrounding generated ASIC register ecosystem:

- `dpcs_4_2_3_offset.h` provides matching `ix...` register addresses for the same `DPCSSYS_CR1_RAWLANE*` names.
- `dpcs_4_2_3_sh_mask.h` is included by `drivers/gpu/drm/amd/display/dc/resource/dcn316/dcn316_resource.c`, along with the offset header, making this DPCS register layout part of DCN 3.1.6 resource initialization.
- Sibling versions such as `dpcs_3_1_4_sh_mask.h`, `dpcs_4_2_0_sh_mask.h`, and `dpcs_4_2_2_sh_mask.h` carry equivalent register families for other ASIC revisions. Consumers rely on selecting the header that matches the active ASIC generation.
- Generic AMD display register helpers typically expect a register address macro and field shift/mask macros. This file supplies only the field side of that contract.

The naming convention is the integration contract. If a consumer constructs names through macros, the exact token spelling of `DPCSSYS_CR1_RAWLANE<n>_DIG_<BLOCK>__<FIELD>__SHIFT` and `..._MASK` must match.

## Risks and Edge Cases

- Boundary incompleteness: this chunk starts after the initial `TX_PCS_IN` `RESET`, `REQ`, `PSTATE`, `LPD`, and `WIDTH` shift definitions for RAWLANE0, and ends before the full RAWLANE2 termination-control input family continues with the non-override `TXRX_TERM_CTRL_IN` and later RX EQ/PH2 fields. The merge lane must combine adjacent chunks to understand the full file.
- Hardware drift risk: generated masks must match the DPCS 4.2.3 register specification. A one-bit shift or mask error can silently corrupt lane bring-up, equalization, IRQ handling, test-mode control, or PHY power/state transitions.
- Version-selection risk: these names also exist in older DPCS and DCN headers. Including the wrong version can compile cleanly while programming the wrong bit layout or using the wrong address map.
- Reserved-bit risk: many blocks include `RESERVED_*` masks covering high bits. Consumer write paths must preserve reserved bits or write documented reset values, especially for override registers where enabling an override bit can force PHY behavior.
- Lane-copy risk: RAWLANE0, RAWLANE1, and RAWLANE2 share repeated schemas. Mechanical generation reduces but does not remove the risk of copy/paste or generation drift between lane instances.
- IRQ semantics risk: IRQ and IRQ clear registers are separated. Accidentally using latch masks against clear registers, or vice versa, can miss hardware events or clear events before the driver observes them.
- Override-enable risk: fields commonly appear as value/enable pairs, for example `*_OVRD_VAL` plus `*_OVRD_EN`. Setting values without enables has no effect; setting enables with stale values can force bad lane configuration.

## Test Signals

Useful validation signals for this chunk are mostly build-time and hardware/integration oriented:

- Compile the AMD display driver configuration that includes `dcn316_resource.c`; missing or renamed macros should fail at compile time.
- Compare generated `dpcs_4_2_3_sh_mask.h` and `dpcs_4_2_3_offset.h` against the authoritative ASIC register database for DPCS 4.2.3.
- Run static consistency checks that every non-reserved field has both a `__SHIFT` and `_MASK`, and that each mask equals the expected width shifted by the shift value.
- Check lane schema consistency across RAWLANE0, RAWLANE1, and RAWLANE2 once adjacent chunks are available.
- Exercise display link bring-up, link training, power-state transitions, RX adaptation, and PHY reset paths on DCN316 hardware using debug logs or register dumps.
- Exercise IRQ paths by verifying RX reset/request/rate/pstate/adapt, phase-2 calibration, loopback, DCC on-demand, and TX reset/request events latch, mask, and clear as expected.
- For ATE/test paths, validate only in controlled manufacturing or PHY validation contexts because these overrides can intentionally bypass normal PCS/PMA sequencing.

## Cross-Chunk Notes

The final per-file report should reconcile this chunk with adjacent parts of `dpcs_4_2_3_sh_mask.h` to capture:

- The complete `DPCSSYS_CR1_RAWLANE0_DIG_PCS_XF_TX_PCS_IN` block that begins before line 31564.
- The remainder of RAWLANE2 after `TXRX_TERM_CTRL_OVRD_IN`, including `TXRX_TERM_CTRL_IN`, RX override output, RX EQ override, PH2 calibration, FSM, IRQ, PMA, TX/RX control, and ATE blocks.
- Other DPCS controller/address blocks outside `CR1`, since this chunk only covers one controller's raw-lane region.
