## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.h

Purpose: declares the host-side decoder VPU instance and command API used by codec-specific decoder backends.

Important APIs/types/functions: `struct vdec_vpu_inst` records IPI IDs, shared VSI pointer, firmware failure status, legacy remote address, ABI version, ABI v2 instance ID, signal flag, decoder context, waitqueue, IPI handler, codec/capture type, and frame-buffer sizes. Public commands cover init, start, end, deinit, reset, core/core-end, and get-param.

Control flow: codec backends allocate or embed `vdec_vpu_inst`, fill IDs/context/codec type, call `vpu_dec_init`, exchange data through `vpu->vsi`, then issue start/end/reset/get-param commands as frames are decoded. LAT/core codecs additionally call `vpu_dec_core` and `vpu_dec_core_end`.

State and persistence behavior: one `vdec_vpu_inst` persists per decoder instance and is the anchor for remote firmware state. It stores both AP-visible status and firmware-visible identity. `fb_sz` is populated by get-param acknowledgements and consumed by picture-info query paths.

Dependencies and integration points: depends on `struct mtk_vcodec_dec_ctx` and the common firmware IPI handler type. It is included by decoder backends and the VPU interface implementation.

Risks: callers must not use `vsi` before successful init or after deinit. ABI version and instance ID rules differ between old VPU firmware and newer SCP firmware. The waitqueue/signal fields can imply asynchronous waiting, but actual synchronization is in the firmware abstraction.

Test signals: backend init/deinit tests should assert `vsi` validity and `ctx->vpu_inst` setup; ABI v2 tests should confirm commands use `inst_id`; get-param tests should confirm `fb_sz` is updated before picture-info consumers read it.
