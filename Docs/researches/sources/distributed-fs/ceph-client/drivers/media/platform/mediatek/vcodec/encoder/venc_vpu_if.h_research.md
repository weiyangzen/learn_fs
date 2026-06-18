## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.h

Purpose: declares the host-side encoder VPU instance and the VPU command API used by H.264 and VP8 backends.

Important APIs/types/functions: `struct venc_vpu_inst` contains waitqueue, signaling/failure fields, last encode state, bitstream size, keyframe flag, remote instance address, mapped VSI pointer, IPI ID, and V4L2 encoder context. Prototypes cover init, set-param, encode, and deinit.

Control flow: codec backends embed `venc_vpu_inst`, set context and IPI ID, call init, exchange configuration through `vsi`, send parameters/encode commands through this API, and deinit during backend teardown.

State and persistence behavior: one instance persists for the codec backend lifetime. Last encode reply fields are overwritten on each encode ack and consumed immediately by backend code.

Dependencies and integration points: includes `venc_drv_if.h` for shared parameter/frame structures. It is the public internal boundary between codec-specific backends and the IPI implementation.

Risks: `signaled`/waitqueue fields are present but explicit waiting is delegated to the firmware IPI send abstraction; future changes must avoid double-waiting. `bs_size` is an int while ABI field is u32, so very large values would truncate on unusual firmware responses.

Test signals: backend initialization checking non-null `vsi`, encode reply propagation to `venc_done_result`, and deinit when init partially failed.
