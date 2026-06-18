# sources/distributed-fs/ceph-client/drivers/usb/host/fhci-tds.c

## Purpose
`fhci-tds.c` owns FHCI endpoint-zero hardware transfer descriptors and packet FIFO plumbing. It allocates CPM MURAM descriptor rings, initializes endpoint parameter RAM, submits packet descriptors to hardware, confirms completed buffer descriptors, maps hardware descriptor errors to FHCI packet statuses, and flushes rings on abort/reset.

## Important APIs, Types, and Functions
- Hardware TD format: local `struct usb_td` and TD bit definitions (`TD_R`, `TD_W`, `TD_I`, `TD_TC`, token/status/error bits).
- Endpoint lifecycle: `fhci_create_ep()`, `fhci_init_ep_registers()`, and `fhci_ep0_free()`.
- Submission/completion: `fhci_host_transaction()`, `fhci_tx_conf_interrupt()`, `fhci_host_transmit_actual_frame()`, and internal `fhci_td_transaction_confirm()`.
- Flush/control helpers: `fhci_flush_bds()`, `fhci_flush_actual_frame()`, and `fhci_push_dummy_bd()`.

## Control Flow
Endpoint creation allocates a combined MURAM area for the TD ring and endpoint PRAM, allocates three pointer FIFOs for confirmation frames, empty frames, and dummy receive buffers, initializes packet/buffer pools, sets wrap on the last descriptor, and stores the endpoint in `usb->ep0`. Register initialization programs endpoint mode, PRAM pointers, function codes, buffer lengths, and TX ring base pointers.

`fhci_host_transaction()` temporarily disables FHCI interrupts, reserves the next empty descriptor, writes the physical data address, token/address/endpoint/type fields, status bits, low-speed PRE behavior, and length, queues the packet in `conf_frame_Q`, and starts the FIFO if this is the first queued frame. Completion scans `conf_td` descriptors that are no longer ready, clears them, skips dummy markers, dequeues the corresponding packet, translates descriptor errors and IN lengths, and calls `fhci_transaction_confirm()`. Flush paths mark ready descriptors timed out, consume confirmations, reset descriptor contents and PRAM pointers, and restore ring cursors.

## State and Persistence Behavior
Persistent runtime state is the endpoint object: MURAM TD ring, endpoint PRAM pointer, ring cursors (`conf_td`, `empty_td`), three kfifos, and `already_pushed_dummy_bd`. Descriptor state is shared with hardware and must be accessed through big-endian I/O helpers. No disk state exists.

## Dependencies and Integration Points
The file depends on CPM MURAM allocation/address translation, FHCI queue helpers (`cq_*`), scheduler confirmation callbacks, QE USB command registers, and Linux physical address translation via `virt_to_phys()`. It is tightly coupled to endpoint zero in this FHCI implementation.

## Risks and Test Signals
Risks include DMA/physical-address assumptions for packet buffers, descriptor-ring wrap/cursor desynchronization, dummy descriptor handling bugs, FIFO exhaustion, and error mapping differences between RX and TX failures. Test signals include IN/OUT/SETUP transfers at ring boundaries, dummy IN receive path, descriptor full condition, TX error/timeout/NAK/stall injection, flush during active descriptors, and repeated create/free cycles under allocation failure.
