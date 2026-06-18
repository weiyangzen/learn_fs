# sources/distributed-fs/ceph-client/drivers/accessibility/speakup/speakup_soft.c

## Purpose
Software synthesizer backend exposing `/dev/softsynth` and `/dev/softsynthu` so user-space speech daemons can read Speakup output and report spoken indexes.

## Important APIs, Types, And Functions
`synth_soft` has no `io_ops`; it registers misc devices through `softsynth_probe()` and deregisters in `softsynth_release()`. File operations include open/close, Latin-1 and Unicode reads, write for index feedback, and poll. `get_initstring()`, `get_index()`, `softsynth_is_alive()`, and `softsynth_adjust()` complete the synth contract.

## Control Flow
Readers wait on `speakup_event` until this synth is current and data or flushing exists. Reads deliver init commands, clear byte, and buffered chars; Unicode path emits UTF-8, while non-Unicode skips non-Latin-1. Writes parse an index number for read-all.

## State And Persistence Behavior
Maintains `misc_registered`, `init_pos`, `synth_soft.alive`, and `last_index`. Device nodes exist only while registered.

## Dependencies, Integration Points, Risks, And Test Signals
Depends on miscdevice, poll/wait queues, user-copy APIs, synth buffers, and read-all indexing. Risks include blocking semantics, one-reader liveness, user-copy failures, and dropped non-Latin-1 on `/dev/softsynth`. Test misc registration, exclusive open, blocking/nonblocking reads, poll, flush byte, UTF-8, index writes, close behavior, and punctuation adjustment.
