<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/uvc.c -->
# sources/distributed-fs/ceph-client/drivers/media/common/uvc.c

## Purpose
`uvc.c` provides common USB Video Class format GUID to V4L2 pixel-format mapping. It lets UVC drivers convert 16-byte UVC format GUIDs from descriptors into kernel fourcc values.

## Important APIs, Types, and Functions
The static `uvc_fmts[]` table maps many `UVC_GUID_FORMAT_*` constants to `V4L2_PIX_FMT_*` values, including YUYV variants, NV12, MJPEG, planar YUV, greyscale/depth, Bayer patterns, RGB/BGR, H.264, HEVC, Intel RealSense formats, and compressed/confidence formats. The exported function is `uvc_format_by_guid(const u8 guid[16])`.

## Control Flow
Callers pass a 16-byte GUID. `uvc_format_by_guid()` linearly scans `uvc_fmts[]`, compares each GUID with `memcmp()`, and returns the matching descriptor pointer or `NULL` when unsupported.

## State and Persistence Behavior
The mapping table is static read-only module state. No runtime mutation or persistence exists.

## Dependencies and Integration Points
The file depends on Linux UVC GUID definitions, V4L2 pixel formats, and module/export infrastructure. It exports `uvc_format_by_guid()` GPL-only for UVC-related drivers.

## Risks and Test Signals
The search is linear but the table is small. Unsupported or vendor-new GUIDs return `NULL`; callers must handle that. Duplicate equivalent mappings, such as YUY2 variants and HEVC/H265 aliases, are intentional. Test signals include descriptor parsing tests for representative GUIDs, NULL behavior for unknown GUIDs, and build coverage when UVC GUID constants evolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/common/uvc.c -->
