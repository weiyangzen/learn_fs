# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.c

## Purpose

`htc_hst.c` is the host-side HTC protocol implementation for ath9k HTC. It wraps and unwraps HTC frame headers, manages service endpoint connection, processes firmware control messages, dispatches non-control frames to endpoint callbacks, reports firmware panic messages, and connects the generic HTC transport layer to ath9k device probe/deinit.

## Important APIs, Types, and Functions

`htc_issue_send()` is the low-level send helper. It pushes `struct htc_frame_hdr`, fills endpoint ID, flags, big-endian payload length, zeroed control bytes, and calls the HIF `send()` callback on the endpoint upload pipe. `htc_send()` obtains the endpoint from `HTC_SKB_CB(skb)->epid`; `htc_send_epid()` sends to an explicit endpoint.

Endpoint setup is performed by `htc_connect_service()`. It selects a temporary unused endpoint slot, fills service ID, queue depth, callback table, and upload/download pipe IDs from `service_to_ulpipe()`/`service_to_dlpipe()`, sends an `HTC_MSG_CONNECT_SERVICE_ID` message on endpoint 0, waits for `cmd_wait`, validates `conn_rsp_epid`, and returns the firmware-assigned endpoint. `htc_process_conn_rsp()` moves the temporary endpoint metadata into the endpoint ID returned by firmware.

Target setup uses `htc_config_pipe_credits()`, `htc_setup_complete()`, and `htc_init()`. These send control messages and wait for HIF TX completion to signal command completion through `ath9k_htc_txcompletion_cb()`. Target readiness is processed by `htc_process_target_rdy()`, which records credit size, reserves endpoint 0 for `HTC_CTRL_RSVD_SVC`, increments `tgt_ready`, and completes `target_wait`.

Receive dispatch is `ath9k_htc_rx_msg()`. It validates frame length and endpoint, recognizes firmware panic endpoint `0x99`, handles endpoint 0 control messages (`HTC_MSG_READY_ID` and `HTC_MSG_CONNECT_SERVICE_RESPONSE_ID`), trims trailers for data endpoints, strips the HTC header, and invokes endpoint RX callbacks.

Allocation and bridge functions are `ath9k_htc_hw_alloc()`, `ath9k_htc_hw_free()`, `ath9k_htc_hw_init()`, and `ath9k_htc_hw_deinit()`.

## Control Flow

The transport starts with `ath9k_htc_hw_alloc()`, which allocates `struct htc_target`, initializes completions, stores HIF/device pointers, and assigns endpoint 0 pipe IDs from the HIF descriptor. Firmware later sends a ready message; `ath9k_htc_rx_msg()` dispatches it to `htc_process_target_rdy()`, unblocking probe.

Service connection is request/response over endpoint 0. The host first reserves a local endpoint as temporary state, sends the service connection message with firmware pipe IDs, and waits up to one second. The response handler validates firmware endpoint ID, finds the temporary endpoint by service ID, clears that slot, copies metadata to the firmware endpoint, records `conn_rsp_epid`, and completes `cmd_wait`.

Data and WMI frames bypass control-message parsing. RX is delivered to the endpoint callback registered by the service owner, while TX completion removes the HTC header and invokes endpoint TX callbacks or frees the SKB.

## State and Persistence Behavior

`struct htc_target` owns endpoint metadata, HIF callbacks, completions, `conn_rsp_epid`, target credits, credit size, `htc_flags`, and target-ready count. Endpoint state persists after service connection and contains service ID, callbacks, queue depth, max message length, and pipe IDs. `htc_flags` is a transient command-completion discriminator for credit config and setup-complete messages. SKB ownership changes at callback boundaries: control SKBs are freed by HTC code; service RX SKBs are handed to endpoint owners; service TX SKBs are handed to endpoint TX callbacks or freed if no callback exists.

## Dependencies and Integration Points

This file depends on `htc_hst.h` protocol structures, `htc.h` private driver definitions, Linux SKB APIs, completions, endian helpers, device logging, and HIF callbacks supplied by USB transport. It integrates upward with `ath9k_htc_probe_device()` and `ath9k_htc_disconnect_device()` and laterally with WMI/TX/RX endpoint callbacks.

## Risks

Length validation is essential because firmware controls RX frame contents. Endpoint connection state is temporarily keyed by service ID and can be confused if duplicate services are connected concurrently. Some timeout/error paths after successful send do not free the SKB because ownership was transferred to HIF; that is intentional but sensitive to HIF semantics. `htc_flags` allows only one pending setup/credit operation style at a time. Firmware panic reporting reads firmware-provided structures and should preserve size checks. Trailer trimming trusts `control[0]` after only broad frame validation.

## Test Signals

Exercise firmware ready handling, service connection success and failure responses, endpoint ID boundary checks, setup-complete and credit-config timeouts, malformed endpoint 0 messages, data endpoint dispatch, missing endpoint callbacks, HIF TX failure, firmware panic patterns, trailer frames, and hot-unplug deinit while target state exists.
