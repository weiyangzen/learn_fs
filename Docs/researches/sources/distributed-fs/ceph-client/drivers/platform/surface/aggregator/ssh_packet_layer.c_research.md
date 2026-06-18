# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.c

## Purpose
Implements the SSH packet transport layer for the Surface Aggregator Module serial hub. It turns raw SSH frames into reliable packet delivery over `serdev`, including ACK/NAK handling, sequence tracking, retransmission, RX parsing, TX serialization, cancellation, and shutdown. It is the lower transport used by the request layer and controller stack.

## Important APIs, Types, And Functions
The exported packet lifetime APIs are `ssh_packet_get()`, `ssh_packet_put()`, and `ssh_packet_init()`. Public transport entry points are implemented here for declarations in `ssh_packet_layer.h`: `ssh_ptl_init()`, `ssh_ptl_destroy()`, `ssh_ptl_tx_start()`, `ssh_ptl_tx_stop()`, `ssh_ptl_rx_start()`, `ssh_ptl_rx_stop()`, `ssh_ptl_submit()`, `ssh_ptl_cancel()`, `ssh_ptl_rx_rcvbuf()`, and `ssh_ptl_shutdown()`. Internal helpers manage priority insertion (`__ssh_ptl_queue_find_entrypoint()`), queue/pending membership, TX completion, ACK pop, NAK resubmission, timeout reaping, RX frame evaluation, and control-packet allocation. `ssh_ctrl_packet_cache_init()` and `ssh_ctrl_packet_cache_destroy()` set up a kmem cache used for ACK/NAK packets.

## Control Flow
Transmit flow starts with `ssh_ptl_submit()`, which validates flush/data invariants, binds the packet to the PTL, inserts it into the priority queue, and wakes the TX kthread. `ssh_ptl_tx_threadfn()` pops sendable packets, adds sequenced packets to the pending set, writes data via `serdev_device_write_buf()`, and completes unsequenced packets immediately. Sequenced packets remain pending until `ssh_ptl_acknowledge()` receives a matching ACK from RX. RX data enters via `ssh_ptl_rx_rcvbuf()` into a kfifo, is copied into `rx.buf`, then `ssh_ptl_rx_eval()` aligns to SYN, validates frames via `sshp_parse_frame()`, dispatches ACK, NAK, sequenced data, and non-sequenced data, sends ACKs for sequenced inbound data, and forwards payloads to `ptl->ops.data_received()`.

## State And Persistence Behavior
The layer is runtime-stateful only. It persists no data outside memory. Packet state lives in bit flags on `struct ssh_packet`, while ownership is controlled by krefs held by the queue, pending set, TX thread, RX/ACK path, and timeout logic. `queue.lock` protects queue state and priority, `pending.lock` protects pending membership and timestamps, and the documented ordering is pending lock before queue lock. `rtx_timeout.reaper` periodically resubmits timed-out packets up to `SSH_PTL_MAX_PACKET_TRIES` and then completes with `-ETIMEDOUT`. A ring of eight recently received sequence IDs suppresses duplicate sequenced frames caused by EC retransmit after ACK loss.

## Dependencies And Integration Points
Depends on Linux kthreads, kfifo, spinlocks, krefs, delayed work, wait queues, `serdev`, `ssh_parser.c`, `ssh_msgb.h`, and protocol definitions in `linux/surface_aggregator/serial_hub.h`. Tracepoints in `trace.h` observe submissions, completions, timeouts, allocation/free, and error-injection paths. When `CONFIG_SURFACE_AGGREGATOR_ERROR_INJECTION` is enabled, injectable hooks simulate dropped ACK/NAK/data packets, write failures, and corrupt TX/RX data.

## Risks
The code is concurrency-sensitive: missed barriers or wrong lock order can cause lost cancellation, double completion, or leaked references. `sshp_find_syn()` is called with spans expected to contain at least one byte; callers currently satisfy that through RX-buffer loop structure, but this invariant is worth preserving. In `ssh_ptl_shutdown()`, the pending-list loop moves `pending_node` entries to `complete_q` while `complete_p` remains unused; the comments describe two completion lists, so this deserves scrutiny for list-node misuse or missed pending reference drops. RX FIFO overflow returns a short count to serdev callers; upstream caller behavior should be checked for backpressure handling.

## Test Signals
Useful tests include injected dropped ACK/NAK/data frames, injected CRC/SYN corruption, forced `serdev_device_write_buf()` errors, flush during active pending packets, cancellation before submit/during TX/while pending, shutdown with queued and pending packets, duplicate inbound sequence handling, and tracepoint validation that each packet gets one completion and one release.
