# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 49697-52181

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask slice. It contains no executable logic; it publishes preprocessor constants that describe bit positions and masks for display hardware registers. Consumers pair these constants with the matching DCN 4.1.0 offset header and AMD display register helpers to pack and unpack MMIO fields.

The range contains 2,094 `#define` entries: 1,050 `__SHIFT` macros and 1,044 `_MASK` macros, plus 19 generated `addressBlock` markers. The mismatch is caused by chunk boundaries: the first line starts inside `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL4`, whose preceding comment is just outside the requested range, and the final line stops at `RDPCSTX1_RDPCSTX_PHY_CNTL0__RDPCS_SRAM_BYPASS_MASK` while `RDPCSTX1_RDPCSTX_PHY_CNTL1` begins immediately afterward.

Although the path is under a local `ceph-client` tree, this file is AMDGPU display hardware metadata. The chunk covers the tail of HPO DisplayPort SYM32 stream encoder instance 3, HPO DP link encoder clock and DPHY SYM32 instances 0-3, DLPC and DPCSSYS control-register windows, all visible RDPCSTX0 transmitter control/PHY/fuse fields, and the beginning of RDPCSTX1.

## Important APIs, Types, And Macros

There are no functions, structs, enums, global variables, includes, locks, or allocation paths in this slice. Its public interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a hardware register field.
- `<REGISTER>__<FIELD>_MASK`: mask for extracting, testing, or updating that field.

The main register families in this chunk are:

- `DP_SYM32_ENC3_*`: stream encoder instance 3 secondary-data-packet and video controls. The chunk starts with GSP control slots 4-14, then covers SDP global enable/control, audio-control fields, metadata packet scheduling, SDP framing, ATP controls, idle pattern enable, MSA/VBID/video-stream controls, panel replay, video CRC controls/results/status, symbol-count controls, ALPM sleep/wake/request/ready/hardware-mode/status/start/interrupt fields, memory power control, and a spare register.
- `DP_LINK_ENC0..3_*`: per-HPO-link encoder clock control and spare fields. Each visible link encoder exposes `DP_LINK_ENC_CLOCK_EN` and `DP_LINK_ENC_CLOCK_ON_SYMCLK32`.
- `DP_DPHY_SYM320..323_*`: four repeated HPO DP DPHY SYM32 layouts. Each instance includes core enable/reset/precoder/mode/lane/output control, status and pending bits, encryption values, SAT update, VC rate numerator/denominator fields for VCs 0-5, SAT source/slot-count programming and readback for VCs 0-5, eDP mode and ASSR seeds, ALPM sleep/wake timing, test-pattern selection/PRBS/custom pattern registers, error status, default overrides, and LLCP/cycle symbol counters.
- `DLPC_*`: display low-power controller fields for enablement, power-up trigger enable/clear/status, OTG resync trigger enable/clear/status, DCN ZSC/LONO power-up trigger enable/clear/status, current-count/snapshot/event values, spare storage, and counter initialization.
- `DPCSSYS_CR0..3_*`: four 16-bit CR address/data access windows named with `RDPCS_TX_CR_ADDR` and `RDPCS_TX_CR_DATA`, used as indexed control-register sideband access into DPCS/RDPCS transmitter state.
- `RDPCSTX0_*`: a full visible transmitter block for DPCS0 transmitter 0. It covers CBUS/SRAM/TX soft reset, TX common-mode override, lane bit-order and packing controls, interrupt masking, PLL update request/pending, FIFO lane enables/start/delay, clock gating/enables/status for PHY/TX/SRAM/OCLA clocks, interrupt status/clear/mask fields, PLL update data, CR address/data, SRAM power controls, scratch/spare registers, CR-convert FIFO status, PHY encoding type, DPALT spare, pattern detect, beacon/TX-data enable delays, PHY controls 0-17, PHY fuse registers 0-3, RX load values, byte-order changes, and PLL override address/data.
- `RDPCSTX1_*`: the next transmitter block begins and repeats the common RDPCSTX control, clock, interrupt, PLL update, CR, SRAM, scratch/spare, pattern-detect, delay, and `PHY_CNTL0` field layout before the chunk boundary.

## Control Flow

This header has no runtime control flow. The effective control flow is in AMDGPU display consumers:

1. DCN 4.1.0 support includes this shift/mask header with the matching offset header.
2. Register-list macros select the instance-specific symbolic register names for HPO DP link encoders, stream encoders, DLPC/DPCSSYS blocks, and RDPCS transmitters.
3. Constructors store the offset, shift, and mask tables in block-specific objects.
4. Runtime code calls helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, `REG_UPDATE`, and `REG_WAIT`; the helpers use these generated masks and shifts to touch individual MMIO fields.

The macros do not encode sequencing. Callers must still order link encoder clock enablement, DPHY reset/enable, lane/mode setup, stream allocation table programming, SAT update and pending polling, test-pattern setup, ALPM entry/exit, SDP/audio/metadata packet scheduling, DLPC trigger clearing, CR-sideband operations, transmitter FIFO/PLL/PHY programming, and interrupt acknowledgement according to hardware rules.

## State And Persistence Behavior

This chunk stores no software state and writes no persistent files. It describes state that lives in DCN display hardware registers.

The stream-encoder state represented here includes GSP one-shot and continuous transmission bits, payload size, SOF reference, line number, deadline-missed/pending/double-buffer-pending status, audio SDP selection and audio pipeline metadata, metadata packet line reference, SDP framing, idle patterns, MSA/VBID/video stream behavior, panel replay control, video CRC capture, base-symbol counters, ALPM sleep/wake requests and pending bits, ALPM hardware-mode frame state, wake interrupt status/clear, and memory power controls.

The HPO DPHY state includes link enable/reset, precoder enable, link mode, lane count, output mode, current status, rate/SAT update pending bits, scheduler and common-mode status, link encryption enable/disable values, VC rate and slot allocation programming, active SAT readback, eDP/ASSR settings, ALPM timing values, PRBS/custom test patterns, link error status, frame interval overrides, and LLCP/cycle counters.

The DLPC and DPCSSYS state includes low-power trigger enable/status/clear bits, current/snapshot/event counter values, counter initialization, and sideband CR address/data windows. The RDPCSTX state includes reset lines, FIFO and lane packing state, clock-gating state, interrupt latches and masks, PLL update request/pending/data/override state, SRAM power state, pattern-detect status, PHY reset and reference-clock detection, lane power/rate/equalization/PLL/fuse parameters, generic PHY buses, scratch registers, and byte-order remapping.

Persistence is hardware-defined. Configuration fields usually survive until a modeset, stream teardown, register reprogramming, power-gate transition, suspend/resume, GPU reset, or ASIC reset. Status, pending, occurred, clear, ack, and interrupt fields may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while the relevant clock and power domains are active; this generated header does not record those access semantics.

## Dependencies And Integration Points

This slice depends on the generated DCN 4.1.0 register database and must stay synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_offset.h`, which provides matching register addresses.
- Adjacent chunks of `dcn_4_1_0_sh_mask.h`, because this chunk starts inside `DP_SYM32_ENC3_DP_SYM32_ENC_SDP_GSP_CONTROL4` and ends just before the rest of `RDPCSTX1_RDPCSTX_PHY_CNTL1`.
- DCN 4.x display code that includes this header, including DMUB/DCN 4.0/4.1 integration paths.
- HPO DP link encoder code, where DPHY fields are consumed through `hpo_le_shift` and `hpo_le_mask`; for example DCN 4.2 state readback uses `DP_DPHY_SYM32_STATUS`, `DP_DPHY_SYM32_CONTROL`, SAT VC, and VC rate fields that map to these generated instance fields.
- Stream encoder, packet/metadata, audio, ALPM, DLPC, DPCSSYS CR, DPCS/RDPCS transmitter, link training, diagnostics, and suspend/resume paths that program these registers through AMD display register helpers.

Behaviorally, the chunk integrates with HPO DisplayPort stream packet emission, audio/metadata SDP scheduling, video CRC diagnostics, link symbol counting, main-link ALPM, eDP ASSR, DP MST stream allocation and throttled VC rates, DP/eDP test patterns, link encryption, low-power display controller trigger handling, indexed PHY/CR access, RDPCS transmitter FIFO and PHY bring-up, PLL programming, interrupt handling, and lane/fuse tuning.

## Risks And Edge Cases

- The constants are untyped preprocessor values. A wrong shift or mask can compile successfully while touching the wrong MMIO bits.
- The file is generated hardware metadata. Manual edits can desynchronize it from silicon documentation, offset headers, firmware expectations, and sibling generated DCN versions.
- The chunk boundary is not semantic. It starts mid-register at `GSP_CONTROL4` and ends mid-RDPCSTX1 block; whole-register and whole-instance conclusions require adjacent chunks.
- Repeated instance layouts can hide instance-specific mistakes. `DP_DPHY_SYM320..323` and `RDPCSTX0/1` mostly repeat the same field families, but a copied wrong mask in one instance would affect only that link/transmitter.
- Status, pending, occurred, clear, mask, and interrupt-mask fields are easy to confuse. Using a status bit as a clear bit, or clearing sticky bits too early, can lose packet deadlines, link errors, DLPC triggers, or transmitter FIFO faults.
- GSP and metadata packet fields are line/frame sensitive. Incorrect line numbers, SOF references, one-shot triggers, double-buffer enables, or pending polling can emit stale SDP metadata, miss a packet deadline, or corrupt receiver-visible audio/video metadata.
- DPHY SAT and VC rate fields control MST bandwidth allocation. Bad stream-source, slot-count, or rate masks can break multi-stream scheduling while leaving simpler single-stream modes apparently functional.
- ALPM/eDP/ASSR fields are interoperability sensitive. Incorrect sleep/wake timing, seed values, or start-from-sleep behavior can cause resume-only link failures, flicker, or panels that fail to wake.
- RDPCSTX PHY and PLL fields are signal-integrity critical. Wrong lane reset, width/rate, P-state, equalization, boost, PLL multiplier/divider/SSC, fuse, or generic-bus masks can cause link training failures, intermittent display loss, or hardware-dependent regressions.
- CR sideband address/data windows expose indexed hardware state; bad masks or ordering can target the wrong PHY control register even when the direct MMIO access compiles cleanly.

## Test Signals

Useful validation combines generated-header checks and hardware behavior:

- Build AMDGPU display support with DCN 4.1.0 enabled. Missing, renamed, or malformed macros should fail in register-table construction or in consumers that token-paste field names.
- Mechanically verify `__SHIFT`/`_MASK` pairing in lines 49697-52181 while allowing the expected boundary exceptions at the start of `GSP_CONTROL4` and the end of `RDPCSTX1_RDPCSTX_PHY_CNTL0`.
- Diff this range against AMD's authoritative DCN 4.1.0 register database and compatible nearby DCN 4.x generated headers where layouts are expected to match.
- Exercise HPO DP link encoder instances 0-3: link enable/disable, lane-count and mode changes, link training, MST SAT updates, throttled VC rates, test-pattern generation, PRBS/custom patterns, eDP ASSR, ALPM sleep/wake, and state readback.
- Exercise stream encoder instance 3 packet paths: GSP one-shot and continuous sends, metadata packet scheduling, audio SDP controls, VBID/MSA/video stream controls, panel replay, video CRC, symbol counters, and ALPM wake interrupts.
- Exercise RDPCSTX0 and the visible RDPCSTX1 fields on matching hardware: clock enable/status, FIFO lane enables/start/delay, PLL update request/pending, CR address/data access, SRAM power state, pattern detection, interrupt clear/mask behavior, PHY reset/ref-clock detection, lane tuning, fuse readback, and byte-order changes.
- Watch kernel logs, display traces, and hardware readback for stuck SAT or rate-update pending bits, GSP deadline misses, stale metadata after modeset, silent DP audio, failed ALPM wake, MST slot allocation errors, RDPCS FIFO errors, PLL update timeouts, CR FIFO full/empty stalls, and link training or resume-only failures.

## Cross-Chunk Notes

The previous chunk contains the beginning of `DP_SYM32_ENC3` GSP controls and the comment for `GSP_CONTROL4`; this chunk continues through the rest of the stream encoder 3 tail. The next chunk continues `RDPCSTX1` starting at `RDPCSTX1_RDPCSTX_PHY_CNTL1`. The final per-file research document should merge adjacent chunks before making whole-file claims about every DCN 4.1.0 display register or every DPCS/RDPCS transmitter instance.
