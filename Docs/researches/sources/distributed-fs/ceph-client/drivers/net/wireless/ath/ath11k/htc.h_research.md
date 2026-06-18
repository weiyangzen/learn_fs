# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/htc.h

## Purpose
`htc.h` defines the public HTC protocol contract for ath11k: wire headers, control message formats, service ids, endpoint ids, credit trailer records, service connection request/response structs, endpoint state, global HTC state, constants, and exported HTC APIs.

## Important APIs, types, and data
The wire header is `struct ath11k_htc_hdr`, with bit masks for endpoint id, flags, payload length, control bytes, and reserved bits. Message structs include READY, READY extended, connect service, connect service response, setup complete extended, generic HTC message, record header, credit report, and trailer record.

Enums define HTC message ids, protocol versions, connection flags/status codes, record ids, service groups, service ids, and endpoint ids. `struct ath11k_htc_ep_ops` supplies endpoint callbacks. `struct ath11k_htc_svc_conn_req` and response structs define the service connection API. `struct ath11k_htc_ep` and `struct ath11k_htc` persist endpoint and global HTC state.

## Control flow
The header has no executable flow. Its declarations define the lifecycle implemented in `htc.c`: initialize endpoint state, wait for target ready, connect services over EP0, start the HTC session, send framed SKBs over CE pipes, receive framed SKBs, process trailers, and dispatch endpoint callbacks.

## State and persistence behavior
All persistent HTC runtime state is in `struct ath11k_htc` and its endpoint array. Credit counts and sequence numbers change as messages are sent and target credit reports arrive. Control responses are transiently stored in a fixed buffer guarded by a completion. No state is persisted to disk.

## Dependencies and integration points
The header includes kernel list/bug/SKB/timer headers and relies on `struct ath11k_base`. Implementations depend on HIF service-to-pipe mapping, CE transport, DMA mapping, completions, and `ab->hw_params.credit_flow`. CE, WMI, DP, and core are direct consumers.

## Risks
HTC wire layout and bit masks must match firmware exactly. Endpoint ids are small and `ATH11K_HTC_EP_UNUSED` is negative, so signed/unsigned handling matters. The fixed control response buffer requires bounds checks. Callback pointers must be initialized before non-control RX/TX traffic is possible.

## Test signals
Target READY parsing, expected credit size/count, service connect responses, endpoint ids and max message lengths, credit reports waking blocked senders, EP0 suspend/wakeup handling, and stable WMI/HTT traffic without invalid endpoint or trailer warnings are the main signals.
