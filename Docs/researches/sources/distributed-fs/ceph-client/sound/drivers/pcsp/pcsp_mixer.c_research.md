# sources/distributed-fs/ceph-client/sound/drivers/pcsp/pcsp_mixer.c

Purpose: implements the ALSA mixer controls for the PC speaker driver. It exposes playback enable, treble/base frequency, and legacy beep switch controls over the standard `snd_kcontrol` interface.

Important APIs, types, and functions: the file depends on `struct snd_pcsp` from `pcsp.h`, ALSA control types from `<sound/control.h>`, and card registration state from `<sound/core.h>`. The three control families are `pcsp_enable_*`, `pcsp_treble_*`, and `pcsp_pcspkr_*`; each provides `.info`, `.get`, and `.put` callbacks. `PCSP_MIXER_CONTROL()` builds `struct snd_kcontrol_new` entries, `snd_pcsp_ctls_add()` registers arrays of controls with `snd_ctl_add()`, and exported local entry `snd_pcsp_new_mixer()` attaches the mixer controls and sets `card->mixername`.

Control flow: probe code elsewhere calls `snd_pcsp_new_mixer(chip, nopcm)`. When PCM is available, the function first registers `"Master Playback Switch"` and `"BaseFRQ Playback Volume"`; it always registers `"Beep Playback Switch"`. Each put callback compares user input with cached fields and returns the ALSA changed flag.

State and persistence: state is entirely in the live `snd_pcsp` instance: `enable`, `treble`, `max_treble`, and `pcspkr`. There is no persistent storage. Treble enum labels are calculated from `PCSP_CALC_RATE()` and the active enum item, so control presentation depends on chip limits.

Dependencies and integration: integrates with the PC speaker PCM and beep logic through shared chip fields. It relies on ALSA control registration and normal card lifetime management; control callbacks receive the chip via `snd_kcontrol_chip()`.

Risks: `.put` callbacks trust value ranges after ALSA info exposure; unusual userspace values should still be considered because the treble setter does not clamp against `max_treble`. There is no explicit locking around chip fields, so concurrency safety depends on ALSA control serialization and benign integer state. Test signals include control enumeration bounds, changed/no-change return values, no-PCM mode only registering beep control, and visible mixer name `"PC-Speaker"`.
