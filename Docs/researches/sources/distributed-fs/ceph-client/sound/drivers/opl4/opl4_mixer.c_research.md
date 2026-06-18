# sources/distributed-fs/ceph-client/sound/drivers/opl4/opl4_mixer.c

## Purpose
Adds ALSA mixer controls for OPL4 FM and wavetable playback volume. The controls manipulate the OPL4 mix-control registers with stereo left/right attenuation values.

## Important APIs, Types, And Functions
`snd_opl4_ctl_info()`, `snd_opl4_ctl_get()`, and `snd_opl4_ctl_put()` implement a two-channel integer control ranging from 0 to 7. `snd_opl4_controls[]` defines `"FM Playback Volume"` and `"Wavetable Playback Volume"`. `snd_opl4_create_mixer()` appends `,OPL4` to the card mixer name and registers both controls.

## Control Flow
On get, the driver reads the register under `reg_lock`, inverts the hardware attenuation values (`7 - value`) into user-facing volume values, and returns left/right values. On put, it converts user values back to hardware attenuation, writes the register, and reports whether the value changed.

## State And Persistence
State is stored in OPL4 mixer registers. ALSA control values are not persisted by the driver; userspace mixers may save/restore them externally.

## Dependencies And Integration
Uses ALSA control APIs and the low-level `snd_opl4_read()`/`snd_opl4_write()` helpers from `opl4_lib.c`.

## Risks And Test Signals
Values are masked to three bits, so out-of-range user values are wrapped rather than rejected. `strcat(card->mixername, ",OPL4")` assumes enough space in the ALSA mixer name buffer. Tests should cover get/put round trips, left/right inversion, invalid high values, and mixer registration during OPL4 probe.
