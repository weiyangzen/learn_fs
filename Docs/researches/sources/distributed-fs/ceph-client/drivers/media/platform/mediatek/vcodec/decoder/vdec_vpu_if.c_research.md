## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/decoder/vdec_vpu_if.c

Purpose: implements decoder firmware/VPU communication for MediaTek vcodec backends. It registers IPI handlers, sends decoder commands, maps firmware VSI memory, validates AP instance pointers, and caches firmware-returned state.

Important APIs/types/functions: exported functions are `vpu_dec_init`, `vpu_dec_start`, `vpu_dec_get_param`, `vpu_dec_core`, `vpu_dec_end`, `vpu_dec_core_end`, `vpu_dec_deinit`, and `vpu_dec_reset`. Key internal handlers are `vpu_dec_ipi_handler`, `handle_init_ack_msg`, `handle_get_param_msg_ack`, `vcodec_vpu_send_msg`, and `vcodec_send_ap_ipi`.

Control flow: init sets the waitqueue, stores the AP `vdec_vpu_inst` on the decoder context, registers the IPI handler for LAT and optionally core IDs, sends init, and expects the handler to map remote VSI memory. Generic command sending chooses LAT or core IPI ID for LAT single-core architecture, fills legacy address or ABI v2 instance ID, sends via `mtk_vcodec_fw_ipi_send`, and returns firmware status. The interrupt-context handler validates that the AP instance still belongs to a live decoder context and that the message ID is in range, handles init/get-param acks, stores failure status, and marks the instance signaled.

State and persistence behavior: `struct vdec_vpu_inst` retains remote VSI pointer, remote instance address, firmware ABI version, instance ID, failure status, codec type, and framebuffer sizes. The handler writes these fields asynchronously during IPI callbacks. The context’s `vpu_inst` pointer is used as a liveness guard.

Dependencies and integration points: depends on `mtk_vcodec_fw_*` abstraction for VPU/SCP transport, decoder context lists guarded by `dev_ctx_lock`, message layouts from `vdec_ipi_msg.h`, and codec backends that copy data into mapped VSI memory before sending commands.

Risks: `signaled` and `wq` are initialized but this layer relies on synchronous `mtk_vcodec_fw_ipi_send` semantics rather than explicitly waiting here. AP instance pointers arrive from firmware, so liveness validation is critical. Unsupported ABI versions set failure but callers must propagate it. Core/LAT IPI routing depends on accurate platform architecture flags.

Test signals: firmware init with VPU and SCP transports, ABI v1/v2 handling, invalid ACK ID and stale AP instance injection, get-param picture info updates, core command routing on LAT single-core hardware, and timeout/failure propagation from `mtk_vcodec_fw_ipi_send`.
