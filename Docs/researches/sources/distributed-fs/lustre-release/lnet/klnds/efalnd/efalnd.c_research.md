# sources/distributed-fs/lustre-release/lnet/klnds/efalnd/efalnd.c

## Purpose
This is the main implementation of Amazon EFA LND for LNet. It registers the `EFALND` transport, manages EFA RDMA resources, maps LNet messages to EFA immediate or RDMA-read protocol flows, polls completions, starts per-CPT scheduler and connection-manager threads, and handles NI/device startup and shutdown.

## Important APIs, Types, And Functions
External LND entry points are wired through `the_efalnd`: `kefalnd_startup()`, `kefalnd_shutdown()`, `kefalnd_send()`, `kefalnd_recv()`, `kefalnd_get_dev_prio()`, and `kefalnd_get_nid_metadata()`. Protocol helpers include `kefalnd_msgtype2size()`, `kefalnd_efa_status_to_errno()`, `kefalnd_errno_to_efa_status()`, `kefalnd_init_tx_protocol_msg()`, `kefalnd_get_srcnid_from_msg()`, and `kefalnd_get_dstnid_from_msg()`. Resource helpers manage TX/FMR pools, QPs, CQs, RX buffers, DMA mapping, and FMR registration/invalidation. Runtime handlers include `kefalnd_send()`, `kefalnd_recv()`, `kefalnd_handle_rx()`, `kefalnd_tx_complete()`, `kefalnd_rx_complete()`, `kefalnd_scheduler()`, `kefalnd_dev_init()`, `kefalnd_create_efa_nid()`, `kefalnd_base_startup()`, and `kefalnd_base_shutdown()`.

## Control Flow
Module init initializes tunables/debugfs and registers the LND. NI startup creates global state if needed, allocates `struct kefa_ni`, selects an IPv4 underlay interface, opens an EFA RDMA device by name, allocates PD/CQ/QP/FMR resources, creates either a small or large EFA NID, creates TX pools, starts scheduler and connection-manager threads, and links the NI into global lists. Sending obtains a TX, finds or starts an initiator connection, and chooses immediate send for small non-GPU payloads or RDMA-read handshakes for larger/GPU PUT, REPLY, and GET traffic. Receiving validates EFALND headers, dispatches LNet request messages into `lnet_parse()`, handles GETR/PUTR completion messages, and forwards connection-establishment packets to `efalnd_connection.c`. Scheduler threads poll CQs in batches and call completion handlers for send, recv, MR registration, RDMA read, and local invalidate completions.

## State, Persistence, And Dependencies
Global state lives in `struct kefa_data kefalnd`: NI list, per-CPT schedulers, per-CPT connection daemons, peer-NI rhashtable, thread count, shutdown flag, and init state. Per-NI state includes epoch, TX pool, connection hash table, cleanup list, and EFA device pointer. Per-device state includes RDMA device, GID, PD, QPs, CQs, FMR pool, local QP selection, interface IP, and CPT. Per-TX state tracks mapped fragments, FMR, RDMA descriptor, completion refs, waiting response flag, send time, and LNet messages to finalize. State is in kernel memory only and is torn down on NI/module shutdown.

## Integration Points
This file depends on LNet core (`lnet_parse()`, `lnet_finalize()`, NI tunables, NID helpers, RDMA utility mapping), Linux RDMA verbs, EFA-specific SRD QP support, libcfs CPT allocation/binding, debug/logging helpers, and connection/peer helpers in the companion EFALND files. Large-NID support integrates with `lnet-types.h`; small-NID support integrates with TCP metadata discovery.

## Risks
Resource cleanup is complex: DMA maps, FMR state, pending FINVs, QPs, CQs, TX refs, and LNet finalization must balance across success, error, timeout, and shutdown. Several TODOs note missing fatal CQ error handling and potential stuck pending TXs after `ib_post_send()` returns `-ENOMEM`. Header validation rejects epoch mismatches and unsupported v1 traffic except connection probes; version negotiation must stay compatible. FMR allocation failure after DMA mapping needs careful unmap via the error path. Small-NID construction assumes IPv4 underlay and PCI parent availability.

## Test Signals
Strong signals include module build/load/unload, NI startup/shutdown with real or mocked EFA devices, immediate PUT/GET/REPLY/ACK traffic, RDMA PUTR and GETR flows, GPU MD forcing RDMA, protocol version and epoch mismatch rejection, CQ completion stress, RNR retry behavior, FMR registration/invalidation churn, low-memory TX/FMR pool failures, connection timeout cleanup, and LNet finalization status propagation.
