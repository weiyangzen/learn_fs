# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath6kl/htc.h

## Purpose
`htc.h` defines the Host Target Communications protocol structures and local driver state used by both mailbox and pipe HTC implementations. It describes frame headers, control messages, service IDs, endpoints, packet containers, callbacks, credit distribution, endpoint stats, backend ops, and `struct htc_target`.

## Important APIs, types, and functions
Protocol definitions include HTC frame flags, RX trailer flags, message IDs (`READY`, `CONN_SVC`, `CONN_SVC_RESP`, setup complete), HTC versions, service IDs for WMI control/data ACs, endpoint IDs, credit report records, lookahead records, bundling limits, and operational flags. `struct htc_frame_hdr` is the packed wire header. Control structures include ready, connect, connect response, setup complete, record header, credit report, and lookahead reports.

Local structures include `struct htc_packet`, endpoint callbacks (`struct htc_ep_callbacks`), service connect request/response, `struct htc_endpoint_credit_dist`, `struct ath6kl_htc_credit_info`, endpoint stats, `struct htc_endpoint`, `struct htc_control_buffer`, pipe credit allocation entries, `struct ath6kl_htc_ops`, and the root `struct htc_target`. Inline helpers initialize TX/RX packet metadata, reset RX packet buffers, and count list depth.

## Control flow and integration
Core/WMI code creates `htc_packet` objects and submits them to the selected backend. Backends parse and generate `htc_frame_hdr`, connect WMI services to endpoints, use callbacks for RX, TX complete, RX refill, queue-full decisions, and multi-TX completion, and update endpoint stats. HIF interrupt or pipe completion paths eventually route packets back through endpoint callbacks.

## State and persistence behavior
`struct htc_target` persists endpoint arrays, credit distribution lists, control buffer pools, locks, target credit size/count, target version, RX/TX bundling limits, scatter sizing, pipe control response buffer, and pipe credit allocation. Endpoint state persists service id, queues, callbacks, queue depths, sequence numbers, connection flags, per-endpoint stats, pipe IDs, and credit-flow mode.

## Dependencies and integration points
`htc.h` depends on ath6kl `common.h` and Linux list/SKB conventions. It is included by `core.h`, HTC backends, HIF wrappers, and debug reporting. It is the main contract between ath6kl upper layers and HTC transports.

## Risks and test signals
Risks include packed wire-structure ABI drift, endpoint ID bounds, payload length validation, trailer parsing, credit accounting, queue-depth helper cost on long lists, and backend differences hidden behind a common ops table. Test signals include service connect responses, WMI data over all AC endpoints, credit report processing, bundled RX/TX, endpoint stat accuracy, setup-complete negotiation for HTC 2.0 versus 2.1, and stop/cleanup with queued packets.
