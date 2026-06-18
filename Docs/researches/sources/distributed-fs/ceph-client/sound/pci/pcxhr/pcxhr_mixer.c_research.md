# sources/distributed-fs/ceph-client/sound/pci/pcxhr/pcxhr_mixer.c

## Purpose

This file implements ALSA mixer controls for PCXHR boards. It creates analog and digital volume controls, playback switches, capture source selection, monitoring controls, clock mode/rate controls, IEC958 controls, and HR222 mic controls when applicable. It bridges ALSA control state to DSP RMH commands or HR222-specific register programming.

## Important APIs, Types, And Functions

- `pcxhr_create_mixer()` is the exported mixer setup entry.
- Analog controls use `pcxhr_analog_vol_*()` and `pcxhr_audio_sw_*()`, with HR222 dispatch where required.
- Digital PCM playback/capture controls use `pcxhr_pcm_vol_*()`, `pcxhr_pcm_sw_*()`, `pcxhr_update_playback_stream_level()`, and `pcxhr_update_audio_pipe_level()`.
- Monitoring controls use `pcxhr_monitor_vol_*()` and `pcxhr_monitor_sw_*()`.
- Capture routing uses `pcxhr_audio_src_*()` and generic `pcxhr_set_audio_source()` or HR222 `hr222_set_audio_source()`.
- Clock controls use `pcxhr_clock_type_*()` and `pcxhr_clock_rate_*()`.
- IEC958 controls use `pcxhr_iec958_*()` and HR222-specific IEC958 helpers when needed.
- `pcxhr_init_audio_levels()` seeds runtime mixer caches and writes initial hardware values where required.

## Control Flow

`pcxhr_create_mixer()` initializes `mixer_mutex`, iterates logical chips, and conditionally adds controls based on playback/capture availability. Playback cards get analog master volume/switch, per-stream PCM volume/switch, and playback IEC958 controls. Capture cards get line capture volume, PCM capture volume, capture source, and capture IEC958 controls. Cards with both directions get monitoring volume/switch. Chip 0 gets manager-wide clock controls. HR stereo capture cards may get mic controls from `hr222_add_mic_controls()`.

Each ALSA `put` callback validates the requested value, updates the cached field in `snd_pcxhr` or `pcxhr_mgr` under `mixer_mutex`, and sends the appropriate hardware command. Generic boards send RMH commands for analog levels, digital stream levels, monitor levels, source routing, SRC programming, IEC958 bit writes, and clock changes. HR stereo boards call `pcxhr_mix22.c` helpers for analog/mic/source/IEC958 details.

## State And Persistence

Mixer state is cached in `struct snd_pcxhr`: analog playback active/volume, analog capture active/volume, digital playback active/volume, digital capture volume, monitoring active/volume, capture source, mic volume/boost/active, phantom power, and AES status bytes. Manager-wide mixer state includes selected and current clock type/rate. State is memory-only and reinitialized at mixer creation.

## Dependencies And Integration Points

This file depends on ALSA control/TLV APIs, shared PCXHR structures, RMH command definitions from `pcxhr_core.h`, firmware availability from `pcxhr_hwdep.h`, and HR222 helpers. It is called after firmware and pipe setup so hardware commands are expected to succeed.

## Risks

- Many controls ignore out-of-range per-channel values by continuing instead of returning `-EINVAL`, so userspace may see partial updates.
- Clock mode changes nest `mixer_mutex` and `setup_mutex` and can send DSP clock commands; lock ordering must remain consistent with PCM open/prepare paths.
- Capture source enumeration size depends on `board_has_aes1` and `board_has_mic`; incorrect board flags expose invalid controls or hide valid ones.
- IEC958 write loops update one bit at a time through DSP commands; partial failures can leave cache and hardware inconsistent because some helper return values are ignored by callers.
- `pcxhr_init_audio_levels()` has extra hardware initialization under `CONFIG_SND_DEBUG`, so debug and non-debug builds differ in initial analog writes for generic boards.

## Test Signals

Use `amixer`/ALSA control tests to enumerate controls per board type, write min/max/out-of-range values, verify playback/capture/monitor levels on running streams, switch clock sources with active/inactive streams, read external clock rates, change IEC958 playback bits, read capture IEC958 bits, and verify HR222-specific mic controls only appear on mic boards.
