# sources/distributed-fs/ceph-client/sound/core/pcm_drm_eld.c

## Purpose

`pcm_drm_eld.c` contains ALSA helpers for HDMI/DisplayPort ELD data. It parses DRM ELD blobs into `snd_parsed_hdmi_eld`, constrains PCM hardware rates/channels based on sink Short Audio Descriptors, and prints ELD information for debug and procfs output.

## Important APIs, Types, and Functions

Exported APIs are `snd_pcm_hw_constraint_eld()`, `snd_parse_eld()`, `snd_show_eld()`, and, under procfs, `snd_print_eld_info()`. Internal helpers include `sad_rate_mask()`, `sad_max_channels()`, `eld_limit_rates()`, `eld_limit_channels()`, `hdmi_update_short_audio_desc()`, and multiple printing helpers for rates, sample bits, speaker allocation, and SAD fields.

## Control Flow

`snd_pcm_hw_constraint_eld()` adds reciprocal hw-rules: rate constraints depend on requested channels, and channel constraints depend on requested rate. The rules walk the ELD SAD list and derive allowed rate masks and maximum channels. `snd_parse_eld()` validates ELD version, baseline length, monitor-name length, SAD bounds, then extracts monitor identity, connection type, speaker allocation, port ID, manufacturer/product IDs, and all SADs. Debug/proc print paths format the parsed structure into human-readable output.

## State and Persistence Behavior

This file does not own long-lived global state. Parsed ELD persists in caller-provided `struct snd_parsed_hdmi_eld`; hw constraints store the caller's ELD pointer as rule private data in the PCM runtime. If speaker allocation is absent but SADs exist, parsing defaults `spk_alloc` to all speakers to avoid over-restricting playback.

## Dependencies and Integration Points

Dependencies include DRM EDID/ELD helpers, HDMI coding constants, ALSA PCM hw-rule APIs, ALSA info buffers, unaligned access helpers, and device logging. HDMI/DP audio drivers use these helpers to limit PCM params to sink capabilities and expose connector audio information.

## Risks and Edge Cases

ELD buffers can be malformed, so bounds checks on monitor names and SAD entries are critical. Compressed formats map channel/rate capabilities differently from LPCM, and unsupported coding types fall back to generic masks. Constraint logic must consider both rate and channel intervals or it can reject valid modes or allow unsupported sink combinations.

## Test Signals

Test valid and malformed ELD blobs, HDMI and DisplayPort connection types, LPCM and compressed SADs, no speaker-allocation fallback, hw-param refinement for rate/channel combinations, debug output, and procfs ELD formatting when `CONFIG_SND_PROC_FS` is enabled.
