# sources/distributed-fs/ceph-client/include/uapi/sound/asound_fm.h

## Purpose
`asound_fm.h` defines the ALSA direct FM synthesizer UAPI for OPL2/OPL3 hardware. It exposes mode selection, voice/operator programming, note control, global FM parameters, SBI patch records, and hwdep ioctl commands.

## Important APIs, Types, and Constants
Mode constants are `SNDRV_DM_FM_MODE_OPL2` and `SNDRV_DM_FM_MODE_OPL3`. Core structures are `snd_dm_fm_info`, `snd_dm_fm_voice`, `snd_dm_fm_note`, and `snd_dm_fm_params`, representing synthesizer mode, operator/voice envelope and modulation settings, note frequency/key state, and global depth/rhythm/percussion settings.

Ioctls include `SNDRV_DM_FM_IOCTL_INFO`, `RESET`, `PLAY_NOTE`, `SET_VOICE`, `SET_PARAMS`, `SET_MODE`, `SET_CONNECTION`, and `CLEAR_PATCHES`. OSS-compatible command numbers are also defined. Patch records use `FM_KEY_SBI`, `FM_KEY_2OP`, `FM_KEY_4OP`, and `struct sbi_patch`.

## Control Flow and State
Userspace opens the relevant hwdep device, queries info, optionally resets the chip, sets OPL mode/connection, programs operator voices and global parameters, then plays notes by sending octave/frequency/key-on state. Patch writes use fixed-size SBI records.

## State and Persistence Behavior
The hardware/driver retains FM register state for mode, operator parameters, rhythm flags, patches, and active notes until changed, reset, or device close/driver reset. The header itself stores no state.

## Dependencies and Integration Points
It relies on ioctl macros from surrounding ALSA/UAPI include context and integrates with ALSA hwdep FM drivers, OSS compatibility paths, and userspace FM patch players/editors.

## Risks and Test Signals
Risks include invalid bit-range values for OPL register fields, OPL2/OPL3 voice count mismatch, and ambiguous OSS compatibility command use. Tests should verify ioctl number stability, mode switching, register writes for voice/note/global parameters, and patch parsing with fixed SBI/2OP/4OP keys.
