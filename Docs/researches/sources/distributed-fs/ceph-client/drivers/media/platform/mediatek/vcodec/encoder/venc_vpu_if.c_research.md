## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_vpu_if.c

Purpose: implements encoder firmware IPI transport for MediaTek vcodec. It registers the encoder IPI handler, validates AP instances, maps firmware VSI memory, sends set-param/encode/deinit messages, and caches encode reply state.

Important APIs/types/functions: exported functions are `vpu_enc_init`, `vpu_enc_set_param`, `vpu_enc_encode`, and `vpu_enc_deinit`. Key helpers include `vpu_enc_ipi_handler`, `handle_enc_init_msg`, `handle_enc_encode_msg`, `vpu_enc_send_msg`, crop/MB calculation helpers, and separate 32-bit/34-bit encode message builders.

Control flow: init registers an IPI handler for the backend-selected ID, sends AP init, and expects an init ack to set `inst_addr` and map `vsi`. Set-param builds base or extended messages; for initial encoder config on extended firmware it sends crop-right, crop-bottom, and macroblock count. Encode validates 16-byte DMA alignment for input planes, chooses 34-bit or 32-bit message format from SoC pdata, includes output bitstream address/size and optional frame info, sends the message, then leaves reply data in `vpu->state`, `bs_size`, and `is_key_frm`. Deinit sends remote instance address.

State and persistence behavior: `venc_vpu_inst` persists per codec instance and stores remote instance address, mapped VSI, last failure, last encode state/size/keyframe, IPI ID, and context. `ctx->vpu_inst` is set for liveness validation against `ctx_list`.

Dependencies and integration points: depends on firmware abstraction, encoder context list locking, ABI structs from `venc_ipi_msg.h`, dispatch structures from `venc_drv_if.h`, and SoC pdata macros for extended and 34-bit paths.

Risks: `vpu_enc_send_msg` treats any firmware failure as `-EINVAL`, losing specific error detail. IPI handler uses firmware-provided AP pointer and must validate it before dereference-sensitive operations. All input planes are checked for 16-byte alignment, including plane slots that may be unused in some formats but are initialized by frontend buffer construction. ABI version support currently accepts only version 1 for non-VPU firmware.

Test signals: init/deinit with stale or invalid AP instance acks, extended set-param values for crop and macroblock count, 16-byte alignment rejection, 34-bit encode messages on MT8188-like pdata, skip/error encode states, and firmware timeout/failure injection.
