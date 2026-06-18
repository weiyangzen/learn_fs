# sources/distributed-fs/ceph-client/sound/pci/mixart/mixart_core.c

## Purpose
This file implements the low-level miXart mailbox protocol and interrupt handling. It sends synchronous, notification-waiting, and nonblocking messages to embedded firmware; retrieves responses from firmware message-frame FIFOs; handles outbound doorbell interrupts; processes timer notifications into ALSA period events; enables/disables mailbox interrupts; and resets the board.

## Important APIs, types, and functions
`retrieve_msg_frame` pops posted outbound message-frame addresses from firmware memory. `get_msg` copies a response descriptor and payload out of card memory, performs big-endian conversion on little-endian hosts, and returns the frame to the outbound-free FIFO. `send_msg` obtains an inbound-free frame, writes the message descriptor/data, optionally marks `mgr->pending_event`, and posts the request to firmware.

Public send APIs are `snd_mixart_send_msg`, which blocks for a direct answer; `snd_mixart_send_msg_wait_notif`, which blocks for a specific notification event; and `snd_mixart_send_msg_nonblock`, which posts a request and lets the IRQ thread process the answer. `snd_mixart_interrupt` is the hard IRQ handler that masks interrupts and wakes the threaded handler. `snd_mixart_threaded_irq` drains message frames, dispatches command/notify/answer types, updates stream positions on `MSG_SERVICES_TIMER_NOTIFY`, reports firmware traces, wakes synchronous waiters, and processes queued nonblocking answers. `snd_mixart_init_mailbox`, `snd_mixart_exit_mailbox`, and `snd_mixart_reset_board` manage mailbox registers and reset.

## Control flow
Synchronous sends acquire `msg_lock`, post a frame with a pending answer or notification marker, sleep on `msg_sleep` with a 400 ms timeout, and then retrieve the answer under `msg_lock`. Nonblocking sends post without a pending marker and increment `msg_processed`; when the answer arrives, the IRQ thread queues or immediately processes it through `snd_mixart_process_msg`, then decrements the counter.

The hard IRQ verifies the outbound-doorbell bit, masks mailbox interrupts, clears the doorbell/status registers, and returns `IRQ_WAKE_THREAD`. The threaded handler serializes with `mgr->lock`, repeatedly retrieves message frames, handles firmware commands such as timer notifications and trace reports, wakes pending synchronous waiters for matching answers/notifications, or processes nonblocking answers. At the end it unmasks outbound doorbell interrupts.

Timer notification handling decodes each `buffer_id` into logical card, PCM, capture flag, and substream. For running streams it compares firmware sample count with `abs_period_elapsed`, advances ring-buffer period counters, updates the fragment offset, temporarily drops `mgr->lock`, and calls `snd_pcm_period_elapsed`.

## State and persistence behavior
Mailbox state lives in firmware FIFO pointers in BAR0 memory plus host fields `pending_event`, `msg_sleep`, `msg_fifo`, `msg_fifo_readptr/writeptr`, and `msg_processed`. `mixart_msg_data` is a static shared IRQ scratch buffer protected by `mgr->lock`. Stream pointer state is persisted in each `mixart_stream` until close or trigger reset. No disk persistence exists.

## Dependencies and integration points
This file depends on BAR access macros and register offsets from `mixart_hwdep.h`, message IDs and payload definitions from `mixart_core.h`, driver state from `mixart.h`, Linux threaded IRQ APIs, waitqueues, atomics, mutexes, and ALSA PCM period notification. It is central to all other miXart files because firmware setup, PCM control, clocking, and mixer changes all use its send APIs.

## Risks and edge cases
Message sizes must be 32-bit aligned and within expected response buffers. FIFO pointer validation prevents some corruption, but a bad firmware pointer can still cause protocol failure. The static IRQ scratch buffer means message processing must remain serialized. `snd_mixart_send_msg_nonblock` increments `msg_processed` even when `send_msg` returns an error, which makes callers rely on later drain behavior. Timer notification validation checks card/PCM/substream bounds; malformed capture substream IDs share playback limits and should be reviewed carefully if stream counts change. Missing wakeups or timeout paths can leave firmware and host state out of sync.

## Test signals
Test signals include successful synchronous firmware commands during setup, no 400 ms response timeouts under normal operation, nonblocking start/stop answers decrementing `msg_processed`, period elapsed callbacks driven by timer notifications, trace messages appearing only at debug level, shared IRQ returning `IRQ_NONE` for unrelated interrupts, and clean masking/unmasking around the threaded handler. Fault injection around malformed sizes, empty inbound-free FIFO, and missing notification events is especially useful.
