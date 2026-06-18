# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_offset.h lines 7876-10402

## Purpose

This chunk is a generated AMD DCN 3.5.1 register-offset header slice. It has no executable C logic; it publishes preprocessor constants that name memory-mapped display-register offsets and their register-base index for DCN351 hardware. Driver code combines these offsets with `dcn_3_5_1_sh_mask.h` field definitions and AMD display register-helper macros to build typed register tables for DIO, stream encoders, link encoders, IRQ service, DMUB service, GPIO/DDC/HPD handling, and panel power sequencing.

The requested range starts in the tail of the `DP_AUX4` AUX-channel register group, then covers the main repeated DIO instance layout for `DIG0` through `DIG4`, common DCIO and GPIO/link-control registers, UNIPHY reserved macro-control ranges for instances 1-4, and the first registers of `PWRSEQ0`. Within lines 7876-10402 there are 2,394 `#define` entries: 1,197 register-offset macros and 1,197 matching `_BASE_IDX` macros. Every `_BASE_IDX` value in this chunk is `2`, meaning these symbols are interpreted through DCN351 base segment index 2 by consumers that compute `BASE(reg..._BASE_IDX) + reg...`.

Although the repository path is under a local `ceph-client` tree, this file is AMDGPU display hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Important APIs, Types, And Macros

There are no functions, structs, enums, variables, includes, locks, or allocation paths in this chunk. The exported interface is the generated macro namespace:

- `reg<NAME>`: a DCN351 register offset within a hardware address block.
- `reg<NAME>_BASE_IDX`: the base-address segment selector used by AMD register helpers when producing the final MMIO address.

The major register families in this range are:

- `regDP_AUX4_*` tail registers at lines 7876-7894: AUX4 DPHY TX/RX control and status, GTC sync control/status/error registers, and AUX PHY wake control. The chunk starts mid-family, so earlier AUX4 software-control, arbitration, interrupt, and data registers are outside this range.
- `regVPG0_*` through `regVPG4_*`: five Video Packet Generator blocks. Each instance exposes generic packet access/data, generic-stream packet frame/immediate update controls, generic status, memory power, ISRC access/data, and MPEG info registers.
- `regAFMT0_*` through `regAFMT4_*`: five audio formatter blocks. Each instance includes ACP, VBI/audio-packet controls, HDMI/DP audio info, IEC 60958 channel status registers, CRC controls/results, ramp controls, infoframe control, interrupt status, audio source control, and memory-power control.
- `regDME0_*` through `regDME4_*`: small Data Mapping Engine groups with `DME_CONTROL` and `DME_MEMORY_CONTROL`.
- `regDIG0_*` through `regDIG4_*`: five digital front-end/back-end and HDMI/TMDS encoder blocks. Each repeated group includes FE clock/enable/control, output CRC/test-pattern/FIFO controls, HDMI metadata/audio/ACR/VBI/infoframe/generic-packet/DB controls, AFMT coupling, BE controls, TMDS control/pattern/DC-balancer registers, and `DIG_VERSION`.
- `regDP0_*` through `regDP4_*`: five DisplayPort link/stream encoder groups. Each instance covers link control, pixel format, MSA colorimetry/config/misc/timing parameters, video stream control, DPHY internal/training/symbol/scrambler/CRC/fast-training controls, secondary-data packet/audio timestamp controls, MST/MSE slot allocation and status, MSO/DSC controls, DP DB control, metadata transmission, ALPM and AUX-less ALPM controls, GSP controls, and stream/link symbol count status/control.
- Common `regDC_*`, `regDCIO_*`, `regUNIPHYA_*` through `regUNIPHYE_*`, and `regINTERCEPT_STATE` registers: generic DC scratch/control registers, DCIO clock/reference clock and write-command delay, link and channel crossbar controls, DCIO pattern generator, global swaplock/genlock pad control, soft reset, and global DCIO spare/pinstrap state.
- GPIO, DDC, HPD, AUX, and pad-power registers: `DC_GPIO_GENERIC`, `DDC1` through `DDC5`, `DDCVGA`, `GENLK`, `HPD`, drive-strength, power-sequence GPIO enables, pad-strength, AUX PHY control, TX impedance, TX12/RX/pull-up/AUX controls, and `AUXI2C_PAD_ALL_PWR_OK`.
- `regDCIO_UNIPHY1_UNIPHY_MACRO_CNTL_RESERVED0` through `RESERVED57`, repeated for UNIPHY1, UNIPHY2, UNIPHY3, and UNIPHY4. `dce_dc_dcio_dcio_uniphy0_dispdec` is present as an address-block marker in this chunk but has no defines in this slice.
- The opening of `regPWRSEQ0_*`: `DC_GPIO_PWRSEQ_EN`, `DC_GPIO_PWRSEQ_CTRL`, `DC_GPIO_PWRSEQ_MASK`, `DC_GPIO_PWRSEQ_A_Y`, and `PANEL_PWRSEQ_CNTL`. The rest of the panel power-sequencer block continues after this chunk.

The repeated DIO register layout is especially important: `DIGn`, `DPn`, `VPGn`, `AFMTn`, and `DMEn` advance together for instances 0-4. DCN351 resource code reports five stream encoders and five digital link encoders, and it initializes arrays such as `stream_enc_regs[5]`, `link_enc_aux_regs[5]`, `link_enc_hpd_regs[5]`, and `link_enc_regs[5]` from these generated register names.

## Control Flow

This header has no runtime control flow. Runtime behavior is supplied by AMDGPU display code that includes this header and consumes its constants:

1. DCN351-specific modules include `dcn_3_5_1_offset.h` together with `dcn_3_5_1_sh_mask.h`.
2. Register-list macros token-paste symbolic names into offset, shift, and mask initializers.
3. Constructors build hardware-block register tables. In `dcn351_resource.c`, this includes DIO construction, stream encoder creation, link encoder creation, VPG/AFMT sub-block creation, and resource-pool wiring for five DIO/link instances. In `irq_service_dcn351.c`, interrupt-source tables are initialized from generated offsets and fields. In `dmub_dcn351.c`, `dmub_srv_dcn351_regs_init()` computes DMUB register offsets as `BASE(reg..._BASE_IDX) + reg...`.
4. Runtime helpers such as `REG_READ`, `REG_WRITE`, `REG_GET`, `REG_SET`, and `REG_UPDATE` use those tables to touch the actual MMIO registers during modeset, link training, audio setup, hotplug handling, AUX/DDC transactions, power sequencing, interrupt handling, suspend/resume, and DMUB communication.

The offsets do not encode ordering. Consumers still must sequence hardware operations correctly: enable and reset DIG/DP blocks at the right time, program HDMI/DP packets after stream format selection, perform DP link training before stream enable, synchronize secondary data packets with active streams, manage HPD/DDC/AUX pads around hotplug and low-power states, and follow panel power/backlight timing rules.

## State And Persistence Behavior

The chunk stores no software state and persists nothing by itself. It names hardware state held in DCN351 display registers:

- DIG/HDMI/TMDS state: encoder enablement, clocking, test patterns, FIFO controls, metadata packets, generic packets, audio clock regeneration, TMDS control characters, output CRC, and back-end state.
- DP link and stream state: link configuration, pixel format, main-stream attributes, video timing, link framing, training pattern and DPHY controls, scrambler/CRC/test controls, MST/MSE allocation, DSC/MSO, secondary-data/audio packets, ALPM, GSP, and symbol counters.
- VPG/AFMT/DME state: packet payload staging, generic/ISRC/MPEG info, audio infoframes, IEC 60958 channel status, CRC diagnostics, ramp controls, audio source selection, and memory-power controls.
- DCIO/link state: display clock/reference controls, UNIPHY channel crossbars, pattern generator, genlock/swaplock pads, soft-reset state, pinstraps, GPIO/HPD/DDC/AUX pad controls, pad drive strength, AUX power readiness, and reserved UNIPHY macro-control space.
- Power-sequencer state at the chunk boundary: GPIO power-sequencer enable/control/mask/data and the first panel power-sequencer control register.

Persistence is hardware-defined. Programmed values may survive until a modeset, stream/link teardown, power-gating event, panel power sequence, suspend/resume, GPU reset, or ASIC reset. Status and interrupt-related registers may be read-only, sticky, write-one-to-clear, self-clearing, or only valid while the relevant clock/power domain is enabled. The generated offset header does not express access semantics, reset values, side effects, or required delays; those come from the hardware spec and the consuming DCN/DCE code.

## Dependencies And Integration Points

This chunk depends on AMD's generated DCN351 register database and must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dcn/dcn_3_5_1_sh_mask.h`, which supplies field shifts and masks for the registers named here.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn351/dcn351_resource.c`, which includes the offset and shift/mask headers and constructs DCN351 DIO, stream encoder, link encoder, VPG, AFMT, HPO, IRQ, and resource-pool objects. The chunk's five `DIGn`/`DPn`/`VPGn`/`AFMTn`/`DMEn` layouts align with `res_cap_dcn351.num_stream_encoder = 5` and `num_dig_link_enc = 5`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/irq/dcn351/irq_service_dcn351.c`, which includes these generated headers and initializes DCN351 interrupt-source register metadata.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dmub/src/dmub_dcn351.c`, where `dmub_srv_dcn351_regs_init()` computes DMUB-visible offsets from `BASE(reg..._BASE_IDX) + reg...`.
- DCN35/DCE shared encoder implementations such as `dcn35_dio_stream_encoder`, `dcn35_dio_link_encoder`, `dcn31_hpo_dp_stream_encoder`, `dcn31_hpo_dp_link_encoder`, and inherited DCE/DIO helpers that expect the generated register tables to match their local register-list macros.
- GPIO, I2C/DDC, AUX, HPD, panel power, link training, audio, MST, DSC/MSO, ALPM, and DMUB paths that indirectly rely on these constants through register tables rather than manually spelling offsets.

The source-tree alignment is important: this is a DCN351 display-register chunk. The final per-file synthesis should merge it with adjacent chunks before making whole-file claims about all offset macros in `dcn_3_5_1_offset.h`.

## Risks And Edge Cases

- These constants are untyped preprocessor values. A wrong offset or base index can compile successfully while reads and writes target the wrong MMIO register.
- All base indices in this chunk are `2`. If a generator or manual edit changes one `_BASE_IDX`, `BASE(reg..._BASE_IDX) + reg...` computations could silently move only one register family to a different MMIO segment.
- The chunk begins and ends at artificial boundaries. It starts after earlier `DP_AUX4` registers and stops at `PWRSEQ0_PANEL_PWRSEQ_CNTL`; callers need adjacent chunks to understand the full AUX4 and panel power-sequencer register groups.
- Repeated instance groups are easy to misalign. A single bad `DIG3`, `DP4`, `AFMT2`, or `VPG1` offset can break one physical connector/encoder path while other ports still work, making failures appear board- or connector-specific.
- HDMI/DP packet registers are timing-sensitive. Incorrect VPG, AFMT, HDMI generic packet, infoframe, audio, ACR, or metadata offsets can lead to missing HDR/VRR/audio metadata, silent HDMI/DP audio, wrong sample-rate reporting, or receiver-specific interoperability failures.
- DP link registers are link-training-sensitive. Bad DPHY, scrambler, CRC, fast-training, MSA, MST/MSE, ALPM, DSC, or symbol-count offsets can cause failed link training, flicker, MST bandwidth allocation bugs, DSC bring-up failures, or low-power display wake issues.
- GPIO, HPD, DDC, AUX, and pad-strength registers interact with physical pins. Wrong offsets can cause missed hotplug events, failed EDID reads, AUX/I2C timeouts, excessive pad drive, or improper pad power handling.
- UNIPHY reserved macro-control offsets are especially risky because names do not describe semantics. They should be treated as generated silicon metadata and not repurposed without authoritative documentation.
- Panel power-sequencer registers can affect display panel safety and resume behavior. Incorrect `PWRSEQ0` offsets or ordering can produce blank internal panels, backlight glitches, or resume-only failures.

## Test Signals

Useful validation combines static generated-header checks with DCN351 hardware coverage:

- Build AMDGPU display support with DCN351 enabled. Missing or renamed macros should fail where `dcn351_resource.c`, `irq_service_dcn351.c`, and `dmub_dcn351.c` instantiate register tables.
- Mechanically verify this range has 1,197 register-offset macros and 1,197 matching `_BASE_IDX` macros, and that every `_BASE_IDX` value is `2`.
- Diff this chunk against AMD's authoritative DCN 3.5.1 register database and nearby generated DCN headers. Pay special attention to repeated `DIG0-4`, `DP0-4`, `VPG0-4`, `AFMT0-4`, `DME0-4`, and `DCIO_UNIPHY1-4` instance strides.
- Exercise all five physical DIO/link instances where hardware exposes them: HDMI, DisplayPort SST, DisplayPort MST, USB-C/DP alt-mode paths, hotplug/unplug, EDID reads, link retraining, suspend/resume, and GPU reset recovery.
- Validate HDMI/DP audio and metadata: ACR programming, infoframes, generic packets, HDR metadata, ISRC/MPEG packets, audio enable/disable, sample-rate changes, multichannel formats, and receiver compatibility.
- Exercise DP-specific features covered here: training patterns, fast training, DPHY CRC, MST MSE allocation/status, DSC enablement, MSO controls, ALPM/AUX-less ALPM, GSP controls, and symbol-count status reporting.
- Watch kernel logs and display diagnostics for AUX/DDC timeouts, HPD storms or missed HPD events, DMUB register access failures, IRQ misrouting, link-training failures, CRC mismatches, stuck secondary-data packets, panel power/backlight sequencing issues, and connector-specific failures that map to one repeated register instance.

## Cross-Chunk Notes

This is a middle chunk of `dcn_3_5_1_offset.h`. Earlier chunks define preceding AUX, audio, GPIO, and other display blocks. Later chunks continue `PWRSEQ0` and additional DCN351 offset families. The merge/reconciliation lane should combine this document with neighboring chunk research before producing the final per-file report.
