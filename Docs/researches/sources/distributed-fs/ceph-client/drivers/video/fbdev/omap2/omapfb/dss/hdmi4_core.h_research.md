# sources/distributed-fs/ceph-client/drivers/video/fbdev/omap2/omapfb/dss/hdmi4_core.h

## Purpose
`hdmi4_core.h` defines the OMAP4 HDMI core register map, field value enums, private video/audio configuration structs, and exported HDMI4 core function prototypes used by `hdmi4_core.c` and its display driver.

## Important APIs, types, and functions
The header declares SYS, DDC, and AV register offsets such as `HDMI_CORE_SYS_SYS_CTRL1`, `HDMI_CORE_DDC_STATUS`, `HDMI_CORE_AV_ACR_CTRL`, and infoframe byte macros. It defines enums for input bus width, dither/truncation, deep-color packet enable, packet modes, TMDS clock multiplier, packet enable/repeat flags, and I2S bit layout. Key structs are `struct hdmi_core_video_config` and `struct hdmi_core_packet_enable_repeat`. Public prototypes cover EDID, video configure, debug dump, core init, and audio config/start/stop.

## Control Flow
The header has no runtime flow, but it encodes the register contract used by OMAP4 HDMI operations. `hdmi4_configure` consumes the video config enums to program SYS and AV registers, while `hdmi4_audio_config` uses the I2S enum bits and AV audio offsets to program ACR and channel-status registers.

## State and Persistence
There is no software state in the header. Its constants describe hardware state that persists in the HDMI core until reset, power loss, or a later configuration call. The packet byte macros define register layout for repeated AVI, SPD, audio, MPEG, and generic packets.

## Dependencies and Integration Points
It includes `hdmi.h` for common OMAP HDMI data structures, common register access macros, and shared audio/video enums. It is tightly coupled to `hdmi4_core.c`; mismatches in bit values or offsets directly affect register programming.

## Risks
Risks are stale or incorrect register offsets, typo-prone enum values, and the legacy typo `HDMI_DEEPCOLORPACKECT...` being part of the local API. The header exposes only the supported subset of the core, so future deep-color or packet features would require carefully extending these constants.

## Test Signals
Build coverage of `hdmi4_core.c`, register dump comparisons against the TRM, EDID/DDC behavior, AVI/audio packet bytes on a sink or analyzer, and audio/video bring-up on OMAP4 variants are the main validation signals.
