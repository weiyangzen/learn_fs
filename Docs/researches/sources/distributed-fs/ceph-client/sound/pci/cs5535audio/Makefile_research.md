# sources/distributed-fs/ceph-client/sound/pci/cs5535audio/Makefile

Purpose: Kbuild fragment for the CS5535/CS5536 ALSA driver.

Important APIs and types: builds `snd-cs5535audio.o` from core `cs5535audio.o` and `cs5535audio_pcm.o`, adds `cs5535audio_pm.o` under `CONFIG_PM_SLEEP`, adds `cs5535audio_olpc.o` under `CONFIG_OLPC`, and exposes the module through `obj-$(CONFIG_SND_CS5535AUDIO)`.

Control flow and integration: this file controls which optional code paths are present at compile time. The C header provides stubs for OLPC helpers when `CONFIG_OLPC` is off, and the PCI driver's `.driver.pm` field is compiled only when PM sleep support is enabled.

State, risks, and test signals: no runtime state. Risks are configuration skew: PM or OLPC code can silently disappear from builds, so test matrix should include default, `CONFIG_PM_SLEEP`, `CONFIG_OLPC`, and both together, verifying unresolved symbols do not occur.
