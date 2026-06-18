# sources/distributed-fs/ceph-client/sound/core/seq/oss/seq_oss_event.h

Purpose: defines the binary OSS sequencer event-record layouts consumed and produced by the OSS emulation layer.

Important APIs and types: defines `SHORT_EVENT_SIZE`, `LONG_EVENT_SIZE`, `struct evrec_short`, `evrec_note`, `evrec_timer`, `evrec_extended`, `evrec_long`, `evrec_voice`, `evrec_sysex`, and `union evrec`. Declares `snd_seq_oss_process_event()`, `snd_seq_oss_process_timer_event()`, and `snd_seq_oss_event_input()`. Macros `ev_is_long()` and `ev_length()` classify record sizes from opcode values.

Control flow: read/write code uses the macros to decide how many bytes to copy; event conversion code casts the union to the format matching the opcode.

State and persistence: no independent state; it defines the byte ABI stored in read queues and copied to/from userspace.

Dependencies and integration: includes `seq_oss_device.h` for device context and is shared by readq, writeq, timer, rw, ioctl, event, MIDI, and synth code.

Risks: layout, packing-by-C ABI, and opcode-size classification must match OSS userspace expectations. Any change would be ABI-visible. Union casts rely on correct opcode validation before interpreting fields.

Test signals: compile-time size checks through ABI tests, userspace read/write compatibility tests for 4-byte and 8-byte records, and round-trip echo/timestamp records.
