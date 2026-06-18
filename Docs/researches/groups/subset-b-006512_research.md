# subset-b-006512 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.c

Purpose: Implements Intel AVS firmware IPC helpers. It converts driver requests into packed global/module IPC headers from `messages.h`, attaches mailbox payloads, calls the lower-level DSP send routines, and decodes returned TLV/config data.

Important APIs/functions: boot and code-load helpers (`avs_ipc_set_boot_config`, `avs_ipc_load_modules`, `avs_ipc_unload_modules`, `avs_ipc_load_library`); pipeline/module lifecycle helpers (`avs_ipc_create_pipeline`, `avs_ipc_delete_pipeline`, `avs_ipc_set_pipeline_state`, `avs_ipc_init_instance`, bind/unbind/delete); large-config helpers for firmware/module parameters; config readers/writers (`avs_ipc_get_fw_config`, `avs_ipc_set_fw_config`, `avs_ipc_get_hw_config`, `avs_ipc_get_modules_info`); runtime controls for copier sink format, peak volume/mute, logs, system time, and debug probe points.

Control flow: Most functions fill a `union avs_global_msg` or `union avs_module_msg`, then send it through `avs_dsp_send_msg`, `avs_dsp_send_msg_timeout`, `avs_dsp_send_pm_msg`, or ROM-specific send helpers. `avs_ipc_set_large_config()` fragments requests by `AVS_MAILBOX_SIZE`, marking initial/final blocks and using the initial offset field as total payload size. `avs_ipc_get_large_config()` allocates a mailbox-sized reply, sends one request, then shrinks the buffer to the reply size.

State and persistence: The file does not own durable state; it updates caller-owned structs such as `avs_fw_cfg`, `avs_hw_cfg`, returned module tables, and returned runtime parameter buffers. Returned payloads from get helpers are heap-owned by callers except internal config readers, which free their temporary payloads.

Dependencies and integration: Depends on `avs_dev`, IPC send primitives from the DSP core, firmware mailbox layout from `messages.h`, `avs_get_module_id()` for probe module lookup, kernel allocation helpers, and optional `CONFIG_DEBUG_FS` for log/probe IPC.

Risks: TLV parsing assumes firmware-provided lengths are sane and advances by `sizeof(*tlv) + tlv->length` without full per-TLV bounds checks. Zero-size module-info payload returns `-EREMOTEIO` without freeing `payload`. The local snapshot contains duplicated source lines in `avs_ipc_peakvol_set_volumes()` and duplicated comment text near unbind, which are build/review signals. Large-config get currently handles only one reply buffer and relies on lower IPC code/firmware to provide final data. Varargs in `avs_ipc_set_fw_config()` require exact type/length/value triples.

Test signals: Exercise IPC header bit packing, large-config fragmentation at 0, 1, exactly 4096, and >4096 bytes, TLV decode with unknown/zero/malformed entries, module-info ownership/freeing, and debugfs probe attach/detach paths. Kernel build should catch the duplicated-line corruption in this snapshot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.h

Purpose: Defines the AVS IPC ABI used by driver and firmware: packed request/reply/notification headers, TLVs, runtime parameter IDs, module UUIDs, audio formats, gateway/DMA configuration payloads, and function prototypes implemented by `messages.c`.

Important APIs/types: `union avs_global_msg`, `union avs_module_msg`, `union avs_reply_msg`, and `union avs_notify_msg` model 64-bit IPC headers. `struct avs_tlv` and `avs_tlv_size()` describe variable firmware configuration entries. `struct avs_fw_cfg`, `struct avs_hw_cfg`, `struct avs_mods_info`, `struct avs_module_entry`, and audio/module config structures describe returned and sent payloads. Runtime parameter sections define copier, peakvol, and probe IPCs.

Control flow role: This header is passive but central: callers use macros such as `AVS_GLOBAL_REQUEST()`, `AVS_MODULE_REQUEST()`, and `AVS_NOTIFICATION()` to initialize bitfields consistently, then send those headers through DSP IPC helpers. Firmware replies are interpreted through the same packed overlays.

State and persistence: No state is stored here. The packed structs are persistent ABI contracts with many `static_assert()` size checks, which protect against compiler/layout drift.

Dependencies and integration: Included by topology/path/PCM/probe/control layers that need module UUIDs, audio formats, and runtime payload definitions. It also declares functions consumed throughout the AVS driver.

Risks: Bitfield layout and packed structs are firmware ABI-sensitive. Any compiler, endianness, or field-width change can break IPC. Flexible-array payloads require strict size validation by callers. `union avs_segment_flags` repeats the member name `type` in this snapshot, which is a source-level build hazard. Many runtime payload sizes are asserted, so changing nested structs can cascade.

Test signals: Build-time `static_assert()` coverage, sparse/clang checks for packed bitfields, ABI tests that compare header encodings to firmware specs, and fault-injection of malformed TLV lengths and module counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/messages.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/mtl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/mtl.c

Purpose: Provides Meteor Lake/ACE 1.x DSP operations for power, stall, IPC interrupt handling, and interrupt enable/disable.

Important APIs/functions: `avs_mtl_core_power()`, `avs_mtl_core_reset()`, `avs_mtl_core_stall()`, `avs_mtl_dsp_interrupt()`, and `avs_mtl_interrupt_control()`. Internal helpers power the DSP domain via HfDSSCS/HfPWRCTL and process IPC acknowledgements/responses through MTL host IPC registers.

Control flow: Power-on sets DSP domain SPA, waits for CPA, prevents power gating, waits for power-gate status, and assigns ownership to host. Power-off allows power gating, clears SPA, and waits CPA clear. IPC interrupt handling disables DONE/BUSY interrupts, completes host request acknowledgements, reads response primary/extension registers, calls `avs_dsp_process_response()`, acknowledges firmware, then reenables IPC control bits.

State and persistence: State lives in device registers and IPC completions. No persistent driver-owned objects are created.

Dependencies and integration: Uses `registers.h` MMIO helpers, `trace_avs_dsp_core_op()`, `avs_dsp_process_response()`, completion in `adev->ipc`, and platform ops tables elsewhere.

Risks: Register ordering is hardware-sensitive. Failure to restore HIPC control bits can wedge IPC. `avs_mtl_core_reset()` is a no-op because ACE 1.x lacks a logical equivalent, so reset assumptions must be platform-aware. Only main core mask is honored.

Test signals: Boot/resume on MTL hardware, IPC round-trip under interrupts, power-gating transitions, timeout paths from `readl_poll_timeout`, and tracepoint validation for core operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/mtl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.c

Purpose: Instantiates topology path templates into live DSP pipelines/modules/bindings, configures module-specific IPC payloads, manages conditional paths, and drives path state transitions.

Important APIs/functions: Public lifecycle/state functions are `avs_path_create()`, `avs_path_free()`, `avs_path_bind()`, `avs_path_unbind()`, `avs_path_reset()`, `avs_path_pause()`, `avs_path_run()`, and `avs_path_set_constraint()`. Runtime control helpers `avs_peakvol_set_volume()` and `avs_peakvol_set_mute()` bridge ALSA controls to firmware parameters. Internal module creators cover copier, WHM, peakvol/gain, mux, micsel, up/down mixer, SRC/ASRC, AEC, WoV, probe, base, and generic extended modules.

Control flow: Creation matches FE/BE hardware params to a topology variant, serializes with `path_mutex` and `comp_list_mutex`, creates pipelines, creates modules through GUID dispatch, sends initial configs, resolves bindings, arms internal bindings, appends the path to `adev->path_list`, then discovers conditional paths. Run/pause/reset walk pipelines in firmware-safe order and maintain `path->state`.

State and persistence: Live state is `struct avs_path` with pipeline/module/binding lists, conditional source/sink links, DMA ID, and current firmware state. Module instance IDs and gateway attributes are stored per module. Lists are protected by `path_mutex`, `comp_list_mutex`, and `path_list_lock` depending on scope.

Dependencies and integration: Consumes parsed topology structures, ACPI NHLT blobs, ALSA PCM params, firmware IPC helpers, module ID utilities, AVS controls, and platform attributes such as `ALTHDA`.

Risks: Error unwinding spans firmware-created pipelines/modules and driver lists. The local snapshot has duplicated lines in `avs_append_dma_cfg()` and duplicate `spin_lock()` in `avs_path_free_unlocked()`, both serious build/deadlock signals. Conditional path matching uses topology names/IDs and can fail silently if topology components are not registered in order. NHLT/default blob size and DWORD alignment are firmware-sensitive.

Test signals: DPCM playback/capture path create/free, all module GUID creator paths, conditional AEC reference paths, NHLT lookup failure/fallback, bind/unbind ordering, repeated trigger state transitions, and lockdep with concurrent FE/BE opens.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.h

Purpose: Declares the live AVS path object model and public path/control APIs used by PCM and control code.

Important APIs/types: `struct avs_path` owns path DMA ID, pipeline list, state, conditional path lists, source/sink pointers, topology template, owner device, and global list node. `struct avs_path_pipeline` stores firmware pipeline instance ID plus module/binding lists. `struct avs_path_module` stores firmware module ID/instance ID and gateway attributes. `struct avs_path_binding` stores resolved source/sink modules and pins. Public functions create/free paths, bind/unbind, reset/pause/run, set PCM constraints, and update peakvol controls.

Control flow role: PCM callbacks use this header to create paths in `hw_params`, prepare them to reset/pause, start them on trigger, and free them in `hw_free`/suspend. Control code can call peak volume/mute update helpers against live module objects.

State and persistence: Defines transient runtime state only. Topology pointers are borrowed and expected to outlive active paths.

Dependencies and integration: Includes `avs.h` and `topology.h`; depends on list heads, `avs_audio_format`/`avs_tplg_*` structures, and ALSA mixer control types.

Risks: Ownership is non-obvious because runtime structures hold borrowed topology pointers and firmware instance IDs. Incorrect list initialization or teardown can corrupt global path state. Conditional path fields share the same struct as normal paths, so code must distinguish spawned paths from standard PCM paths by context.

Test signals: Compile coverage for all users, KASAN/lockdep during repeated stream open/close, and control updates after path creation but before path free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/path.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.c

Purpose: Implements the ASoC PCM/component layer for AVS. It registers CPU DAIs for FE, HDA, DMIC, and I2S paths; maps ALSA DPCM callbacks to AVS path operations; configures HDA host/link streams; loads topology and libraries; and replays stream setup across suspend/resume.

Important APIs/functions: DAI callbacks include FE/non-HDA/HDA startup, shutdown, hw_params, hw_free, prepare, trigger, plus `avs_period_elapsed()`. Component callbacks include probe/remove/suspend/resume/open/pointer/mmap/pcm_new. Registration functions are `avs_register_component()`, `avs_register_dmic_component()`, `avs_register_i2s_component()`, and `avs_register_hda_component()`.

Control flow: Startup finds a path template through DAPM graph edges, allocates `avs_dma_data`, applies constraints, and assigns host or link streams. `hw_params` creates an `avs_path`, with FE paths also binding FE-to-BE. Prepare programs HDA stream format and resets/pauses the path. Triggers start/stop HDA streams and run/pause/reset AVS paths. Suspend frees FE paths first, then BE paths; resume recreates BE paths first, then FE paths, then prepares link before host.

State and persistence: `struct avs_dma_data` is stored as DAI DMA data per substream and carries template, live path, stream pointer, constraints, link, substream, and period work. Component probe creates `avs_tplg`, loads firmware topology, loads libraries, refreshes module info, and links the component into `adev->comp_list`.

Dependencies and integration: Integrates ALSA ASoC, HDA extended streams, topology parsing, path lifecycle, firmware/library loading, debugfs topology name, runtime PM, and platform attributes.

Risks: FE/BE ordering is critical; misordering can leak or double-bind paths. L1SEN toggling for single capture stream is hardware-sensitive. The local source snapshot contains duplicated/corrupted blocks and malformed-looking duplicated arguments/braces around prepare, topology debugfs/library code, buffer allocation, and DAI templates; a kernel build is the first required signal. Resume depends on saved position registers and may mark substreams disconnected on failure.

Test signals: Kernel build, DPCM playback/capture, HDA codec PCM enumeration, fallback topology loading, suspend/resume with active FE/BE streams, ignore_suspend low-power paths, pointer/DPIB behavior, XRUN prepare replay, and memory/error unwinding on topology/library load failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.h

Purpose: Minimal public PCM header exposing period-elapsed notification for AVS streams.

Important APIs/types: Declares `void avs_period_elapsed(struct snd_pcm_substream *substream);`.

Control flow role: Interrupt or stream code can call `avs_period_elapsed()` to schedule the work item that invokes `snd_pcm_period_elapsed()` from process context.

State and persistence: No state is declared here; state lives in `struct avs_dma_data` inside `pcm.c`.

Dependencies and integration: Includes `<sound/pcm.h>` for `struct snd_pcm_substream`. Used by AVS stream/interrupt code that needs to notify ALSA PCM.

Risks: Because only a function is exposed, callers must ensure the substream still has valid DAI DMA data and the work item has not been disabled during shutdown.

Test signals: Period interrupt/callback tests, stream shutdown race tests, and compile coverage for external users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/probes.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/probes.c

Purpose: Registers a compressed capture component for AVS probe extraction and manages the firmware probe module plus host HDA stream used to copy extracted samples to userspace.

Important APIs/functions: `avs_register_probe_component()` registers the component and DAI. Compressed callbacks include open/free/set_params/trigger/pointer/copy. Internal helpers initialize/delete the firmware probe module and fetch the assigned host stream.

Control flow: Open enforces a single extractor stream and assigns an HDA host stream. Set params allocates compressed pages, programs HDA format/setup, disables D0ix for active probing, initializes the probe module on first stream, and increments `num_probe_streams`. Trigger starts/stops the HDA stream under `bus->reg_lock`. Free disconnects probe points targeting the extractor node, deletes the probe module when the last stream closes, reenables D0ix, cleans up stream/pages, and clears `adev->extractor`.

State and persistence: Uses `adev->extractor` as singleton host stream, `adev->num_probe_streams` as lifetime count, stream private data, and firmware probe module instance zero.

Dependencies and integration: Depends on compressed ALSA APIs, HDA stream helpers, AVS debug/probe IPCs, module metadata lookup, D0ix control, and firmware probe UUID definitions.

Risks: Error paths in `set_params()` after page allocation or stream setup rely on later shutdown for cleanup. Copy returns `count - ret` on copy fault, which follows partial-copy semantics but deserves testing. Probe-point disconnection filters by vindex only. Singleton extraction prevents concurrent users.

Test signals: Compressed open/set_params/trigger/copy/free, concurrent open rejection, D0ix disable/enable balance, probe point connect/disconnect through debug tooling, and wraparound copy from ring buffer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/ptl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/ptl.c

Purpose: Supplies Panther Lake DSP operation table and power-domain handling, reusing most MTL/LNL/ICL helpers while switching to PTL-specific power-gating registers.

Important APIs/functions: Internal `avs_ptl_core_power_on()`, `avs_ptl_core_power_off()`, `avs_ptl_core_power()`, and exported `const struct avs_dsp_ops avs_ptl_dsp_ops`.

Control flow: Power-on sets DSP domain SPA, waits for CPA, prevents power gating through `MTL_REG_HfPWRCTL2`, waits for `MTL_REG_HfPWRSTS2`, and assigns host ownership. Power-off allows power gating through the PWRCTL2 path, clears SPA, and waits for CPA clear. The ops table delegates reset/interrupt/load/log/coredump/D0ix behavior to platform-compatible helpers.

State and persistence: State is hardware register state only.

Dependencies and integration: Uses MTL register definitions and helpers from `registers.h`, tracepoints, `avs_mtl_*` IPC interrupt controls, `avs_lnl_core_stall`, HDA firmware loading, ICL logging/D0ix helpers, and AVS ops dispatch in the parent device.

Risks: PTL shares MTL names for registers but uses PWRCTL2/PWRSTS2 for DSP HP power gating; incorrect register selection would break power transitions. Main-core masking means additional cores are ignored by this path.

Test signals: PTL boot and runtime PM transitions, firmware loading through HDA path, IPC interrupt handling via reused MTL code, and D0ix entry/exit on active/inactive streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/ptl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/registers.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/registers.h

Purpose: Centralizes AVS/HDA DSP register offsets, bit masks, SRAM window helpers, and typed MMIO read/write/update/poll macros.

Important APIs/types: Defines PCI power/clock-gating masks, generic ADSP core-control/status bits, IPC register layouts for SKL/CNL/MTL, MTL flag/power registers, SRAM base/window sizes for SKL/APL/MTL, firmware status/error windows, uplink/downlink windows, and `snd_hdac_adsp_*` accessors.

Control flow role: Platform files use these constants to power/stall/reset cores, handle IPC interrupts, load firmware, dump logs, and access SRAM mailboxes. Poll macros wrap kernel `read*_poll_timeout()` for hardware state waits.

State and persistence: No state is owned; macros compute addresses from `adev->dsp_ba` and platform specs.

Dependencies and integration: Includes kernel IO, polling, and size headers; expects `adev` to have `base.core`, `dsp_ba`, and `spec` with SRAM/HIPC metadata.

Risks: Register offsets are hardware ABI. Update macros are read-modify-write without locking; callers must serialize where required. Polling MMIO after device removal or power loss can return invalid values such as `UINT_MAX`, which callers often check inconsistently.

Test signals: Build coverage across all platform ops, hardware smoke tests for each supported generation, fault-injection for timeout paths, and sparse/static analysis for macro side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/registers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/skl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/skl.c

Purpose: Implements Skylake/cAVS 1.5 platform DSP operations, including IPC/CLDMA interrupts, debug log handling, coredump capture, and unsupported D0ix stubs.

Important APIs/functions: `avs_skl_ipc_interrupt()`, internal `avs_skl_dsp_interrupt()`, `avs_skl_enable_logs()`, `avs_skl_log_buffer_offset()`, `avs_skl_log_buffer_status()`, `avs_skl_coredump()`, and `const struct avs_dsp_ops avs_skl_dsp_ops`.

Control flow: DSP interrupt reads ADSPIS, dispatches CLDMA interrupts to the code loader and IPC interrupts to `avs_skl_ipc_interrupt()`. IPC handler clears HIPC control, completes host acknowledgements, reads HIPCT/HIPCTE responses, calls `avs_dsp_process_response()`, acknowledges firmware busy, and re-enables control bits. Log status reads firmware write pointer to dump the active half-buffer. Coredump copies firmware register SRAM to devcoredump.

State and persistence: Uses IPC completion state, CLDMA code-loader state, firmware log buffers in SRAM, and devcoredump artifacts. D0ix state is intentionally unsupported/no-op.

Dependencies and integration: Integrates `cldma.h`, `debug.h`, `messages.h`, `registers.h`, firmware logging helpers, and generic core power/reset/stall ops.

Risks: Half-buffer log selection assumes firmware write pointer semantics. Coredump copies a fixed 4 KiB firmware register window. D0ix no-op behavior must not be mistaken for real low-power support. Interrupt acknowledgement order is critical.

Test signals: SKL firmware load via CLDMA, IPC request/reply interrupts, CLDMA interrupt during module transfer, debug log wakeups, forced firmware exception coredumps, and D0ix policy callers on SKL.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/skl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/sysfs.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/sysfs.c

Purpose: Exposes AVS firmware version through a device sysfs attribute group.

Important APIs/functions: `fw_version_show()` formats `adev->fw_cfg.fw_version`; `DEVICE_ATTR_RO(fw_version)` declares the read-only attribute; `avs_attr_groups` exports the `avs/fw_version` group.

Control flow: Sysfs read converts the device to `avs_dev`, reads cached firmware version fields, and emits `major.minor.hotfix.build`.

State and persistence: Reads cached firmware config populated elsewhere through IPC. Does not allocate or mutate state.

Dependencies and integration: Depends on `avs.h`, Linux sysfs helpers, and parent device registration using `avs_attr_groups`.

Risks: If firmware config was not populated before sysfs exposure, users may see zeros or stale data. No locking is used around the cached config read; values are expected stable after firmware init.

Test signals: Sysfs presence under the AVS device, expected version after firmware boot, behavior before/after runtime suspend, and read formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/tgl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/tgl.c

Purpose: Defines Tiger Lake platform DSP operations, limiting generic core controls to the main core and configuring base firmware with crystal frequency and bus hardware ID.

Important APIs/functions: Main-core wrappers `avs_tgl_dsp_core_power()`, `avs_tgl_dsp_core_reset()`, `avs_tgl_dsp_core_stall()`, firmware config helpers `avs_tgl_set_xtal_freq()` and `avs_tgl_config_basefw()`, and `avs_tgl_dsp_ops`.

Control flow: Core wrappers mask to `AVS_MAIN_CORE_MASK` before calling generic operations. Base firmware config reads CPUID leaf 0x15 ECX when available and sends `AVS_FW_CFG_XTAL_FREQ_HZ`; then sends PCI device/subsystem/revision as `AVS_FW_CFG_BUS_HARDWARE_ID`.

State and persistence: Writes firmware runtime configuration; reads PCI IDs and CPU CPUID. No long-lived local state.

Dependencies and integration: Uses PCI device data from `adev->base.pci`, CPUID helpers, firmware config IPC, CNL interrupt handling, ICL firmware loading/logging/D0ix helpers, and HDA library/module transfer helpers.

Risks: CPUID frequency may be absent; code intentionally treats that as success. Hardware ID packing combines subsystem vendor/device into one word and is firmware ABI-sensitive. Only main core operations are forwarded.

Test signals: TGL boot firmware config IPCs, CPUID-present and CPUID-absent systems, PCI ID correctness, D0ix behavior, and firmware load/library/module transfer.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/tgl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.c

Purpose: Parses Intel AVS ASoC topology firmware into driver-owned topology dictionaries and path templates, wires topology callbacks into ASoC, loads/removes topology firmware, and attaches control/widget/link behavior.

Important APIs/functions: Token parsing framework (`avs_parse_tokens`, dictionary helpers, pointer parsers), manifest parser `avs_manifest()`, object parsers for libraries, audio formats, base/ext module configs, pin formats, pipeline configs, bindings, path/conditional path templates, initial configs, and NHLT configs. ASoC callbacks include route/widget/dai/link/control load handlers. Public functions are `avs_tplg_new()`, `avs_load_topology()`, and `avs_remove_topology()`.

Control flow: The manifest is parsed in a fixed dictionary order: header, libraries, audio formats, base configs, extended configs, pipeline configs, bindings, conditional path templates, optional initial configs, and optional NHLT configs. Widget load parses path templates from DAPM widget private data and stores the template in `w->priv`. DAI load assigns FE ops. Link load adjusts trigger ordering and merged format behavior. Controls parse private IDs and seed inverted values.

State and persistence: Parsed objects are devm-managed under the card device and stored in `struct avs_tplg`. Path templates are list-linked for later PCM lookup. Raw initial config and NHLT blobs are copied into managed allocations.

Dependencies and integration: Consumes UAPI AVS topology tokens, ALSA topology/DAPM/DAI/control APIs, machine data from `snd_soc_acpi_mach`, utility naming helpers, `control.h`, and structures from `topology.h`/`messages.h`.

Risks: Parser correctness depends on tuple order, entry boundary tokens, and little-endian size fields. The local snapshot contains duplicated lines in `modcfg_ext_parsers` and `parse_path_template()`, which are build/test signals. Several pointer parsers trust dictionary indices but require complete manifest ordering. Dynamic SSP/TDM name substitution only works for singular SSP/TDM machines. Raw data sections for initial/NHLT configs require precise length accounting.

Test signals: Load real topology files for HDA/DMIC/I2S, malformed tuple size/order fuzzing, singular and multi-SSP naming, conditional path parsing, controls with inverted defaults, NHLT blobs with raw payload, and build validation for duplicated-source corruption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.h

Purpose: Declares the parsed AVS topology object model shared by topology parsing, PCM path lookup, and path instantiation.

Important APIs/types: `struct avs_tplg` owns manifest metadata and dictionaries for libraries, audio formats, module configs, pipeline configs, bindings, conditional path templates, init configs, and NHLT configs. Other key types include `avs_tplg_modcfg_ext`, `avs_tplg_pplcfg`, `avs_tplg_binding`, `avs_tplg_path_template`, `avs_tplg_path`, `avs_tplg_pipeline`, and `avs_tplg_module`. Public APIs create/load/remove topology.

Control flow role: `topology.c` fills these structures from firmware topology; `pcm.c` discovers path templates from widgets; `path.c` traverses templates to create live pipelines/modules and configure firmware.

State and persistence: Parsed topology is managed for the lifetime of the ASoC card/component. Runtime paths borrow pointers into these structures, so topology must not be removed while paths are active.

Dependencies and integration: Includes list support and `messages.h` for audio format, UUID, DMA, and module configuration definitions. Expects ALSA component/widget forward declarations.

Risks: Many members are borrowed pointers into dictionary arrays, making load order and lifetime critical. Unioned extended config fields depend on module UUID interpretation. Conditional path templates carry cross-topology names/IDs that must match registered components.

Test signals: Compile users, topology load/unload, active stream during component removal prevention, path creation across every supported module type, and conditional path cross-topology matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/topology.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.c

Purpose: Defines AVS tracepoints and provides a helper to split IPC payloads into trace-safe chunks.

Important APIs/functions: `CREATE_TRACE_POINTS` instantiates events declared in `trace.h`. `trace_avs_msg_payload()` chunks arbitrary payloads by `MAX_CHUNK_SIZE` and emits `trace_avs_ipc_msg_payload()`.

Control flow: The helper loops over remaining bytes, emits each chunk with offset and total size, then advances until the full payload has been traced. `MAX_CHUNK_SIZE` is calculated to keep formatted hex dumps within a page-sized trace event budget.

State and persistence: No persistent state. Trace data is emitted into the kernel tracing subsystem.

Dependencies and integration: Depends on `trace.h`, kernel tracepoint infrastructure, `PAGE_SIZE`, and the AVS IPC tracing macros used by lower IPC code.

Risks: Payload tracing can be high-volume and may expose firmware/control payload data to trace readers. Chunk-size math depends on trace header overhead assumptions. Null data/zero size is filtered by the trace event condition.

Test signals: Enable tracepoints while sending IPC with no payload, small payload, and multi-page payload; verify offsets and total sizes in trace output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.h

Purpose: Declares AVS trace events for DSP core operations, IPC headers/payloads, and D0ix decisions, plus convenience macros for tracing requests, replies, and notifications.

Important APIs/types: `TRACE_EVENT(avs_dsp_core_op)`, event class `avs_ipc_msg_hdr`, derived events for request/reply/notify headers, conditional payload event `avs_ipc_msg_payload`, `TRACE_EVENT(avs_d0ix)`, helper declaration `trace_avs_msg_payload()`, and macros `trace_avs_request/reply/notify`.

Control flow role: IPC and platform code call these macros around message send/receive and power operations. Header events log primary/extension/status/error; payload events dump hex chunks; D0ix traces note ignored/proceeded transitions.

State and persistence: Events write to ftrace buffers only and do not mutate driver state.

Dependencies and integration: Uses Linux tracepoint macros and must keep `TRACE_INCLUDE_PATH`/`TRACE_INCLUDE_FILE` aligned with the file location for `define_trace`.

Risks: Trace macro arguments must be valid pointers and sizes. Payload dumps can leak sensitive firmware/control data to privileged trace consumers. Any field layout changes require trace format compatibility awareness.

Test signals: Kernel build with tracepoints, ftrace/perf visibility of `intel_avs:*`, payload chunk formatting, and D0ix/core-op event emissions during runtime PM and firmware IPC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/trace.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.c

Purpose: Provides AVS module metadata lookup, module instance ID allocation/freeing, firmware module-info refresh, and firmware request caching.

Important APIs/functions: `avs_get_module_entry()`, `avs_get_module_id_entry()`, `avs_get_module_id()`, `avs_is_module_ida_empty()`, `avs_module_info_init()`, `avs_module_info_free()`, `avs_module_id_alloc()`, `avs_module_id_free()`, `avs_request_firmware()`, `avs_release_last_firmware()`, and `avs_release_firmwares()`.

Control flow: Module lookup locks `modres_mutex`, scans `adev->mods_info`, copies entries, and unlocks. Module-info init obtains the firmware module table through IPC, reallocates/refreshes one `ida` per module, swaps `adev->mods_info`, and keeps instance allocation continuity unless purged. Firmware request first searches `adev->fw_list`, otherwise requests firmware, stores name/fw in a new list entry, and reuses it later.

State and persistence: Owns `adev->mods_info`, `adev->mod_idas`, and cached firmware entries on `adev->fw_list`. Firmware cache persists across runtime suspend/resume so files changing on disk do not affect loaded firmware.

Dependencies and integration: Uses IPC from `messages.c`, kernel IDA, firmware loader, list APIs, and locks in `avs_dev`. Consumed by path/probe/library loading code.

Risks: `avs_module_ida_alloc()` assumes non-purge refresh preserves ordering/count compatibility; if firmware reorders modules, reused IDA state could mismatch. `avs_release_last_firmware()` assumes the list is non-empty. `avs_ipc_get_modules_info()` zero-payload leak propagates here if it fails without freeing.

Test signals: Module table refresh with purge true/false, IDA exhaustion and free/reuse, invalid module ID paths, firmware cache hit/miss, request failure cleanup, and driver removal freeing all cached firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.h

Purpose: Declares machine-platform helper data and inline helpers for resolving SSP/TDM topology naming assumptions.

Important APIs/types: `struct avs_mach_pdata` carries codec pointer, TDM bitmap array, DMIC codec name, and obsolete-card naming flag. Inline helpers detect singular SSP, get SSP port, detect singular TDM slot, get TDM slot, and validate/fill both through `avs_mach_get_ssp_tdm()`. `AVS_STRING_FMT()` helps build SSP or SSP:TDM format strings.

Control flow role: Topology parsing and route/widget name substitution use these helpers to expand `%d` placeholders only when the machine describes exactly one SSP/TDM target.

State and persistence: No owned state; helpers read `snd_soc_acpi_mach` and pdata fields.

Dependencies and integration: Includes `<sound/soc-acpi.h>` and relies on kernel bit operations. Used by topology and PCM registration code. Exposes `obsolete_card_names` flag consumed by component registration.

Risks: Helpers assume `mach->pdata` is an `avs_mach_pdata` and that TDM arrays are valid for the selected port. `__ffs()` is only safe when masks are nonzero, so callers must respect singular checks.

Test signals: Machine entries with zero, one, and multiple SSP links; absent/present TDM arrays; dynamic topology names with and without `%d`; and obsolete-card-name registration behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/utils.h -->
