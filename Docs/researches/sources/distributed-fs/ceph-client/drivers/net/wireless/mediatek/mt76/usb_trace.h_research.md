# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/usb_trace.h

## Purpose
Declares mt76 USB tracepoints for vendor-register reads/writes and URB transfer activity.

## Important APIs, Types, And Functions
Defines event class `dev_reg_evt` and events `usb_reg_rr` and `usb_reg_wr`. Defines event class `urb_transfer` and events `submit_urb` and `rx_urb`. Each record includes a wiphy name plus register/value or URB pipe/length fields.

## Control Flow
No executable control flow. USB code emits these tracepoints around control-message register access and URB submission/completion.

## State And Persistence
Trace records persist in tracing buffers only. URB records capture pipe and transfer length, not payload data.

## Dependencies And Integration Points
Depends on Linux tracepoints, `mt76.h`, and `usb_trace.c` for instantiation. Used heavily by `usb.c`.

## Risks
Event names and field formats are diagnostic ABI for trace tooling. The fixed 32-byte wiphy field can truncate names.

## Test Signals
Enabled tracepoints show correct register, value, pipe, and length during USB register access and RX/TX URB flow.
