<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.c -->
# sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.c

## Purpose
This file implements synchronous command submission to the BDC hardware command processor. It is used by endpoint configuration, address assignment, stall/reset/stop operations, dequeue pointer changes, and USB3 function wake notifications.

## Important APIs, Types, And Functions
`bdc_issue_cmd()` writes command parameters, uses a write memory barrier, sets `BDC_CMD_CWS | BDC_CMD_SRD`, and polls command status until not busy or timeout. `bdc_submit_cmd()` validates the command processor is idle, converts BDC completion codes into Linux errors, and logs failures. Exported internal helpers are `bdc_config_ep()`, `bdc_dconfig_ep()`, `bdc_ep_bla()`, `bdc_address_device()`, `bdc_function_wake_fh()`, `bdc_function_wake()`, `bdc_ep_set_stall()`, `bdc_ep_clear_stall()`, and `bdc_stop_ep()`.

## Control Flow
Endpoint enable calls `bdc_config_ep()` after a descriptor list exists. This builds command parameters from descriptor max packet size, endpoint type, interval, burst/mult fields, and gadget speed, then reinitializes the BD list on success. Deconfigure drops the endpoint from hardware. Dequeue and some cancellation paths use `bdc_stop_ep()` followed by `bdc_ep_bla()` to redirect the hardware dequeue pointer. Standard SET_ADDRESS uses `bdc_address_device()`. Clear-stall may first force a stall, issues reset endpoint, optionally resets sequence numbers, and notifies transfer fetching.

## State And Persistence
The file mutates hardware command registers and endpoint flags. `ep_bd_list_reinit()` resets enqueue/dequeue indexes and marks the first BD with stop-buffer-fetch so software can safely requeue. `bdc_stop_ep()` sets `BDC_EP_STOP` after a successful stop command. Address and wake commands update hardware state indirectly; `bdc->dev_addr` is set by callers.

## Dependencies And Integration Points
The command layer depends on `bdc.h` register definitions, endpoint descriptors from the USB core, speed state maintained by `bdc_udc.c`, and debug helpers. It is called from endpoint, EP0, gadget, link-state, and remote wake paths.

## Risks
Commands are serialized only by callers holding the controller lock; calling without that lock could race command register programming. Timeouts are short busy-poll loops in atomic context, so hardware latency changes can surface as `-ECONNRESET`. Endpoint configuration is sensitive to interval conversion for full-speed interrupt/isochronous endpoints and to optional superspeed companion descriptors. Clear-stall behavior intentionally stalls an unstalled non-EP0 endpoint before resetting it, which must match hardware sequence-number requirements.

## Test Signals
Exercise SET_ADDRESS, endpoint enable/disable for bulk/interrupt/isochronous descriptors at each speed, halt/clear-halt, dequeue of in-flight requests, and USB3 remote/function wake. Command timeout and parameter error logs are key diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/usb/gadget/udc/bdc/bdc_cmd.c -->
