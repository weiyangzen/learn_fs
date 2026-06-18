# sources/distributed-fs/ceph-client/drivers/media/platform/st/sti/hva/hva-h264.c

Purpose: implements HVA H.264 encoding backend descriptors for NV12 and NV21 input, including firmware/hardware task descriptor construction, codec-private buffer allocation, slice/SEI/filler NAL handling, and task execution.

Important APIs and functions: exports `nv12h264enc` and `nv21h264enc`. Key functions are `hva_h264_open`, `hva_h264_close`, `hva_h264_encode`, `hva_h264_prepare_task`, `hva_h264_fill_slice_header`, `hva_h264_fill_sei_nal`, `hva_h264_fill_data_nal`, and helpers to read output size/stuffing from hardware post-output.

Control flow: open validates ESRAM capacity, allocates codec-private sequence info, reference frame, reconstructed frame, and task descriptor buffers. For each frame, prepare fills `hva_h264_td` with dimensions, GOP-derived picture type, BRC mode, entropy mode, bitrate/CPB clamping based on H.264 level/profile, framerate workaround for hardware BRC overflow, source/reference/output addresses, ESRAM subregions, slice header placement, SPS/PPS payload handling, optional SEI stereo info, and non-VCL size. Encode executes the task through `hva_hw_execute_task`, adds hardware-reported bitstream bytes to existing payload, appends filler NAL bytes if requested, increments stream count, and swaps reference/reconstructed buffers.

State and persistence: `struct hva_h264_ctx` stores allocated hardware buffers across frames for one encoder instance. `pctx->stream_num`, controls, error counters, and stream buffer metadata drive per-frame state. Reference/reconstructed frames persist between encodes until close.

Dependencies and integration points: depends on HVA core structures and controls from `hva.h`, DMA allocation helpers, hardware executor command `H264_ENC`, V4L2 H.264 controls, and the V4L2 front end that pre-fills SPS/PPS payloads in keyframe stream buffers.

Risks: task descriptor fields are a dense hardware ABI, and many addresses are truncated to `u32`, requiring 32-bit reachable DMA. Level indexing assumes V4L2 level enum values align with `h264_infos_list` order. The keyframe SPS/PPS check compares flags for exact equality to `V4L2_BUF_FLAG_KEYFRAME`, which may miss keyframes with additional flags. Framerate correction can divide by computed `td->framerate_num`; very low rates need validation. Only one slice is configured.

Test signals: encode NV12 and NV21 at supported sizes, IDR/P-frame GOP transitions, bitrate/CPB clamp behavior for each H.264 level/profile, CABAC/CAVLC, SPS/PPS payload length, optional SEI, buffer-size exhaustion, ESRAM-size rejection, and hardware error interrupts.
