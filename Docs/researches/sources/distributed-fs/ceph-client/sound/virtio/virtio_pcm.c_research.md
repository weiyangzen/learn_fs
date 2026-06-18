# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm.c

## Purpose
Implements VirtIO sound PCM discovery and ALSA PCM device construction. It converts VirtIO stream descriptors into `snd_pcm_hardware`, groups substreams by function node id, builds ALSA PCM devices, and handles asynchronous VirtIO PCM events.

## Important APIs, Types, And Functions
- Module parameters `pcm_buffer_ms`, `pcm_periods_min`, `pcm_periods_max`, `pcm_period_ms_min`, and `pcm_period_ms_max` bound derived ALSA hardware limits.
- `g_v2a_format_map` and `g_v2a_rate_map` translate VirtIO PCM format/rate bits into ALSA format masks and rate ranges.
- `virtsnd_pcm_build_hw()` validates channel/rate/format data and computes `buffer_bytes_max`, `period_bytes_min`, and `period_bytes_max`.
- `virtsnd_pcm_find()` and `virtsnd_pcm_find_or_create()` manage `snd->pcm_list` entries keyed by VirtIO function node id.
- `virtsnd_pcm_validate()` rejects invalid module parameter combinations before the device starts.
- `virtsnd_pcm_parse_cfg()` queries `VIRTIO_SND_R_PCM_INFO`, initializes every `virtio_pcm_substream`, and counts stream directions per PCM node.
- `virtsnd_pcm_build_devs()` creates `snd_pcm` devices, attaches kernel substreams back to VirtIO substream records, sets ops, and installs vmalloc managed buffers.
- `virtsnd_pcm_event()` handles VirtIO PCM events, currently marking xruns under the substream lock.

## Control Flow
Initialization first calls validation, then `virtsnd_pcm_parse_cfg()` reads the VirtIO config stream count, preinitializes substream synchronization fields, fetches all stream info through the control queue, converts each stream to ALSA hardware constraints, and increments playback/capture counts. `virtsnd_pcm_build_devs()` then makes an ALSA PCM per node, allocates per-direction substream pointer arrays, binds ALSA substream numbers to `virtio_pcm_substream` entries, and registers `virtsnd_pcm_ops` for playback/capture.

## State And Persistence
Persistent runtime state lives in devm-managed `snd->substreams`, `snd->pcm_list`, and per-substream fields such as `hw`, `features`, `direction`, `buffer_bytes`, `hw_ptr`, `xfer_enabled`, `xfer_xrun`, and wait/work structures. There is no disk persistence. Device lifetime relies on the parent `virtio_snd` and ALSA card lifetime; module parameters persist only as loaded module settings.

## Dependencies And Integration Points
This file depends on Linux VirtIO config access, ALSA PCM core, `virtio_card.h`, and the VirtIO sound UAPI structures. It integrates with `virtio_pcm_ops.c` through `virtsnd_pcm_ops`, with `virtio_pcm_msg.c` through substream message fields, and with `virtio_ctl_msg` query/send helpers.

## Risks
- Hardware limits are derived using integer math on milliseconds and rates; unusual low rates or formats can expose zero/minimum period edge cases.
- Unsupported VirtIO formats/rates are ignored; a device advertising only unsupported bits fails initialization.
- `VIRTIO_SND_EVT_PCM_PERIOD_ELAPSED` is not implemented for shared-memory elapsed reporting, so message completion remains the main period signal.
- `virtsnd_pcm_build_devs()` assumes ALSA substream numbering matches the populated `vs->substreams` order.

## Test Signals
Useful signals include boot/probe with multiple playback and capture streams under one node, invalid module parameter rejection, ALSA `aplay`/`arecord` with several formats/rates, xruns from the device, and teardown/reprobe under module unload. Kernel logs for "invalid channel range", "no supported PCM sample formats", and "snd_pcm_new failed" are direct failure indicators.
