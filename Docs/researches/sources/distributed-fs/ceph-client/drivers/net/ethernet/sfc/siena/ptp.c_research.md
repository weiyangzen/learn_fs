# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/ptp.c

## Purpose

`ptp.c` implements hardware timestamping and PTP clock support for Siena-family SFC devices. It coordinates firmware-assisted PTP over MCDI, optional MAC TX timestamps, RX timestamp matching or inline timestamp reconstruction, PHC registration, PPS notification, timestamp configuration, PTP multicast filters, and workqueue-based deferred processing so slow MCDI operations do not run in the datapath.

## Important APIs, Types, and Functions

Local state is held in `struct efx_ptp_data`, which contains the PTP channel, RX/TX SKB queues, receive event pools, workqueues, multicast filter IDs, current `kernel_hwtstamp_config`, mode/enabled flags, time conversion callbacks, timestamp correction values, event fragments, synchronization DMA buffer, PHC clock info, PPS work, stats, and transmit function pointer. Matching/event structs are `struct efx_ptp_match`, `struct efx_ptp_event_rx`, and `struct efx_ptp_timeset`.

Public APIs include `efx_siena_ptp_defer_probe_with_channel()`, `efx_siena_ptp_channel()`, `efx_siena_ptp_is_ptp_tx()`, `efx_siena_ptp_tx()`, `efx_siena_ptp_get_mode()`, `efx_siena_ptp_change_mode()`, timestamp config/info getters/setters, `efx_siena_ptp_event()`, `efx_siena_time_sync_event()`, `__efx_siena_rx_skb_attach_timestamp()`, `efx_siena_ptp_start_datapath()`, `efx_siena_ptp_stop_datapath()`, stats describe/update, and `efx_siena_ptp_nic_to_kernel_time()`.

Time conversion helpers support seconds+nanoseconds, seconds+27-bit fraction, and seconds+quarter-nanoseconds formats. PHC operations are `efx_phc_adjfine()`, `efx_phc_adjtime()`, `efx_phc_gettime()`, `efx_phc_settime()`, and `efx_phc_enable()`.

## Control Flow

Probe is deferred through an extra PTP channel. `efx_siena_ptp_defer_probe_with_channel()` first checks support by issuing PTP disable; if it succeeds, it installs `efx_ptp_channel_type`. Channel pre-probe allocates `efx_ptp_data`, a coherent start flag buffer, workqueues, queues, event objects, conversion attributes, timestamp corrections, and, for primary functions, a PHC and PPS workqueue.

Starting PTP inserts required multicast filters for PTP event and general UDP ports, enables firmware PTP mode, resets event assembly, and resets frequency adjustment state. Mode changes disable/re-enable as needed, then require a baseline synchronization before marking the mode enabled.

Synchronization issues `MC_CMD_PTP_OP_SYNCHRONIZE` asynchronously with a DMA start flag. The driver waits briefly for firmware readiness, repeatedly writes compact host time into NIC memory for a bounded period, finishes the MCDI request, parses multiple timesets, rejects invalid or too-large/too-small windows, and derives the host PPS timestamp from the best firmware sample.

TX PTP packets are queued to a workqueue. Depending on hardware capability, the worker transmits through a dedicated timestamped TX queue or linearizes/checksums/copies the packet into `MC_CMD_PTP_OP_TRANSMIT` and returns the firmware timestamp to the socket. RX PTP packets are queued by the extra channel's `receive_skb` hook. For non-inline timestamping, firmware PTP events are assembled from fragments, placed in an event list, matched by UUID/sequence, and delivered when matched or timed out. For inline timestamping, RX SKB timestamp attachment reconstructs full time from packet minor timestamp plus the latest sync event major/minor.

## State and Persistence Behavior

Persistent state lives in `efx->ptp_data`, `efx->extra_channel_type[EFX_EXTRA_CHANNEL_PTP]`, PTP multicast filter IDs, PHC registration, MCDI firmware PTP enable state, queued SKBs/events, timestamp corrections, synchronization stats, and per-channel sync event state. Workqueues serialize slow TX/RX/timing tasks. Datapath stop temporarily disables sync events, stops PTP, flushes queued RX/TX packets, and returns pending event objects to the free list.

## Dependencies and Integration Points

This file depends on Linux PTP clock/PPS APIs, skb timestamp APIs, IPv4/UDP parsing, MCDI PTP commands, filter insertion/removal, TX enqueue helpers, RX timestamp attachment in `rx.c`, event processing in farch code, and NIC type callbacks for host-time writes, timestamp sync events, and timestamp config validation.

## Risks and Test Signals

Risk areas include event fragment ordering, RX packet/event matching races, bounded event pool overflow, timestamp wrap reconstruction from partial MAC timestamps, synchronization quality filtering, PPS workqueue lifetime, PHC registration only on primary functions, and mode changes during netdev stop/start. Tests should cover PTP unsupported firmware, primary/secondary functions, V1/V2/enhanced matching, event-before-packet and packet-before-event ordering, timeout delivery without timestamp, MAC TX vs MC TX paths, PHC adjfine/adjtime/get/set, PPS enable, reset/restart, and timestamp config validation across supported filters.
