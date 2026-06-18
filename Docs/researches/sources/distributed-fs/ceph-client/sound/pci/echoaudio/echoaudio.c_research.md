# sources/distributed-fs/ceph-client/sound/pci/echoaudio/echoaudio.c

## Purpose

This is the shared ALSA PCI driver implementation included by each Echoaudio card wrapper. It handles firmware caching, PCM devices, controls, IRQs, probe/create/free, and suspend/resume using card-specific macros and DSP functions supplied by the including file.

## Important APIs, types, and functions

Major groups are firmware helpers (`get_firmware()`, `free_firmware_cache()`), PCM callbacks (`pcm_open()`, `init_engine()`, `pcm_prepare()`, `pcm_trigger()`, `pcm_pointer()`), control handlers for output/input gain, nominal levels, monitor/vmixer, digital mode, SPDIF mode, clock source, phantom power, automute, VU meters, and channel info, IRQ handler `snd_echo_interrupt()`, creation functions `snd_echo_create()` and `__snd_echo_probe()`, and PM callbacks `snd_echo_suspend()`/`snd_echo_resume()`. The PCI driver is registered as `echo_driver`.

## Control flow

Probe creates a managed ALSA card with `struct echoaudio`, maps DSP registers, requests IRQ, allocates the DSP comm page, calls card-specific `init_hw()` and `set_mixer_defaults()`, then registers PCM, MIDI if enabled, controls based on feature macros and runtime capability flags, and the ALSA card. PCM open installs constraints and SG-list memory; hw_params allocates pipes, builds DSP SG instructions, sets the global sample rate, and stores the substream. Prepare sets audio format. Trigger starts/stops/pauses transport for grouped substreams. IRQ service calls card DSP service code, checks every running substream for period advancement, and forwards MIDI input.

## State and persistence behavior

Persistent state is `struct echoaudio`: locks, mode mutex, open-count/rate gating, PCM/MIDI handles, firmware cache, DSP register mapping, comm page, pipe allocation/cyclic masks, sample rate, digital mode, clock source, gains, monitor/vmixer matrices, nominal levels, meter state, ASIC/firmware status, and optional MIDI/3G fields. Firmware entries are cached until card free. Suspend sends the DSP comatose vector, frees IRQ, clears DSP code; resume reloads hardware, restores DSP settings, restores selected comm-page arrays, and re-requests IRQ.

## Dependencies and integration points

It depends on the including card file for `ECHOCARD_*` macros, `snd_echo_ids`, `card_fw`, `pcm_hardware_skel`, and card-specific DSP functions. It uses ALSA core/PCM/control/rawmidi APIs, PCI managed resources, firmware loader, DSP helper functions from `echoaudio_dsp.c`, optional `midi.c`, and optional 3G helpers.

## Risks and test signals

Risks include include-based compile-unit coupling, global sample-rate policy across open streams, lock ordering between `mode_mutex` and spinlocks, period detection without hardware source IDs, firmware cache lifetime, suspend/resume restoration gaps, and many feature-macro paths that compile only for some cards. Test signals include all selected card modules building, probe/remove, firmware load and cache release, PCM constraints for analog/digital paths, grouped trigger behavior, mixer control get/put, VU meters, MIDI IRQ path, PM resume with previous mixer/format settings, and race testing while opening streams and changing digital/clock modes.
