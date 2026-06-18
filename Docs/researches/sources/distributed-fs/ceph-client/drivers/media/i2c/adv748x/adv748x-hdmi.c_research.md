<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-hdmi.c

## Purpose
`adv748x-hdmi.c` implements the ADV748x HDMI receiver/component processor V4L2 subdevice. It supports HDMI signal detection, DV timings query/set/enumeration, RGB888 source format reporting, EDID storage/programming into the repeater/EDID page, picture controls, test patterns, and stream-time power control of the selected CSI-2 transmitter.

## Important APIs, Types, and Functions
- `adv748x_hdmi_timings_cap` and `adv748x_hdmi_video_standards[]` define supported CEA/DMT timings and hardware `VID_STD`/frequency codes.
- `adv748x_hdmi_query_dv_timings()` reads measured HDMI timing registers and pixel clock.
- `adv748x_hdmi_s_dv_timings()` validates timings, programs CP/IO timing registers, updates interlace bits, and caches timings.
- `adv748x_hdmi_set_edid()` caches up to four EDID blocks, writes them in SMBus-sized chunks, updates aspect ratio, and enables/disables repeater EDID.
- `adv748x_hdmi_get_format()` returns RGB888 format from cached timings and propagates pixel rate to the remote TX.
- Controls write CP brightness, contrast, saturation, hue, and pattern generator registers.

## Control Flow
Init seeds default 1280x720p30 timings, sets default 16:9 aspect ratio, initializes the subdevice, sink/source pads, and controls. Timing query returns cached timings when the pattern generator is enabled, otherwise requires signal lock, reads timing registers, fills optional V4L2 fields, and updates cached timings. Streaming locks the parent and powers the selected TX on/off, then logs HDMI lock status.

## State and Persistence
Cached `timings`, `format`, `aspect_ratio`, EDID buffer/presence/block count, selected `tx`, controls, and pads live in memory. EDID is also written into device EDID memory/repeater registers but is not persistent across reset/remove. Timings are updated by set/query and drive format dimensions and pixel rate.

## Dependencies and Integration Points
This file depends on parent regmap helpers, V4L2 DV timings helpers, HDMI/CEA timing definitions, V4L2 EDID pad ops, media links to TXA, and the shared parent mutex. It integrates as the HDMI source feeding TXA in the media graph.

## Risks
- No interrupt handling exists for cable/timing changes; comments note timings should be updated on IRQ in the future.
- `adv748x_hdmi_check_dv_timings()` loops until `stds[i].timings.bt.width` but the standards array has no explicit zero sentinel, risking out-of-bounds reads.
- Pixel-rate propagation ignores the return from `adv748x_hdmi_query_dv_timings()`, so no-signal cases can push stale/zero timing data.
- EDID set validates block count but not EDID CRC/header.
- Stream power requires `hdmi->tx` to be set by media links.

## Test Signals
Test DV timings set/query for every table entry, invalid/out-of-range timings, no-signal `-ENOLINK`, interlaced height handling, format reporting and pixel-rate propagation, EDID set/get/clear with 0-4 blocks and over-limit `-E2BIG`, test pattern query behavior, HDMI-to-TXA stream on/off, and media graph link switching away from HDMI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/i2c/adv748x/adv748x-hdmi.c -->
