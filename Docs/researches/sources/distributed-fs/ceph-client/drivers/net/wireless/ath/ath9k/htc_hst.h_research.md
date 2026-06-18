# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/htc_hst.h

## Purpose

`htc_hst.h` declares the host-side HTC transport contract used by ath9k HTC. It defines HIF transport callbacks, HTC endpoint IDs, wire-format control messages, service IDs, endpoint callback structures, target state, and the public host transport APIs consumed by the USB HIF, WMI, and ath9k HTC driver layers.

## Important APIs, Types, and Functions

`enum ath9k_hif_transports` currently contains `ATH9K_HIF_USB`, making USB the supported HIF transport. `struct ath9k_htc_hif` describes the transport implementation: list linkage, transport name, control pipe IDs, `start`, `stop`, `sta_drain`, and `send` callbacks.

`enum htc_endpoint_id` defines endpoint 0 through endpoint 8 plus `ENDPOINT_MAX = 22` and `ENDPOINT_UNUSED = -1`. Endpoint 0 is reserved for HTC control. `struct htc_frame_hdr` is the packed wire header with endpoint ID, flags, big-endian payload length, and four control bytes. `HTC_FLAGS_RECV_TRAILER` indicates a trailer exists.

Control messages include `struct htc_ready_msg`, `struct htc_config_pipe_msg`, `struct htc_conn_svc_msg`, `struct htc_conn_svc_rspmsg`, and `struct htc_comp_msg`, with message IDs in `enum htc_msg_id`. Firmware panic formats are `struct htc_panic_bad_vaddr` and `struct htc_panic_bad_epid`.

`struct htc_ep_callbacks` carries endpoint owner callbacks for TX completion and RX delivery. `struct htc_endpoint` stores service ID, callbacks, max queue depth, max message length, and pipe IDs. `struct htc_target` is the main transport object: HIF/device pointers, driver private pointer, endpoint table, completions, list linkage, last connect response endpoint, credits, credit size, flags, and atomic ready count.

Service IDs are built with `MAKE_SERVICE_ID()` and include reserved HTC control plus WMI control, beacon, CAB, UAPSD, management, and four data access categories. Public functions include `htc_init()`, `htc_connect_service()`, `htc_send()`, `htc_send_epid()`, `htc_stop()`, `htc_start()`, `htc_sta_drain()`, RX/TX callbacks from HIF, and target allocation/init/deinit helpers.

## Control Flow

The header describes a layered flow: HIF allocates and starts an `htc_target`; endpoint 0 receives ready and connect responses; service owners connect WMI/data services by service ID; data senders attach endpoint IDs in `HTC_SKB_CB`; HIF receive calls `ath9k_htc_rx_msg()`; HTC dispatches control messages internally and service frames to registered endpoint callbacks.

## State and Persistence Behavior

The state defined here persists for the life of the USB device. `htc_target.endpoint[]` is the routing table for service callbacks and pipe IDs. `target_wait` and `cmd_wait` serialize target readiness and command responses. `credits` and `credit_size` store transport flow-control parameters discovered/configured during startup. `htc_flags` stores in-flight operation bits for setup and pipe credit commands. The callback structures preserve the owner pointer used to return SKBs to `struct ath9k_htc_priv` paths.

## Dependencies and Integration Points

The header depends on Linux list, completion, atomic, device, SKB, and endian types through included driver headers. It integrates with USB HIF transport, `htc_hst.c`, WMI service setup, TX/RX code, and device probe/deinit functions in `htc_drv_init.c`.

## Risks

All wire structs are packed and endian-tagged; any change to fields or byte order must match firmware. `ENDPOINT_MAX` is larger than the explicitly named endpoint constants, so loops and bounds checks must use `ENDPOINT_MAX` rather than assuming only 0 through 8. Callback ownership is not self-describing; endpoint owners must know whether they receive an HTC-stripped SKB and whether they must free it. Service IDs and pipe IDs are firmware ABI, not local policy.

## Test Signals

Compile-time structure layout compatibility, endpoint bounds checks, service ID mapping, callback invocation for every WMI service, target ready completion, command completion, and USB transport start/stop/drain behavior are the main signals. ABI-sensitive changes should be tested against real firmware or firmware protocol emulation.
