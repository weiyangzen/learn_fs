# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_midi.h

Purpose: declares the OSS MIDI-device management interface shared by open/reset, event conversion, ioctl, and proc code.

Important APIs: declarations cover discovery (`lookup_ports`, `check_new_port`, `check_exit_port`, `clear_all`), per-open setup/cleanup, open/close/reset, byte output, ALSA input callback, mode query, legacy `midi_info` creation, and address lookup.

Control flow: `seq_oss_init.c` calls setup/open/cleanup and announcement handlers; `seq_oss_event.c` calls `putc` for `SEQ_MIDIPUTC`; `seq_oss_ioctl.c` queries info/open tests; synth MIDI emulation uses address and open helpers.

State and persistence: no state itself; describes functions manipulating `seq_oss_midi.c` globals and `seq_oss_devinfo` snapshots.

Dependencies and integration: includes the central OSS device header and OSS legacy definitions for `struct midi_info`.

Risks: callers must pair open/cleanup and respect `dp->max_mididev` bounds enforced inside the implementation. Input callback may run in atomic contexts, so exported functions used there must not sleep except where documented.

Test signals: compile users of all prototypes and run OSS MIDI discovery/open/input/output tests through the public interface.
