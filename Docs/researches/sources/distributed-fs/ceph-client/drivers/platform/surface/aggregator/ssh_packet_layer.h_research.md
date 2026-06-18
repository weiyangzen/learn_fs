# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/ssh_packet_layer.h

## Purpose
Defines the in-kernel interface and state container for the SSH packet transport layer. It exposes packet-layer lifecycle, submission, cancellation, RX ingress, and control packet cache APIs to the surrounding Surface Aggregator serial hub code.

## Important APIs, Types, And Functions
`enum ssh_ptl_state_flags` currently defines `SSH_PTL_SF_SHUTDOWN_BIT`. `struct ssh_ptl_ops` contains the upper-layer `data_received()` callback. `struct ssh_ptl` embeds the full packet-layer state: serdev pointer, shutdown state, queue, pending set, TX kthread state, RX kthread/fifo/parser buffer/retransmit suppression state, retransmission timeout work, and callbacks. Public declarations include `ssh_ptl_init()`, `ssh_ptl_destroy()`, TX/RX start/stop functions, `ssh_ptl_shutdown()`, `ssh_ptl_submit()`, `ssh_ptl_cancel()`, `ssh_ptl_rx_rcvbuf()`, `ssh_packet_init()`, and control-packet cache lifecycle. `ssh_ptl_get_device()` and `ssh_ptl_tx_wakeup_transfer()` are inline helpers.

## Control Flow
This header establishes the layering contract. Lower serial code pushes bytes through `ssh_ptl_rx_rcvbuf()` and wakes transfer availability through `ssh_ptl_tx_wakeup_transfer()`. Upper layers submit `struct ssh_packet` instances with initialized ops and data. The packet layer then calls `data_received()` for validated inbound data payloads and packet completion/release callbacks through packet ops defined in the public serial-hub header.

## State And Persistence Behavior
All fields in `struct ssh_ptl` are volatile runtime state. The queue and pending sets are list-based and protected by spinlocks. TX uses completions and a wait queue; RX uses kfifo plus an `sshp_buf` parsing buffer. The retransmission reaper tracks timeout interval and currently scheduled expiration. No disk, firmware, or NVRAM state is stored.

## Dependencies And Integration Points
Includes kernel atomic, kfifo, ktime, list, serdev, spinlock, wait, workqueue, and Surface Aggregator protocol definitions. It depends on `ssh_parser.h` for RX buffer handling. Consumers are expected to supply a live `serdev_device` and `ssh_ptl_ops`; the request layer embeds `struct ssh_ptl` inside `struct ssh_rtl`.

## Risks
Because `struct ssh_ptl` exposes internal synchronization fields, maintainers must preserve lock semantics documented in the `.c` file. `ssh_ptl_tx_wakeup_transfer()` ignores wakeups after shutdown, so callers must tolerate dropped TX-space notifications during teardown. `ssh_ptl_get_device()` may return `NULL` if called before serdev setup or after partial teardown.

## Test Signals
Compile-time coverage should catch declaration drift against `ssh_packet_layer.c`. Runtime checks should exercise initialization/destruction ordering, shutdown wakeup suppression, RX byte injection, packet submission/cancel paths, and embedding via `to_ssh_ptl()`.
