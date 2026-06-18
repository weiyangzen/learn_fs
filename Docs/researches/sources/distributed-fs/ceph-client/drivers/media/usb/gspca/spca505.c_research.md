# sources/distributed-fs/ceph-client/drivers/media/usb/gspca/spca505.c

## Purpose
`spca505.c` supports SPCA505/SPCA505B raw video cameras, including Intel PC Camera Pro and Creative NX Ultra. It initializes one of two bridge/CCD register tables, supports raw `V4L2_PIX_FMT_SPCA505` modes from 160x120 through 640x480, starts and stops the ISO packet machine, assembles raw frames, and exposes brightness control.

## Important APIs, types, and functions
`struct sd` stores the GSPCA base and subtype (`IntelPCCameraPro` or `Nxultra`). Static tables `spca505_init_data`, `spca505_open_data_ccd`, `spca505b_init_data`, and `spca505b_open_data_ccd` describe bridge, global, compression, CCD, brightness, gamma, and color setup. `reg_write` and `reg_read` perform vendor control transfers. `write_vector` writes `{request,value,index}` tables until a zero request sentinel. `setbrightness` writes a split inverted brightness value to register group `0x05` indices `0x00` and `0x01`.

## Control flow
`sd_config` selects the raw mode table and restricts Intel PC Camera Pro to all modes except 640x480. `sd_init` writes the subtype-specific init table. `sd_start` writes the subtype-specific open table, reads register `0x06/0x16` and expects `0x0101`, writes a follow-up register sequence needed for repeated streaming, selects compression mode registers from `mode_tb` based on current mode `.priv`, and enables USB streaming by writing `SPCA50X_REG_USB/SPCA50X_USB_CTRL` with `SPCA50X_CUSB_ENABLE`. `sd_stopN` disables the ISO packet machine. `sd_stop0` performs additional reset/power-control writes when the device is still present.

Packet scanning is the same basic raw SPCA50x pattern: marker byte `0` starts a new frame after skipping a 10-byte header, marker `0xff` is dropped, and other packets skip one prefix byte and append payload.

## State and persistence
The only durable in-memory state is subtype. Hardware state is rebuilt from tables on init and start. There is no host-side persistence. Control writes while idle are skipped, so brightness defaults are mainly carried by the initialization tables until streaming controls are changed.

## Dependencies and integration points
This file integrates with GSPCA through standard callbacks and emits `V4L2_PIX_FMT_SPCA505`, shared conceptually with `spca506.c`. It uses only USB control transfers and GSPCA frame assembly, not `jpeg.h`.

## Risks
The init/open tables are long trace-derived sequences with comments showing uncertainty about some reset, compression, and snap-control bits. `write_vector` uses a zero request as sentinel, so a legitimate request zero could not be represented in those tables. `sd_start` logs an unexpected register read but continues after non-`0x0101` status, which may mask initialization failure. Packet scanning lacks short-packet validation for the 10-byte header. The control handler initializes capacity for five controls but registers only one, which is harmless but misleading.

## Test signals
Validate mode availability differs by subtype, init/open sequence success, expected `0x0101` status after open vectors, repeated stream starts after stop, raw frame boundaries from captures, brightness write bit-splitting, and disconnect/stop0 behavior with `present` false.
