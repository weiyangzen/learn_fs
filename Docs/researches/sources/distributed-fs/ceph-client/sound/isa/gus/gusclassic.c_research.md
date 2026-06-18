<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusclassic.c -->
# sources/distributed-fs/ceph-client/sound/isa/gus/gusclassic.c

Purpose: ALSA ISA driver for Gravis UltraSound Classic and ACE-style plain GF1 cards.

Important APIs/types/functions: module parameters cover card identity, port, IRQ, two DMAs, joystick DAC, active voices, and PCM channels. Main functions are `snd_gusclassic_create()`, `snd_gusclassic_detect()`, `snd_gusclassic_probe()`, and PM wrappers around `snd_gus_suspend/resume()`.

Control flow: match checks `enable[n]`. Probe allocates an ALSA card, ensures at least two PCM channels, auto-finds IRQ/DMAs/port when requested, calls `snd_gus_create()`, resets/release-tests GF1, initializes common GUS state, rejects MAX/Extreme detections, creates GF1 mixer and PCM, creates rawmidi unless ACE, appends resource info to `longname`, registers the card, and stores drvdata.

State and persistence: runtime state is mostly common `struct snd_gus_card`; this file sets `joystick_dac` and module parameter arrays. Hardware and ALSA objects are volatile across module load/unload and PM.

Dependencies and integration: uses shared `snd-gus-lib`, legacy resource auto-probe helpers, ISA driver framework, and ALSA card registration.

Risks: broad port auto-probing can touch legacy hardware ranges. Detection only checks GF1 reset bits, while later common version detection distinguishes Classic/MAX/ACE/Extreme. Test signals are module load on real/emulated GF1, auto-resource fallback, rejection of MAX/Extreme, PCM and rawmidi devices, ACE rawmidi omission, and PM suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/isa/gus/gusclassic.c -->
