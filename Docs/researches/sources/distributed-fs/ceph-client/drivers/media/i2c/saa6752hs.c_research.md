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
