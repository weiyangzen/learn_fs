# sources/distributed-fs/ceph-client/sound/core/seq/Makefile

Purpose: maps sequencer Kconfig symbols to ALSA sequencer object files and modules.

Important build objects: `snd-seq-y` contains core files `seq.o`, `seq_lock.o`, `seq_clientmgr.o`, `seq_memory.o`, `seq_queue.o`, `seq_fifo.o`, `seq_prioq.o`, `seq_timer.o`, `seq_system.o`, and `seq_ports.o`. Optional pieces add `seq_info.o` for procfs and `seq_ump_convert.o` for UMP. Separate modules are built for MIDI, MIDI emulation, MIDI event conversion, dummy, virmidi, and UMP client support.

Control flow: `obj-$(CONFIG_SND_SEQUENCER)` builds the core `snd-seq.o`; `obj-$(CONFIG_SND_SEQUENCER_OSS)` descends into `oss/`; other `obj-*` lines produce optional companion modules.

State and persistence: no runtime state; it controls binary composition and symbol availability.

Dependencies and integration: mirrors `Kconfig` and establishes which files provide exported APIs consumed by rawmidi bridges, OSS emulation, dummy client, and UMP conversion.

Risks: object grouping matters because `seq_clientmgr.c` includes `seq_compat.c` directly, and `seq_info.o` is only present with procfs. Missing `seq_midi_event.o` breaks MIDI byte/event conversion users.

Test signals: validate all configured modules link, particularly `CONFIG_SND_PROC_FS=n`, `CONFIG_SND_SEQ_UMP=y`, and OSS module builds.
