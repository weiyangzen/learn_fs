# sources/distributed-fs/ceph-client/drivers/usb/usbip/stub_rx.c

## Purpose

`stub_rx.c` is the host-side USB/IP receive path. It receives remote submit/unlink PDUs, validates them against the exported device, reconstructs local URBs, handles control requests requiring local USB core APIs, receives payloads/iso descriptors, and submits or unlinks URBs on the physical device.

## Important APIs, Types, and Functions

Special-request detectors/tweakers handle `CLEAR_FEATURE(ENDPOINT_HALT)`, `SET_INTERFACE`, `SET_CONFIGURATION`, and port reset. `stub_recv_cmd_unlink()` finds pending submits, marks them unlinking, and calls `usb_unlink_urb()`, or queues an immediate unlink reply. `stub_priv_alloc()` creates request state in `priv_init`. `get_pipe()` maps USB/IP endpoint/direction to a real pipe and validates isochronous packet count. `masking_bogus_flags()` constrains wire-provided URB flags. `stub_recv_cmd_submit()` allocates buffers or SG lists, optionally splits SG into multiple URBs, unpacks the PDU, receives data, and submits.

## Control Flow

`stub_rx_loop()` repeatedly calls `stub_rx_pdu()` until stopped or an event appears. Each PDU header is read exactly, endian-corrected, validated by stable `devid` and `SDEV_ST_USED`, and dispatched by command. Submit handling allocates state before payload receive so event cleanup can free it. Completion flows later through `stub_tx.c`.

## State and Persistence Behavior

Remote submit state lives in `stub_priv` lists. For HCDs without SG support, one remote request is split into several URBs and reassembled by TX. There is no persistent state.

## Dependencies and Integration Points

It depends on common USB/IP wire helpers, USB core URB submission/unlink/control APIs, SG allocation, physical endpoint descriptors, and host TX completion queues.

## Risks and Test Signals

Risks include malformed remote headers, negative or oversized lengths, SG zero-length cases, special-control requests changing device configuration mid-stream, unlink completion races, and wire-supplied isochronous metadata. Test signals include valid/invalid endpoint submit, OUT payload receive, IN submit completion, unlink before and after completion, SG split path, special control requests, and TCP/error event generation.
