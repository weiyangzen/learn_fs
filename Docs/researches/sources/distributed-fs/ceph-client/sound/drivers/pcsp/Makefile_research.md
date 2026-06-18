# sources/distributed-fs/ceph-client/sound/drivers/pcsp/Makefile

## Purpose
Defines the PC speaker ALSA module composition. It links platform/card setup, PCM playback engine, mixer controls, and input beeper support into `snd-pcsp.o`.

## Important APIs, Types, And Functions
`snd-pcsp-y := pcsp.o pcsp_lib.o pcsp_mixer.o pcsp_input.o` and `obj-$(CONFIG_SND_PCSP) += snd-pcsp.o` are the complete build declarations.

## Control Flow
Kbuild compiles the four object files when `CONFIG_SND_PCSP` is enabled and links them into one module.

## State And Persistence
No runtime state exists in this file.

## Dependencies And Integration
The object list references `pcsp_mixer.c`, which is outside the requested source list but is required for `snd_pcsp_new_mixer()` used by `pcsp.c`.

## Risks And Test Signals
Omitting any object breaks link-time symbols for PCM, mixer, or input support. Build tests with `CONFIG_SND_PCSP=m/y` are the main signal.
