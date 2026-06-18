# sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.c

Purpose: Implements Intel AVS firmware IPC helpers. It converts driver requests into packed global/module IPC headers from `messages.h`, attaches mailbox payloads, calls the lower-level DSP send routines, and decodes returned TLV/config data.

Important APIs/functions: boot and code-load helpers (`avs_ipc_set_boot_config`, `avs_ipc_load_modules`, `avs_ipc_unload_modules`, `avs_ipc_load_library`); pipeline/module lifecycle helpers (`avs_ipc_create_pipeline`, `avs_ipc_delete_pipeline`, `avs_ipc_set_pipeline_state`, `avs_ipc_init_instance`, bind/unbind/delete); large-config helpers for firmware/module parameters; config readers/writers (`avs_ipc_get_fw_config`, `avs_ipc_set_fw_config`, `avs_ipc_get_hw_config`, `avs_ipc_get_modules_info`); runtime controls for copier sink format, peak volume/mute, logs, system time, and debug probe points.

Control flow: Most functions fill a `union avs_global_msg` or `union avs_module_msg`, then send it through `avs_dsp_send_msg`, `avs_dsp_send_msg_timeout`, `avs_dsp_send_pm_msg`, or ROM-specific send helpers. `avs_ipc_set_large_config()` fragments requests by `AVS_MAILBOX_SIZE`, marking initial/final blocks and using the initial offset field as total payload size. `avs_ipc_get_large_config()` allocates a mailbox-sized reply, sends one request, then shrinks the buffer to the reply size.

State and persistence: The file does not own durable state; it updates caller-owned structs such as `avs_fw_cfg`, `avs_hw_cfg`, returned module tables, and returned runtime parameter buffers. Returned payloads from get helpers are heap-owned by callers except internal config readers, which free their temporary payloads.

Dependencies and integration: Depends on `avs_dev`, IPC send primitives from the DSP core, firmware mailbox layout from `messages.h`, `avs_get_module_id()` for probe module lookup, kernel allocation helpers, and optional `CONFIG_DEBUG_FS` for log/probe IPC.

Risks: TLV parsing assumes firmware-provided lengths are sane and advances by `sizeof(*tlv) + tlv->length` without full per-TLV bounds checks. Zero-size module-info payload returns `-EREMOTEIO` without freeing `payload`. The local snapshot contains duplicated source lines in `avs_ipc_peakvol_set_volumes()` and duplicated comment text near unbind, which are build/review signals. Large-config get currently handles only one reply buffer and relies on lower IPC code/firmware to provide final data. Varargs in `avs_ipc_set_fw_config()` require exact type/length/value triples.

Test signals: Exercise IPC header bit packing, large-config fragmentation at 0, 1, exactly 4096, and >4096 bytes, TLV decode with unknown/zero/malformed entries, module-info ownership/freeing, and debugfs probe attach/detach paths. Kernel build should catch the duplicated-line corruption in this snapshot.
