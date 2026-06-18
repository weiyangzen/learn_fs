# sources/distributed-fs/ceph-client/drivers/gpu/drm/omapdrm/dss/hdmi5_core.h

Purpose: Declares the OMAP5 HDMI core register map, video configuration structs, CSC coefficient table, packet mode enum, and public OMAP5 core/audio/DDC APIs.

Important APIs/types: Register definitions cover identification, interrupt handler status/mute, video sampler, packetizer, frame composer, audio core, generic parallel audio, main controller, CSC, HDCP/CEC masks, and I2C master registers. `enum hdmi_core_packet_mode` declares pixel-packing packet modes. `struct hdmi_core_vid_config` combines a wrapper/frame-composer `hdmi_config`, packet mode, data enable polarity, vertical blank oscillator flag, and blanking lengths. `struct csc_table` stores 3x4 fixed-point CSC coefficients. Public prototypes include DDC init/read/uninit, core dump/init/configure, and `hdmi5_audio_config()`.

Control flow: This header supports `hdmi5_core.c` register programming and is included by the HDMI5 top-level driver. Callers are expected to initialize `struct hdmi_core_data` with `hdmi5_core_init()` before video, audio, DDC, or dump operations.

State and persistence: No runtime state is allocated by the header. It defines register constants and stack/config data shapes used to program volatile HDMI hardware.

Dependencies/integration: Includes common `hdmi.h` definitions for shared OMAP HDMI structs and enums. Integrates with DRM bridge enable, EDID read, OMAP HDMI audio, and debugfs register dumping.

Risks and test signals: Register map correctness is critical because helper macros do raw MMIO field writes. The header includes a broad register surface, but implementation uses a subset; unused offsets still need compile-time consistency with the core IP. Test by building HDMI5/DRA7 configs and exercising video, DDC, audio, interrupt masking, and debugfs paths.
