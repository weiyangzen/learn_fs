# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/mars.c

## Purpose
`mars.c` is a standalone GSPCA subdriver for Mars-Semi MR97311A JPEG webcams, binding USB ID `093a:050f`. It configures the bridge and MI sensor, builds JPEG headers, exposes image and illuminator controls, and detects frame starts in the device's JPEG payload stream.

## Important APIs, Types, And Functions
`struct sd` extends `gspca_dev` with brightness, saturation, sharpness, gamma, two illuminator controls, and a cached JPEG header. USB helpers are `reg_w()` for bulk endpoint 4 writes and `mi_w()` for MI sensor writes. Control setters write bridge registers for brightness, color, gamma, sharpness, and illuminators. GSPCA callbacks are `sd_config()`, `sd_init()`, `sd_init_controls()`, `sd_start()`, `sd_stopN()`, and `sd_pkt_scan()`.

## Control Flow
Probe registers two JPEG modes, 320x240 and 640x480. Start generates a JPEG 4:2:2 header at fixed quality, writes bridge dimensions and compression/frame-size registers, applies current gamma/saturation/brightness/sharpness, initializes 32 MI sensor registers, enables isochronous transfer, and applies illuminator state. Control changes are ignored while stopped except the clustered illuminator values are kept mutually exclusive. Packet scanning searches for `ff ff 00 ff 96 64..67`, ends the previous frame, inserts the cached JPEG header as the first packet, skips a 16-byte device header, and appends the remaining data.

## State, Persistence, And Dependencies
State is in V4L2 controls and `jpeg_hdr`. Hardware state is volatile bridge/sensor register programming. Dependencies include GSPCA, `jpeg.h`, USB bulk endpoint 4, V4L2 illuminator controls, and the device's marker format.

## Integration Points
The `sd_desc` hooks integrate with GSPCA and standard PM helpers. The output format is `V4L2_PIX_FMT_JPEG`, and the driver supplies JPEG headers because the device stream carries frame data without a complete standard header at each SOF.

## Risks
`reg_w()` records only the first USB error in `usb_err`, so later writes are skipped until the caller resets it. Packet scanning always appends an `INTER_PACKET` even if no SOF was found, relying on GSPCA frame state. Illuminator mutual exclusion mutates peer control values manually and depends on cluster/update semantics. The start script is mostly trace-derived magic constants.

## Test Signals
USB probe on `093a:050f`, both JPEG modes, JPEG header validity, SOF detection with split/offset markers, controls during active streaming, illuminator exclusivity and stop-time off command, and bulk-write failure propagation.
