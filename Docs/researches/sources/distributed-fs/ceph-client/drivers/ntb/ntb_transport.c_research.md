# sources/distributed-fs/ceph-client/drivers/ntb/ntb_transport.c

## Purpose
Implements the software queue-pair transport layer over NTB. It registers an `ntb_transport` bus for higher-level clients, negotiates MW and queue parameters through scratchpads, creates queue pairs, copies TX payloads into peer-visible MWs by CPU or DMA, receives payloads from local MW buffers, and signals peers with doorbells or optional NTB MSI.

## Important APIs, Types, And Functions
- `struct ntb_transport_ctx` is per-NTB-device state: MW vector, QP vector, queue bitmap, MSI settings, link work, client devices, and debugfs node.
- `struct ntb_transport_qp` is a queue pair with TX/RX rings, free/pending/post lists, DMA channels, MSI descriptors, tasklet, delayed link work, callbacks, stats, and optional TX-copy kthread.
- `struct ntb_transport_mw` tracks peer-visible outbound mapping plus local coherent inbound buffer and translation.
- `ntb_transport_register_client_dev()` / `ntb_transport_unregister_client_dev()` create/remove transport client devices across all active NTB transports.
- `ntb_transport_register_client()` registers a transport client driver on the custom bus.
- `ntb_transport_create_queue()` allocates a free QP, installs callbacks, optional DMA channels, RX/TX entries, unmasks DB, and returns the QP.
- `ntb_transport_tx_enqueue()` and `ntb_transport_rx_enqueue()` are the core data-plane APIs for clients.
- `ntb_transport_link_up()` / `ntb_transport_link_down()` mark client readiness and coordinate QP link bits.

## Control Flow
Probe requires inbound MW translation support, optionally reserves the last MW for MSI, checks scratchpad capacity, maps peer MW BARs, derives QP count from doorbell bits/MW count/client limit, initializes QPs, registers the NTB context, joins the transport bus list, enables the NTB link, and triggers a link event.

The device-level link work writes local MW sizes, QP count, MW count, and protocol version to peer scratchpads, reads the peer's matching values, programs local inbound MW translations sized from the peer's advertised MWs, partitions each MW among QPs, and schedules QP link work for ready clients. QP link work sets the local QP ready bit in the peer scratchpad and waits until the peer also advertises the bit, then marks the QP active and schedules receive processing.

TX enqueue removes a free TX entry, stores callback/data/length, checks frame size and ring space, writes length and version into the peer-visible header, copies payload by DMA if configured and aligned or by `memcpy_toio()`, marks `DESC_DONE_FLAG`, orders/flushes the posted write, rings the peer by MSI or doorbell, calls the TX completion callback, and returns the entry to the TX free list.

RX processing runs in a tasklet after doorbell/MSI. It checks the local RX header's done/link-down flags and version, moves a pending client buffer to the post queue, copies payload by DMA or CPU, marks the entry done, clears the header, updates remote RX index (`qp->rx_info->entry`) for peer flow control, invokes the RX callback, and continues until the ring is empty or a fairness limit is hit.

Teardown cleans link state, sends link-down messages when clients request link down, masks DB, kills tasklets, stops optional TX-copy threads, waits/terminates DMA, frees all queue entries, clears MW translations, unmaps peer BARs, unregisters transport bus devices, and frees state.

## State And Persistence
State is volatile in memory, scratchpads, doorbells/MSI descriptors, and MW translations. Scratchpads are explicitly cleared during link cleanup because hardware may retain values across remote resets. The queue protocol persists ring indices in shared MW headers and `struct ntb_rx_info`, while QP ownership is tracked by `qp_bitmap_free`. Debugfs stats expose byte/packet/error counters while the QP is active.

## Dependencies And Integration Points
Depends on generic NTB APIs, DMAengine, PCI/ioremap, debugfs, tasklets, kthreads, workqueues, and optional NTB MSI helper. It is a middle layer between NTB providers such as Switchtec and consumers that register `struct ntb_transport_client`.

## Risks And Edge Cases
- Only two-port NTB devices are supported (`PIDX` fixed to default peer), despite warnings for multi-port devices.
- Queue state is split across spinlocks, tasklets, work items, DMA callbacks, and optional kthreads; teardown ordering is critical.
- `last_cookie` is shared for TX/RX DMA waits, so concurrent channel use may make termination diagnostics less precise.
- `ntb_transport_tx_free_entry()` trusts `remote_rx_info`; stale or unmapped MW state can corrupt flow-control decisions.
- Link negotiation depends on both sides using the exact protocol version, QP count, and MW count.
- Optional MSI consumes a doorbell bit and the highest MW; incorrect accounting breaks QP or MW count.
- CPU copy to WC/I/O memory relies on barriers and posted-write flushes before interrupting the peer.

## Test Signals
Build with NTB core, DMAengine, optional MSI, and transport clients. Runtime validation includes transport client probe/remove, link-up/down churn, ping tests over QPs, DMA and CPU copy modes, `use_msi=1`, `tx_memcpy_offload=1`, and debugfs `stats` counters. Watch for RX version mismatches, ring-full/no-buffer counters, stale scratchpad values after reset, and clean queue free without warnings about non-empty queues.
