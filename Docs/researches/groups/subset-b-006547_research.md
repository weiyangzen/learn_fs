<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-control.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-control.c

## Purpose
IPC4 ALSA kcontrol implementation for SOF. It translates mixer, switch, enum, bytes, and extended bytes control operations into IPC4 module large-config set/get messages, keeps the kernel-side control cache coherent with firmware, and handles firmware-originated ALSA control update notifications.

## APIs, Types, and Functions
The exported integration object is `tplg_ipc4_control_ops`. Key helpers are `sof_ipc4_set_get_kcontrol_data()`, `sof_ipc4_set_volume_data()`, `sof_ipc4_set_generic_control_data()`, `sof_ipc4_set_get_bytes_data()`, bytes TLV handlers `sof_ipc4_bytes_ext_put()` and `_sof_ipc4_bytes_ext_get()`, `sof_ipc4_control_update()`, `sof_ipc4_widget_kcontrol_setup()`, and `sof_ipc4_set_up_volume_table()`. The code consumes `struct sof_ipc4_control_data`, `struct sof_ipc4_control_msg_payload`, `struct sof_ipc4_gain_params`, and `struct sof_abi_hdr` definitions from `ipc4-topology.h`.

## Control Flow, State, and Persistence
Runtime `put` callbacks update `scontrol->ipc_control_data` first, then send IPC only when the component is runtime-active. The common IPC helper locates the owning widget by `comp_id`, locks or asserts the widget setup mutex, patches the module instance id into the message template, and skips firmware access when the widget is not set up. Volume controls send either one all-channel gain payload or one payload per channel. Switch and enum controls use generic `{id,num_elems,chanv}` payloads. Bytes controls either use generic raw parameter payloads or the IPC4 bytes-control wrapper with ABI header, size checks, and dirty-cache refresh. Extended bytes put keeps `old_ipc_control_data` as a rollback copy and restores it if firmware rejects the new payload. Firmware notifications search the active widget and control by module id, instance id, parameter id, and control index, update cached values or mark the control dirty, then call `snd_ctl_notify_one()`.

## Dependencies and Integration
Depends on SOF component/control lists, runtime PM state, widget setup mutexes, IPC ops `set_get_data()`, topology-provided control metadata, ALSA TLV/user-copy APIs, and the IPC4 module notification format. `ipc4-topology.c` initializes the control data and embeds module ids once widget module information is known.

## Risks and Test Signals
Risks include stale cached values when firmware changes a control but the follow-up refresh fails, user TLV size or ABI-header mistakes, rollback relying on a valid previous bytes payload, skipped firmware writes while suspended, and duplicated widget lookup logic by `comp_id`. Test signals are mixer/switch/enum read-write round trips, extended bytes invalid magic/oversize tests, runtime-suspended put/get behavior, firmware notification delivery to user space, widget setup pushing defaults, and failure injection for rejected bytes payload rollback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-control.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-fw-reg.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-fw-reg.h

## Purpose
Defines the host-visible IPC4 firmware register memory layout used by the SOF driver for firmware status, ROM information, pipeline stream offsets, peak-volume telemetry, and link-position readings.

## APIs, Types, and Functions
This header has no functions. It defines `SOF_IPC4_INVALID_STREAM_POSITION`, register capacity constants, ABI version `SOF_IPC4_FW_REGS_ABI_VER`, ROM-info bit masks, and packed/aligned structures: `sof_ipc4_pipeline_registers`, `sof_ipc4_peak_volume_regs`, `sof_ipc4_llp_reading`, `sof_ipc4_llp_reading_extended`, `sof_ipc4_llp_reading_slot`, and top-level `sof_ipc4_fw_registers`.

## Control Flow, State, and Persistence
The structures describe shared memory populated by firmware and read by the kernel. `ipc4-pcm.c` reads `abi_ver` during PCM setup to decide whether delay reporting is supported, reads `pipeline_regs` for stream start/end offsets, and scans LLP slots to map a DAI gateway node id to its position counter. The invalid stream-position sentinel represents uninitialized stream statistics after reset or before first data movement.

## Dependencies and Integration
The layout relies on fixed IPC4 firmware ABI packing and 4-byte alignment. It integrates with SOF mailbox accessors, host/DAI copier node ids from topology, and PCM pointer/delay logic. The ROM status masks are available to platform code that reads `fw_status`, `lec`, `lnec`, or `rom_info`.

## Risks and Test Signals
The main risk is ABI drift between firmware and this host layout; a wrong offset corrupts delay math or status decoding. Capacity constants also cap the number of supported pipeline, peak-volume, GPDMA, SoundWire, EVAD, and core slots. Test signals are ABI version gating, correct mailbox offsets from `offsetof()`, valid stream offsets after playback, LLP slot node-id matching for HDA/GPDMA/SoundWire/EVAD paths, and graceful fallback when firmware reports an older ABI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-fw-reg.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-loader.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-mtrace.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-mtrace.c

## Purpose
Implements IPC4 firmware mtrace debug logging for CAVS 2 platforms. It enables firmware logs, maps per-core log slots from the debug window, exposes one debugfs file per core, supports log-priority mask tuning, updates log positions from firmware notifications, and drains logs on crash.

## APIs, Types, and Functions
The exported tracing ops object is `ipc4_mtrace_ops`. Cross-file API `sof_ipc4_mtrace_update_pos()` updates a core write pointer and wakes readers. Important internal functions are `ipc4_mtrace_init()`, `ipc4_mtrace_enable()`, `ipc4_mtrace_disable()`, `sof_mtrace_find_core_slots()`, `sof_ipc4_mtrace_dfs_open/read/release()`, priority-mask debugfs handlers, `ipc4_mtrace_fw_crashed()`, suspend and resume handlers. State is held in `struct sof_mtrace_priv`, `struct sof_mtrace_core_data`, and `struct sof_log_state_info`.

## Control Flow, State, and Persistence
Initialization checks firmware-reported log size and IPC4 mtrace type, allocates per-core state, seeds timer periods and base firmware log priorities, sends system time for log alignment, enables logs with `SOF_IPC4_FW_PARAM_ENABLE_LOGS`, scans debug-slot descriptors, and creates debugfs nodes. Each core debugfs file is exclusive-open, allocates a temporary read buffer, waits on a waitqueue for `host_read_ptr != dsp_write_ptr`, reads circular log data from the mailbox debug slot, prefixes the user buffer with available byte count, writes the new host read pointer back to firmware, and advances local state only while enabled. Position updates read the DSP write pointer from the core slot, align it to 4 bytes, and wake readers; early updates are delayed until slot discovery.

## Dependencies and Integration
Depends on SOF debug box layout, IPC4 debug-slot constants, SOF mailbox read/write, debugfs, wait queues, runtime tracing hooks, and firmware configuration parsed by `ipc4-loader.c`. It integrates with crash handling because a crashed DSP may stop sending log-buffer notifications.

## Risks and Test Signals
Risks include debug-window layout mismatch, lost log data on circular-buffer wrap, reads returning 0 while slot discovery is delayed, unchecked disable IPC result, priority masks changed while tracing is active, and tracing disabled silently to avoid blocking audio stack bring-up. Test signals are debugfs `mtrace/coreN` open/read/release behavior, logs waking after position notifications, crash-time drain, suspend disable/resume enable, invalid core update rejection, priority mask parse errors, and operation with unsupported mtrace type or zero log bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-mtrace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-pcm.c

## Purpose
IPC4 PCM runtime operations for SOF. It controls pipeline state transitions for PCM triggers, handles special ChainDMA streams, performs DAI link hardware-parameter fixups, allocates per-stream pipeline/time state, and computes PCM pointer plus delay from host counters and firmware register windows.

## APIs, Types, and Functions
The exported ops object is `ipc4_pcm_ops`; `sof_ipc4_set_pipeline_state()` is exported for direct pipeline state changes. Important helpers include `sof_ipc4_set_multi_pipeline_state()`, trigger-list ordering helpers, `sof_ipc4_chain_dma_trigger()`, `sof_ipc4_trigger_pipelines()`, DAI fixup helpers, `sof_ipc4_pcm_setup/free()`, `sof_ipc4_build_time_info()`, `sof_ipc4_pcm_hw_params()`, `sof_ipc4_get_stream_start_offset()`, `sof_ipc4_pcm_pointer()`, and `sof_ipc4_pcm_delay()`. Local state lives in `sof_ipc4_pcm_stream_priv` and `sof_ipc4_timestamp_info`.

## Control Flow, State, and Persistence
PCM trigger commands map to IPC4 RUNNING or PAUSED; `hw_free` maps to RESET. For normal pipelines, the code builds a priority-sorted trigger list while holding `pipeline_state_mutex`, sends an intermediate PAUSED transition when required, then sends final RUNNING/PAUSED/RESET via single-pipeline or multi-pipeline IPC. It updates `started_count`, `paused_count`, and each `sof_ipc4_pipeline.state` only for pipelines actually triggered. ChainDMA bypasses module pipeline triggering and constructs a global ChainDMA IPC from host/link DMA ids, allocation/enable bits, SCS, and fifo size; stream-private `chain_dma_allocated` prevents duplicate reset. PCM setup allocates per-direction pipeline lists sized by firmware `max_num_pipelines` and enables playback delay reporting only when firmware register ABI and host byte-counter callbacks are available.

## Dependencies and Integration
Depends on ASoC PCM callbacks, SOF IPC send paths, topology-created pipeline lists and copier data, platform stream tags, host/DAI counter ops, `ipc4-fw-reg.h` shared-memory layout, and DAI link hw_config records for SSP fixup. It is the runtime consumer of topology format decisions and firmware register telemetry.

## Risks and Test Signals
Risks include incorrect trigger order around forks, started/paused reference-count drift after failed IPC, ChainDMA requiring both host and link pipelines to be marked consistently, DAI fixup ambiguity when topology exposes multiple rates/channels, delay errors from invalid stream offsets or counter wrap, and fallback to `-EOPNOTSUPP` disabling precise pointer reporting. Test signals are start/pause/release/stop/hw_free sequences, multi-pipeline priority ordering, xrun/suspend reset behavior, ChainDMA allocation/pause/reset on playback and capture, SSP hw_config selection, ABI-gated delay support, pointer wrap tests, and mixed-rate DAI-to-host frame conversion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-priv.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-priv.h

## Purpose
Private IPC4 integration header for the SOF core. It defines IPC4-specific firmware/library/module state, fixed mailbox/debug window indices, mtrace capability enum, shared operation tables, and cross-file helper prototypes.

## APIs, Types, and Functions
Defines `enum sof_ipc4_mtrace_type`, `struct sof_ipc4_fw_module`, `struct sof_ipc4_fw_library`, and `struct sof_ipc4_fw_data`. It declares operation tables `ipc4_loader_ops`, `ipc4_tplg_ops`, `tplg_ipc4_control_ops`, `ipc4_pcm_ops`, and `ipc4_mtrace_ops`, plus helpers for pipeline state, mtrace position, split release completion, firmware configuration query, library reload, module lookup by UUID, active widget lookup by module/instance ids, CPC update, debug slot lookup by type, mic privacy change, and pipeline-state string formatting.

## Control Flow, State, and Persistence
`sof_ipc4_fw_data` is the persistent per-device IPC4 state stored in `sdev->private`. It carries the firmware manifest header offset, xarray of loaded firmware libraries, optional NHLT data, mtrace type and log size, playback/capture DMA counts, maximum pipeline/library counts, context-save and library-restore flags, platform library-loading and mic-privacy callbacks, and `pipeline_state_mutex` used by runtime trigger and pipeline deletion paths.

## Dependencies and Integration
Includes Linux IDR/IDA and IPC4 manifest/header definitions, plus SOF private state. All implementation files in this subset include it to share state and exported ops. Platform-specific SOF code fills callback fields and capability values before IPC4 loader, topology, PCM, and tracing code consume them.

## Risks and Test Signals
Risks are mostly contract drift: a field updated by platform code may be assumed initialized by topology/PCM/tracing, `fw_lib_xa` lifetime must outlive module-private pointers, and `pipeline_state_mutex` must cover every path that mutates pipeline ref counts or firmware state. Test signals are full IPC4 probe/boot, library xarray lifecycle, suspend/resume with context save, mtrace capability gating, concurrent trigger serialization, and build coverage for all declared cross-file helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.c

## Purpose
Exposes IPC4 firmware exception telemetry through debugfs. It locates the telemetry debug slot, maps the exception payload in the mailbox BAR, and provides a read-only `exception` file for crash/debug collection.

## APIs, Types, and Functions
The public entry point is `sof_ipc4_create_exception_debugfs_node()`. Internal helpers are `sof_ipc4_query_exception_address()` and `sof_telemetry_entry_read()`, with `sof_telemetry_fops` backing the debugfs file.

## Control Flow, State, and Persistence
Node creation allocates a `snd_sof_dfsentry`, marks it as always-accessible IOMEM, records a size of one debug slot minus the leading separator word, links it into `sdev->dfsentry_list`, and creates `debugfs/exception`. Reads validate position and count, locate the telemetry slot via `sof_ipc4_find_debug_slot_offset_by_type()`, skip the first separator magic word, copy the slot contents from I/O memory into a temporary kernel buffer, copy the requested range to user space, and advance `ppos`.

## Dependencies and Integration
Depends on debugfs, SOF debug entry bookkeeping, BAR/mailbox mapping in `sdev->bar[sdev->mailbox_bar]`, IPC4 debug-slot constants, and the debug-slot search helper declared in `ipc4-priv.h`. The binary layout of the payload is defined by `ipc4-telemetry.h`.

## Risks and Test Signals
Risks include missing telemetry slot descriptors, invalid BAR mapping, stale exception data after reboot/crash recovery, and allocating a full slot-sized buffer for every read. Test signals are debugfs node creation, correct zero-length behavior past EOF, successful reads after firmware exception, `-EFAULT` when no telemetry slot exists, and binary dump parsing against the coredump header structures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.h

## Purpose
Defines the IPC4 exception telemetry/coredump binary headers used by firmware and the debugfs telemetry reader.

## APIs, Types, and Functions
Declares `enum sof_ipc4_coredump_tgt_code`, coredump magic/header constants, Xtensa-specific constants, packed `struct sof_ipc4_coredump_hdr`, packed `struct sof_ipc4_coredump_arch_hdr`, packed/flexible `struct sof_ipc4_telemetry_slot_data`, and the prototype `sof_ipc4_create_exception_debugfs_node()`.

## Control Flow, State, and Persistence
The header has no executable control flow. It defines the persistent crash-slot layout: a separator word, generic coredump header with target, pointer size, flags and reason, architecture-specific block header, and variable architecture data. Firmware writes this into a telemetry debug slot, while `ipc4-telemetry.c` exposes it as a raw debugfs binary range after skipping the first separator word.

## Dependencies and Integration
Used by IPC4 telemetry code and any decoder that consumes the debugfs `exception` binary. The Xtensa constants identify Intel ADSP/Zephyr/XCC dump format details expected in `arch_data`.

## Risks and Test Signals
Risks include packed-structure ABI drift, endian/width assumptions in external parsers, and new target architectures needing enum/header extensions. Test signals are compile-time layout compatibility, parsing real Xtensa exception dumps, validation of `ZE` and `A` identifiers, and graceful decoder behavior for unknown target codes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-telemetry.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.c

## Purpose
IPC4 topology implementation for SOF. It parses IPC4 topology tokens, creates per-widget IPC configuration objects, maps topology widgets to firmware modules, prepares runtime audio formats and gateway blobs, creates/deletes module and pipeline instances, binds/unbinds routes, configures DAIs, parses topology manifest data, and publishes the IPC4 topology ops table.

## APIs, Types, and Functions
The exported object is `ipc4_tplg_ops`; public helpers are `sof_ipc4_find_swidget_by_ids()` and `sof_ipc4_copier_is_single_bitdepth()`. Major function groups include token parsers and debug printers, audio-format selectors (`sof_ipc4_get_audio_fmt()`, `sof_ipc4_init_input_audio_fmt()`, `sof_ipc4_init_output_audio_fmt()`), widget setup/free functions for pipeline, copier, DAI, PGA, mixer, SRC, ASRC and process modules, prepare functions for each module class, control loaders, `sof_ipc4_widget_setup/free()`, queue-id and route setup/free helpers, `sof_ipc4_dai_config()`, `sof_ipc4_parse_manifest()`, `sof_ipc4_dai_get_param()`, and `sof_ipc4_link_setup()`.

## Control Flow, State, and Persistence
Topology loading parses token arrays into widget-private IPC4 structures and resolves each widget UUID to a firmware module from the loader. Pipeline widgets store scheduling priority, core, low-power, direction and ChainDMA flags; non-ChainDMA pipelines are assigned runtime pipeline IDs when created. Copiers carry base config, available input/output pin formats, gateway config, DAI type/index, DMA TLVs and optional ALH aggregation data. Runtime prepare selects formats from topology against FE/pipeline params, queries NHLT blobs for SSP/DMIC/ALH when available, computes gateway DMA buffer sizes, constructs IPC payloads, updates pipeline memory usage and CPC from manifests, and appends DP-domain extended init objects. Widget setup assigns module instance IDs, fills pipeline IDs and parameter sizes, sends `MOD_INIT_INSTANCE` or create-pipeline IPCs, and frees IDA allocations on failure. Route setup allocates source/destination queue IDs, optionally programs copier sink format for nonzero source pins, then sends bind IPC; free sends unbind across pipeline boundaries and releases queue IDs.

## Dependencies and Integration
Depends on SOF topology token machinery, ASoC DAPM widgets/routes/DAI links, IPC4 headers, firmware module manifests from `ipc4-loader.c`, NHLT ACPI helpers when enabled, platform DAI data, ALSA hw_params helpers, SOF PCM stream pipeline lists, and IPC control ops from `ipc4-control.c`. It is the central producer of private data consumed by IPC4 PCM, controls, and runtime DAI configuration.

## Risks and Test Signals
Risks include incomplete or inconsistent topology tokens, UUIDs missing from firmware manifests, assumptions that pin-0 input/output formats are paired by index, limited multi-format support in SRC and DAI fixups, ALH group ID exhaustion or incorrect channel masks, ChainDMA requiring matching pipeline attributes, memory/CPC estimates drifting from firmware object sizes, and route queue ID leaks on bind failure. Test signals are topology load for every supported widget type, module instance ID allocation/free, format negotiation for playback/capture and conversion pipelines, NHLT blob fallback paths, ALH aggregation, ChainDMA card component marking, DP-domain extended init payloads, route bind/unbind with multiple pins, DAI config on hw_params/hw_free, manifest NHLT parsing, and suspend teardown through `sof_pcm_free_all_streams()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.h

## Purpose
Private IPC4 topology data contract for SOF. It defines the module, pipeline, copier, control, gain, mixer, SRC, ASRC, process, DMA, gateway, audio format, queue, and ChainDMA structures shared by IPC4 topology, controls, and PCM code.

## APIs, Types, and Functions
Defines constants for firmware pages/object sizes, module type bits, sample types, node IDs, gain volume, DMA limits, ChainDMA sentinel IDs and buffer sizes, ALH multi-gateway ranges, and IPC4 control parameter IDs. Important types include `sof_ipc4_pipeline`, `ipc4_pipeline_set_state_data`, `sof_ipc4_pin_format`, `sof_ipc4_available_audio_format`, `sof_copier_gateway_cfg`, `sof_ipc4_copier_data`, `sof_ipc4_copier`, DMA config/TLV structs, `sof_ipc4_control_data`, `sof_ipc4_control_msg_payload`, `sof_ipc4_gain(_data/_params)`, `sof_ipc4_mixer`, `sof_ipc4_src`, `sof_ipc4_asrc`, `sof_ipc4_base_module_cfg_ext`, and `sof_ipc4_process`. It declares `sof_ipc4_copier_is_single_bitdepth()`.

## Control Flow, State, and Persistence
The header has no logic, but its structs are persistent runtime state. Topology setup allocates these as `swidget->private`, DAI private data, or `scontrol->ipc_control_data`; PCM trigger code reads pipeline state and ChainDMA fields; controls read/write control payloads; route setup uses pin counts, node ids and gateway formats; prepare/unprepare paths allocate and free IPC payload buffers referenced by copier/process records.

## Dependencies and Integration
Includes IPC4 base headers and is included by `ipc4-topology.c`, `ipc4-control.c`, and `ipc4-pcm.c`. It ties topology token parsing to firmware IPC payload layouts, ASoC DAPM widget types, SOF firmware manifest metadata, and firmware register/pipeline runtime behavior.

## Risks and Test Signals
Risks include ABI-sensitive packing, flexible-array sizing mistakes, bitfield/node-id macro misuse, object-size constants diverging from firmware memory accounting, and ownership confusion around pointers such as `copier_config`, `ipc_config_data`, and pin-format arrays. Test signals are `struct_size()` allocation checks, KASAN/KMEMLEAK during topology load/unload, route setup with multi-pin modules, ChainDMA and normal copier paths, firmware accepting generated IPC payloads, and build coverage when IPC4 header definitions change.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/ipc4-topology.h -->
