# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-dvb.h

## Purpose
This header declares the cx18 DVB registration API used by stream setup and cleanup code.

## Important APIs, Types, and Functions
It includes `cx18-driver.h` for `struct cx18_stream` and declares `int cx18_dvb_register(struct cx18_stream *stream);` and `void cx18_dvb_unregister(struct cx18_stream *stream);`.

## Control Flow
The header has no executable flow. It allows stream/device registration code to conditionally create or tear down DVB support for TS streams.

## State and Persistence
No state is held here. The actual DVB state is `struct cx18_dvb` embedded through `struct cx18_stream`.

## Dependencies and Integration Points
This is the narrow interface between cx18 stream registration and the DVB implementation. It relies on stream setup to allocate/populate `stream->dvb` before registration.

## Risks and Edge Cases
Because it includes the full main driver header, any user inherits many media and Linux dependencies. The API assumes callers do not pass non-TS streams or streams lacking `dvb` allocation.

## Test Signals
Build signals confirm stream setup can call these functions. Runtime signals are successful DVB registration/unregistration on cards with `CX18_HW_DVB` and no calls for analog-only boards.
