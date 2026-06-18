# sources/distributed-fs/ceph-client/drivers/media/pci/ivtv/ivtv-vbi.c

## Purpose
This file implements ivtv Vertical Blanking Interval support. It converts raw and sliced VBI capture data, packages sliced VBI for MPEG insertion, decodes reinsertion data from MPEG streams, accepts sliced VBI output data from userspace, and schedules WSS/VPS/closed-caption updates to the video encoder.

## Important APIs, Types, and Functions
Public functions are `ivtv_write_vbi_from_user`, `ivtv_process_vbi_data`, `ivtv_disable_cc`, and `ivtv_vbi_work_handler`. Internal helpers handle VPS/CC/WSS output, parity checks, sliced-line ingestion, MPEG private-stream packaging, ivtv VBI private-format conversion, raw/sliced buffer compression, and passthrough VBI polling.

## Control Flow
Capture-side processing byteswaps hardware buffers, compresses raw SAV-framed lines or decodes sliced VBI lines through the video subdevice, stores at least one sliced record, and optionally builds MPEG insertion packets. Decoder VBI reinsertion byteswaps and converts ivtv private VBI blocks into V4L2 sliced data, then writes the data to output state. The work handler runs outside hard IRQ to push pending WSS, CC, or VPS changes, or in passthrough mode to poll input VBI and mirror it to SAA7127 output.

## State and Persistence Behavior
The file mutates `itv->vbi` payload buffers, frame counters, sliced MPEG ring entries, WSS/VPS/CC payloads and missing counters, and update bits in `itv->i_flags`. Output VBI state persists in the SAA7127 subdevice until changed or disabled.

## Dependencies and Integration Points
It depends on V4L2 sliced VBI formats, video-subdevice `decode_vbi_line` and `g_vbi_data`, SAA7127 VBI output calls, ivtv queue buffer swapping, ioctl service conversion helpers, IRQ deferred work, and stream VBI setup.

## Risks
VBI line numbering differs by standard and field; off-by-one errors break captions/WSS/VPS. The MPEG private format has alignment and linemask special cases. Passthrough missing counters can intentionally keep or clear stale VBI. Buffer byteswapping assumes 4-byte alignment except for the handled decoder offset case.

## Test Signals
Test raw VBI capture, sliced VBI capture in PAL and NTSC, closed caption parity, MPEG VBI insertion/extraction round trips, sliced VBI output from userspace, passthrough WSS/CC mirroring, CC disable, and VBI behavior during stream start/stop.
