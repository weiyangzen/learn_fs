# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_venc.c

## Purpose
Implements encoder-specific V4L2 session initialization, raw/compressed format negotiation, crop selection, frame-rate parameters, event subscription, stream-on sequencing, buffer queueing, and encoder START/STOP drain handling.

## Important APIs And Functions
- `iris_venc_inst_init()` allocates formats, sets default H.264 capture and NV12 output, initializes crop/rates/scaling fields, copies encoder firmware caps, and initializes controls.
- `iris_venc_formats_cap` exposes H.264 and HEVC compressed capture formats.
- `iris_venc_formats_out` exposes NV12 and QC08C raw input formats.
- `iris_venc_enum_fmt()`, `iris_venc_try_fmt()`, and `iris_venc_s_fmt()` implement format negotiation.
- `iris_venc_s_fmt_input()` aligns raw input, propagates colorimetry, updates crop and scaling defaults, and refreshes output format if dimensions changed.
- `iris_venc_s_fmt_output()` sets compressed codec, bitstream dimensions, optional scaling dimensions, output buffer size, and colorimetry.
- `iris_venc_validate_format()` checks raw or compressed formats.
- `iris_venc_subscribe_event()` supports EOS and control events.
- `iris_venc_s_selection()` implements output crop and updates encoded output dimensions.
- `iris_venc_s_param()`/`iris_venc_g_param()` set/get operating rate and frame rate with cap and core-throughput checks.
- `iris_venc_streamon_input()` and `iris_venc_streamon_output()` set firmware properties, allocate ARP persistent buffers, create/queue internal buffers, and send stream-on.
- `iris_venc_qbuf()` converts and queues buffers, with timestamp metadata on raw input and deferred behavior before queue streaming.
- `iris_venc_start_cmd()` resumes after drain-last and clears drain/pause sub-states.
- `iris_venc_stop_cmd()` sends firmware drain, sets drain sub-state, and scales power.

## Control Flow And Integration Points
Generic V4L2 ioctls in `iris_vidc.c` dispatch encoder operations here. vb2 stream/qbuf paths call encoder helpers from `iris_vb2.c`. Control setters use `inst->fw_caps` copied from platform gen1/gen2 data. VPU buffer sizing uses encoder dimensions, scaling, rotation, codec, and rate-control state.

## State And Persistence Behavior
Owns `inst->fmt_src`, `fmt_dst`, codec, crop, `operating_rate`, `frame_rate`, raw/scaled encoder dimensions, buffer counts/sizes, firmware caps, and drain sub-states. Format and parameter changes persist until changed or instance close.

## Dependencies
Depends on V4L2 events/mem2mem, Iris buffer/common/control/instance/power/VPU-buffer helpers, HFI command ops, and platform caps.

## Risks
- Output format helper name (`iris_venc_s_fmt_output`) refers to V4L2 capture/compressed output; caller context must avoid confusing raw output plane terminology.
- Scaling is inferred when compressed dimensions differ from raw input dimensions and affects VPSS buffer allocation.
- Frame-rate changes while streaming run aggregate core MBPF/MBPS checks; failure resets only the changed rate to default.
- Stream-on output allocates ARP buffers too; repeated or partial error paths need leak coverage.

## Test Signals
- H.264/HEVC encode format negotiation for NV12/QC08C input.
- Crop and scaling tests verify output bitstream dimensions and VPSS allocation.
- `VIDIOC_S_PARM`/`G_PARM` for operating/frame rate and max-rate rejection.
- Drain STOP/START sequence with EOS/LAST behavior.
