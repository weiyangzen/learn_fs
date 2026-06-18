# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/Kconfig

## Purpose
This Kconfig file declares the ivtv PCI media driver family: MPEG encoder/decoder support, optional ALSA PCM capture, and optional framebuffer support for Conexant cx23415/cx23416 devices.

## Important APIs, Types, And Data
`VIDEO_IVTV` is the main tristate driver for cx23415/cx23416 PCI PVR cards. It depends on `VIDEO_DEV`, `PCI`, `I2C`, and `RC_CORE`, selects several tuner/video/audio decoder/encoder helper drivers, and builds the `ivtv` module. `VIDEO_IVTV_ALSA` depends on `VIDEO_IVTV` and `SND`, selects `SND_PCM`, and builds `ivtv-alsa`. `VIDEO_FB_IVTV` depends on `VIDEO_IVTV` and `FB`, selects framebuffer I/O memory helpers, and builds `ivtvfb`. `VIDEO_FB_IVTV_FORCE_PAT` optionally forces framebuffer init under x86 PAT.

## Control Flow
The Kconfig choices determine which ivtv companion modules are available. The ALSA option provides a PCM capture interface in addition to the V4L2 PCM stream.

## State And Persistence
No runtime state is represented here.

## Dependencies And Integration Points
The file integrates ivtv with V4L2, PCI, I2C, RC core, ALSA PCM, framebuffer support, tuner drivers, EEPROM support, and multiple analog video/audio subdevice drivers.

## Risks And Test Signals
The broad `select` list can force-build many helper drivers; configuration tests should cover modular and built-in combinations. ALSA must not be selectable without main ivtv and sound core. Framebuffer PAT behavior should be tested only on relevant x86 systems.
