# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_decoder.c

## Purpose
`au8522_decoder.c` implements the AU8522 analog video decoder V4L2 subdevice side. It supports CVBS and S-video routing, limited NTSC/PAL-M standard setup, audio SIF setup, V4L2 controls, tuner signal reporting, and I2C-driver registration.

## Important APIs, Types, And Functions
The file defines filter coefficient tables, LP audio filter coefficients, V4L2 subdev ops, and I2C probe/remove. Important functions include `setup_decoder_defaults()`, `au8522_setup_cvbs_mode()`, `au8522_setup_cvbs_tuner_mode()`, `au8522_setup_svideo_mode()`, `set_audio_input()`, `au8522_s_ctrl()`, `au8522_video_set()`, `au8522_s_stream()`, `au8522_s_video_routing()`, `au8522_s_std()`, `au8522_s_audio_routing()`, `au8522_g_tuner()`, and `au8522_probe()`.

## Control Flow
Probe verifies I2C SMBus byte-data support, obtains shared AU8522 state, initializes the V4L2 I2C subdev, optionally sets media-controller pads, registers brightness/contrast/saturation/hue controls, initializes default NTSC/composite/no-audio state, and opens the tuner I2C gate. Starting stream clears digital current frequency, resets module control, programs video route defaults based on `state->vid_input`, configures audio, and marks analog mode. Stopping stream reduces power and marks suspend mode. Routing/std/audio setters update state and reprogram hardware if analog streaming is active. Tuner status reads decoder lock and PLL registers to report signal.

## State And Persistence
Analog state shares `struct au8522_state` with digital code. Fields include V4L2 subdev, control handler, media pads, standard, video input, audio input, operational mode, client pointer, id/rev, and digital caches cleared when analog starts. There is no persistence beyond module lifetime.

## Dependencies And Integration Points
The decoder depends on V4L2 core/subdev/control APIs, Linux I2C, AU8522 public/private headers, and common register/state helpers. It is built under `DVB_AU8522_V4L` and selects common support through Kconfig.

## Risks
Developer notes state that true analog demodulator code is not implemented; the driver is enough for CVBS/S-video inputs such as tuner-provided CVBS. Many register writes are fire-and-forget with no error propagation. Only a subset of routes is accepted despite enum definitions. Media-entity init failure returns without releasing shared state in that branch. The S-video path intentionally uses CVBS filter type due to hardware/board behavior, which is surprising but documented in comments.

## Test Signals
V4L2 tests should cover probe/remove, control writes, stream on/off, composite and S-video routing, PAL-M/NTSC standard changes, audio SIF enable/disable, ADV_DEBUG register access when enabled, and media-controller pad registration. Hardware tests should confirm analog/digital handoff does not corrupt the DTV frontend state.
