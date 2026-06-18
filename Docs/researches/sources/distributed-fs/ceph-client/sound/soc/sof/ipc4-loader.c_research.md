# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-loader.c

## Purpose
IPC4 firmware loader support for SOF. It parses IPC4 extended manifests, records base firmware and library module metadata, supports split-release and UUID-triggered library loading, queries firmware/hardware configuration, reloads libraries after context loss, and derives module CPC values from manifest entries.

## APIs, Types, and Functions
The exported loader ops object is `ipc4_loader_ops` with `.validate` and `.parse_ext_manifest`. Other cross-file APIs are `sof_ipc4_complete_split_release()`, `sof_ipc4_find_module_by_uuid()`, `sof_ipc4_query_fw_configuration()`, `sof_ipc4_reload_fw_libraries()`, and `sof_ipc4_update_cpc_from_manifest()`. Internal helpers include `sof_ipc4_fw_parse_ext_man()`, `sof_ipc4_load_library()`, and `sof_ipc4_load_library_by_uuid()`.

## Control Flow, State, and Persistence
Base firmware parsing validates the extended manifest magic, uses `manifest_fw_hdr_offset`, reads the IPC4 firmware binary header, stores the base firmware version in `sdev->fw_version`, allocates module records, copies manifest module entries, attaches module configuration tables, initializes each module instance IDA, and inserts the base library as xarray id 0. Library loading requests firmware files, parses them the same way, fixes module ids by embedding the library id at bit 12, calls the platform `load_library()` callback, and inserts the result into `ipc4_data->fw_lib_xa`. Split releases try optional `openmodules` and `debug` `.ri` siblings. UUID lookup searches loaded libraries, loads an external UUID-named `.bin` when allowed, and re-searches. Firmware configuration queries populate `mtrace_log_bytes`, `max_libs_count`, `max_num_pipelines`, `fw_context_save`, `libraries_restored`, and optional Intel mic privacy capabilities.

## Dependencies and Integration
Depends on Linux firmware loading, xarray, IDA, IPC4 manifest structs, SOF IPC `set_get_data()`, platform library loaders, tracepoints, and topology code that looks up modules by UUID and updates base config CPC. `ipc4-priv.h` defines the persistent `sof_ipc4_fw_data`, library, and module records.

## Risks and Test Signals
Risks include malformed manifest bounds, missing `manifest_fw_hdr_offset`, optional split libraries silently absent, max-library off-by-one behavior in UUID lookup, stale library reload after context loss, and CPC fallback when manifest IBS/OBS entries are incomplete. Test signals are parse failures for short/bad firmware, basefw version exposure, module UUID lookup across base and external libraries, split-release optional loading, firmware configuration tuple parsing, library reload after suspend/resume, and CPC selection for matching and nonmatching IBS/OBS.
