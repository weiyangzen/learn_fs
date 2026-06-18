# sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.h

Purpose: Defines the AVS IPC ABI used by driver and firmware: packed request/reply/notification headers, TLVs, runtime parameter IDs, module UUIDs, audio formats, gateway/DMA configuration payloads, and function prototypes implemented by `messages.c`.

Important APIs/types: `union avs_global_msg`, `union avs_module_msg`, `union avs_reply_msg`, and `union avs_notify_msg` model 64-bit IPC headers. `struct avs_tlv` and `avs_tlv_size()` describe variable firmware configuration entries. `struct avs_fw_cfg`, `struct avs_hw_cfg`, `struct avs_mods_info`, `struct avs_module_entry`, and audio/module config structures describe returned and sent payloads. Runtime parameter sections define copier, peakvol, and probe IPCs.

Control flow role: This header is passive but central: callers use macros such as `AVS_GLOBAL_REQUEST()`, `AVS_MODULE_REQUEST()`, and `AVS_NOTIFICATION()` to initialize bitfields consistently, then send those headers through DSP IPC helpers. Firmware replies are interpreted through the same packed overlays.

State and persistence: No state is stored here. The packed structs are persistent ABI contracts with many `static_assert()` size checks, which protect against compiler/layout drift.

Dependencies and integration: Included by topology/path/PCM/probe/control layers that need module UUIDs, audio formats, and runtime payload definitions. It also declares functions consumed throughout the AVS driver.

Risks: Bitfield layout and packed structs are firmware ABI-sensitive. Any compiler, endianness, or field-width change can break IPC. Flexible-array payloads require strict size validation by callers. `union avs_segment_flags` repeats the member name `type` in this snapshot, which is a source-level build hazard. Many runtime payload sizes are asserted, so changing nested structs can cascade.

Test signals: Build-time `static_assert()` coverage, sparse/clang checks for packed bitfields, ABI tests that compare header encodings to firmware specs, and fault-injection of malformed TLV lengths and module counts.
