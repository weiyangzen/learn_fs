<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.c

## Purpose
`solo6x10-tw28.c` detects and configures Techwell TW2815/TW2864/TW2865 video/audio decoder chips and the SAA7128 output encoder used on SOLO6x10 cards, and exposes decoder controls to V4L2/ALSA code.

## Important APIs, Types, and Functions
Large PAL/NTSC register templates feed `tw2865_setup()`, `tw2864_setup()`, and `tw2815_setup()`. `solo_tw28_init()` probes chip IDs and performs setup. `tw28_get_video_status()`, `tw28_has_sharpness()`, `tw28_set_ctrl_val()`, `tw28_get_ctrl_val()`, `tw28_get_audio_gain()`, and `tw28_set_audio_gain()` are exported to other SOLO files. `saa712x_setup()` programs the video output encoder.

## Control Flow
Initialization scans one TW chip per four video channels over the SOLO TW I2C adapter, classifies each chip by ID registers, verifies the expected chip count, configures SAA7128 PAL/NTSC output, and writes the appropriate decoder template for each chip. TW2864/TW2865 setup modifies template fields for channel count, cascade/ALINK/IRQ mode, and chip address before skipping read-only registers and writing with verification. TW2815 setup builds active timing fields, configures audio routing, writes per-channel decoder registers, then writes shared SFR audio/control registers.

## State and Persistence
Detected chip masks `tw2865`, `tw2864`, `tw2815`, and `tw28_cnt` live in `struct solo_dev`. Decoder settings are volatile I2C-programmed hardware registers. Picture and audio gain controls persist only while hardware remains powered.

## Dependencies and Integration Points
The file depends on the SOLO I2C adapters, V4L2 control IDs, `solo_dev->video_type` and `nr_chans`, and TW28 register macros from `solo6x10-tw28.h`. Live and encoded V4L2 nodes use video status and picture controls; ALSA uses audio gain controls.

## Risks and Edge Cases
Probe requires all expected decoder chips; partial detection fails the whole init. Template writes rely on magic hardware tables and selective read-only skips. `tw28_set_ctrl_val()` checks chip number against `TW_NUM_CHIP` but assumes channel numbers are otherwise valid. The sharpness path uses a TW286x macro with the chip number where other calls use the on-chip channel, which deserves hardware regression attention.

## Test Signals
Check detection for TW2815, TW2864, TW2865, PAL and NTSC setup, 4/8/16-channel audio/video routing, SAA7128 programming, video loss reporting per channel, V4L2 brightness/contrast/saturation/hue/sharpness controls, and ALSA capture gain changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/solo6x10/solo6x10-tw28.c -->
