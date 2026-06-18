# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp.c

## Purpose
Provides the platform-driver entry point for the ALSA PC speaker driver. It creates the global `pcsp_chip`, registers the input beeper device, optionally creates PCM playback, creates mixer controls, and stops the speaker on suspend/shutdown/free.

## Important APIs, Types, And Functions
Defines module parameters `index`, `id`, `enable`, and `nopcm`, plus global `struct snd_pcsp pcsp_chip`. Important functions are `snd_pcsp_create()`, `snd_card_pcsp_probe()`, `alsa_card_pcsp_init()`, `pcsp_probe()`, `pcsp_stop_beep()`, `pcsp_suspend()`, `pcsp_shutdown()`, `pcsp_init()`, and `pcsp_exit()`.

## Control Flow
Module init registers a platform driver named `pcspkr` unless disabled. Probe first registers the input beeper device, then creates an ALSA card and initializes timer parameters based on hrtimer resolution and CPU loop calibration. If timer resolution is insufficient, it forces `nopcm` mode. Otherwise it creates the PCM device via `snd_pcsp_new_pcm()`, always creates mixer controls, names/registers the card, and records chip driver data. Suspend, shutdown, and card free all stop PCM/beep output.

## State And Persistence
`pcsp_chip` is a single global runtime object containing the card, input device, hrtimer, playback pointers, port state, enable flags, treble settings, and PCM state. There is no persistence beyond module parameters.

## Dependencies And Integration
Depends on platform device alias `platform:pcspkr`, ALSA core/PCM, hrtimer setup, input beeper initialization, mixer creation, and PC speaker PIT helpers.

## Risks And Test Signals
The design is single-device only and rejects nonzero device numbers. PCM availability depends on hrtimer resolution and can silently degrade to beep-only mode with warnings. Tests should cover module enable/nopcm combinations, platform probe, debug-pagealloc warning, suspend/shutdown stop behavior, and card registration with and without PCM.
