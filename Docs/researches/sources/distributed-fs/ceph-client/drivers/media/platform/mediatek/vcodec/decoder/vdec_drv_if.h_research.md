## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_drv_if.h

Purpose: declares the decoder interface used by generic V4L2 decoder code and codec-specific backends. It also defines frame-buffer status values and parameter-query types shared across decoder implementations.

Important APIs/types/functions: `enum vdec_fb_status` marks normal/display/free buffer states. `enum vdec_get_param_type` includes display/free frame buffer, picture info, crop info, and DPB size queries. `struct vdec_fb_node` links `vdec_fb` instances into state lists. The header declares all backend `vdec_common_if` instances and public dispatcher functions.

Control flow: this file has no implementation flow, but its declarations define the expected sequence: `vdec_if_init` after format selection, repeated `vdec_if_decode`, optional `vdec_if_get_param`, and `vdec_if_deinit` during teardown. Passing `bs == NULL` to decode is documented as flush/end-of-stream behavior.

State and persistence behavior: state is represented by caller-owned `mtk_vcodec_dec_ctx`, backend-owned `drv_handle`, and frame-buffer lists using `vdec_fb_node`. Query comments explicitly state that returned display/free buffers are not owned by the caller and remain valid only until decoder deinit.

Dependencies and integration points: includes `mtk_vcodec_dec.h`, depends on `struct vdec_common_if` from the base header for backend symbols, and is consumed by decoder frontend, codec backends, and VPU interface code.

Risks: ownership comments are important because misuse of returned frame buffers can cause use-after-free or double-free in frontend code. Extending `enum vdec_get_param_type` requires updating all backend switch statements and decoder firmware parameter paths. The `bs == NULL` flush convention must remain consistent across all implementations.

Test signals: compile-time coverage for all declared backend symbols; runtime tests for parameter queries and flush behavior per codec; static analysis for switch exhaustiveness after enum changes.
