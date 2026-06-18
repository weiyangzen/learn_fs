<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_defs.h -->
# sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_defs.h

Purpose: defines common firmware command/message IDs, IRQ codes, memory-resource types, start-code types, firmware event payload structs, and bitrate constants.

Important APIs/types: `enum MSG_TYPE` is mailbox boot/command signaling; IRQ constants describe boot/snapshot/sync events; command IDs and message IDs provide driver-normalized firmware operations/events. Payload structs include `vpu_pkt_mem_req_data`, `vpu_enc_pic_info`, `vpu_dec_codec_info`, `vpu_dec_pic_info`, `vpu_fs_info`, and `vpu_ts_info`.

Control/state behavior: no code executes here, but the structs are the cross-file data contract for command packing/unpacking, V4L2 event generation, buffer completion, memory-resource allocation, and timestamp submission.

Dependencies and integration: consumed by command, message, encoder, decoder, Windsor/Malone iface, helpers, and debug code. It relies on V4L2 constants and `VIDEO_MAX_PLANES` through include context.

Risks: spelling `VPU_ENC_MEMORY_RESOURSE` is harmless but persistent. Any change to IDs or payload layout must be reflected in firmware-specific mapping arrays. Firmware-provided sizes and counts influence DMA allocations and buffer payloads, so validation at consumers is critical.

Test signals: compile-time use across all Amphion objects, firmware ABI compatibility tests for each message/command, and runtime validation of decoded sequence metadata, memory requests, encoded frame info, and EOS timestamp behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/platform/amphion/vpu_defs.h -->
