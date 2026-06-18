## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/venc_ipi_msg.h

Purpose: defines the encoder AP-to-VPU/SCP IPI message ABI for init, set-param, encode, and deinit commands plus firmware acknowledgements.

Important APIs/types/functions: message IDs start at `0xC000` for AP commands and `0xD000` for firmware replies. AP structs include init, set-param, extended set-param, encode, extended encode, 34-bit extended encode, and deinit formats. Reply structs include common, init, set-param, encode, and deinit formats. `enum venc_ipi_msg_enc_state` reports frame/partial/skip/error encode states.

Control flow: init sends AP instance pointer and receives remote VPU instance address plus ABI version. Set-param sends the remote instance address, parameter ID, and optional data words. Encode sends bitstream mode, input plane addresses, output bitstream address/size, and optional frame-info data. Firmware replies update status and, for encode, state, keyframe flag, and bitstream size.

State and persistence behavior: the init reply establishes `vpu_inst_addr` stored in `venc_vpu_inst`. Encode replies update transient per-frame state consumed by H.264/VP8 backends.

Dependencies and integration points: consumed by `venc_vpu_if.c` and codec backends. It must match 32-bit VPU firmware layout while allowing 64-bit AP pointers and 34-bit IOVA variants for newer SoCs.

Risks: struct padding and field widths are ABI-sensitive. The base encode message uses 32-bit DMA addresses, so 34-bit SoCs must take the explicit `_ext_34` path. Extended data arrays have fixed capacity and callers must keep `data_item` consistent with firmware expectations.

Test signals: IPI encode on legacy VPU, SCP extended firmware, and 34-bit IOVA SoCs; skip-frame ack handling; invalid status handling; build layout review when changing any struct.
