# sources/distributed-fs/ceph-client/sound/core/oss/route.c

## Purpose

`route.c` implements the OSS PCM channel-routing plugin. It adapts channel counts when sample format and rate already match, supporting mono expansion, channel reduction, direct channel copies, and silence for missing destination channels.

## Important APIs, Types, and Functions

The exported builder is `snd_pcm_plugin_build_route()`. It validates identical source/destination rate and format, creates a plugin named `route conversion`, and installs `route_transfer()`. Internal helpers `zero_areas()` and `copy_area()` silence or copy `struct snd_pcm_plugin_channel` areas.

## Control Flow

`route_transfer()` clamps frames to destination channel capacity. If there is one source channel, it copies that channel into every destination. Otherwise it copies matching source-to-destination channels until either side ends, then silences remaining wanted destination channels. The plugin returns the number of destination frames processed.

## State and Persistence Behavior

The route plugin is stateless after construction; all behavior derives from plugin source/destination channel counts and per-transfer channel arrays. Destination channel `enabled` flags are updated on each call.

## Dependencies and Integration Points

It depends on `pcm_plugin.h`, `snd_pcm_area_copy()`, and `snd_pcm_area_silence()`. `pcm_plugin.c` inserts it before rate conversion for channel reduction and after format/rate conversion for channel extension.

## Risks and Edge Cases

The route policy is simple duplication/truncation rather than a mixing matrix. Multi-channel downmix does not combine channels; it drops channels beyond destination count. Missing destinations are silenced only when `wanted` is set, so callers must populate channel metadata correctly.

## Test Signals

Exercise mono-to-stereo expansion, stereo-to-mono reduction, multichannel truncation, capture and playback directions, disabled destination channels, and format/rate mismatch rejection in the builder.
