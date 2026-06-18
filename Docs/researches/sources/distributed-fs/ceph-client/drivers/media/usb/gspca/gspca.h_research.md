<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.h -->
## sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.h

Purpose: `gspca.h` defines the public contract between the GSPCA core and individual USB camera subdrivers.

Important APIs, types, and functions: debug levels and `gspca_dbg/gspca_err` wrap V4L2 logging. `struct cam` describes mode tables, bulk/isoc transport, endpoint constraints, bandwidth behavior, and framerate tables. `struct sd_desc` lists mandatory and optional subdriver callbacks. `enum gspca_packet_type` defines frame assembly events. `struct gspca_buffer` wraps vb2 buffers, while `struct gspca_dev` holds the complete per-device core state. The header declares probe/disconnect, frame assembly, PM, and autogain helper APIs.

Control flow: subdrivers embed `struct gspca_dev` as their first field, fill an `sd_desc`, and pass both to `gspca_dev_probe()`. During streaming, subdriver `pkt_scan` callbacks translate USB payloads into `gspca_frame_add()` calls using the packet type enum.

State and persistence: all persistent runtime state is in `struct gspca_dev`: USB device, V4L2 device, controls, URBs, current image assembly fields, queue/list locks, mode, sequence, endpoint, altsetting, present/streaming flags, and optional input state.

Dependencies and integration points: includes Linux module/kernel/USB, V4L2, videobuf2, controls, and mutex APIs. It is included by every researched subdriver.

Risks: struct layout comments are contractual; `struct gspca_dev` must be first in subdriver structs because casts rely on it. Callback omissions are handled selectively, so mandatory operations must be present. Test signals are compile-time type compatibility and runtime probe/streaming through representative subdrivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/usb/gspca/gspca.h -->
