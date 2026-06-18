# sources/distributed-fs/ceph-client/include/sound/mixer_oss.h

Source read summary: 66 lines, ALSA OSS mixer emulation interface.

Purpose: declares the structures and registration helpers that map ALSA controls onto legacy OSS mixer device semantics.

Important APIs, types, and functions: `struct snd_mixer_oss_file` represents an open OSS mixer file, `struct snd_mixer_oss_slot` describes per-OSS-channel mapping/control state, and `struct snd_mixer_oss` stores card, device, slots, mask/stereo/record masks, and private state. APIs include OSS mixer register/disconnect functions, ioctl handling, and helpers for notifying control changes.

Control flow: when OSS emulation is enabled, ALSA card registration creates an OSS mixer facade; OSS ioctls are translated to ALSA control reads/writes through slots.

State and persistence behavior: state is per-card OSS mapping/cache state and open-file state. Mixer values persist in ALSA controls/hardware, not in this header.

Dependencies and integration points: depends on ALSA core/control and OSS emulation configs. It integrates `/dev/mixer` compatibility with native ALSA controls.

Risks and edge cases: channel masks and record-source semantics differ from ALSA controls; stereo/mono mapping can be lossy; disconnect must handle open OSS files.

Test signals: OSS mixer ioctls, volume and capture source mapping, stereo/mono controls, card disconnect with open files, and builds without OSS emulation.
