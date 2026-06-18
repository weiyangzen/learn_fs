# sources/distributed-fs/ceph-client/drivers/staging/greybus/usb.c

## Purpose
Implements a skeleton Greybus USB host-controller driver for `GREYBUS_PROTOCOL_USB`. It wires Greybus HCD start/stop and hub-control operations into a Linux `usb_hcd`, but probe intentionally disables the protocol because required USB core changes are not upstream.

## Important APIs, Types, and Functions
`struct gb_usb_device` stores the Greybus connection and gbphy device inside `usb_hcd` private data. `hcd_start()` and `hcd_stop()` send `GB_USB_TYPE_HCD_START` and `GB_USB_TYPE_HCD_STOP`. `hub_control()` forwards root hub control fields through `GB_USB_TYPE_HUB_CONTROL` and copies the response buffer. `urb_enqueue()`, `urb_dequeue()`, `get_frame_number()`, and `hub_status_data()` are stubs. `usb_gb_hc_driver` registers these callbacks with USB core.

## Control Flow and State
Probe creates an HCD, creates/enables a Greybus connection, stores cross-pointers, sets `hcd->has_tt`, then always warns and exits with `-EPROTONOSUPPORT` before `usb_add_hcd()`. Remove assumes an HCD was added and calls `usb_remove_hcd()`, then tears down the connection and HCD.

## Dependencies and Integration Points
Depends on Greybus core, gbphy, and USB HCD core. It models a USB2 host with transaction translator support. The remote protocol owns hub behavior; this host driver only passes root hub control requests through.

## Risks and Test Signals
Because probe is disabled, real runtime coverage is mostly negative: enabling the Greybus USB interface should fail with `-EPROTONOSUPPORT` and release all resources. If re-enabled, stubs for URB enqueue/dequeue make the driver non-functional for normal USB I/O. Additional risks include remove ordering if future changes allow partial registration and `hub_control()` response-length validation for unspecified lengths.
