# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath10k/htc.h

Purpose: declares the ath10k HTC wire protocol and host-side HTC data structures. It documents frame layout, endpoint/service namespaces, control messages, trailer records, credit reports, bundle encoding, callback contracts, and public HTC APIs.

Important APIs/types/functions: protocol types include `struct ath10k_htc_hdr`, TX/RX flag enums, message IDs, connection flags/statuses, READY/READY_EXT, CONNECT_SERVICE request/response, SETUP_COMPLETE_EXT, record IDs, credit and lookahead records, and `ath10k_htc_get_bundle_count`. Host-side types include service IDs, endpoint IDs, callback tables, connection structs, `struct ath10k_htc_ep`, and `struct ath10k_htc`.

Control flow: TX frames are `<htc_hdr><payload>`; RX frames are `<htc_hdr><payload><trailer>`. EP0 handles control. Services connect before sending data, target-assigned endpoints route callbacks, and trailers carry credit/lookahead metadata.

State and persistence: the header allocates no state but defines volatile endpoint arrays, credits, control buffers, completion, and bundle parameters held by `struct ath10k_htc`. No state persists across device teardown.

Dependencies/integration: included by HTT, HTC, and bus-facing code; must match firmware ABI with packed/aligned little-endian structures; service IDs must align with HIF pipe mapping.

Risks: ABI layout changes can break firmware communication; fixed endpoint count requires strict validation; bundle count decoding shares flag bits; duplicated enum type names can confuse searches; some connection response fields are not central in current call paths.

Test signals: struct size/offset checks, READY/connect/setup messages, trailer credit/lookahead parsing, bundle count decoding, unsupported services, and cross-bus WMI/HTT/pktlog routing.
