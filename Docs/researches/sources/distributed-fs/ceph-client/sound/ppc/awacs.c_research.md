# sources/distributed-fs/ceph-client/sound/ppc/awacs.c

## Purpose

This file implements codec programming, mixer controls, optional CUDA amplifier controls, suspend/resume replay, and automute for PowerMac AWACS and Screamer codecs.

## Important APIs, types, and functions

`snd_pmac_awacs_init()` is the exported initialization entry. Low-level writers `snd_pmac_awacs_write()`, `snd_pmac_awacs_write_reg()`, and `snd_pmac_awacs_write_noreg()` program codec registers and maintain `chip->awacs_reg[]`. `snd_pmac_awacs_set_format()` is installed as `chip->set_format`. Numerous ALSA controls are generated through `AWACS_VOLUME` and `AWACS_SWITCH`; optional `struct awacs_amp` controls are used on CUDA amplifier systems. `snd_pmac_awacs_detect_headphone()` and `snd_pmac_awacs_update_automute()` integrate jack detection.

## Control flow

Initialization chooses model-specific mixer sets based on Open Firmware machine compatibility and device id, seeds codec register cache with muted defaults, writes all registers, reads manufacturer/revision, optionally initializes the external amplifier, builds ALSA controls, installs PM and automute callbacks, and updates mute routing. Format changes update the sample-rate bits in codec register 1. Resume restores cached registers, recalibrates Screamer when needed, and replays amplifier state.

## State and persistence behavior

`chip->awacs_reg[0..7]` is the authoritative codec cache. Additional state includes `chip->hp_stat_mask`, `chip->master_sw_ctl`, `speaker_sw_ctl`, `hp_detect_ctl`, and optional `struct awacs_amp` in `chip->mixer_data`. The code uses `reg_lock` around cached register updates.

## Dependencies and integration points

It depends on `pmac.c` for MMIO mapping, control interrupt handling, PCM format callbacks, and `snd_pmac_add_automute()`. It uses AWACS register definitions from `awacs.h`, Open Firmware machine matching, NVRAM history comments, ALSA control/vmaster APIs, and optional CUDA ADB I2C-like amplifier access.

## Risks and test signals

Risks include model-detection mistakes, cached register divergence, long Screamer recalibration delays, a likely typo in `snd_pmac_awacs_put_volume()` returning `oldval != reg`, and fragile automute differences across iMac/PowerBook/G4 variants. Test mixer enumeration per machine family, headphone/speaker automute notifications, suspend/resume audio restoration, rate switching, and external amplifier controls where available.
