# sources/distributed-fs/ceph-client/drivers/media/usb/as102/as102_fw.h

## Purpose
Declares AS102 firmware packet layout and firmware upload entry point.

## Important APIs, types, and functions
`MAX_FW_PKT_SIZE` is 64 bytes. `struct as10x_raw_fw_pkt` contains a four-byte address and data bytes sized to fit a 64-byte packet minus request/length overhead. `struct as10x_fw_pkt_t` overlays two request bytes or length bytes before the raw firmware payload. `as102_fw_upload()` is exported for kernel callers. `dual_tuner` is declared for firmware selection.

## Control flow and state
This header has no executable flow, but its packed layout defines the wire protocol used by `as102_fw.c` and `as102_usb_drv.c`. The `__packed` annotations are part of the ABI to the device firmware loader.

## Dependencies and integration points
Consumes `struct as10x_bus_adapter_t` from the driver and is included by firmware and USB files. It integrates with firmware upload by giving the USB endpoint code a byte-accurate packet structure.

## Risks and test signals
Risks are structure-size drift and alignment changes if fields are edited. Test signals are `sizeof(struct as10x_fw_pkt_t)` remaining compatible with 64-byte packets, successful upload of both firmware stages, and no short bulk writes.
