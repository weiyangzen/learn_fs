# sources/distributed-fs/ceph-client/include/sound/minors.h

Source read summary: 97 lines, ALSA device minor numbering contract.

Purpose: defines static and dynamic minor-number layout for ALSA card devices, OSS emulation offsets, and helpers for deriving card/device numbers from minors.

Important APIs, types, and functions: macros include `SNDRV_MINOR_*` offsets for control, sequencer, timer, hwdep, rawmidi, PCM playback/capture, and OSS devices, plus `SNDRV_OS_MINORS`, `SNDRV_MINOR_DEVICES`, `SNDRV_MINOR_CARD()`, and `SNDRV_MINOR_DEVICE()`. Dynamic-minor builds change PCM device counts elsewhere.

Control flow: ALSA core uses these constants when registering character devices and resolving open minors back to card/device/interface instances.

State and persistence behavior: no runtime state is stored; minor allocation state lives in ALSA core. The numbering is ABI-visible and persistent across kernel/user expectations.

Dependencies and integration points: integrates ALSA core, UAPI device nodes, OSS emulation, PCM, rawmidi, hwdep, timer, and sequencer device registration.

Risks and edge cases: changing offsets breaks userspace device nodes; dynamic minors and OSS emulation must not collide; card/device extraction macros must match registration.

Test signals: device node creation for multiple cards, static vs dynamic minor builds, OSS emulation minors, open routing to correct ALSA device, and udev compatibility.
