# sources/distributed-fs/ceph-client/drivers/greybus/es2.c

## Purpose

`es2.c` is a USB host-controller driver for Toshiba ES2 AP bridge devices. It implements a `gb_hd_driver` that carries Greybus operation messages over USB bulk endpoints, handles APBridge RPC control commands over vendor control requests plus a response endpoint, exposes optional APB log debugfs files, and registers a Greybus host device when the USB interface probes.

## Important APIs, Types, and Functions

- `struct es2_ap_dev` is the host-private state behind `gb_host_device::hd_priv`: USB device/interface, Greybus host pointer, CPort IN/OUT URB pools, ARPC endpoint/list, CDSI allocation state, and APB log state.
- `message_send()` packs the destination CPort into the operation header pad byte, submits an OUT bulk URB, and completes through `cport_out_callback()`.
- `message_cancel()` kills a submitted OUT URB and protects preallocated URBs from reuse while cancellation is in progress.
- `cport_in_callback()` unpacks the CPort from the received header and passes valid traffic to `greybus_data_rcvd()`.
- `arpc_sync()` sends APBridge RPCs, tracks them by ID in `es2->arpcs`, waits for `arpc_in_callback()`, and maps remote errors to `-EREMOTEIO`.
- CPort-management callbacks include `es2_cport_allocate()`, `es2_cport_release()`, `cport_enable()`, `es2_cport_connected()`, `es2_cport_flush()`, `es2_cport_shutdown()`, `es2_cport_quiesce()`, `es2_cport_clear()`, and latency tag enable/disable.
- `ap_probe()` discovers USB endpoints, allocates URBs/buffers, reserves CDSI CPorts, enables ARPC, adds the Greybus host, and starts CPort receive URBs.
- `ap_disconnect()` removes the host, disables URBs, and frees resources through `es2_destroy()`.

## Control Flow

Probe reads the CPort count using a vendor control request, clamps it to one-byte CPort IDs, creates a Greybus host with `ES2_GBUF_MSG_SIZE_MAX`, records USB endpoints, allocates inbound CPort URBs, ARPC URBs, and outbound URB pool entries, then enables ARPC and calls `gb_hd_add()`. Only after the Greybus host is added does it submit the CPort IN URBs.

Outgoing Greybus messages reserve a pooled or dynamically allocated URB, store it in `message->hcpriv`, pack CPort routing in `header->pad[0]`, submit to the bulk OUT endpoint, and report completion to the operation layer in the callback. Incoming bulk data must include a Greybus header; the driver unpacks the CPort and forwards the message to connection dispatch. CPort state changes such as connected, flush, shutdown, quiesce, and clear run through ARPC, not through normal Greybus operation messages.

## State and Persistence Behavior

The driver maintains persistent USB/host state per probed interface. The outbound URB pool is protected by `cport_out_urb_lock`, while ARPC state is protected by `arpc_lock`. APB logging uses a kernel thread and a fixed-size FIFO under debugfs. `cdsi1_in_use` persists offloaded CDSI allocation. Disconnect tears down the Greybus host first, then kills receive URBs and frees all USB resources.

## Dependencies and Integration Points

The file depends on USB core, Greybus host/operation APIs, `arpc.h`, debugfs, kfifo, kthreads, tracepoints, and unaligned-safe message handling. It exports no symbols; it registers through `module_usb_driver()` with USB ID `18d1:1eaf`.

## Risks and Edge Cases

- CPort ID transport uses one byte of `gb_operation_msg_hdr::pad`; the code clamps CPort count to `U8_MAX`, so any protocol change requiring wider CPorts would need a framing change.
- `message_cancel()` assumes `message->hcpriv` is a valid URB and calls `usb_get_urb()` without a null check.
- The dynamic URB fallback can allocate outside the fixed pool under pressure; cancellation and completion paths must continue to distinguish pooled from dynamic URBs correctly.
- ARPC timeout removes the RPC from the active list; late responses are logged as invalid IDs and dropped.
- Debugfs APB logging is optional and polling-based, so log loss is expected under FIFO pressure.
- Probe error paths route through `es2_destroy()`; partially initialized fields must remain safe for NULL-aware USB/debugfs cleanup.

## Test Signals

Exercise USB probe with missing endpoints, CPort count failure, URB allocation failure, `gb_hd_add()` failure, normal disconnect, bulk IN message forwarding, OUT completion and cancellation races, ARPC timeout and remote-error responses, CDSI reserved/offloaded CPort allocation, latency tag vendor requests, and APB log debugfs enable/read/disable.
