# sources/distributed-fs/ceph-client/sound/core/oss/pcm_plugin.h

## Purpose

`pcm_plugin.h` defines the OSS PCM plugin interface shared by `pcm_oss.c` and the individual conversion plugins. It is the contract for plugin chain construction, frame-size conversion, channel-area layout, transfer callbacks, and fallback stubs when OSS plugins are disabled.

## Important APIs, Types, and Functions

Important types are `enum snd_pcm_plugin_action`, `struct snd_pcm_channel_area`, `struct snd_pcm_plugin_channel`, `struct snd_pcm_plugin_format`, and `struct snd_pcm_plugin`. The plugin object stores source/destination format triples, physical sample widths, access mode, frame-count callbacks, channel-buffer callback, transfer callback, action callback, list links, owning substream, optional private data, and scratch buffers.

Function declarations cover base plugin allocation/free, chain allocation, client/slave frame conversion, concrete builders for I/O, linear, mu-law, rate, route, and copy plugins, format-chain construction, transfer execution, client channel setup, and area copy/silence helpers. The header also exports OSS low-level read/write helpers used by plugin I/O nodes.

## Control Flow

Consumers build a chain by allocating concrete plugins with builder functions and linking them through `snd_pcm_plugin_append()` or insertion helpers in `pcm_oss.c`. During transfer, plugin callbacks consume arrays of `snd_pcm_plugin_channel` entries and optionally produce downstream channel arrays. `INIT` and `PREPARE` actions let stateful plugins reset conversion state before use.

## State and Persistence Behavior

The header does not store state directly, but it defines the state shape embedded in `runtime->oss` plugin lists. With `CONFIG_SND_PCM_OSS_PLUGINS` disabled, inline stubs make client/slave frame sizes identity mappings and return the requested format directly, so callers can compile without plugin conversion support.

## Dependencies and Integration Points

It depends on ALSA PCM types and is included by `pcm_oss.c`, `pcm_plugin.c`, `rate.c`, `route.c`, and other OSS plugin implementations. `FULL` and `HALF` expose route resolution constants from the wider OSS plugin subsystem.

## Risks and Edge Cases

The interface is sensitive to format width and channel count consistency. Plugins must honor channel `enabled`, `wanted`, `frames`, `area.first`, and `area.step`, or downstream code may copy invalid memory. Stub behavior when plugins are disabled means callers must still be able to operate in direct-compatible modes.

## Test Signals

Build both plugin-enabled and plugin-disabled configurations. Runtime validation should cover each concrete builder, `PREPARE` action reset behavior, channel-area interleaved and noninterleaved layouts, and OSS direct-mode fallback.
