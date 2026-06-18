<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/kinect.c -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/kinect.c

Purpose: `kinect.c` is a GSPCA driver for Microsoft Kinect camera interfaces, supporting either video or depth operation selected by the `depth_mode` module parameter. It programs the device through vendor control commands and parses Kinect stream packet headers.

Important APIs, types, and functions: `struct sd` stores command tag, stream flag, and command buffers. `struct pkt_hdr` describes stream packets; `struct cam_hdr` describes control command/reply framing. `send_cmd()` builds tagged control messages, validates replies, and increments `cam_tag`. `write_register()` wraps command `0x03`. `sd_config_video()` and `sd_config_depth()` choose mode tables, endpoint `0x81` or `0x82`, and stream flags. `sd_pkt_scan()` validates `RB` packet magic and maps flags to FIRST/INTER/LAST.

Control flow: probe chooses video or depth descriptor based on `depth_mode`. Start functions write register sequences for video or depth stream configuration. Video mode supports Bayer, UYVY, and Y10B variants; depth mode exposes 640x480 Y10B-packed. Packets carry a header whose flag identifies start, middle, or end using `stream_flag | {1,2,5}`.

State and persistence: `cam_tag` persists across control commands for reply matching. `stream_flag` identifies the active stream type. No V4L2 controls are exposed.

Dependencies and integration points: depends on GSPCA isochronous endpoint selection, V4L2 custom pixel formats, USB vendor control transfers, and Kinect firmware command protocol.

Risks: `send_cmd()` loops while reads return zero with no explicit retry limit. It returns `-1` for several protocol errors rather than specific errno values. `sd_pkt_scan()` silently ignores packets shorter than the header. Test signals include successful command/reply tag matching, valid video and depth frames, correct endpoint selection, and reliable stream reset on stop.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/kinect.c -->
