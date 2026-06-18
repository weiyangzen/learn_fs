<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/hdspm.h -->
# sources/distributed-fs/ceph-client/include/uapi/sound/hdspm.h

Purpose: defines the user/kernel hardware-dependent ALSA control ABI for RME HDSPM cards, including MADI-family card discovery, metering, clock/sync state, LTC status, and matrix mixer access.

Important APIs and types: the public surface is the `SNDRV_HDSPM_IOCTL_*` ioctl set plus ABI structs `hdspm_peak_rms`, `hdspm_config`, `hdspm_ltc`, `hdspm_status`, `hdspm_version`, `hdspm_channelfader`, `hdspm_mixer`, and `hdspm_mixer_ioctl`. Enums encode card type, sample speed, sync states, MADI input/channel/frame formats, sync sources, and LTC format/frame/input status. `HDSPM_MAX_CHANNELS` and `HDSPM_MIXER_CHANNELS` fix the ABI at 64 channels.

Control flow: userspace opens the ALSA hwdep device and issues read-only ioctls to fetch current metering, configuration, timecode, status, version/add-on data, or mixer coefficients. `SNDRV_HDSPM_IOCTL_GET_MIXER` uses an indirect userspace pointer because the mixer matrix is too large for normal ioctl size encoding.

State and persistence: this header stores no state; it describes snapshots of live device registers and driver-maintained mixer state. Mixer, clocking, sync, and meter values are runtime device state, while firmware revision, card type, serial, and TCO add-on flags are hardware identity.

Dependencies and integration points: depends on Linux integer types and ioctl macros from the ALSA UAPI include chain. It integrates with the HDSPM ALSA driver, hwdep ioctl handling, pro-audio control tools, and userspace mixers that understand the 64x128-to-64 matrix format.

Risks and test signals: ABI risks are struct padding differences from `int`/enum fields, unchecked userspace mixer pointers, stale 64-channel assumptions, and confusion between single/double/quad speed channel availability. Test by compiling UAPI consumers on 32/64-bit, exercising every ioctl against MADI/AIO/AES32/RayDAT variants, validating meter array bounds, and reading mixer state under active streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/sound/hdspm.h -->
