# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_4_1_0_sh_mask.h lines 54588-57438

## Purpose

This chunk is a generated AMD DCN 4.1.0 register shift/mask table. It contains no executable C functions, structs, or enums; its public surface is a set of C preprocessor symbols that describe bit positions and bit masks for MMIO register fields. The chunk defines 2,031 macros across 344 register names in the requested line range.

The range starts at the end of the `AZCONTROLLER1` HDA controller fields, continues through HDA/Azalia endpoint and stream descriptor fields, then covers a large set of display debug-indirect fields for CNVC, color management, writeback, MPC/MPCC, OTG, DIO/link blocks, and finally resumes Azalia codec/pin/audio-descriptor fields. These macros are paired with generated register-offset macros from `dcn_4_1_0_offset.h`; downstream DCN401 code combines offset macros with these shift/mask macros through helper macros such as `FN`, `FD`, `SF`, `SR`, `SRI`, and related register-table initializers.

## Hardware Surface

The main register families in this chunk are:

- `AZCONTROLLER1_*`: immediate-command status, DMA position lower/upper base address, and wall-clock counter alias fields. These describe HDA controller command/result state and the DMA position buffer address layout.
- `AZENDPOINT1_*`, `AZINPUTENDPOINT1_*`, and `AZROOT1_*`: immediate command input/output data and index fields for endpoint/root command paths.
- `AZSTREAM0_1` through `AZSTREAM7_1`: repeated HDA output stream descriptor control/status, link position, cyclic buffer length, last valid index, FIFO size, format, BDL pointer lower/upper address, and position alias fields.
- Empty or marker-only address blocks for several HDCP key-database and display debug blocks. These comments preserve generated address-block boundaries even when this chunk has no field macros for that block.
- `ID*_CNVC_*` and `ID*_CM_*`: debug-indirect fields for CNVC and color-management flow control, bypass/status, and register-to-floating-point conversion snapshots.
- `ID01_WB_*` through `ID12_WB_*`: MCIF writeback formatter, manager, arbiter, and P010 debug words.
- `ID*_MPC_*`, `MPCC0_*` through `MPCC3_*`: MPC output CSC mode debug fields and repeated MPCC debug fields for selection, top/bottom gains, background color, blending mode, stereo mode, pixels, recout geometry, MPC geometry, sideband, flip/update pending, interlace/stereo/vbi, GSL, master update lock, and TMZ status/mask.
- `MPCC_OGAM*` and `MPCC_MCM*`: output gamma and multi-color-management debug fields for four MPCC instances.
- `OTG0_*` through `OTG3_*`: output timing generator debug data and interface fields, including scaler interface, `DOUT_INTERFACE_01_A/B`, and `DOUT_INTERFACE_02` status/control-style debug fields.
- Numerous DIO, DP, DIG, AUX, HPD, HPO, encoder, DPHY, APG, DCIO, power-sequencing, DMCUB, RBBMIF, IHC, DMU, DCCG, and other debug-indirect address-block markers with no local fields in this chunk.
- `AZALIA_F2_CODEC_*`, `AZALIA_F2_PIN_*`, and `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR8`: HDMI/DP audio codec converter, pin control, channel allocation, ACP/audio descriptor, multichannel enable, channel status override, LPIB snapshot, format-change, keepalive, widget capability, pin capability, connection-list length, and audio descriptor capability fields.

## APIs, Types, And Macros

The exported API is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for a field.
- `<REGISTER>__<FIELD>_MASK` gives the field mask in the containing register word.

The stream descriptor groups are highly regular. For each `AZSTREAMn_1_OUTPUT_STREAM_DESCRIPTOR_CONTROL_AND_STATUS`, the fields include `STREAM_RESET`, `STREAM_RUN`, interrupt enables, `STRIPE_CONTROL`, `TRAFFIC_PRIORITY`, `STREAM_NUMBER`, completion/error status bits, and `FIFO_READY`. The associated format registers expose `NUMBER_OF_CHANNELS`, `BITS_PER_SAMPLE`, `SAMPLE_BASE_DIVISOR`, `SAMPLE_BASE_MULTIPLE`, and `SAMPLE_BASE_RATE`; the BDL lower address masks reserve the unimplemented low address bits and expose the aligned buffer descriptor base.

The debug-indirect families are also regular. CNVC and CM flow-control registers expose ready/startup/dynamic-clock and ready-to-receive/ready-to-send style handshakes. MPCC debug registers expose repeated database and live pixel/sideband state for instances 0 through 3. OTG debug registers expose generic debug words plus structured interface fields for scaler and DOUT state. The Azalia codec fields align with HDA/HDMI audio concepts: converter format, channel/stream ID, digital converter control, audio widget capabilities, pin sense/config/default response words, speaker/channel allocation, ACP/audio-descriptor indexing, multichannel mute/channel enables, IEC 60958 channel-status override words, LPIB snapshot state, and sink/widget capabilities.

There are no local functions or data structures. Consumers compile these symbols into generation-specific register-field tables, usually through `FN(reg_name, field_name)` or `FD(reg__field)` style helper macros that select the matching `__SHIFT` and `_MASK` values.

## Control Flow

This header chunk has no runtime control flow. Its control role is compile-time macro expansion:

1. DCN401 display code includes `dcn_4_1_0_sh_mask.h`, usually together with `dcn_4_1_0_offset.h`.
2. A consumer macro such as `FN(AZALIA_F2_CODEC_CONVERTER_CONTROL_CONVERTER_FORMAT, NUMBER_OF_CHANNELS)` or a generated register-list initializer concatenates the register and field tokens.
3. The preprocessor resolves those tokens to the shift and mask macros in this file.
4. The compiled driver stores the resulting constants in register-field structures or uses them in direct field access helpers.
5. Runtime register helpers apply masks and shifts while reading, modifying, writing, polling, or decoding MMIO fields.

For the HDA/Azalia stream and codec fields, the runtime path is generally audio programming and audio status decode for HDMI/DP outputs. For the debug-indirect display blocks, the runtime path is mostly diagnostic or debug-dump access to internal DCN pipeline state; the same constants are still hardware ABI, because the bit layout determines how collected debug data is interpreted.

## State And Persistence

The header itself stores no state and persists nothing. It describes state held in hardware registers.

Important state represented by this chunk includes HDA immediate-command busy/result state, DMA position-buffer enable and base address, output-stream run/reset/error/FIFO status, stream format and BDL address fields, CNVC/CM pipeline handshake and bypass/debug snapshot state, writeback formatter/manager/arbiter debug data, MPCC blend/sideband/pixel/geometry state, OTG interface debug state, and Azalia codec converter/pin/audio descriptor state.

Persistence is hardware-scoped. Values written by driver code to fields such as stream run/reset, converter format, channel/stream ID, multichannel enables, channel-status override, keepalive, and LPIB snapshot control remain in the relevant register until changed by software, hardware reset, power transition, or block-level reinitialization. Status fields such as FIFO errors, descriptor errors, output active, format changed, link-position-in-buffer, and debug sideband/pixel snapshots are produced by hardware and must be decoded with the exact masks in this header.

## Dependencies And Integration Points

The direct dependency is the C preprocessor plus the generated AMD register-header convention. The functional dependencies are:

- `dcn_4_1_0_offset.h`, which provides the matching register offsets and base-index selectors.
- DC register-helper macros such as `FD`, `FN`, `SF`, `SR`, `SRI`, `SRI_ARR`, and related generation-specific initializers.
- AMD display MMIO helpers that use compiled shift/mask tables to read, update, and decode fields.
- Audio, stream encoder, link encoder, MPC/MPCC, OTG, IRQ/debug, DMUB, and resource construction code that includes the DCN401 generated register headers.

Observed include/use signals in this source tree include `display/dmub/src/dmub_dcn401.c` including `dcn_4_1_0_sh_mask.h`, and many DCN401 modules defining `FN`/`SR`/`SRI`-style helpers for generated offset/mask consumption. `display/dc/resource/dcn401/dcn401_resource.c`, `display/dc/dio/dcn401/dcn401_dio_stream_encoder.c`, `display/dc/dio/dcn401/dcn401_dio_link_encoder.c`, `display/dc/mpc/dcn401/dcn401_mpc.c`, `display/dc/optc/dcn401/dcn401_optc.c`, `display/dc/hwss/dcn401/dcn401_hwseq.c`, `display/dc/hubbub/dcn401/dcn401_hubbub.c`, `display/dc/hubp/dcn401/dcn401_hubp.c`, `display/dc/dsc/dcn401/dcn401_dsc.c`, and `display/dc/irq/dcn401/irq_service_dcn401.c` are representative integration points for the generated header pair, even though a specific register family may be consumed by shared DCE/DCN audio or debug helpers rather than by a file whose name matches the register block.

The Azalia/HDA portions also align with generated enum definitions in broader AMD include headers, such as enum values for converter format, digital converter bits, widget control, downmix, multichannel mute, and audio descriptor interpretation. Those enums provide semantic values; this chunk provides the bit placement needed to encode or decode them.

## Risks

The biggest risk is silent hardware misprogramming or misdecode. These macros are numeric constants; if a shift or mask is wrong but still compiles, the driver can write the wrong bits, preserve the wrong bits during read-modify-write, or misinterpret a status/debug register.

Repeated instance families increase the chance of copy-generation mistakes. `AZSTREAM0_1` through `AZSTREAM7_1`, `MPCC0` through `MPCC3`, `MPCC_OGAM0` through `MPCC_OGAM3`, `MPCC_MCM0` through `MPCC_MCM3`, `OTG0` through `OTG3`, and `AUDIO_DESCRIPTOR0` through `AUDIO_DESCRIPTOR8` must remain instance-consistent. A field that is correct for one instance but shifted differently for another would likely compile and fail only during per-instance runtime exercise.

Address-block markers without local field macros are another reconciliation risk. They are expected in generated headers, but merge tooling must not assume every `addressBlock` comment has following field definitions inside the same chunk. Some block contents may live in adjacent chunks or may have no generated field macros.

Audio fields are user-visible when wrong. Incorrect masks for stream format, channel/stream ID, converter enable, multichannel mute, speaker/channel allocation, IEC 60958 channel-status override, or HBR/keepalive fields can present as missing HDMI/DP audio, wrong channel mapping, wrong sample format, receiver compatibility issues, silent-stream failures, or format-change events that are not acknowledged correctly.

Debug fields are easy to under-test. CNVC/CM/WB/MPCC/OTG debug-indirect fields may not be exercised by normal display modes, yet they are important for bring-up diagnostics and failure triage. A bad mask can make hardware dumps misleading even when the main display pipeline appears functional.

## Test Signals

Useful validation is a mix of build-time checks, generated-header consistency checks, and hardware behavior:

- Build the DCN401 display stack with `dcn_4_1_0_offset.h` and `dcn_4_1_0_sh_mask.h` together. Missing or renamed symbols should fail in resource, DMUB, DIO, MPC, OPTC, IRQ, hubbub/hubp, DSC, clock, or shared audio/debug code.
- Run generated-header consistency checks that each field has both a `__SHIFT` and `_MASK`, that mask width matches the expected field width, and that repeated families such as `AZSTREAMn_1`, `MPCCn`, `OTGn`, and `AUDIO_DESCRIPTORn` have consistent field sets.
- Exercise HDMI/DP audio across sample rates, bit depths, 2-channel and multichannel layouts, HBR where supported, and silent-stream/keepalive cases. Expected signals are stable audio enumeration, correct channel mapping, no unexpected format-change storms, and correct LPIB/progress reporting.
- Exercise stream start/stop and reset paths for HDA output streams. Expected signals are correct `STREAM_RUN`, `STREAM_RESET`, FIFO-ready, completion, FIFO-error, and descriptor-error behavior.
- Capture debug-indirect dumps for CNVC, CM, WB, MPCC, and OTG blocks on active displays. Expected signals are plausible ready/handshake states, MPCC pixel/sideband geometry that matches active pipes, OTG DOUT/scaler interface state that matches timing configuration, and no cross-instance aliasing.
- Validate per-instance behavior on multi-display configurations, especially when several pipes or audio endpoints are active at once. This is the best signal for instance-number drift in repeated generated macro families.
