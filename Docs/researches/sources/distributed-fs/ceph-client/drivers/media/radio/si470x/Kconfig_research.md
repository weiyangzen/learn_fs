# sources/distributed-fs/ceph-client/drivers/media/radio/si470x/Kconfig

Purpose: defines Kconfig options for the Silicon Labs Si470x FM radio receiver support split into common, USB, and I2C modules.

Important APIs and symbols: `RADIO_SI470X` is the common tristate depending on `VIDEO_DEV`. `USB_SI470X` depends on `USB && RADIO_SI470X` and builds USB support. `I2C_SI470X` depends on `I2C && RADIO_SI470X` and builds I2C support.

Control flow: selecting the common symbol enables shared Si470x V4L2 code. Selecting a bus symbol causes the Makefile to build the corresponding bus transport module. Help text lists known USB products and recommends `SND_USB_AUDIO` when USB devices are used for audio rather than only RDS.

State and persistence: no runtime state. These symbols persist in kernel build configuration and determine which modules are available.

Dependencies and integration points: integrates with the media radio Kconfig tree, V4L2 core, USB, I2C, and ALSA USB audio recommendations in documentation. The module names in help text match the Makefile objects.

Risks: the common module alone is not useful without a bus-specific frontend. USB help text can become stale as IDs are added. There is no explicit select for sound support because audio is separate and optional.

Test signals: `menuconfig` visibility, allmodconfig and randconfig coverage, module name/help consistency with the Makefile, and configurations with common-only, USB, I2C, and both bus drivers.
