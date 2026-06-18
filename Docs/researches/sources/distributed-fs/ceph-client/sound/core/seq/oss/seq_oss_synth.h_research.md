# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_synth.h

Purpose: declares the OSS synth management and conversion interface for the OSS sequencer module.

Important APIs: registration callbacks `snd_seq_oss_synth_probe()`/`remove()`, per-open setup/cleanup, reset, patch loading, synth info lookup, sysex/address/ioctl/raw-event conversion, and legacy `synth_info` creation.

Control flow: `seq_oss.c` registers the probe/remove driver, `seq_oss_init.c` calls setup/cleanup/reset, `seq_oss_event.c` uses info/address/sysex/raw conversion, and ioctl paths use make-info/ioctl/load-patch.

State and persistence: no state in the header, but the declarations operate on global synth registrations and per-open `seq_oss_devinfo` synth arrays.

Dependencies and integration: includes central OSS state, OSS legacy structs, and sequencer-device registration.

Risks: exported functions often accept an OSS device index; callers must pass indexes validated against per-open `max_synthdev`, and implementations may map MIDI pseudo-synths differently from real synths.

Test signals: compile all users and run open/reset/ioctl/event conversion tests through the declared APIs.
