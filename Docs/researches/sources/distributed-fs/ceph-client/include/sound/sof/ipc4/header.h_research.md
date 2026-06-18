<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/ipc4/header.h -->
# sources/distributed-fs/ceph-client/include/sound/sof/ipc4/header.h

## Purpose

`sources/distributed-fs/ceph-client/include/sound/sof/ipc4/header.h` is SOF IPC4 ABI header defining
the 64-bit message header split, global and module message IDs, pipeline/module bitfield encoders,
audio-format descriptors, firmware configuration tuples, notifications, and extended module
initialization payloads. The source was read as a complete 666-line header for this report.

## Important APIs, Types, and Functions

types: `sof_ipc4_msg`, `sof_ipc4_tuple`, `sof_ipc4_audio_format`, `sof_ipc4_base_module_cfg`,
`sof_ipc4_fw_version`, `sof_ipc4_dx_state_info`, `sof_ipc4_intel_mic_privacy_cap`,
`sof_ipc4_notify_resource_data`, `sof_ipc4_notify_module_data`, `sof_ipc4_module_init_ext_init`,
`sof_ipc4_module_init_ext_object`, `sof_ipc4_mod_init_ext_dp_memory_data`; enums:
`sof_ipc4_msg_target`, `sof_ipc4_global_msg`, `sof_ipc4_msg_dir`, `sof_ipc4_pipeline_state`,
`sof_ipc4_channel_config`, `sof_ipc4_interleaved_style`, `sof_ipc4_sample_type`,
`sof_ipc4_module_type`, `sof_ipc4_base_fw_params`, `sof_ipc4_fw_config_params`,
`sof_ipc4_hw_config_params`, `sof_ipc4_notification_type`, `sof_ipc4_mod_init_ext_obj_id`;
macros/constants: `__INCLUDE_SOUND_SOF_IPC4_HEADER_H__`, `SOF_IPC4_MSG_MAX_SIZE`,
`SOF_IPC4_MSG_TARGET_SHIFT`, `SOF_IPC4_MSG_TARGET_MASK`, `SOF_IPC4_MSG_TARGET`,
`SOF_IPC4_MSG_IS_MODULE_MSG`, `SOF_IPC4_MSG_DIR_SHIFT`, `SOF_IPC4_MSG_DIR_MASK`, `SOF_IPC4_MSG_DIR`,
`SOF_IPC4_MSG_TYPE_SHIFT`, `SOF_IPC4_MSG_TYPE_MASK`, `SOF_IPC4_MSG_TYPE_SET`,
`SOF_IPC4_MSG_TYPE_GET`, `SOF_IPC4_GLB_PIPE_INSTANCE_SHIFT`, and 141 more

## Control Flow

The host builds `sof_ipc4_msg` primary and extension words with target, direction, type, IDs,
payload sizes, and module or pipeline parameters. Firmware replies reuse the same top bits with
status in the low field; asynchronous firmware notifications are decoded by notification type and
optional module/resource payloads.

## State and Persistence Behavior

No state is owned here; the layouts are mailbox ABI contracts. State represented by these structures
includes pipeline IDs/states, module IDs/instances, debug slot descriptors, firmware configuration
values, module initialization objects, and optional payload pointers held by callers.

## Dependencies and Integration Points

Direct includes: `linux/types.h`, `uapi/sound/sof/abi.h`. Integrates with the SOF Linux driver,
topology parser, mailbox IPC transport, and matching DSP firmware ABI.

## Risks and Edge Cases

Risks are ABI bitfield drift, payload size truncation, endian and packing assumptions, incorrect use
of first/last block flags for large configs, message type/target confusion, notification parsing
that trusts event sizes, and the `SOF_IPC4_MOD_EXT_EXTENDED_INIT` macro referencing an inconsistent
shift token.

## Test Signals

Test encode/decode of every global and module message family, pipeline create/state messages, large
config chunking, notification routing, debug slot parsing, firmware config tuple reads, mic privacy
capability payloads, and 32/64-bit builds for packed layout sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sof/ipc4/header.h -->
