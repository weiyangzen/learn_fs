<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/dtcs033.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/dtcs033.c

Purpose: `dtcs033.c` is a compact GSPCA subdriver for the Scopium DTCS033 astro camera (`0547:7303`). It exposes two 640x480 modes from the same bulk stream: `V4L2_PIX_FMT_GREY` for raw monochrome-looking Bayer bytes and `V4L2_PIX_FMT_SRGGB8` for consumers that want the Bayer pattern declared. The driver uses one bulk URB sized as `640 * 512`, then strips the first and last sixteen sensor lines to deliver a 640x480 frame.

Important APIs, types, and functions: `struct dtcs033_usb_requests` encodes vendor control requests used by `reg_reqs()`. `reg_rw()` sends a vendor control message through `usb_rcvctrlpipe()` even for request types that include `USB_DIR_OUT`; this follows the local source but is a point to inspect if control writes fail on hardware. `sd_config()` sets bulk transport fields in `struct cam`; `dtcs033_pkt_scan()` is the frame parser; `dtcs033_setexposure()` maps V4L2 exposure and gain controls into two vendor request writes; `dtcs033_init_controls()` creates an exposure/gain cluster.

Control flow: probe calls `gspca_dev_probe()`, which calls `sd_config()`, `sd_init()`, and control initialization. Stream start replays the large `dtcs033_start_reqs` table. Each full-size bulk packet is treated as a complete sensor readout: `FIRST_PACKET`, one `INTER_PACKET` with cropped data, then `LAST_PACKET`. Stream stop replays `dtcs033_stop_reqs`.

State and persistence: only V4L2 control values are retained in `struct sd`; the hardware state is rewritten on stream start and when controls change during streaming. `gspca_dev->usb_err` short-circuits subsequent control requests.

Dependencies and integration points: depends on `gspca.h`, V4L2 controls, USB bulk transfer setup in `gspca.c`, and the shared GSPCA frame assembly contract.

Risks: strict packet length checking discards any short transfer; all capture correctness depends on fixed 512-line bulk packets. Gain/exposure conversions use integer arithmetic and assume the UI ranges enforced by V4L2. The control helper does not validate returned byte counts. Test signals include successful probe, start request completion, stable 640x480 payload size, no `frame overflow`, and observable exposure/gain changes while streaming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/dtcs033.c -->
