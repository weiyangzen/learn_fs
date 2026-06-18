# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/htc.h

## Purpose

`htc.h` defines the ath12k HTC wire protocol structures, service IDs, endpoint IDs, credit/trailer formats, endpoint callback contracts, HTC state object, and public HTC APIs.

## Important APIs, Types, and Functions

Bit masks define HTC header fields, service message fields, READY fields, service response fields, and setup-complete fields.

Protocol enums include TX/RX flags, HTC message IDs, HTC versions, service connection threshold flags/statuses, trailer record IDs, service groups, service IDs, and endpoint IDs.

Wire structs include `ath12k_htc_hdr`, `ath12k_htc_ready`, `ath12k_htc_ready_extended`, `ath12k_htc_conn_svc`, `ath12k_htc_conn_svc_resp`, `ath12k_htc_setup_complete_extended`, `ath12k_htc_msg`, `ath12k_htc_record_hdr`, `ath12k_htc_credit_report`, and `ath12k_htc_record`.

Runtime structs include `ath12k_htc_ep_ops`, `ath12k_htc_svc_conn_req`, `ath12k_htc_svc_conn_resp`, `ath12k_htc_ep`, `ath12k_htc_svc_tx_credits`, and `ath12k_htc`.

Public APIs are `ath12k_htc_init()`, `ath12k_htc_wait_target()`, `ath12k_htc_start()`, `ath12k_htc_connect_service()`, `ath12k_htc_send()`, `ath12k_htc_alloc_skb()`, and `ath12k_htc_rx_completion_handler()`.

## Control Flow and Integration

Endpoint users construct `ath12k_htc_svc_conn_req` with callbacks, connect to a service, receive endpoint ID/max message length in the response, send skbs with `ath12k_htc_send()`, and receive inbound skbs through `ep_rx_complete`. Boot code initializes HTC, waits for target READY, connects WMI/HTT services, then calls `ath12k_htc_start()`.

## State and Persistence Behavior

`struct ath12k_htc` persists for device lifetime and stores endpoint table, TX lock, control response buffer/completion, credit allocation state, target credit size, and WMI endpoint count. Endpoint entries persist service IDs, callbacks, pipe IDs, credit state, flow-control status, and sequence number.

## Dependencies and Integration Points

The header depends on Linux kernel list/bug/skb/timer headers and `struct ath12k_base`. It is consumed by HTC implementation, WMI, HTT, CE completion paths, boot, suspend, and service clients.

## Risks and Contract Notes

- Packed/aligned wire structs are firmware ABI; field order and bit masks must remain synchronized with target firmware.
- `ATH12K_HTC_EP_UNUSED = -1` is in an enum also used for array indices; code must validate before indexing.
- Control buffer size is fixed at 256 bytes; future firmware control messages larger than this need explicit handling.
- Service IDs are generated from group/index values. New service IDs must not collide with firmware-defined IDs.

## Test Signals

Compile and sparse checks for packed wire structs, service connect tests for every service ID used by the driver, endpoint index validation, credit accounting tests, and boot/suspend event tests are useful header-level signals.
