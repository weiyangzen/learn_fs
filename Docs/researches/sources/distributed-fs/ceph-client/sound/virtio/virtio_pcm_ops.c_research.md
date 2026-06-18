# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_ops.c

## Purpose
Provides ALSA PCM operations for VirtIO sound playback and capture. It negotiates parameters with the device, allocates I/O messages, starts/stops streams, exposes hardware pointers, and bridges ALSA indirect transfer callbacks to VirtIO period messages.

## Important APIs, Types, And Functions
- `g_a2v_format_map` and `g_a2v_rate_map` translate ALSA selections to VirtIO protocol values.
- `virtsnd_pcm_open()` installs hardware constraints and synchronously releases stale queue state.
- `virtsnd_pcm_dev_set_params()` sends `VIRTIO_SND_R_PCM_SET_PARAMS` with selected buffer/period/channel/format/rate and negotiated feature bits.
- `virtsnd_pcm_hw_params()` rejects non-drained queues, sets device params, frees old messages, and allocates new per-period messages.
- `virtsnd_pcm_prepare()` resets local transfer state or reprograms the device after suspend, initializes indirect PCM state, and sends PREPARE.
- `virtsnd_pcm_trigger()` handles START/STOP/PAUSE/SUSPEND commands and sends VirtIO START/STOP control messages.
- `virtsnd_pcm_sync_stop()` sends RELEASE and waits for `msg_empty` so device-owned messages can be freed safely.
- Playback/capture `pointer` and `ack` callbacks use `snd_pcm_indirect_*` helpers.

## Control Flow
Open loads `runtime->hw`, marks whether old messages are pending, and calls sync stop. `hw_params` sends backend params and prepares messages. `prepare` resets buffer pointer state and sends PREPARE. On START, capture prequeues the whole buffer, enables transfer under locks, then sends START. Playback sends messages from `ack` as userspace writes into periods. STOP/PAUSE/SUSPEND disable transfer and send STOP; later `sync_stop` RELEASEs the stream and waits for queue drain.

## State And Persistence
Mutable per-stream state includes `stopped`, `suspended`, `xfer_enabled`, `xfer_xrun`, `msg_count`, `buffer_bytes`, `hw_ptr`, and `pcm_indirect`. The most important persistence behavior is not disk persistence but device ownership: messages may remain owned by the backend after stop until RELEASE completion drains them.

## Dependencies And Integration Points
Depends on ALSA PCM and indirect PCM helpers, `virtio_pcm_msg.c` for message send/free/pending, and VirtIO control messages. It is exported as `virtsnd_pcm_ops[]` for playback and capture in `virtio_pcm.c`.

## Risks
- START enables `xfer_enabled` before the START control message returns; failure paths only clear it for allocation failure, so backend START errors should be scrutinized.
- `sync_stop` may timeout or be interrupted, leaving messages allocated until a later safe cleanup point.
- Capture prequeues the full buffer at start, so buffer size and period configuration directly affect initial queue pressure.
- Suspend path relies on reprogramming params in `prepare`; coverage must include suspend/resume with pending streams.

## Test Signals
Test ALSA open/close, repeated hw_params without hw_free, rapid stop/start, pause/release, suspend/resume, release timeout, capture start prequeue, playback ack-driven queuing, and xrun/error injection. `msg_count` reaching zero after RELEASE is the key safety signal.
