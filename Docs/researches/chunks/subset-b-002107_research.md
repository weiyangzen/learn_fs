# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h lines 44296-46513

## Purpose

This chunk is a generated DCN 3.5.1 register field shift/mask slice for AMD display hardware. It does not implement executable logic; it supplies preprocessor constants that higher-level AMDGPU display code uses to compose, update, poll, and decode memory-mapped display register fields without hard-coding bit positions.

The line range spans several related display blocks:

- The tail of `MPCC_OGAM3` output gamma and gamut-remap definitions, including RAM-B exponent region descriptors and A/B double-buffered gamut-remap coefficients.
- Core `MPC` definitions for clock/reset, CRC capture, pending-update status, DPP/OPP/DWB routing, denormalization clamps, and output color-space conversion for four outputs.
- Display perfmon blocks `DC_PERFMON22` and `DC_PERFMON23`.
- Link/output packet blocks `AFMT5`, `VPG9`, `DME9`, `HPO_TOP`, and `DP_STREAM_MAPPER_CONTROL0..3`.
- Four repeated ABM instances, `ABM0..ABM3`, covering backlight PWM levels, ambient backlight control, ACE curves, histogram/luma statistics, frame-synchronized update locks, and histogram result registers.
- The beginning of `DPIA_MU_RBBMIF` timeout/status fields. The requested line range ends at `DPIA_MU_RBBMIF_STATUS__RBBMIF_INVALID_ACCESS_ADDR__SHIFT`; later status masks and AZ controller definitions are outside this chunk.

## Important APIs, Types, and Register Families

The public surface here is macro-only. Each field is represented by two macro families:

- `REGISTER__FIELD__SHIFT` gives the bit offset used when packing/unpacking field values.
- `REGISTER__FIELD_MASK` gives the field mask used by `REG_SET`, `REG_UPDATE`, `REG_GET`, and similar AMD display register helper macros.

Important register families in this chunk:

- `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_26_27` through `_32_33` describe pairs of output-gamma RAM-B expansion regions. Each region has a 9-bit LUT offset and a 3-bit segment count. The chunk starts mid-register-family, so region 26's shift definitions are in the previous chunk while its masks appear here.
- `MPCC_OGAM3_MPCC_GAMUT_REMAP_*` and `MPCC_OGAM3_MPC_GAMUT_REMAP_Cxx_Cyy_{A,B}` define the gamut-remap matrix path for MPCC OGAM instance 3. The `MODE_CURRENT` bitfield is readback/status; A/B coefficient banks indicate double-buffered hardware programming.
- `MPC_CLOCK_CONTROL`, `MPC_SOFT_RESET`, `MPC_CRC_*`, `MPC_DPP_PENDING_STATUS`, and `MPC_PENDING_STATUS_MISC` expose global MPC operation, diagnostics, and update synchronization. CRC selection can target DPP, OPP, or DWB sources, and result registers split A/R, G/B, and C channels into 16-bit fields.
- `ADR_CFG_CUR_VUPDATE_LOCK_SET{0..3}`, `ADR_CFG_VUPDATE_LOCK_SET{0..3}`, `ADR_VUPDATE_LOCK_SET{0..3}`, `CFG_VUPDATE_LOCK_SET{0..3}`, and `CUR_VUPDATE_LOCK_SET{0..3}` define per-pipe vertical-update lock sets for atomic cursor/address/config updates.
- `MPC_DWB0_MUX` and `MPC_OUT{0..3}_MUX` define output routing and flow/rate control. Output mux fields select source paths, expose overflow errors, and include error-ack bits.
- `MPC_OUT{0..3}_DENORM_*`, `MPC_OUT_CSC_COEF_FORMAT`, and `MPC_OUT{0..3}_CSC_*` define denormalization clamps and output CSC matrices. Matrix coefficients are split into 16-bit pairs and A/B banks.
- `DC_PERFMON22_*` and `DC_PERFMON23_*` define event selection, counter state, run gating, count-off interrupts, interrupt ack/status bits, and high/low counter readback.
- `AFMT5_*` defines audio formatter controls: VBI packet pacing, audio packet layout/channel controls, HDMI/DP audio stream ID, IEC 60958 channel-status words, audio CRC generation/result, ramp/test controls, FIFO overflow status/ack, infoframe update, source selection, and memory power state.
- `VPG9_*` defines video packet generator generic packet byte access, frame/immediate update controls for generic packets 0-14, pending flags, conflict status/clear, memory power state, ISRC packet data, and MPEG infoframe update.
- `DME9_*` defines display metadata engine enable, HUBP requester ID, stream type, double-buffer pending/taken/clear, missed-transmission status/clear, and memory power controls.
- `HPO_TOP_*` defines high-performance output clock gating controls for display, SoC, HDMI stream/char, DP stream, and symbol clocks plus top-level HPO IO enable.
- `DP_STREAM_MAPPER_CONTROL{0..3}` maps each stream to a link target through a 3-bit target field.
- `ABM{0..3}_*` repeats the adaptive backlight management register layout for four instances. Each instance includes PWM level registers, ABM enable/bypass, IPS color-space coefficient selection, ACE offset/slope/threshold programming, missed-frame flags, HGLS read-progress and read-missed flags, histogram/luma statistics, sample-rate controls, histogram bin shift tables, 24 histogram result registers, and master-lock controls.
- `DPIA_MU_RBBMIF_TIMEOUT_CTRL`, `DPIA_MU_RBBMIF_TIMEOUT_CTRL2`, and the first three `DPIA_MU_RBBMIF_STATUS` shift definitions expose timeout delay/hold, timeout disable, invalid-access flag/type/address field positions for the DPIA memory-unit RBBM interface.

## Control Flow

There is no C control flow in this chunk. Runtime control flow appears in consumers that include this generated header and pass these constants into register helper macros.

The implied hardware programming flow is:

1. Driver resource construction selects the DCN 3.5.1 register set for matching ASICs and includes `dcn_3_5_1_sh_mask.h`.
2. Display block constructors build per-block register, shift, and mask tables from generated macros.
3. Runtime display code uses those tables to update bitfields during mode set, pipe programming, CRC capture, audio/video packet updates, ABM programming, and diagnostics.
4. Status fields in this chunk are polled or read back to decide whether an update took effect, whether a double-buffered write is pending, whether a CRC/result is ready, or whether an error condition must be acknowledged.

Several field groups imply important sequencing:

- `*_LOCK`, `*_REG_UPDATE_PENDING`, `*_UPDATE_AT_FRAME_START`, and `*_READBACK_DB_REG_VALUE_EN` fields on MPCC/ABM/VPG paths indicate double-buffered or frame-bound programming. Writers must lock or stage values, request update at a safe boundary, then wait for pending bits to clear before assuming hardware has latched the new value.
- `MPC_CRC_CTRL` has enable, continuous/one-shot pending, source select, update-enabled, and update-lock fields. CRC tests must sequence source selection before enabling capture and read result fields only after the relevant pending/update state is resolved.
- `MPC_OUT*_MUX` includes rate-control overflow and error-ack fields. Error handling must preserve routing fields while writing ack bits.
- `AFMT5` and `VPG9` packet update bits are separate from pending/status bits; packet payload writes through indexed byte registers should be followed by frame or immediate update requests and checked for conflict/pending status.
- `DME9_DME_CONTROL` double-buffer and missed-transmission bits require clear-on-write style handling for taken/missed flags.

## State and Persistence Behavior

The macros describe persistent MMIO register fields. Values programmed through these fields live in display hardware state until overwritten, reset, or power-gated. They are not filesystem state and do not persist across GPU reset or relevant display block power loss.

Stateful categories in this chunk:

- Latched configuration: color matrices, denorm clamps, mux selections, ABM PWM parameters, ACE thresholds/slopes, sample-rate values, audio packet metadata, and stream-to-link mapper targets.
- Double-buffered/frame-synchronous state: MPCC gamut-remap modes and coefficient banks, MPC pending-update status, ABM group locks, VPG packet updates, AFMT infoframe/audio channel-status updates, and DME metadata double-buffer controls.
- Diagnostic/readback state: MPC CRC result registers, DC perfmon counters and interrupt status, AFMT audio CRC/status, VPG conflict status, ABM histogram/luma readbacks, read-in-progress/missed-frame bits, and DPIA RBBMIF invalid-access/timeout status.
- Power/clock state: MPC/HPO clock gate disable fields, AFMT/VPG/DME memory power control fields, and ABM lock/update-at-frame-start fields that interact with display timing.

The line range contains a partial `DPIA_MU_RBBMIF_STATUS` definition. Any consumer needing complete DPIA status decode must use the full header, not just this chunk, because this chunk includes only three status shifts and not the remaining status masks.

## Dependencies and Integration Points

This header is generated from AMD ASIC register metadata and is tightly coupled to matching register-offset headers, block-specific register table macros, and AMD display helper macros. It depends on convention rather than C symbols: the macro names must match register table initializers in DCN block code.

Observed integration points in the surrounding tree include:

- DC resource and block constructors for DCN 3.5/3.5.1 include generated `dcn_3_5_1_sh_mask.h` and populate per-block shift/mask structs for MPC, ABM, AFMT/VPG, DME, HPO, perfmon, and related display engines.
- `dce_abm.h` uses `ABM_SF(...)` style macros against ABM register field names matching the ABM families in this chunk. The repeated `ABM0`-based field lists in common ABM code are adapted across ABM instances by generated register tables.
- CRC register names such as `MPC_CRC_CTRL` are referenced from display hardware sequencing and resource definitions. These constants support debugfs/KMS CRC capture and validation paths.
- `dmub/src/dmub_dcn351.c` includes the same generated header for DCN 3.5.1 register initialization, although this specific chunk is mostly display-pipe/audio/video/backlight rather than DMUB mailbox state.
- Link/audio/video programming code relies on AFMT, VPG, DME, HPO, and DP stream mapper field positions to align audio infoframes, generic packets, metadata, and link routing with stream encoder and link-encoder state.

## Risks and Edge Cases

- This is generated hardware-interface code; manual edits are high risk. A one-bit shift or mask error can silently misprogram unrelated bits in a display register.
- The chunk begins mid-family at `MPCC_OGAM3_MPCC_OGAM_RAMB_REGION_26_27`, where some shift definitions for region 26 are outside the chunk. Research consumers should merge adjacent chunks before making final per-file conclusions.
- The chunk ends mid-register at `DPIA_MU_RBBMIF_STATUS`; the remaining status fields and masks are outside this chunk. Treating this chunk as a complete DPIA status definition would miss timeout readback and clear bits.
- Several registers include write-one-to-clear or ack-like fields (`*_ACK`, `*_CLEAR`, `*_CLR`, error ack, missed-frame clear). Register update helpers must avoid read-modify-write patterns that accidentally re-clear status bits or preserve stale ack bits.
- Double-buffered fields can be timing-sensitive. Programming ABM, VPG, AFMT, DME, or gamut-remap fields without respecting lock, pending, and frame-start bits can cause missed frames, stale readback, or visible color/backlight artifacts.
- `MPC_SOFT_RESET` and clock/memory-power fields affect shared display blocks. Incorrect writes may reset active MPCC/SFR/SFT paths, gate clocks while a block is in use, or leave memory in a forced low-power state.
- Repeated instance blocks (`MPC_OUT0..3`, `ABM0..3`, `DP_STREAM_MAPPER_CONTROL0..3`) invite copy/paste mistakes in table generation. Instance N register names must map to instance N offsets.
- Mask widths encode hardware limits: e.g. 16-bit CSC coefficients, 10-bit luma thresholds, 17-bit PWM levels, 24-bit pixel counts, 32-bit histogram results, and 3-bit DP link targets. Higher-level code must clamp or validate values before packing them.

## Test Signals

Useful validation signals for consumers of these macros:

- Build coverage for DCN 3.5.1 display code with `dcn_3_5_1_sh_mask.h` included catches renamed or missing macro fields at compile time.
- KMS CRC tests and debugfs CRC capture should exercise `MPC_CRC_CTRL`, source selection, pending bits, and result field extraction.
- Atomic modeset and plane/cursor update tests should verify that `MPC_DPP_PENDING_STATUS`, `MPC_PENDING_STATUS_MISC`, and vertical-update lock-set fields converge after commits.
- Color-management tests should exercise MPCC OGAM/gamut-remap and MPC output CSC programming, including A/B double-buffer transitions and coefficient-format selection.
- Audio over HDMI/DP tests should verify AFMT packet controls, IEC 60958 channel-status programming, audio CRC completion, FIFO overflow handling, and infoframe update behavior.
- HDR/metadata and infoframe tests should exercise VPG generic packet updates, VPG conflict clear, MPEG/ISRC packet programming, and DME metadata double-buffer/missed-transmission flags.
- DisplayPort/HPO link tests should confirm DP stream mapper target selection and HPO clock/IO enable behavior during link bring-up and teardown.
- Backlight/ABM tests should verify PWM level programming, ambient/user/target/current/final duty-cycle readback, ABM enable/bypass, frame-start updates, missed-frame flags, luma statistics, and histogram result stability across all four ABM instances.
- Perf counter diagnostics should confirm `DC_PERFMON22` and `DC_PERFMON23` event selection, run gating, interrupt status/ack behavior, and high/low counter readback.
- Error-injection or register-access diagnostics should validate the complete DPIA RBBMIF status register using the full header, since this chunk only contains the first status shift fields.
