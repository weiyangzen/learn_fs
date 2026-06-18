# sources/distributed-fs/ceph-client/sound/virtio/virtio_pcm_msg.c

## Purpose
Implements VirtIO PCM period I/O message allocation, scatter-gather construction, queue submission, completion handling, and queue notify callbacks. It turns vmalloc-backed ALSA PCM buffers into VirtIO messages.

## Important APIs, Types, And Functions
- `struct virtio_pcm_msg` wraps a `virtio_snd_pcm_xfer` request, a `virtio_snd_pcm_status` response, payload length, and flexible SG array.
- `virtsnd_pcm_sg_num()` and `virtsnd_pcm_sg_from()` compute and populate physically contiguous SG segments for vmalloc memory.
- `virtsnd_pcm_msg_alloc()` creates one message per ALSA period, with xfer/status/data SG entries.
- `virtsnd_pcm_msg_send()` accumulates updated bytes by period and enqueues complete-period messages to the TX or RX virtqueue.
- `virtsnd_pcm_msg_complete()` advances `hw_ptr`, updates runtime delay from device latency, schedules period work, and wakes stop waiters when drained.
- `virtsnd_pcm_tx_notify_cb()` and `virtsnd_pcm_rx_notify_cb()` dispatch queue completions.
- `virtsnd_pcm_ctl_msg_alloc()` builds PCM control messages with the stream id set.

## Control Flow
`hw_params` allocates messages per period. Playback/capture ack paths call `virtsnd_pcm_msg_send()` with changed ring-buffer ranges while queue and substream locks are held. When enough bytes fill a period, the message is submitted with request/data/status SG ordering appropriate for playback or capture. Virtqueue interrupts run `virtsnd_pcm_notify_cb()`, drain completed buffers with callbacks disabled/enabled safely, and call `virtsnd_pcm_msg_complete()`.

## State And Persistence
Each message tracks `length`, which is reset on completion. `vss->msg_count` counts in-flight messages; `vss->hw_ptr` is advanced modulo `buffer_bytes`; `runtime->delay` stores backend latency in frames. `msg_empty` is signaled when transfer is disabled and all messages are complete. State is transient and tied to ALSA hw_params/hw_free lifetime.

## Dependencies And Integration Points
Uses ALSA `pcm_params`, Linux scatterlist/vmalloc/page helpers, VirtIO virtqueues, and `virtio_ctl_msg` helpers. It expects lock ordering from `virtio_pcm_ops.c`: queue lock plus substream lock for submissions, queue lock in notify path, and substream lock for mutable transfer state.

## Risks
- `virtsnd_pcm_sg_num()` assumes `vmalloc_to_page()` succeeds for the DMA area.
- Message freeing is unsafe unless the queue is drained; this is handled by ops but is a central lifetime risk.
- `offset + bytes - 1` assumes nonzero `bytes`.
- Capture completion tolerates short/invalid status by advancing by message length; this avoids stalls but can hide backend bugs.
- Queue notification is skipped for devices using message polling; tests need both feature states.

## Test Signals
Use playback and capture with vmalloc buffers spanning multiple pages, periods smaller/larger than page fragments, stop with pending messages, timeout during release, polling-feature devices, and backend-provided `latency_bytes`. Look for period callbacks, pointer movement, and absence of use-after-free on rapid open/hw_params/hw_free cycles.
