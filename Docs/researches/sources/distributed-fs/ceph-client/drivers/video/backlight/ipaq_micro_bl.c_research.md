# sources/distributed-fs/ceph-client/drivers/video/backlight/ipaq_micro_bl.c

## Purpose
This platform child driver exposes an iPAQ microcontroller backlight command as a raw backlight device.

## Important APIs, Types, and Functions
`micro_bl_update_status()` builds `struct ipaq_micro_msg` with ID `MSG_BACKLIGHT`, instance byte 1, on/off byte, and 0-255 intensity, then sends it with `ipaq_micro_tx_msg_sync()`. `micro_bl_ops` uses `BL_CORE_SUSPENDRESUME`; `micro_bl_props` sets max brightness 255 and default 64.

## Control Flow
Probe fetches the parent `struct ipaq_micro`, registers `ipaq-micro-backlight`, stores the backlight as platform data, and immediately applies default brightness. There is no explicit remove path because devm manages registration.

## State and Persistence
No driver-private mutable state is kept. The microcontroller may retain its last brightness, while the Linux side relies on backlight core properties.

## Dependencies and Integration Points
The driver depends on the iPAQ micro MFD interface and platform child name `ipaq-micro-backlight`. It integrates with suspend/resume through the backlight core.

## Risks
The message protocol is fixed to instance `0x01`; platforms with multiple backlights would need changes. There is no `get_brightness()` to read controller state. All failures come from synchronous microcontroller messaging.

## Test Signals
Test probe with valid parent data, default update message contents, zero brightness on/off byte, nonzero brightness, transport failure propagation, and suspend/resume updates.
