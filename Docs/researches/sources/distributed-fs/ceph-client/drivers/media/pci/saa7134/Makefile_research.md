# sources/distributed-fs/ceph-client/drivers/media/pci/saa7134/Makefile

Purpose: Kbuild metadata for the Philips SAA7134 driver family.

Important APIs, types, and functions: `saa7134-y` composes the base driver from card, core, I2C, TS, TV audio, VBI, and video objects. `saa7134-$(CONFIG_VIDEO_SAA7134_RC)` conditionally adds remote input support. Object lines build `saa7134.o` and `saa7134-empress.o` for the base option, plus optional `saa7134-go7007.o`, `saa7134-alsa.o`, and `saa7134-dvb.o`. Include flags add tuner, DVB frontend, and go7007 USB encoder headers.

Control flow: Build-time only. Kbuild links the base composite object and optional feature modules according to the Kconfig symbols.

State and persistence: No runtime state.

Dependencies and integration points: Mirrors the SAA7134 feature split from Kconfig. The base module includes the core analog/video/transport-stream support, while ALSA, DVB, and go7007 integrations are separate modules/objects.

Risks: `obj-$(CONFIG_VIDEO_SAA7134) += saa7134.o saa7134-empress.o` builds empress support whenever the base option is enabled, so dependencies must remain satisfied by the base Kconfig. Conditional RC object composition must match the bool dependency constraints. New board support that needs additional headers or feature objects must update both Kconfig and Makefile.

Test signals: Build all option combinations, verify expected modules are emitted, confirm `saa7134-input.o` appears only when RC is enabled, and run link checks for optional DVB/ALSA/go7007 objects.
