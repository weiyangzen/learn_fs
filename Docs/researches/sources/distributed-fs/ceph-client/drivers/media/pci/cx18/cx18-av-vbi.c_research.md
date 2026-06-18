# sources/distributed-fs/ceph-client/drivers/media/pci/cx18/cx18-av-vbi.c

## Purpose
This file implements A/V decoder VBI subdev operations. It configures raw VBI and sliced VBI capture registers, reports the current sliced VBI service layout, and decodes VIP ancillary data lines into V4L2 sliced VBI records.

## Important APIs, Types, and Functions
Entry points are `cx18_av_g_sliced_fmt()`, `cx18_av_s_raw_fmt()`, `cx18_av_s_sliced_fmt()`, and `cx18_av_decode_vbi_line()`. `struct vbi_anc_data` describes the ancillary payload layout from the decoder. `decode_vps()` converts biphase-coded VPS bytes. The file maps hardware line-control nibbles to V4L2 services for teletext, WSS, closed captions, and VPS.

## Control Flow
Format getters read decoder line-control registers and translate them into V4L2 `service_lines`. Raw mode runs `cx18_av_std_setup()`, writes the slicer delay, and sets output control for raw active VBI. Sliced mode also runs standard setup, selects ancillary data output, clears impossible service lines for PAL/NTSC, programs `CXADEC_VBI_LINE_CTRL*`, and adjusts VBI timing. Decode flow validates the ancillary preamble and DID, converts slicer line numbers with `slicer_line_offset`, maps SDID to V4L2 service type, validates parity for captions, and decodes VPS when needed.

## State and Persistence
State is split between decoder registers and `cx18_av_state` VBI timing fields. The requested service lines live in hardware until reconfigured. Decoded VBI data is per-line transient and handed to upper VBI code.

## Dependencies and Integration Points
It depends on `cx18_av_std_setup()`, decoder MMIO helpers, Linux bit/parity helpers, and V4L2 subdev VBI operations. It integrates with `cx18-ioctl.c` sliced/raw format ioctls and with higher-level VBI processing that inserts sliced data into MPEG private streams or exposes sliced VBI to userspace.

## Risks and Edge Cases
The code assumes a VIP ancillary layout and ignores lines with bad preambles or unsupported SDIDs. PAL and NTSC legal line ranges differ and are forcibly cleared. Slicer line delay/offset must match `cx18_av_std_setup()` or data will be attributed to the wrong field line. VPS decoding mutates the payload buffer in place.

## Test Signals
Exercise `VIDIOC_G/S_FMT` for raw and sliced VBI, confirm service-line sanitization for 525/625 standards, capture closed captions and WSS/VPS, and verify malformed ancillary data produces zero type/line rather than corrupt output.
