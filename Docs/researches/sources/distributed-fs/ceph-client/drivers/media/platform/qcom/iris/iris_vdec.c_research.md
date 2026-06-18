# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_vdec.c

## Purpose
Implements decoder-specific V4L2 session initialization, format enumeration/try/set, event subscription, source-change notification, stream-on sequencing, buffer queueing, and decoder START/STOP command handling.

## Important APIs And Functions
- `iris_vdec_inst_init()` allocates source/capture formats, sets defaults, initializes buffer counts/sizes, copies decoder firmware caps, and initializes controls.
- `iris_vdec_formats_cap` exposes NV12 and QC08C capture formats.
- `find_format()` and `find_format_by_index()` search platform compressed input formats or local capture formats.
- `iris_vdec_enum_fmt()`, `iris_vdec_try_fmt()`, and `iris_vdec_s_fmt()` implement decoder format negotiation with alignment and colorimetry propagation.
- `iris_vdec_validate_format()` validates either compressed or raw decoder formats.
- `iris_vdec_subscribe_event()` supports EOS, source-change, and control events.
- `iris_vdec_src_change()` queues `V4L2_EVENT_SOURCE_CHANGE` for resolution changes.
- `iris_vdec_streamon_input()` sets input properties, allocates persistent buffers, creates/queues input-side internal buffers, and sends stream-on input.
- `iris_vdec_streamon_output()` sets capture config params, creates/queues output-side internal buffers, sends stream-on output, and unwinds with streamoff on error.
- `iris_vdec_qbuf()` converts vb2 buffer to Iris buffer, stores timestamp metadata for input, defers if queue is not streaming, scales power, and queues to firmware.
- `iris_vdec_start_cmd()` resumes after DRC or drain last-buffer state and clears sub-state bits.
- `iris_vdec_stop_cmd()` sends firmware drain and marks drain sub-state.

## Control Flow And Integration Points
`iris_vidc.c` dispatches decoder ioctls here. `iris_vb2.c` calls stream-on and qbuf helpers. HFI responses trigger source-change and completion behavior in other files. VPU buffer sizing is queried whenever formats or buffer counts change.

## State And Persistence Behavior
Allocates and owns `inst->fmt_src`/`fmt_dst` until close. Mutates `inst->codec`, crop, colorimetry, buffer sizes/counts, firmware caps copy, sub-state bits, last-buffer state, and timestamp metadata. Source-change and drain state persists until START command clears it.

## Dependencies
V4L2 events/mem2mem, Iris buffer/common/control/instance/power/VPU-buffer helpers, and HFI command ops.

## Risks
- `iris_vdec_inst_init()` allocates two format objects but does not check for allocation failure before dereferencing; unlike encoder init, this can fail unsafely under memory pressure.
- Width/height zero is accepted for bitstream input and replaced with defaults; clients must handle later source-change to real dimensions.
- Capture try-fmt clamps dimensions to source dimensions while source queue streams, affecting DRC behavior.
- Stream-on output error handling must avoid leaking internal buffers after partial creation.

## Test Signals
- V4L2 decode format enumeration and set/try format tests for compressed input and NV12/QC08C output.
- H.264/HEVC/VP9/AV1 decode stream-on, qbuf, source-change, drain STOP/START, and EOS event tests.
- Low-memory fault injection around `kzalloc_obj()` and internal buffer creation.
