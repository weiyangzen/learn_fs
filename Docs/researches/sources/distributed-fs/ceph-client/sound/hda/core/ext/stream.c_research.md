# sources/distributed-fs/ceph-client/sound/hda/core/ext/stream.c

## Purpose
`ext/stream.c` implements extended HDA stream handling for decoupled host/link DMA paths, processing-pipe registers, stream assignment/release for PCM and compressed streams, and Apollo Lake-specific setup sequencing.

## Important APIs, Types, and Functions
Exports include `snd_hdac_ext_host_stream_setup()`, `snd_hdac_ext_stream_init_all()`, `snd_hdac_ext_stream_free_all()`, `snd_hdac_ext_stream_decouple_locked()`, `snd_hdac_ext_stream_decouple()`, `snd_hdac_ext_stream_start()`, `snd_hdac_ext_stream_clear()`, `snd_hdac_ext_stream_reset()`, `snd_hdac_ext_stream_setup()`, `snd_hdac_ext_stream_assign()`, `snd_hdac_ext_stream_release()`, and `snd_hdac_ext_cstream_assign()`.

## Control Flow
Stream init allocates `hdac_ext_stream` objects, assigns host setup callbacks, computes processing-pipe host/link register addresses when `ppcap` exists, and calls base stream init. Assignment supports coupled streams via base assignment, host streams by finding unopened streams and decoupling them, and link streams by finding unlocked link streams and decoupling them. Release recouples only when the paired host/link side is no longer in use.

## State and Persistence Behavior
Each ext stream tracks base `hstream`, processing-pipe addresses, decoupled state, host setup callback, link lock flag, and associated PCM/compress substream pointers. State is protected by `bus->reg_lock` for assignment/decoupling/release.

## Dependencies and Integration Points
The code depends on base HDA stream helpers, PCI IDs for Apollo Lake setup selection, processing-pipe capability registers, ALSA PCM/compress stream structures, and extended bus capability parsing.

## Risks
Processing-pipe operations require `bus->ppcap`; assignment returns NULL if unsupported. Decoupling/recoupling must respect simultaneous host and link users. Reset/setup functions poll hardware bits with bounded loops but do not report reset timeout errors. Apollo Lake setup relies on temporary coupling state.

## Test Signals
Test stream initialization/free, coupled/host/link assignment exhaustion, release recoupling rules, compressed stream assignment, start/clear/reset/setup register programming, APL host setup, and lock coverage under concurrent PCM open/close.
