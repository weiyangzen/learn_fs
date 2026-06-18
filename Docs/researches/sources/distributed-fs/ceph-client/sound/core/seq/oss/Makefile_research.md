# sources/distributed-fs/ceph-client/sound/core/seq/oss/Makefile

Purpose: builds the OSS sequencer emulation module from its component files.

Important build objects: `snd-seq-oss-y` combines device registration, open/close, timer, ioctl, event conversion, read/write, synth, MIDI, read queue, and write queue objects.

Control flow: `obj-$(CONFIG_SND_SEQUENCER_OSS)` emits `snd-seq-oss.o` only when OSS sequencer emulation is enabled.

State and persistence: no runtime state. The build composition makes the OSS layer a single module that registers both OSS minors and the synth driver.

Dependencies and integration: depends on the parent sequencer module and `SND_SEQ_MIDI_EVENT` selected by Kconfig.

Risks: all OSS subcomponents are linked together, so missing one object leaves unresolved internal APIs. Procfs support is conditional inside `seq_oss.c`, not in this Makefile.

Test signals: module link/load tests for `snd-seq-oss`, with and without procfs and as built-in versus module.
