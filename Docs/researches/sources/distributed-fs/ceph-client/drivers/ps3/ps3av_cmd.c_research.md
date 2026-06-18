# sources/distributed-fs/ceph-client/drivers/ps3/ps3av_cmd.c Research

## Purpose
`ps3av_cmd.c` builds PS3 AV command packets and translates high-level mode/audio requests into the firmware packet formats consumed by `ps3av_do_pkt()`. It is the protocol encoding companion to `ps3av.c`.

## Important APIs, Types, And Functions
The file exports command helpers such as `ps3av_cmd_init()`, `ps3av_cmd_fin()`, mute/TV/HDMI mode functions, `ps3av_cmd_set_av_video_cs()`, `ps3av_cmd_set_video_mode()`, `ps3av_cmd_video_format_black()`, `ps3av_cmd_set_audio_mode()`, `ps3av_cmd_set_av_audio_param()`, `ps3av_cmd_audio_mode()`, `ps3av_cmd_audio_mute()`, `ps3av_cmd_audio_active()`, `ps3av_cmd_avb_param()`, `ps3av_cmd_av_get_hw_conf()`, and `ps3av_cmd_video_get_monitor_info()`. Conversion tables map video color spaces and video IDs to AV backend constants. Audio helpers convert sample rate, word width, FIFO maps, channel layouts, IEC channel status, and HDMI audio info frames.

## Control Flow
Most helpers zero a packet struct, populate command-specific fields, call `ps3av_do_pkt()` with exact send and user-buffer sizes, then return `get_status()` from the reply. `ps3av_cmd_init()` initializes video, audio, then AV modules in order; `ps3av_cmd_fin()` shuts down AV. `ps3av_cmd_set_video_mode()` only formats an in-memory sub-packet for an AVB aggregate; the caller later submits it via `ps3av_cmd_avb_param()`. `ps3av_cmd_avb_param()` takes `ps3_gpu_mutex` around the packet transaction, coupling mode programming with GPU access.

## State And Persistence
The file has little private runtime state. `ps3av_mode_cs_info` is exported as default audio channel-status bytes and can be reused by other PS3 audio code. Hardware state changes persist in the AV backend after command submission: muting, video color space, HDMI mode, video timings, audio route and channel status, and active/inactive audio bits.

## Dependencies And Integration Points
It depends on packet definitions in `asm/ps3av.h`, PS3 firmware version checks via `ps3_compare_firmware_version()`, GPU locking via `ps3_gpu_mutex`, and the transport provided by `ps3av_do_pkt()` in `ps3av.c`. Callers are expected to provide valid AV port ids and video mode ids chosen by higher-level code.

## Risks
Several conversion fallbacks silently choose defaults, for example RGB8 or 480p, which can hide invalid inputs. `ps3av_cnv_ns()` appears to index the 44 kHz row for all valid sample rates rather than indexing by `fs - BASE`, so audio N values deserve regression attention. Aggregated AVB packet length is accumulated by callers and must remain within firmware packet limits. Many errors are logged but not escalated by higher layers.

## Test Signals
Test by comparing generated packet bytes for each supported video and audio mode against firmware documentation, validating status propagation for every command CID, exercising HDMI range options on firmware below and above 1.8.0, checking AVB length composition, and verifying audio sample-rate/channel combinations over HDMI and SPDIF.
