# sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.c

Purpose: Provides AVS module metadata lookup, module instance ID allocation/freeing, firmware module-info refresh, and firmware request caching.

Important APIs/functions: `avs_get_module_entry()`, `avs_get_module_id_entry()`, `avs_get_module_id()`, `avs_is_module_ida_empty()`, `avs_module_info_init()`, `avs_module_info_free()`, `avs_module_id_alloc()`, `avs_module_id_free()`, `avs_request_firmware()`, `avs_release_last_firmware()`, and `avs_release_firmwares()`.

Control flow: Module lookup locks `modres_mutex`, scans `adev->mods_info`, copies entries, and unlocks. Module-info init obtains the firmware module table through IPC, reallocates/refreshes one `ida` per module, swaps `adev->mods_info`, and keeps instance allocation continuity unless purged. Firmware request first searches `adev->fw_list`, otherwise requests firmware, stores name/fw in a new list entry, and reuses it later.

State and persistence: Owns `adev->mods_info`, `adev->mod_idas`, and cached firmware entries on `adev->fw_list`. Firmware cache persists across runtime suspend/resume so files changing on disk do not affect loaded firmware.

Dependencies and integration: Uses IPC from `messages.c`, kernel IDA, firmware loader, list APIs, and locks in `avs_dev`. Consumed by path/probe/library loading code.

Risks: `avs_module_ida_alloc()` assumes non-purge refresh preserves ordering/count compatibility; if firmware reorders modules, reused IDA state could mismatch. `avs_release_last_firmware()` assumes the list is non-empty. `avs_ipc_get_modules_info()` zero-payload leak propagates here if it fails without freeing.

Test signals: Module table refresh with purge true/false, IDA exhaustion and free/reuse, invalid module ID paths, firmware cache hit/miss, request failure cleanup, and driver removal freeing all cached firmware.
