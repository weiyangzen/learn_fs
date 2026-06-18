# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 1-2381

## Scope

This chunk is the opening range of the generated AMD DCN 4.1.0 shift/mask header. It contains preprocessor constants for register-field bit positions and masks, not executable C code. The range starts with the include guard and the first DCCG/DENTIST clock-control definitions, then covers DC clock generation, pixel/stream/symbol clock routing, DCCG gate disables, DPP/DSC/DP/HDMI/audio DTO controls, DCCG vsync counters, FGSEC secure-group metadata, DMU RBBMIF timeout/status fields, GPU timer capture fields, and a long interrupt-status chain through DMCUB, DSC, DPIA, DCPG, HUBP, OTG, DIG, AUX/I2C, HPD, audio, DCIO, and DCCG interrupt destination fields.

The assigned range ends mid-register at `DCPG_INTERRUPT_DEST2`: lines 2362-2381 define the power-domain interrupt destination shifts for domains 16-25, while the matching masks begin on line 2382 outside this chunk.

## Purpose

The purpose of this header range is to encode the DCN 4.1 hardware bit layout consumed by the AMD display driver register access layer. Each pair of `__SHIFT` and `_MASK` macros maps a named hardware field to its bit offset and width in a 32-bit MMIO register.

The covered hardware areas are:

- DCCG and DENTIST clock programming: `DENTIST_DISPCLK_CNTL`, DPPCLK/DSCCLK/DP DTO registers, DP/HDMI stream clocks, DTBCLK, AOMCLK, ref clocks, pixel-clock resync controls, and time-base divisors.
- Clock gating and resets: `DCCG_GATE_DISABLE_CNTL*`, `*_CGTT_BLK_CTRL_REG`, `DCCG_GLOBAL_FGCG_REP_CNTL`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, `DCCG_SOFT_RESET`, `FORCE_SYMCLK_DISABLE`, and related root/leaf gate fields.
- Link and stream clock routing: `SYMCLKA` through `SYMCLKG`, `SYMCLK32_SE/LE`, `PHY*SYMCLK_CLOCK_CNTL`, `HDMICHARCLK*`, `HDMISTREAMCLK*`, and `DPSTREAMCLK_CNTL`.
- OTG pixel-rate programming: `OTG0_PIXEL_RATE_CNTL` through `OTG5_PIXEL_RATE_CNTL`, `DP_DTO*_PHASE`, `DP_DTO*_MODULO`, `OTG*_PHYPLL_PIXEL_RATE_CNTL`, and `OTG_PIXEL_RATE_DIV`.
- Security and management fabric fields: `SECURE_GROUP0_CONFIG` through `SECURE_GROUP7_CONFIG`, `SECURE_INTERRUPT0_INFO*`, `DMCUB_RBBMIF_SEC_CNTL`, and RBBMIF timeout/status/disable registers.
- Timing and interrupt telemetry: GPU timer start-position and readback registers, DCCG vsync latch values/control/interrupts, `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE*`, and interrupt destination registers for DCCG, DMU, and DCPG.

Correctness here determines whether DCN 4.1 display code writes the intended clock, reset, power, interrupt, and diagnostic bits when using `REG_GET`, `REG_UPDATE`, `REG_SET`, `REG_WAIT`, and table-driven register helpers.

## Important APIs, Types, And Macros

This chunk declares no functions or C types. Its API is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit.
- `<REGISTER>__<FIELD>_MASK` gives the bit mask used to isolate or compose that field.
- Address-block comments, such as `dcn_dcec_dccg_dccg_dispdec`, `dcn_dcec_dmu_fgsec_dispdec`, `dcn_dcec_dmu_rbbmif_dispdec`, and `dcn_dcec_dmu_ihc_dispdec`, identify hardware blocks.

Important register families in the range include:

- DCCG clocks: `DENTIST_DISPCLK_CNTL`, `DPPCLK_CTRL`, `DPPCLK_DTO_CTRL`, `DPPCLK{0..5}_DTO_PARAM`, `DSCCLK_DTO_CTRL`, `DSCCLK{0..5}_DTO_PARAM`, `DP_DTO_DBUF_EN`, `DP_DTO{0..5}_{PHASE,MODULO}`, `DCCG_AUDIO_DTO_SOURCE`, and `DCCG_AUDIO_DTO{0,1,2}_{PHASE,MODULE/MODULO}`.
- Stream/link clocks: `DPSTREAMCLK_CNTL`, `HDMISTREAMCLK_CNTL`, `HDMISTREAMCLK0_DTO_PARAM`, `HDMICHARCLK{0..5}_CLOCK_CNTL`, `SYMCLK{A..G}_CLOCK_ENABLE`, `SYMCLK32_SE_CNTL`, `SYMCLK32_LE_CNTL`, and `PHY{A..G}SYMCLK_CLOCK_CNTL`.
- Clock gating and reset: `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2` through `DCCG_GATE_DISABLE_CNTL6`, `DISPCLK_CGTT_BLK_CTRL_REG`, `DPPCLK_CGTT_BLK_CTRL_REG`, `DPREFCLK_CGTT_BLK_CTRL_REG`, `REFCLK_CGTT_BLK_CTRL_REG`, `SOCCLK_CGTT_BLK_CTRL_REG`, `SYMCLK_CGTT_BLK_CTRL_REG`, `DCCG_SOFT_RESET`, and `DCCG_DISP_CNTL_REG`.
- Timing and counters: `MICROSECOND_TIME_BASE_DIV`, `MILLISECOND_TIME_BASE_DIV`, `DISPCLK_FREQ_CHANGE_CNTL`, `DCCG_VSYNC_CNT_CTRL`, `DCCG_VSYNC_CNT_INT_CTRL`, `DCCG_VSYNC_OTG{0..5}_LATCH_VALUE`, `DC_GPU_TIMER_READ`, `DC_GPU_TIMER_READ_CNTL`, and `DC_GPU_TIMER_START_POSITION_*`.
- DMU/RBBMIF/security: `SECURE_GROUP*`, `SECURE_INTERRUPT0_INFO*`, `DMCUB_RBBMIF_SEC_CNTL`, `RBBMIF_TIMEOUT`, `RBBMIF_STATUS`, `RBBMIF_STATUS_2`, `RBBMIF_INT_STATUS`, `RBBMIF_TIMEOUT_DIS`, `RBBMIF_TIMEOUT_DIS_2`, and `RBBMIF_STATUS_FLAG`.
- Interrupt map: `DISP_INTERRUPT_STATUS`, `DISP_INTERRUPT_STATUS_CONTINUE` through `DISP_INTERRUPT_STATUS_CONTINUE25`, `DCCG_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST`, `DMU_INTERRUPT_DEST2`, `DCPG_INTERRUPT_DEST`, and the beginning of `DCPG_INTERRUPT_DEST2`.

Concrete consumers in this tree pair this file with `dcn_4_1_0_offset.h`. `display/dc/resource/dcn401/dcn401_resource.c` builds `dccg_shift` and `dccg_mask` from `DCCG_MASK_SH_LIST_DCN401(__SHIFT)` and `DCCG_MASK_SH_LIST_DCN401(_MASK)`. `display/dc/dccg/dcn401/dcn401_dccg.h` lists many of the DCCG fields from this chunk for the `struct dccg_shift` and `struct dccg_mask` tables. `display/dc/resource/dcn401/dcn401_resource.c` also includes chunk registers in hardware-sequencer lists, including `DCCG_GATE_DISABLE_CNTL`, `DCCG_GATE_DISABLE_CNTL2`, `DC_MEM_GLOBAL_PWR_REQ_CNTL`, `OTG*_PIXEL_RATE_CNTL`, `OTG*_PHYPLL_PIXEL_RATE_CNTL`, `MICROSECOND_TIME_BASE_DIV`, `MILLISECOND_TIME_BASE_DIV`, `DISPCLK_FREQ_CHANGE_CNTL`, `RBBMIF_TIMEOUT_DIS`, and `RBBMIF_TIMEOUT_DIS_2`. `display/dmub/src/dmub_dcn401.c` includes this header for DMUB register field extraction, although most directly listed DMUB fields are outside this exact line range.

## Control Flow

There is no local control flow in this header. Runtime behavior is indirect:

1. DCN 4.1 resource setup includes `dcn_4_1_0_offset.h` and this shift/mask header.
2. Register-list macros such as `SR`, `SRII`, `DCCG_SF`, `DCCG_SFI`, and `DCCG_SFII` expand symbol names from this header into register, shift, and mask tables.
3. Component code stores those tables in structures such as `dccg_regs`, `dccg_shift`, `dccg_mask`, and hardware-sequencer register tables.
4. Runtime code calls `REG_GET`, `REG_UPDATE`, `REG_SET_2`, `REG_WRITE`, and `REG_WAIT`; those helpers use the generated shifts and masks to read or write individual MMIO fields.

Examples from nearby code paths:

- `dcn401_clk_mgr.c` reads and updates `DENTIST_DISPCLK_CNTL.DENTIST_DISPCLK_WDIVIDER` and waits on `DENTIST_DISPCLK_CHG_DONE` when programming display clock dividers.
- DCCG functions declared in `dcn401_dccg.h` program DPP DTOs, DSC clocks, DP stream clocks, symbol clocks, DTB clock source selection, and pixel-rate dividers using fields defined in this range.
- Hardware sequencing uses `RBBMIF_TIMEOUT_DIS` and `RBBMIF_TIMEOUT_DIS_2` to disable timeout clients, following inherited DCE/DCN patterns that write all ones to those registers.
- Interrupt handling and source-ID mapping rely on the `DISP_INTERRUPT_STATUS_CONTINUE*` bit layout to route OTG, HUBP, DMCUB, DCPG, AUX/HPD, HDCP, audio, DSC, DPIA, and other display events to the expected interrupt source.

## State And Persistence Behavior

The file itself has no software state. It describes persistent hardware state in DCN 4.1 registers:

- Clock-selection and enable fields persist until reprogrammed or reset. This includes DTO phase/modulo values, DTO enables, stream clock source selects, symbol clock source selects, PHYPLL pixel-rate sources, DPPCLK enables, and DENTIST divider state.
- Gate-disable, reset, and power-request fields can keep clocks, roots, or memory requests forced on/off. These fields are sensitive during display bring-up, link training, idle entry/exit, and power-gated resume.
- Time-base and GPU timer fields persist as diagnostic/timing configuration, while readback/latch registers expose sampled hardware timing state.
- RBBMIF timeout registers hold timeout delays, client-disable masks, fault/status indicators, invalid access metadata, and interrupt status/ack/mask fields.
- Interrupt status registers are chained with `*_CONTINUE*` bits. Many status bits are sticky or interrupt-latched in hardware, while destination registers choose where events are delivered. Incorrect masks can cause an event to be missed, falsely reported, or routed to the wrong handler.
- Security fields describe secure read/write levels, trust levels, source IDs, secure interrupt metadata, and DMCUB RBBMIF access controls. Misprogramming can change access enforcement or fault attribution.

## Dependencies And Integration Points

Primary dependencies:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h` supplies offsets and base indices for the same register names.
- AMD display register helper macros depend on exact generated names. Any rename or mismatch breaks macro expansion or, worse, compiles into wrong field operations if a stale symbol still exists.
- `display/dc/dccg/dcn401/dcn401_dccg.h` is the main DCCG field-list consumer for this chunk.
- `display/dc/resource/dcn401/dcn401_resource.c` builds the DCN 4.1 DCCG and hardware-sequencer tables from the generated fields.
- `display/dc/clk_mgr/dcn401/dcn401_clk_mgr.c` consumes DENTIST fields for clock programming.
- `display/dmub/src/dmub_dcn401.c` includes this header and the matching offset header to build DMUB register tables.
- `include/ivsrcid/dcn/irqsrcs_dcn_1_0.h` documents and maps many interrupt source IDs to `DISP_INTERRUPT_STATUS*` fields that appear in this range.

The chunk is also cross-generation sensitive. Many DCCG, RBBMIF, GPU timer, and interrupt-chain names exist in older DCN 3.x headers, but DCN 4.1 adds or reshapes fields such as 4-pipe DCCG lists, extended interrupt continues, DMCUB/DPIA/MMHUBBUB interrupt bits, and DCPG domains 16-25. Consumers must use the DCN 4.1 offset and shift/mask tables together.

## Risks

- A wrong shift/mask can compile cleanly while writing the wrong hardware bits. Clock, reset, and interrupt fields are especially high impact because adjacent bits often control unrelated display pipelines or links.
- Clock-divider and DTO field drift can cause bad pixel clocks, unstable stream clocks, DSC clock mismatch, audio DTO errors, FIFO errors, link-training failures, or display blanking.
- Gate-disable fields are split across several `DCCG_GATE_DISABLE_CNTL*` registers and root/leaf clock domains. A one-bit mistake can leave a clock gated during active display or forced on during low-power states.
- The interrupt chain depends on continuation bits at bit 31. Incorrect `DISP_INTERRUPT_STATUS_CONTINUE*` masks can stop status traversal or make software attribute events to the wrong OTG, DIG, HPD/AUX, HUBP, DMCUB, DCPG, DSC, DPIA, or audio source.
- Several field names encode instance numbers in both register and field names, for example `OTG3_PIXEL_RATE_CNTL__DP_DTO3_ENABLE` and `DISP_INTERRUPT_STATUS_CONTINUE17__HUBP7_IHC_FLIP_INTERRUPT`. Instance skew can silently route a pipe/link event to the wrong instance.
- RBBMIF timeout and invalid-access fields are diagnostic and control-sensitive. Bad masks can hide timeout clients, fail to acknowledge a timeout, mask real faults, or report the wrong offending address/client.
- Security fields in `SECURE_GROUP*`, `SECURE_INTERRUPT0_INFO*`, and `DMCUB_RBBMIF_SEC_CNTL` affect secure/trusted access classification. Incorrect values can break firmware access or weaken isolation assumptions.
- The chunk boundary splits `DCPG_INTERRUPT_DEST2`; merge/reconciliation must combine this document with the following chunk before making complete conclusions about that register.

## Test Signals

Useful validation for changes touching this generated header or its generator:

- Build DCN 4.1 display support with `dcn401_resource.c`, `dcn401_dccg.h`, `dcn401_clk_mgr.c`, and `dmub_dcn401.c` enabled. Missing shift/mask names should fail at compile time in table initializers or accessor macros.
- Compare the file mechanically against the trusted vendor register XML/header output for DCN 4.1. For generated shift/mask files, source-of-truth diffing is one of the strongest signals.
- Boot/probe on DCN 4.1 hardware and verify display bring-up, DMUB initialization, RBBMIF timeout disable programming, and DCCG table construction without MMIO faults.
- Clock programming tests: exercise DISPCLK changes, DPPCLK DTO updates, DSCCLK/DSC configuration, DP DTO phase/modulo programming, HDMI stream/character clocks, and pixel-rate dividers. Check for `REG_WAIT` timeout on `DENTIST_DISPCLK_CHG_DONE` and for DIO FIFO error counters.
- Link and stream tests across DP, HDMI, HPO stream encoders, multiple OTGs, DSC enabled/disabled, and different PHY/symbol clock selections.
- Low-power tests across idle, clock gating, display off/on, suspend/resume, and memory power request transitions. These exercise DCCG gate-disable, CGTT delay, soft-reset, and global power-request fields.
- Interrupt tests for HPD/RX, AUX/I2C, HDCP, OTG vupdate/vstartup/vready/DRR, HUBP vblank/vline/timeout/flip, DCPG power up/down, DMCUB inbox/outbox/timer/fault, DSC core errors, DPIA, and DCCG vsync latch interrupts.
- RBBMIF fault-injection or timeout diagnostics that confirm timeout client bits, status flags, invalid-access capture, ack/mask behavior, and interrupt routing.

## Notes For Merge Lane

This is only the first 2,381 lines of a 145,870-line generated header. The final per-file report should merge this with later chunks before drawing whole-file conclusions. This range is mostly complete for the initial DCCG, DMU RBBMIF, GPU timer, and interrupt-chain groups, but it ends inside `DCPG_INTERRUPT_DEST2` before the matching mask definitions.
