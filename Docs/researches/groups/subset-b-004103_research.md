# Research Report: subset-b-004103

This grouped report covers Linux media I2C drivers under `sources/distributed-fs/ceph-client/drivers/media/i2c`. Each file section is delimited for reconciliation into the required source-tree-aligned per-file research document.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa6588.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa6588.c

## Purpose
`saa6588.c` implements a V4L2 I2C subdevice driver for the Philips/NXP SAA6588 RDS decoder. It periodically polls the chip over I2C, converts chip-specific RDS block layout into the V4L2 RDS block format, buffers blocks in a small in-kernel ring buffer, and exposes RDS read/poll/close semantics to the parent radio driver through `SAA6588_CMD_*` subdev core commands.

## Important APIs, Types, and Functions
- `struct saa6588` is the full runtime state: `v4l2_subdev`, delayed poll work, spinlock, byte ring buffer, read/write indices, block count, last RDS block number, wait queue, read-availability flag, and sync status.
- `saa6588_probe()` allocates state and the `bufblocks * 3` byte ring buffer with devm allocation, initializes subdev ops, configures the chip, and starts delayed polling.
- `saa6588_i2c_poll()` reads six bytes from the chip, validates sync and duplicate block numbers, maps status bits to V4L2 RDS block flags, pushes a three-byte block to the ring buffer, and wakes blocked readers.
- `read_from_buf()`, `block_from_buf()`, and `block_to_buf()` implement the producer/consumer ring buffer with spinlock protection around buffer indices and block count.
- `saa6588_command()` handles `SAA6588_CMD_READ`, `SAA6588_CMD_POLL`, and `SAA6588_CMD_CLOSE`.
- Tuner ops `saa6588_g_tuner()` and `saa6588_s_tuner()` advertise RDS capabilities and reconfigure the decoder.

## Control Flow and State
Probe configures mode bytes from module parameters `xtal`, `mmbs`, `plvl`, and `bufblocks`, then schedules `saa6588_work()` immediately. The work item calls `saa6588_i2c_poll()` every 20 ms for the device lifetime. On each successful synchronized read, the driver swaps chip byte order from status/MSB/LSB into V4L2 LSB/MSB/status order, normalizes E-block handling, stores the block, sets `data_available_for_read`, and wakes `read_queue`.

Readers enter through parent-driver subdev commands. Blocking reads sleep on `read_queue` until data is available or interrupted; nonblocking reads return available data only. Ring-buffer overflow drops the oldest block by advancing `rd_index` when `wr_index` catches it. `SAA6588_CMD_CLOSE` forces a wakeup so blocked file operations can unwind.

## Dependencies and Integration Points
The driver depends on Linux I2C raw reads/writes, V4L2 subdev core/tuner ops, `media/i2c/saa6588.h` command definitions, wait queues, delayed work, spinlocks, and `copy_to_user()`. It registers as an I2C driver named `saa6588`, and parent radio drivers are expected to bridge radio file operations to the custom subdev commands.

## Risks and Edge Cases
- The ring buffer has no explicit lower bound for `bufblocks`; a zero module parameter would allocate a zero-size buffer and make buffering unsafe.
- `i2c_master_send()` and `i2c_master_recv()` errors are logged but mostly not propagated to callers, so user-visible failures can look like no RDS data.
- `data_available_for_read` is sometimes written outside the spinlock, while reads also inspect it outside the lock for wait conditions; this is simple but relies on waitqueue ordering and repeated polling rather than strict synchronization.
- The 20 ms polling cadence is fixed and can continue even if no users are reading.
- `mmbs` block-E handling is hard-coded to map most E blocks to invalid, which may not fit uncommon RDS/RBDS uses.

## Test Signals
Useful validation includes module loading and I2C probe detection, verifying three-byte RDS block reads through the parent radio device, blocking read wakeup behavior, poll readiness transitions, ring-buffer overflow behavior with small `bufblocks`, tuner capability bits `V4L2_TUNER_CAP_RDS` and `V4L2_TUNER_CAP_RDS_BLOCK_IO`, and remove-time cancellation of the delayed work without use-after-free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa6588.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa6752hs.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa6752hs.c

## Purpose
`saa6752hs.c` is a V4L2 I2C subdevice driver for the Philips SAA6752HS MPEG-2 encoder. It configures video dimensions, TV standard, MPEG transport stream PID layout, audio encoding and bitrate, video bitrate policy, MPEG PSI tables, and chip start/reconfigure commands.

## Important APIs, Types, and Functions
- `struct saa6752hs_state` stores the subdev, V4L2 control handler, bitrate control cluster, chip revision, AC-3 capability, MPEG parameter snapshot, selected video format, and standard.
- `struct saa6752hs_mpeg_params` persists TS PID, audio, and video encoding parameters that are written during encoder initialization.
- `saa6752hs_chip_command()` writes command bytes and polls status register `0x10` until the chip clears its busy bit or a three-second timeout expires.
- `saa6752hs_set_bitrate()` programs bitrate mode, target/peak video bitrate, audio encoding and bitrate, and total mux bitrate.
- `saa6752hs_init()` writes the selected format, line count, GOP/Q-scale/output settings, leading null bytes, PAT/PMT tables with CRC32, audio/video/PCR PIDs, starts the encoder, and patches aspect ratio.
- Pad ops `saa6752hs_get_fmt()` and `saa6752hs_set_fmt()` map requested frame sizes to D1, 2/3 D1, 1/2 D1, or SIF.
- Control ops `saa6752hs_try_ctrl()` and `saa6752hs_s_ctrl()` keep the parameter snapshot and bitrate cluster coherent.

## Control Flow and State
Probe reads revision bytes at register `0x13`, marks AC-3 support for revision `0x0206`, initializes MPEG defaults, creates a fixed menu of MPEG audio/video/stream controls, clusters bitrate mode/target/peak controls, and defaults to 625-line input. Format selection stores only an enum until `.init` runs. The parent bridge calls `.init` with a leading-null-byte count; that routine reprograms the chip and starts encoding.

Runtime state is mostly V4L2 control state mirrored into `h->params`. Bitrate values exposed in bits per second are converted to kbit/s in `saa6752hs_s_ctrl()`. For VBR, the peak bitrate control is made active and coerced to at least the target value. PAT and PMT tables are generated locally each init, with AC-3 PMT layout selected when the audio encoding control requests AC-3.

## Dependencies and Integration Points
The driver depends on V4L2 subdev core/video/pad/control APIs, Linux I2C, CRC32 BE helpers, and MPEG V4L2 control IDs. It registers as `saa6752hs` and is intended to be controlled by a host capture/encoder board driver that supplies TV standard, media-bus format, MPEG controls, and initialization timing.

## Risks and Edge Cases
- Low-level `i2c_master_send()`/`recv()` helpers often ignore short transfers, so hardware communication failures can be silent.
- `saa6752hs_chip_command()` sends and receives without validating return values before inspecting status.
- The frame-size mapping is PAL-height biased; comments note incomplete NTSC translation for 480/240-line modes.
- PID defaults in controls differ from `param_defaults` ordering for audio/video, so tests should confirm actual intended PID assignment.
- AC-3 support is revision-gated and only two bitrates are exposed.
- `saa6752hs_init()` uses stack buffers sized to 256 bytes for PSI templates; current templates fit, but future table expansion must preserve bounds.

## Test Signals
Validation should cover successful probe revision reads, V4L2 control enumeration and clustering, VBR peak coercion, PAL/NTSC line programming, all four frame-size choices, generated PAT/PMT CRC correctness, AC-3 PMT selection on revision `0x0206`, command timeout behavior, and stream output inspection for expected PIDs and aspect-ratio signaling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa6752hs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7110.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa7110.c

## Purpose
`saa7110.c` provides a legacy V4L2 I2C subdevice driver for the Philips SAA7110/SAA7110A analog video decoder. It initializes decoder registers, selects among composite and S-Video input mux modes, detects PAL/NTSC/SECAM, exposes basic video controls, and enables or disables YUV output.

## Important APIs, Types, and Functions
- `struct saa7110` stores the subdev, control handler, 0x35-byte register cache, current norm, input index, output-enable flag, and a wait queue used for detection delays.
- `saa7110_write()` and `saa7110_write_block()` update the hardware and local cache, using raw I2C autoincrement when available and SMBus writes otherwise.
- `saa7110_selmux()` writes the per-input analog front-end table for nine input modes and updates `decoder->input`.
- `determine_norm()` reinitializes the chip, waits for lock, reads decoder status, and maps status bits to unknown, NTSC, PAL, or SECAM.
- Video ops provide `.s_std`, `.s_routing`, `.s_stream`, `.querystd`, and `.g_input_status`.
- Control ops map brightness, contrast, saturation, and hue to fixed decoder registers.

## Control Flow and State
Probe requires SMBus byte read/write support, initializes the subdev and controls, writes `initseq`, performs a few version/status reads, and leaves the device in PAL-like defaults with output enabled. Input routing validates a maximum of nine inputs and calls `saa7110_selmux()` only when the requested input changes. Standard changes update a few chroma/luma timing registers depending on NTSC, PAL, or SECAM.

Norm detection is active rather than passive: it rewrites the full init sequence, reapplies the mux, waits 250 ms, and probes status. For 50 Hz signals it performs a second wait/read to distinguish SECAM from PAL. The register cache mirrors writes but is not used for reads; hardware status is always read directly by `saa7110_read()`.

## Dependencies and Integration Points
The driver is a standalone `module_i2c_driver()` named `saa7110`. It integrates through V4L2 subdev video and control operations and expects a parent capture bridge to route input indices, set standards, and consume YUV output. It uses V4L2 standard masks and input status flags.

## Risks and Edge Cases
- `determine_norm()` rewrites the full chip configuration as part of query-standard, which can perturb active capture.
- Detection sleeps are implemented through a wait queue plus timeout, but no event ever wakes the queue; it is effectively a timed sleep.
- `saa7110_write_block()` caches data after raw I2C send without checking that the full block length was transferred.
- Output parameter in routing is ignored, since only one YUV output is modeled.
- The init and mux tables are magic register sequences with limited validation against board-specific analog wiring.
- Remove only unregisters and frees controls; it does not explicitly disable output.

## Test Signals
Test through a host bridge by probing the chip, enumerating and setting controls, switching all valid input indices and rejecting index 9+, toggling stream output register `0x0e`, querying standards with known PAL/NTSC/SECAM/no-signal inputs, checking `V4L2_IN_ST_NO_SIGNAL` and `V4L2_IN_ST_NO_COLOR`, and exercising adapters with and without raw I2C support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7110.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7115.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa7115.c

## Purpose
`saa7115.c` is the main Philips/NXP SAA711x analog video decoder driver, covering SAA7111, SAA7111A, SAA7113, GM7113C, SAA7114, SAA7115, SAA7118, and compatible clones. It handles chip detection, model-specific register initialization, input/output routing, standard selection, scaling, audio clock generation, raw and sliced VBI, tuner signal reporting, media-controller pads, and basic image controls.

## Important APIs, Types, and Functions
- `struct saa711x_state` tracks subdev, optional media pads, controls, standard, input/output, stream enable, radio mode, scaler size, chip identity, audio clock/crystal configuration, and clock-generator flags.
- `saa711x_has_reg()` gates register writes by model to avoid reserved or absent register addresses.
- `saa711x_writeregs()` applies register tables while honoring `saa711x_has_reg()`.
- Large init/config tables define per-model startup, 50/60 Hz video modes, scaler reset, VBI task enable/disable, and scaler defaults.
- `saa711x_set_v4lstd()` switches 50/60 Hz configuration, updates size, handles legacy chroma standard bits, and refreshes audio clock.
- `saa711x_set_size()` programs task-B output dimensions and horizontal/vertical scaling.
- VBI helpers `saa711x_set_lcr()`, `saa711x_decode_vbi_line()`, `saa711x_decode_vps()`, and `saa711x_decode_wss()` configure slicer lines and decode payloads.
- `saa711x_detect_chip()` auto-detects Philips/NXP and clone IDs by repeated reads from version register 0.

## Control Flow and State
Probe checks SMBus byte support, detects the chip, initializes V4L2 controls, optionally initializes media pads, selects the appropriate register table, applies platform-data overrides for SAA7113-like devices, sets NTSC defaults, and runs control setup. Routing updates mux bits, chroma trap bypass, output enables, and I-port polarity. Stream enable toggles I-port output where supported.

Format setting accepts only pad 0 and `MEDIA_BUS_FMT_FIXED`, then updates task-B scaling. Standard changes avoid unnecessary reprogramming because disabling the I-port during active capture can confuse downstream devices. VBI state is encoded in LCR registers; raw VBI enables both tasks while sliced VBI programs requested line services and disables raw capture. Tuner and input-status reads use status registers `0x1e` and `0x1f`.

## Dependencies and Integration Points
The driver depends on `saa711x_regs.h`, `media/i2c/saa7115.h`, V4L2 subdev core/audio/tuner/video/vbi/pad/control APIs, optional media-controller entity pads, and Linux I2C SMBus byte data transfers. Parent bridge drivers use input constants, output constants, crystal-frequency flags, and platform-data knobs from the media header.

## Risks and Edge Cases
- Model support relies on many magic register tables and model-specific reserved-register rules; regressions can affect only one variant.
- Several I2C writes do not propagate exact errors to high-level operations, and reads assume valid data.
- The scaler code has comments acknowledging weak bounds checking and hardcoded task-B behavior.
- VBI support for some models is explicitly experimental and relies on payload patterns and parity checks.
- Probe paths with media-controller pad initialization return early on later failures without an explicit `media_entity_cleanup()` in all branches.
- Platform-data bit pointer fields are optional; invalid board values can program unsupported timing or RTS modes.

## Test Signals
Useful signals include probing each supported ID path, reserved-register debug logs, control get/set behavior including chroma AGC/gain clustering, standard switching without unnecessary I-port disruption, format scaling to several widths/heights, tuner signal and input-status reads for locked/unlocked sources, raw and sliced VBI service-line programming, VBI decode samples for CC/WSS/VPS/teletext, media graph pad creation, and remove-time control cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7115.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa711x_regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa711x_regs.h

## Purpose
`saa711x_regs.h` is the register map companion for `saa7115.c` and related SAA711x decoder work. It provides named numeric constants for the Philips/NXP SAA711x video decoder family, including front-end decoder registers, component/interrupt registers, audio clock generator registers, VBI slicer registers, scaler task A/B registers, PLL/pulse-generator registers, and selected SAA7113 bit masks.

## Important APIs, Types, and Definitions
- `R_00_CHIP_VERSION` through `R_1F_STATUS_BYTE_2_VD_DEC` name the core video decoder registers.
- `R_23_INPUT_CNTL_5` through `R_2F_INTERRUPT_MASK_3` cover component processing and interrupt masks.
- `R_30_AUD_MAST_CLK_CYCLES_PER_FIELD`, `R_34_AUD_MAST_CLK_NOMINAL_INC`, and `R_3A_AUD_CLK_GEN_BASIC_SETUP` support audio clock programming.
- `R_40_SLICER_CNTL_1`, `R_41_LCR_BASE`, and `R_58` through `R_62` define VBI slicer control/status space.
- `R_80` through `R_EF` map scaler global registers and task A/task B acquisition, output, prescale, FIR, phase, and vertical-scaling registers.
- `R_F0` through `R_FF` name PLL2 and pulse-generator registers.
- SAA7113 masks such as `SAA7113_R_08_FSEL`, `SAA7113_R_08_AUFD`, `SAA7113_R_10_VRLN_MASK`, and `SAA7113_R_12_RTS*_MASK` support safe platform-data bit updates.

## Control Flow and State
This header has no runtime control flow and no persistent state. Its operational effect is compile-time naming of register addresses and bit fields. `saa7115.c` consumes these definitions in init tables, register-presence checks, scaler calculations, VBI configuration, and platform-data overrides.

## Dependencies and Integration Points
The file assumes Linux kernel integer types are available from the including C file. It is included directly by `saa7115.c`, and its constants align that driver with datasheet names and table comments. The `#if 0` block contains an unused future debug register-description table, showing intended diagnostic integration but no compiled code.

## Risks and Edge Cases
- Header correctness is foundational: a wrong constant silently writes the wrong hardware register in any consuming table or helper.
- Some names in the disabled debug table are stale or inconsistent, including references like `R_41_LCR` that do not match the active `R_41_LCR_BASE` macro. This is harmless while disabled but risky if resurrected.
- The register map intentionally spans multiple SAA711x variants; not every register is valid on every chip, so consumers must keep using model guards such as `saa711x_has_reg()`.
- There are no include guards in the snippet, so repeated inclusion in one translation unit would rely on current include structure rather than protection.

## Test Signals
The best validation is indirect: compile coverage of all active macros, runtime debug logs from `saa711x_has_reg()` for reserved writes, successful standards/scaler/VBI operations in `saa7115.c`, and any future debug-table enablement should first compile-check all macro names and compare register addresses against datasheets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa711x_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7127.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa7127.c

## Purpose
`saa7127.c` implements a V4L2 I2C subdevice driver for Philips SAA7127/SAA7129 video encoders and compatible SAA7126/SAA7128 variants. It configures analog TV output standard, output connector mode, test color bars, video enable, and VBI insertion services such as WSS, VPS, closed captions, and XDS.

## Important APIs, Types, and Functions
- `struct saa7127_state` stores the subdev, current standard, chip identity, input/output type, video enable flag, VBI enable/data state, and cached register values `reg_2d`, `reg_3a`, `reg_3a_cb`, and `reg_61`.
- `saa7127_write()` retries SMBus byte writes up to three times; `saa7127_read()` reads single registers.
- `saa7127_set_std()` selects 60 Hz, 50 Hz PAL, or 50 Hz SECAM register tables and updates DAC control state.
- `saa7127_set_output_type()` translates V4L2 routing output constants to DAC and input-port control register values.
- `saa7127_set_input_type()` selects normal input or the internal color-bar generator.
- `saa7127_set_wss()`, `saa7127_set_vps()`, `saa7127_set_cc()`, and `saa7127_set_xds()` validate service line/field and program VBI payload registers.
- Subdev ops cover core log/debug registers, video standard/routing/stream, and VBI data/sliced-format reporting.

## Control Flow and State
Probe validates SMBus support and performs two hardware identity checks: status/version bits in register 0 and reset value in burst-end register `0x29`. It then uses explicit I2C device data or writable SAA7129-only fade-key register probing to determine model identity. Initialization writes common registers, defaults to NTSC, enables both S-Video and composite output, disables all VBI services with a zeroed `v4l2_sliced_vbi_data`, optionally enables test image, turns video output on, and applies SAA7129 extras.

Routing first changes input type, then output type. Stream state maps to output/DAC registers: disabling masks output port control and sets DAC shutdown bits. VBI state persists in the state structure and is reflected through `.g_sliced_fmt()` and `.log_status()`.

## Dependencies and Integration Points
The driver depends on `media/i2c/saa7127.h` for input/output constants, V4L2 subdev video and VBI APIs, Linux I2C SMBus byte data, and optional advanced debug register access. Host board drivers select routing outputs and supply sliced VBI payloads.

## Risks and Edge Cases
- `saa7127_write_inittab()` ignores individual write failures, so table programming can partially fail while returning success.
- `saa7127_set_wss()` indexes `wss_strs[data->data[0] & 0xf]`; the mask is safe, but some modes are explicitly invalid yet still programmable.
- The `output_strs[output]` debug access assumes validated output; current switch validates before use.
- VBI line validation is strict and will reject board/user attempts to place services on alternate lines.
- Probe model auto-detection writes to a register to test SAA7129 behavior; this relies on the original value being restored.

## Test Signals
Test chip detection for explicit and auto IDs, standard switching among NTSC/PAL/SECAM-capable paths, each output type including SAA7127 versus SAA7129 differences, normal versus test-image input, stream disable register effects, valid and invalid WSS/VPS/CC/XDS payloads, `.g_sliced_fmt()` service bits, log status output, and advanced debug register access when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7127.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa717x.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa717x.c

## Purpose
`saa717x.c` is a reverse-engineered V4L2 I2C subdevice driver for Philips SAA717xHL audio/video decoder chips. It initializes decoder, scaler, gamma, and audio blocks from captured register sequences, supports NTSC-centric video capture, routes tuner/composite/S-Video inputs, controls audio volume/balance/bass/treble/mute, reports tuner audio status, and programs scaler output size.

## Important APIs, Types, and Functions
- `struct saa717x_state` stores video state, radio/playback flags, current audio mode, main audio controls, and selected audio input.
- `saa717x_write()` and `saa717x_read()` implement the device's mixed register protocol, using one-byte or three-byte values depending on address ranges.
- `reg_init_initialize` is the large startup script for video, scaler, and sound blocks. Smaller `reg_init_*_input` tables adjust tuner/composite/S-Video behavior.
- `get_inf_dev_status()` reads demodulator status register `0x528` and derives stereo/dual flags.
- `set_audio_mode()` programs output selection registers `0x46c` and `0x470`; `set_audio_regs()` maps V4L2 audio controls to volume/balance and tone registers.
- `saa717x_s_video_routing()`, `saa717x_set_fmt()`, `saa717x_s_stream()`, `saa717x_s_tuner()`, and `saa717x_g_tuner()` are the main runtime operations.

## Control Flow and State
Probe checks SMBus byte-data functionality, initializes the subdev, unlocks/reads chip ID registers, accepts known IDs, creates V4L2 image and audio controls, writes the full initialization table, applies controls, and sleeps for two seconds. Input routing strips a tuner flag from the high bit, validates mode numbers 0-9 except reserved mode 5, updates input selection and chroma trap, selects tuner or forced stereo audio mapping, and writes the matching input init table.

Format setting accepts fixed media-bus format, validates dimensions up to 1440x960, then computes NTSC-based horizontal prescale/fine-scale and vertical scale for both task A and B. Streaming toggles register `0x193` between output-enabled and disabled values. Standard setting only stores the requested standard and explicitly logs that implementation is missing.

## Dependencies and Integration Points
The driver uses V4L2 subdev core/tuner/video/audio/pad/control APIs and Linux I2C transfers. It registers as `saa717x`, expecting a parent bridge driver to route inputs, set format, and expose tuner/audio controls. The audio status logic was adapted from the SAA7134 driver family.

## Risks and Edge Cases
- The file states the driver is reverse engineered and currently only working for NTSC; PAL/SECAM standard setting is not implemented.
- `saa717x_write()` returns a boolean-like success value rather than standard negative errno, and many table writes ignore failures.
- `saa717x_read()` ignores `i2c_transfer()` return status and may interpret zeroed buffers as real data.
- The large init table has many unknown registers and repeated programming sequences, making changes difficult to validate.
- Format scaling uses NTSC constants regardless of `decoder->std`.
- Probe sleeps for two seconds unconditionally after initialization.

## Test Signals
Validation should include ID detection for accepted chip IDs, init table write tracing, tuner/composite/S-Video routing including rejected mode 5, audio mute/volume/balance/tone control writes, tuner audio status reads for mono/stereo/dual cases, stream toggle register effects, scaler programming for common NTSC output sizes, and negative tests showing non-NTSC standard requests do not actually reconfigure timing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa717x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7185.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/saa7185.c

## Purpose
`saa7185.c` is a V4L2 I2C subdevice driver for the Philips SAA7185B video encoder. It initializes PAL/NTSC encoder registers, supports standard switching, selects between upstream video inputs or internal color bars, and disables output on remove.

## Important APIs, Types, and Functions
- `struct saa7185` stores the subdev, a 128-byte register cache, and current output norm.
- `saa7185_write()` updates the register cache and writes one SMBus byte-data register.
- `saa7185_write_block()` batches sequential register/value pairs into raw I2C autoincrement blocks where supported, falling back to individual SMBus writes.
- `init_common`, `init_pal`, and `init_ntsc` are the fixed initialization tables.
- `saa7185_init()` applies common registers and the norm-specific table.
- `saa7185_s_std_output()` switches between PAL and NTSC tables.
- `saa7185_s_routing()` selects input source 0, input source 1, or color bars by programming colorbar, RTCE, and trigger registers.

## Control Flow and State
Probe requires SMBus byte-data support, allocates state, defaults to NTSC, initializes the subdev, writes common and NTSC tables, and logs chip revision from the read byte. Runtime state is minimal: standard changes rewrite only the small norm table and update `encoder->norm`; routing uses the cached `0x61` value to preserve unrelated bits while toggling RTCE behavior.

Input routing mode 0 is documented as input from SAA7111, mode 1 as input from ZR36060, and mode 2 as internal colorbar generation. Remove unregisters the subdev and writes bit `0x40` into register `0x61`, documented as active output-off.

## Dependencies and Integration Points
The driver integrates through V4L2 subdev core `.init` and video `.s_std_output`/`.s_routing` ops. It uses Linux I2C raw transfers or SMBus byte-data writes and is intended to sit behind older capture/codec bridge drivers that feed digital video to the encoder.

## Risks and Edge Cases
- `saa7185_write_block()` comments mention `adv7175`, suggesting copied batching logic; behavior still matches autoincrement register writes but should be reviewed carefully.
- The register cache is updated before confirming raw I2C transfer success, so cache can diverge from hardware on short writes.
- There is no explicit validation of output argument in routing; only input selects behavior.
- Standard support is only NTSC/PAL; SECAM or other V4L2 standards return `-EINVAL`.
- Probe does not fail on init write errors; it logs debug output and still returns success.

## Test Signals
Test probe on adapters with and without raw I2C support, common and NTSC/PAL table writes, `.s_std_output()` rejection of unsupported standards, routing modes 0/1/2 and invalid inputs, colorbar enable bit behavior, cached register preservation for `0x61`, revision logging, and output-off write during remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/saa7185.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/sony-btf-mpx.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/sony-btf-mpx.c

## Purpose
`sony-btf-mpx.c` implements a V4L2 I2C subdevice driver for the Sony BTF MPX audio processor used with analog TV tuners. It selects audio demodulation/prescale/system settings for TV standards and changes mono/stereo/bilingual routing according to V4L2 tuner audio mode.

## Important APIs, Types, and Functions
- `struct sony_btf_mpx` stores the subdev, selected MPX mode index, and current V4L2 audio mode.
- `mpx_audio_modes[]` is the central table of mode-specific register values for Auto, B/G, I, D/K, L/L', A2, and NICAM variants.
- `mpx_write()` sends a five-byte I2C message containing target device page, 16-bit register address, and 16-bit value.
- `mpx_setup()` resets the MPX block, selects the effective mode, derives the source-routing value for mono/stereo/lang1/lang2, writes all mode registers, and optionally writes A2 forced-mono control.
- `sony_btf_mpx_s_std()` maps V4L2 TV standards to default MPX mode table indices.
- `sony_btf_mpx_g_tuner()` advertises supported audio capabilities; `sony_btf_mpx_s_tuner()` changes requested audio mode and reprograms the device.

## Control Flow and State
Probe checks for `I2C_FUNC_SMBUS_I2C_BLOCK`, initializes the subdev, defaults mode to Auto and audio mode to stereo, and does not immediately program the chip. The first standard or tuner-audio change calls `mpx_setup()`. Standard changes pick the mono entry for the relevant family; if the user audio mode is not mono, `mpx_setup()` advances to the paired A2/NICAM entry where the table is arranged that way.

The state is purely volatile and kept in `mpxmode` and `audmode`. There is no register cache and no suspend/resume handling in this file.

## Dependencies and Integration Points
The driver depends on V4L2 subdev tuner and video standard ops, tuner audio constants, and Linux I2C transfers. It registers as `sony-btf-mpx`; a parent analog TV bridge/tuner driver is expected to call `.s_std`, `.g_tuner`, and `.s_tuner` as channel standards and user audio preferences change.

## Risks and Edge Cases
- `mpx_write()` ignores the return value from `i2c_transfer()` and always returns success.
- The `force_mpx_mode` module parameter is declared but never used, so it has no runtime effect.
- `mpx_setup()` increments `mode` when `audmode != MONO`; this depends on paired table ordering and could go out of range if `mpxmode` is forced or extended incorrectly.
- Probe's functionality check uses SMBus block capability while actual transfers use raw `i2c_transfer()`.
- No locking protects `mpxmode` and `audmode`; callers normally serialize subdev operations through the parent stack.

## Test Signals
Test standard-to-mode mapping for PAL B/G, PAL I, PAL D/K, and SECAM L; tuner mode changes for mono, stereo, lang1, and lang2; I2C write sequences for A2 forced mono versus stereo; advertised tuner capability and rxsubchans; behavior with unavailable I2C transfer support; and confirmation that `force_mpx_mode` currently has no observable effect.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/sony-btf-mpx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/st-mipid02.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/st-mipid02.c

## Purpose
`st-mipid02.c` is a V4L2 subdevice driver for the ST MIPID02 CSI-2 to parallel video bridge. It discovers the upstream CSI-2 sensor through async notifier plumbing, validates firmware endpoints, translates sink serial media-bus formats to source parallel formats, configures MIPI lane timing/polarity/data type and parallel bus width, and manages runtime power around streaming.

## Important APIs, Types, and Functions
- `struct mipid02_dev` stores I2C/regmap, supplies, subdev, media pads, xclk, reset GPIO, parsed RX/TX endpoints, async notifier state, bound source subdev, and a register-image cache.
- Format helpers `bpp_from_code()`, `data_type_from_code()`, `get_fmt_code()`, and `serial_to_parallel_code()` map V4L2 bus codes to MIPI CSI-2 data types, bit depth, and parallel output codes.
- `mipid02_set_power_on()` and `mipid02_set_power_off()` manage xclk, regulators, reset GPIO, and runtime PM callbacks.
- `mipid02_configure_from_rx()`, `_from_rx_speed()`, `_from_tx()`, and `_from_code()` build register values from endpoint and format state.
- Stream ops `mipid02_enable_streams()` and `mipid02_disable_streams()` power the device, program registers with CCI helpers, and delegate stream on/off to the upstream subdev.
- `mipid02_parse_rx_ep()`, `mipid02_parse_tx_ep()`, and async notifier callbacks establish firmware graph integration.

## Control Flow and State
Probe allocates state, validates xclk rate in the 6-27 MHz range, obtains reset GPIO and supplies, creates a 16-bit CCI regmap, initializes three media pads, finalizes subdev state, powers the chip for detection, parses TX and RX endpoints, registers an async notifier for the remote sensor, enables autosuspended runtime PM, and registers the subdev.

Active format state lives in the V4L2 subdev state object. Enabling streams clears the cached register image, derives lane enables/swap/polarity and UI timing from remote link frequency, derives parallel bus flags and width from TX endpoint, sets manual data type except for JPEG, writes all bridge registers, and then enables the upstream stream. Disabling streams stops upstream first, disables all lanes, and releases runtime PM.

## Dependencies and Integration Points
The driver uses V4L2 fwnode endpoint parsing, async subdev notifiers, media-controller pads/links, CCI regmap helpers, runtime PM, regulators, clocks, GPIO descriptors, and MIPI CSI-2 data type constants. Device tree compatible is `st,st-mipid02`.

## Risks and Edge Cases
- Only sink pad 0 is supported; sink 1 returns `-EINVAL`.
- Clock lane must be lane 0 and at most two data lanes are supported.
- `mipid02_configure_from_rx_speed()` requires the upstream entity pad and link-frequency controls to be available; missing controls fail stream-on.
- Error cleanup in stream-on disables lanes and releases runtime PM, but upstream stream is only enabled after register writes, so no upstream disable is needed in that path.
- JPEG bypasses manual data type, relying on hardware auto-detection.
- Probe powers the device before endpoint parsing and must unwind notifier, PM, power, and media entity state correctly on failures.

## Test Signals
Test endpoint parsing for valid and invalid lane counts, clock-lane remapping rejection, lane swap/polarity register values, all supported media-bus code enumeration and source-code conversion, link-frequency failure when the upstream sensor lacks controls, stream-on/off register writes, runtime PM autosuspend, async media link creation, and remove cleanup after a bound sensor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/st-mipid02.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/t4ka3.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/t4ka3.c

## Purpose
`t4ka3.c` is a V4L2 sensor subdevice driver for the Toshiba T4KA3 8 MP Bayer camera sensor. It supports ACPI-enumerated hardware, CSI-2 endpoint validation, CCI register access, runtime power via GPIOs, crop/format selection with optional 2x binning, exposure/gain/blanking/flip/test-pattern controls, and stream start/stop sequences.

## Important APIs, Types, and Functions
- `struct t4ka3_data` stores the subdev, source pad, state mutex, controls, current calculated mode, device/regmap/GPIOs, streaming flag, and CSI-2 link metadata.
- `struct t4ka3_ctrls` groups V4L2 controls for flips, blanking, exposure, gain, test pattern, link frequency, and pixel rate.
- Register tables `t4ka3_init_config`, `t4ka3_pre_mode_set_regs`, and `t4ka3_post_mode_set_regs` program undocumented sensor setup and mode sequencing.
- `t4ka3_calc_mode()` decides 1x or 2x binning and computes centered crop-window start after binning.
- `t4ka3_set_pad_format()` clamps aligned output size to the crop rectangle, updates active state, recalculates mode, and adjusts vblank/hblank controls.
- `t4ka3_s_ctrl()` applies powered controls, including exposure range updates when vblank changes.
- `t4ka3_enable_stream()` powers the sensor, writes init/mode tables under group hold, restores controls, clears group hold, and starts streaming.
- `t4ka3_check_hwcfg()` validates the fwnode CSI-2 endpoint and requires exactly four data lanes.

## Control Flow and State
Probe checks firmware link frequencies and lane count, initializes the mutex and subdev, obtains powerdown and optional reset GPIOs, initializes a 16-bit CCI regmap, powers the sensor and verifies product ID `0x1490`, enables runtime PM, initializes media entity and active state, creates controls, registers the sensor subdev, and idles runtime PM.

Format and crop state are managed through the V4L2 subdev active state. The default crop is the active 3280x2460 area starting at row 2. Format changes are rejected while active streaming, preserve Bayer order according to flip controls, and choose 2x binning when requested dimensions fit within half the crop. Streaming state is separately tracked by `sensor->streaming` to block layout-changing flip and active format changes. Runtime PM resume deasserts GPIOs, waits, and re-detects the chip; suspend asserts powerdown and reset.

## Dependencies and Integration Points
The driver depends on ACPI ID `XMCC0003`, V4L2 subdev sensor registration, media entity source pad, CCI regmap helpers, V4L2 fwnode endpoint parsing and link-frequency matching, runtime PM, GPIO descriptors, mutex-backed control locking, and V4L2 stream helpers. Downstream bridge drivers consume its source pad, media-bus code, frame sizes, and link-frequency/pixel-rate controls.

## Risks and Edge Cases
- Many register values and timing constants are based on reverse engineering or comments without a datasheet; link frequency and vblank limits are approximations.
- `t4ka3_set_selection()` recalculates mode using the old crop pointer before assigning the new crop, so crop-size changes deserve focused review.
- Flip controls are blocked while streaming because they change Bayer order/layout.
- `t4ka3_disable_stream()` returns 0 even when the stream-off register write fails, only logging the error.
- Probe sets `sensor->sd.state_lock = sensor->ctrls.handler.lock` before controls initialize the handler lock, which should be checked against current V4L2 subdev expectations.
- Runtime resume performs chip detection every power-up, making resume dependent on I2C availability and sensor boot timing.

## Test Signals
Test ACPI probe, four-lane endpoint validation, link-frequency bitmap matching, product-ID failure and success paths, default crop/format initialization, crop and format alignment/clamping, full-size and half-size frame-size enumeration, vblank-driven exposure range changes, hblank read-only value updates, flip Bayer-order changes while stopped and `-EBUSY` while streaming, stream-on register sequence with group hold, runtime suspend/resume GPIO levels, and logged stream-off failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/t4ka3.c -->
