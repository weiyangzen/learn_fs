# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Kconfig

Purpose: Defines build options for Philips SAA713x PCI video capture support and related ALSA audio, remote-control, DVB/ATSC, and go7007 encoder integrations.

Important APIs, types, and functions: `VIDEO_SAA7134` is the main tristate depending on `VIDEO_DEV`, `PCI`, and `I2C`, selecting VB2 DMA scatter-gather, tuner, tveeprom, CRC32, and optional subdevices. `VIDEO_SAA7134_ALSA` enables DMA audio support with ALSA PCM. `VIDEO_SAA7134_RC` enables remote controller support as a bool with dependency constraints for built-in/module combinations. `VIDEO_SAA7134_DVB` enables DVB/ATSC support and autoselects many frontend/tuner/LNB drivers. `VIDEO_SAA7134_GO7007` enables go7007 MPEG encoder support.

Control flow: Build-time only. These symbols control which objects are compiled by the local Makefile and which media subdrivers are available for runtime board variants.

State and persistence: No runtime state. Configuration choices persist in the kernel `.config`.

Dependencies and integration points: Integrates with V4L2, PCI, I2C, remote-control core, ALSA, DVB core, VB2, go7007, frontend/tuner modules, and media autoselect policy. The RC option includes a guard against `RC_CORE=m` with built-in SAA7134.

Risks: The main SAA7134 family supports many boards, so missing autoselect entries can surface as runtime feature loss on specific board variants. Feature symbols are split, so enabling base video does not imply ALSA, DVB, RC, or go7007 support. The RC bool default `y` can surprise minimal builds unless dependencies are adjusted.

Test signals: Kconfig matrix tests should cover base-only, base+ALSA, base+RC, base+DVB, base+go7007, built-in/module dependency combinations, and autoselect coverage for every frontend/tuner referenced by SAA7134 board tables.
