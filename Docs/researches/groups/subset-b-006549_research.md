# subset-b-006549 Research

Grouped research for the source files assigned to `subset-b-006549`. Each file section is bounded by the required reconciliation markers and preserves the original source path in its title.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.c

Purpose: implements the SOF auxiliary client driver for probe extraction, exposing a small ASoC compressed-capture card and debugfs controls for adding, removing, and listing firmware probe points. The client is opt-in through the `enable` module parameter and binds to platform-provided host callbacks for HDA/ACP-style probe DMA setup plus IPC3 or IPC4 probe operations.

Important APIs/functions: `sof_probes_client_probe()` validates `sof_probes_host_ops`, selects `ipc3_probe_ops` or `ipc4_probe_ops`, registers the compressed DAI/component/card, creates `probe_points`, `probe_points_remove`, and `probe_points_available` debugfs entries, and enables autosuspend runtime PM. The compressed stream path uses `sof_probes_compr_startup()`, `set_params()`, `trigger()`, `pointer()`, and `shutdown()` to hold the SOF core module, allocate SG pages, boot the DSP, initialize/deinitialize probe IPC, and disconnect active points on close. Debugfs helpers parse integer arrays from userspace and call IPC `points_add`, `points_remove`, and `points_info`.

Control flow/state: `priv->extractor_stream_tag` is the gate for debugfs operations; it is invalid until host startup assigns a stream tag and is reset on shutdown. Runtime PM is resumed around debugfs IPC access and idled with autosuspend afterward. Compressed copy reads from the circular DMA buffer using `total_bytes_transferred`.

Dependencies/integration: depends on `sof-client.h`, `sof-client-probes.h`, ASoC compressed PCM, debugfs, runtime PM, and IPC-specific probe implementations. It expects host ops in auxiliary platform data and stores `sof_probes_priv` in `cdev->data`.

Risks/test signals: debugfs creation assigns both `probe_points` and `probe_points_available` to `priv->dfs_points`, so removal only tracks the last of those two dentries. `sof_probes_compr_set_params()` can leak allocated compressed pages on later host/IPC failures unless the ALSA close path always unwinds. Useful tests are module probe with `enable=1`, compressed capture open/close, debugfs add/remove/list during active capture, runtime suspend/resume while reading debugfs, and IPC3/IPC4-specific probe point formatting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.h

Purpose: defines the shared contract between the generic SOF probes auxiliary client, platform host drivers, and IPC-specific probe implementations. It is intentionally small and contains no inline logic.

Important APIs/types: `struct sof_probes_host_ops` describes host-side compressed-stream setup callbacks: startup, shutdown, set_params, trigger, and pointer. `struct sof_probe_point_desc` is the packed userspace/IPC description with `buffer_id`, `purpose`, and `stream_tag`. `enum sof_probe_info_type` selects active or available probes. `struct sof_probes_ipc_ops` abstracts firmware IPC operations for init, deinit, point discovery, printable formatting, add, and remove. `struct sof_probes_priv` stores debugfs dentries, extractor stream tag, the temporary ASoC card, IPC-private state, and selected host/IPC operation tables.

Control flow/state: the header models state owned by `sof-client-probes.c`; the only persistent fields are the active stream tag, the embedded card object, and callback pointers. `ipc_priv` is reserved for IPC3/IPC4 implementation-private state.

Dependencies/integration: forward declares ALSA compressed and ASoC DAI types and exposes `ipc3_probe_ops`/`ipc4_probe_ops` to the generic client. Consumers must include this header when registering platform-dependent probe clients from SOF platform code.

Risks/test signals: `PROBES_INFO_AVAILABE_PROBES` is misspelled but used as an ABI-like internal enum, so renaming would require coordinated changes. The packed descriptor is parsed from debugfs integer arrays, so size/alignment assumptions should be tested on 32-bit and 64-bit builds. Build tests should cover both IPC3-only, IPC4-only, and combined configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client-probes.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.c

Purpose: provides the SOF auxiliary-client framework used by optional debug, probe, and platform-specific client drivers. It creates auxiliary devices under the SOF core device, forwards IPC operations across IPC3/IPC4, dispatches firmware notifications, and exposes helper accessors to client modules.

Important APIs/functions: `sof_register_clients()` registers built-in debug clients and delegates platform-specific client registration through `snd_sof_dsp_ops`. `sof_client_dev_register()`/`unregister()` allocate `sof_client_dev_entry`, initialize/add/delete auxiliary devices, copy optional platform data, and maintain `sdev->ipc_client_list`. `sof_client_ipc_tx_message()`, `sof_client_ipc_set_get_data()`, and `sof_client_ipc_rx_message()` adapt IPC3 header sizes and IPC4 message sizes. Accessors expose debugfs root, DMA device, firmware version/state, IPC type/max payload, DSP boot, and SOF core module refcounting. Event registration APIs add IPC RX and firmware-state callbacks and dispatchers iterate matching handlers.

Control flow/state: auxiliary device lifetime is managed by `sof_client_auxdev_release()` after `auxiliary_device_uninit()`. Built-in debug clients are unwound in reverse order on registration failure. Client suspend/resume walks loaded auxiliary drivers under `ipc_client_mutex`. IPC notification dispatch derives message type from IPC3 global command bits or IPC4 notification type bits.

Dependencies/integration: integrates with Linux auxiliary bus, SOF IPC internals, `ipc3-priv.h`, `ipc4-priv.h`, module refcounting, and SOF core state in `snd_sof_dev`. Exported symbols live in namespace `SND_SOC_SOF_CLIENT`.

Risks/test signals: unregister functions for IPC and firmware-state handlers lock `ipc_client_mutex`, while registration/dispatch use `client_event_handler_mutex`; this split can cause race or list corruption risk. `sof_register_ipc_flood_test()` error unwind unregisters from the current failed index down to zero, which should be checked for off-by-one behavior against devices that were never added. Tests should cover auxiliary probe/remove, concurrent notification registration/removal, IPC3/IPC4 message forwarding, and SOF core module unload while a client stream is active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.h

Purpose: public header for SOF auxiliary client drivers. It defines the client device wrapper, conversion macros, IPC helper APIs, DSP/firmware accessors, and notification registration types.

Important APIs/types: `struct sof_client_dev` embeds `struct auxiliary_device` and a client-private `data` pointer. Macros convert auxiliary devices or devices back to `sof_client_dev`. IPC APIs include transmit with optional reply, no-reply inline helper, set/get data, and IPC3 receive injection. IPC4-specific helpers locate firmware modules and widgets by ID. Accessors return debugfs root, DMA device, firmware version, IPC max payload, IPC type, and firmware state. `sof_client_boot_dsp()` requests firmware boot, and `sof_client_core_module_get()/put()` protect the parent SOF module. Callback typedefs and registration functions expose IPC notification and firmware-state subscriptions.

Control flow/state: this header only declares operations; the caller owns callback lifetime and must unregister before its auxiliary driver/device disappears. `cdev->data` is the main persistence hook for client-specific runtime state.

Dependencies/integration: depends on auxiliary bus, Linux device/list types, and SOF public enums. It is consumed by probe/debug client modules and platform clients that need controlled access to the SOF core.

Risks/test signals: clients must respect IPC-type constraints and should not assume IPC4 helpers exist in non-IPC4 builds unless Kconfig selects the needed symbols. Notification callback concurrency depends on the implementation in `sof-client.c`; client tests should unregister handlers during remove and verify no callbacks arrive after teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-client.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.c

Purpose: generic OF/Device Tree front-end for SOF DSP platform drivers. It translates a platform device match into `snd_sof_pdata`, applies optional deprecated module-parameter file overrides, and delegates probe/remove/shutdown to the common SOF device core.

Important APIs/functions: `sof_of_probe()` allocates `snd_sof_pdata`, obtains the `sof_dev_desc` from `device_get_match_data()`, validates descriptor ops, fills IPC default and firmware/topology override profile fields, installs `sof_of_probe_complete()`, and calls `snd_sof_device_probe()`. `sof_of_probe_complete()` enables runtime PM and autosuspend after successful core probe. `sof_of_remove()` disables runtime PM and removes the core device; `sof_of_shutdown()` forwards shutdown. `sof_of_pm` exports common prepare/complete/system/runtime PM callbacks.

Control flow/state: state is devm-allocated and owned by the platform device. Runtime PM is only enabled after SOF core probe completion. File path/name module parameters are read-only and described as deprecated because the main `snd-sof` module owns them.

Dependencies/integration: depends on OF match data supplied by platform-specific SOF drivers, SOF core `snd_sof_device_*` helpers, and runtime PM. Exported symbols let per-SoC OF drivers share this boilerplate.

Risks/test signals: probe fails early without match data or descriptor ops. Runtime PM disable in remove should be paired with the completion path; test failed probe paths to ensure PM is not disabled/enabled inconsistently. Device Tree binding tests should verify descriptor availability, firmware/topology override handling, suspend/resume, runtime idle, and shutdown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.h

Purpose: declares the generic SOF OF/Device Tree platform helpers and a small machine descriptor used by OF platforms.

Important APIs/types: `struct snd_sof_of_mach` carries compatible string, machine driver name, firmware filename, and topology filename. The header exports `sof_of_pm`, `sof_of_probe()`, `sof_of_remove()`, and `sof_of_shutdown()` for platform-specific drivers.

Control flow/state: no implementation state is stored here; callers provide platform devices whose match data points to `sof_dev_desc` instances consumed by `sof_of_probe()`.

Dependencies/integration: integrates OF platform drivers with the common SOF probe/remove/PM layer. It relies on the platform device and `dev_pm_ops` types being visible from including source files.

Risks/test signals: because it is a shared interface, signature changes affect all OF SOF platform drivers. Build coverage should include at least one OF SOF driver using `sof_of_pm` and the probe/remove/shutdown helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-of-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.c

Purpose: generic PCI front-end for SOF DSP devices. It handles PCI enable/resource claiming, DMI topology/key quirks, firmware/topology override profiles, IPC-type selection, runtime PM completion, and delegation to the common SOF core.

Important APIs/functions: `sof_pci_probe()` validates `sof_dev_desc` and ops from the PCI ID table, enables the PCI device with managed helpers, requests BAR regions, stores subsystem IDs, selects IPC type from descriptor default or deprecated `ipc_type` module parameter, applies firmware/library/topology path overrides, applies community-key postfixed paths via DMI, applies DMI topology filename overrides, installs `sof_pci_probe_complete()`, and calls `snd_sof_device_probe()`. `sof_pci_remove()` removes the SOF core and restores PCI runtime PM usage count if probe completed. `sof_pci_shutdown()` forwards shutdown. `sof_pci_pm` exports common SOF PM callbacks.

Control flow/state: DMI callbacks update static globals `sof_dmi_override_tplg_name` and `sof_dmi_use_community_key`; these are process-global for the module. Runtime PM is forbidden by PCI initially and allowed only after successful probe completion unless `sof_pci_debug` disables runtime PM.

Dependencies/integration: depends on PCI managed resource APIs, DMI, Intel SOF ACPI matching helpers, common SOF device core, and `sof_dev_desc` instances supplied by per-platform PCI ID tables. Exports symbols in namespace `SND_SOC_SOF_PCI_DEV`.

Risks/test signals: static DMI state can persist across probes, so multi-device or reprobe scenarios need careful validation. Deprecated module parameters still affect path selection. Tests should cover DMI override matches, community key platforms, invalid IPC type, runtime PM disable flag, remove after partial probe failure, and subsystem ID propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.h

Purpose: declares the shared PCI helper interface for SOF PCI platform drivers.

Important APIs/types: exports `sof_pci_pm`, `sof_pci_probe()`, `sof_pci_remove()`, and `sof_pci_shutdown()`. Platform-specific PCI drivers can set these in their `pci_driver` table instead of duplicating common SOF setup.

Control flow/state: no local state. Probe behavior depends on each PCI ID's `driver_data` pointing to a valid `sof_dev_desc`.

Dependencies/integration: requires PCI device and ID types from including code and the common SOF PCI helper implementation. The PM ops are namespace-exported by the C file.

Risks/test signals: build tests should include multiple SOF PCI platform modules to verify namespace imports and PM symbol visibility. Runtime tests should confirm platform PCI IDs carry correct descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-pci-dev.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-priv.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-priv.h

Purpose: central private SOF core header. It defines debug flags, common constants, device state, DSP operation vectors, IPC operation vectors, trace/PM/loader interfaces, debugfs descriptors, and prototypes shared by SOF core, IPC, topology, stream, client, and platform code.

Important APIs/types: `struct snd_sof_dsp_ops` is the hardware abstraction for probe/remove, firmware boot/reset, register and block IO, mailbox IO, IPC send, firmware loading, PCM stream ops, PM, clocking, debug dumps, trace DMA, machine selection, IPC clients, DAI drivers, and architecture ops. `struct snd_sof_dev` holds the live SOF device state: device pointer, firmware images, ASoC component, power/firmware state, IPC object, mailbox windows, BARs, debugfs state, topology lists, client lists, core refcounts, tracing state, and platform-private data. `struct sof_ipc_ops` groups IPC-version callbacks for topology, PM, PCM, loader, tracing, transmit, set/get data, reply, and receive. Other key types include `snd_sof_ipc`, `snd_sof_ipc_msg`, `sof_ipc_fw_tracing_ops`, `sof_ipc_pm_ops`, `sof_ipc_fw_loader_ops`, `dsp_arch_ops`, and debugfs map/entry structs.

Control flow/state: this header documents most long-lived SOF persistence. `snd_sof_dev` lists own PCM/kcontrol/widget/pipeline/DAI/route objects loaded from topology; firmware state and boot wait queues coordinate boot; `dsp_core_ref_count` tracks enabled cores; client and event-handler lists coordinate auxiliary clients; mutexes/spinlocks protect IPC, hardware IO, power state, client lists, and DSP boot.

Dependencies/integration: bridges Linux device, ASoC, HDA, SOF public UAPI, firmware, PM, debugfs, IPC3/IPC4 ops, and optional client support. Many helpers are prototypes implemented across SOF core files.

Risks/test signals: because it is broad shared state, field lifecycle mismatches easily become use-after-free or PM bugs. The client stub behavior under `!CONFIG_SND_SOC_SOF_CLIENT` must remain ABI-compatible. Tests should exercise firmware boot/crash/recovery, topology load/unload, stream open/close, runtime/system PM, debugfs access with D0-only regions, IPC TX disable, and both IPC3/IPC4 operation tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.c

Purpose: provides a generic SOF utility for building compressed firmware page tables from ALSA scatter-gather DMA buffers.

Important APIs/functions: `snd_sof_create_page_table()` computes the number of aligned pages with `snd_sgbuf_aligned_pages()`, retrieves each page frame number with `snd_sgbuf_get_addr() >> PAGE_SHIFT`, and packs 20-bit PFN chunks into a compact little-endian byte table, where two PFNs occupy five bytes. It returns the page count and exports the symbol.

Control flow/state: the function is stateless and writes only the caller-supplied `page_table` buffer. Odd/even pages share bytes; odd entries preserve the low nibble already written by the previous even entry.

Dependencies/integration: depends on ALSA memalloc scatter-gather helpers, unaligned little-endian stores, and the SOF firmware/IPC convention for compressed page tables. It is used by stream or firmware paths that need DSP-readable DMA page lists.

Risks/test signals: callers must provide a large enough page table buffer; the function does not validate `size` against `page_table` capacity. Tests should cover one, two, and odd page counts, high PFNs, SG buffers crossing page boundaries, and byte-for-byte expected packing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.h -->
# sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.h

Purpose: declares the SOF utility API for page table generation.

Important APIs/types: forward declares `struct snd_dma_buffer` and `struct device`, and declares `snd_sof_create_page_table()`.

Control flow/state: no state; consumers pass all buffers and sizes explicitly.

Dependencies/integration: included by code that needs SOF compressed page-table creation without pulling the full private SOF header. It relies on ALSA DMA buffer types supplied by including compilation units.

Risks/test signals: signature changes affect stream/page-table callers. Build tests should ensure users include the right ALSA headers for full type definitions before calling the function.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/sof-utils.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/stream-ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/stream-ipc.c

Purpose: implements generic mailbox-based stream position IPC helpers and PCM stream private-data setup for SOF.

Important APIs/functions: `sof_ipc_msg_data()` reads stream position data either from the legacy DSP mailbox or from a stream-specific offset stored in PCM/compress runtime private data. `sof_set_stream_data_offset()` validates stream-box bounds/alignment, converts a stream-relative offset to absolute mailbox offset, and stores it in PCM or compressed stream private data. `sof_stream_pcm_open()` allocates `struct sof_stream`, attaches it to `substream->runtime->private_data`, and applies ALSA period constraints. `sof_stream_pcm_close()` detaches and frees that state.

Control flow/state: PCM runtime private data persists between open and close and stores only `posn_offset`. Compressed streams use `struct sof_compr_stream` from `sof-priv.h`. Closed streams return `-ESTRPIPE` when position data is requested after private data is cleared.

Dependencies/integration: depends on SOF mailbox ops, ASoC PCM/compress state, and firmware-provided stream box layout. Exports all helper symbols for platform/IPC users.

Risks/test signals: `sof_set_stream_data_offset()` checks `posn_offset > stream_box.size`, so an offset equal to size passes before adding base, which may be one element past the stream window depending on caller size. Tests should cover no stream box fallback, PCM and compress paths, close-while-position-update race, offset alignment/bounds, and period constraint behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/stream-ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/topology.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/topology.c

Purpose: implements SOF topology loading glue for ASoC topology files. It parses vendor tokens, builds SOF-side control/widget/DAI/route/PCM objects, delegates IPC-version-specific setup, supports function topology fragments, and finalizes pipelines.

Important APIs/functions: token helpers include `sof_update_ipc_object()`, `sof_parse_token_sets()`, `sof_copy_tuples()`, `get_token_*()` converters, and DAI/frame lookup helpers. Control loading functions allocate `snd_sof_control`, parse volume/enum/bytes controls, compute volume tables from TLV data, apply LED access flags, and unload IPC/private data. Widget loading allocates `snd_sof_widget`, parses pin counts/bindings and IPC tuples, connects DAI widgets to BE DAI links, creates scheduler pipelines, binds events, and handles DSPless variants. PCM and DAI-link loaders allocate `snd_sof_pcm` and `snd_sof_dai_link`, bind host component IDs, parse DAI-specific token sets, and allocate/free page tables. `sof_complete()` performs IPC-specific control/widget setup, assigns widgets to pipelines, optionally verifies topology by setup/teardown, then sets up static pipelines. `snd_sof_load_topology()` loads function topology fragments when available or a monolithic topology otherwise.

Control flow/state: topology state is persisted in `sdev` lists: kcontrols, widgets, pipelines, DAIs, DAI links, routes, and PCMs. `sdev->next_comp_id` assigns component IDs. Function-topology loading may load multiple firmware blobs into the same component before completion. DSPless mode swaps in dummy control ops and only preserves enough DAI widget state for FE/BE wiring.

Dependencies/integration: depends on ASoC topology parser callbacks, SOF IPC topology ops, firmware request APIs, machine `get_function_tplg_files`, debug flags, snd_ctl LED support, and SOF audio helper lookup functions.

Risks/test signals: token parsing trusts token tables and topology private sizes; malformed counts, multi-set tokens, or missing DAI links can abort load. Error paths after partially adding PCMs/widgets must be validated by ASoC component removal. Tests should load valid IPC3/IPC4 topologies, malformed token arrays, function topologies with missing fragments and `dummy` fallback rules, DSPless mode, dynamic pipeline verification, multi-pin bindings, LED controls, and unload/reload cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/trace.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/trace.c

Purpose: thin IPC-version-neutral wrapper around firmware tracing operations.

Important APIs/functions: `sof_fw_trace_init()` gets `fw_tracing` ops from `sof_ipc_get_ops()` and disables trace support when absent. `sof_fw_trace_free()`, `sof_fw_trace_fw_crashed()`, `sof_fw_trace_suspend()`, and `sof_fw_trace_resume()` gate calls on `sdev->fw_trace_is_supported` and then invoke optional or mandatory IPC tracing callbacks.

Control flow/state: persistent state is `sdev->fw_trace_is_supported` and IPC-specific `sdev->fw_trace_data`. Suspend/resume and crash notifications are no-ops when tracing is unsupported.

Dependencies/integration: depends on `sof-priv.h` IPC ops and is called by SOF core PM/crash paths. IPC3/IPC4 implementations provide the actual trace buffer, DMA, or mtrace mechanics.

Risks/test signals: `sof_fw_trace_suspend()` and `resume()` assume the `suspend`/`resume` callbacks are present when tracing is supported; IPC ops must honor that contract. Tests should cover tracing disabled by missing ops, init failure behavior, crash notification, runtime/system suspend-resume, and cleanup ordering after IPC teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/trace.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Kconfig

Purpose: declares the hidden/tristate Kconfig symbol for SOF Xtensa DSP architecture support.

Important APIs/types: `config SND_SOC_SOF_XTENSA` is a tristate selected by platform drivers that need Xtensa oops/stack decoding.

Control flow/state: no runtime state. The symbol controls whether the `snd-sof-xtensa-dsp` module/object is built.

Dependencies/integration: used by SOF platform Kconfig entries for Xtensa-based DSPs.

Risks/test signals: build coverage should ensure platforms that reference `sof_xtensa_arch_ops` select this symbol and import the namespace correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Makefile

Purpose: builds the SOF Xtensa DSP support object.

Important APIs/types: `snd-sof-xtensa-dsp-y := core.o` and `obj-$(CONFIG_SND_SOC_SOF_XTENSA) += snd-sof-xtensa-dsp.o`.

Control flow/state: no runtime state; build output is controlled by `CONFIG_SND_SOC_SOF_XTENSA`.

Dependencies/integration: integrates `xtensa/core.c` into the kernel/module build when selected.

Risks/test signals: module namespace export should be verified by building SOF platform modules that consume `sof_xtensa_arch_ops` as modules and built-ins.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/core.c -->
# sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/core.c

Purpose: implements Xtensa-specific SOF DSP crash decoding callbacks for firmware oops and stack dumps.

Important APIs/functions: `xtensa_exception_causes[]` maps Xtensa exception cause IDs to names/descriptions. `xtensa_dsp_oops()` prints the firmware oops header, matched exception cause, and Xtensa registers such as EXCCAUSE, EXCVADDR, PS, SAR, EPC/EPS registers, INTENABLE, and INTERRUPT. `xtensa_stack()` prints stack words in hex lines and, when present, AR register dumps from the oops structure. `sof_xtensa_arch_ops` exports these callbacks as `dsp_arch_ops`.

Control flow/state: stateless; it formats data supplied by SOF crash handling. Stack pointer and AR count come from the firmware oops platform header.

Dependencies/integration: depends on SOF Xtensa UAPI structures and `sof-priv.h` architecture callback plumbing. Exported in namespace `SND_SOC_SOF_XTENSA`.

Risks/test signals: malformed firmware oops data could produce misleading dumps if `stack_words` or `numaregs` do not match allocated data. Tests should inject known oops structures, unknown exception causes, zero AR registers, and stack lengths not multiples of four to validate logging boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sof/xtensa/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sophgo/Kconfig

Purpose: Kconfig menu for Sophgo CV1800B/SG2002 ASoC support.

Important APIs/types: `SND_SOC_CV1800B_TDM` builds the I2S/TDM CPU DAI and selects generic DMAEngine PCM. `SND_SOC_CV1800B_ADC_CODEC` builds the internal RXADC codec DAI. `SND_SOC_CV1800B_DAC_CODEC` builds the internal TXDAC codec DAI. The menu depends on `COMPILE_TEST || ARCH_SOPHGO`.

Control flow/state: no runtime state; controls which platform components are available to Device Tree machine descriptions.

Dependencies/integration: intended for Device Tree/simple-audio-card integration with the Sophgo SoC audio blocks.

Risks/test signals: build matrix should cover each symbol as module and built-in, plus compile-test without ARCH_SOPHGO.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sophgo/Makefile

Purpose: maps Sophgo audio Kconfig symbols to object files.

Important APIs/types: builds `cv1800b-tdm.o`, `cv1800b-sound-adc.o`, and `cv1800b-sound-dac.o` under their respective config symbols.

Control flow/state: no runtime state.

Dependencies/integration: links the CPU DAI and codec drivers into kernel/module builds selected by `sophgo/Kconfig`.

Risks/test signals: verify module names match Kconfig help expectations and that all three drivers build independently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-adc.c -->
# sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-adc.c

Purpose: ASoC codec driver for the internal CV1800B/SG2002 RXADC capture block.

Important APIs/functions: `cv1800b_adc_probe()` maps registers and registers the component/DAI. `cv1800b_adc_dai_set_sysclk()` stores the external MCLK rate. `cv1800b_adc_hw_params()` programs the BCLK divider and ADC decimation/init bits for the requested capture rate. `cv1800b_adc_dai_trigger()` enables/disables RXADC and I2S TX on PCM trigger. Volume controls use `cv1800b_adc_volume_get()`/`set()` with a 0-48 dB, 2 dB step TLV scale and a hardware gain lookup table.

Control flow/state: `struct cv1800b_priv` stores MMIO base, device, and MCLK rate. Hardware register state persists across stream opens until overwritten. Capture DAI is fixed to up to two channels, 48 kHz, S16_LE.

Dependencies/integration: integrates with ASoC component/DAI registration and Device Tree compatible `sophgo,cv1800b-sound-adc`. Usually paired with the CV1800B TDM CPU DAI.

Risks/test signals: BCLK divider depends on machine driver calling `set_sysclk`; missing MCLK yields `-EINVAL`. The gain getter decodes bit masks by first-set-bit and may not exactly invert arbitrary register values. Tests should cover DT probe, sysclk absence/presence, 48 kHz capture, trigger enable/disable, volume get/set for both channels, and invalid divider ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-adc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-dac.c -->
# sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-dac.c

Purpose: ASoC codec driver for the internal CV1800B/SG2002 TXDAC playback block.

Important APIs/functions: `cv1800b_dac_probe()` maps MMIO and registers the component/DAI. `cv1800b_dac_hw_params()` accepts only 48 kHz, clears overwrite mute, sets decimation to 64, and programs the vendor delay value. `cv1800b_dac_dai_trigger()` toggles TXDAC and I2S RX enable bits. Helpers control DAC enable, overwrite mute, decimation, and init delay fields.

Control flow/state: `struct cv1800b_priv` stores MMIO base and device. Playback DAI is fixed to stereo, 48 kHz, S16_LE. Hardware state is maintained in registers and not cached except during immediate helper calls.

Dependencies/integration: Device Tree compatible `sophgo,cv1800b-sound-dac`; intended to connect to a CV1800B I2S/TDM CPU DAI via ASoC machine/simple-card.

Risks/test signals: unsupported rates fail at hw_params; machine constraints should prevent userspace from selecting other rates. There is no explicit remove-time mute/disable path beyond managed component teardown. Tests should cover 48 kHz playback, invalid rate rejection, trigger stop/start, overwrite mute bit behavior, and DT resource mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-sound-dac.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-tdm.c -->
# sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-tdm.c

Purpose: ASoC CPU DAI driver for the Sophgo CV1800B I2S/TDM controller with DMAEngine PCM support.

Important APIs/functions: probe maps registers, records FIFO DMA addresses, enables `i2s` and `mclk` clocks, initializes TDM/DMA mode, registers a DAI cloned from `cv1800b_i2s_dai_template`, and registers DMAEngine PCM. DAI ops include startup trigger ordering, `hw_params()` slot/frame programming, MCLK/BCLK divider calculation, word-length programming, TX/RX mode selection, FIFO/I2S reset, trigger enable/disable, I2S-only format selection, fixed BCLK ratio, and sysclk output control. Remove disables I2S, audio clocks, MCLK output, and asserts reset bits.

Control flow/state: `struct cv1800b_i2s` stores MMIO, clocks, DMA data, optional configured MCLK rate, and optional fixed BCLK ratio. If no MCLK is supplied by the machine driver, the driver computes a 256fs MCLK and programs the common clock framework. Register state is reset during hw_params and disabled during remove.

Dependencies/integration: depends on CCF clocks named `i2s` and `mclk`, Device Tree compatible `sophgo,cv1800b-i2s`, DMAEngine PCM, and ASoC DAI format/sysclk callbacks.

Risks/test signals: only I2S format is accepted despite TDM naming; clock-rate mismatch logs but does not fail after `clk_set_rate`. BCLK divider uses rounded division and warns on misalignment, so audio clock accuracy should be measured. Tests should cover playback/capture, 16/24-bit formats, 8-192 kHz rates, master/slave formats, fixed BCLK ratio, sysclk output, DMA addresses, remove-time disable, and invalid slots/widths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sophgo/cv1800b-tdm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spacemit/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/spacemit/Kconfig

Purpose: Kconfig menu for SpacemiT K1 I2S ASoC support.

Important APIs/types: `SND_SOC_K1_I2S` is a tristate driver option depending on `DMA_CMA`, selecting generic DMAEngine PCM, and gated by `COMPILE_TEST || ARCH_SPACEMIT` plus clock support.

Control flow/state: no runtime state; controls whether the K1 I2S CPU DAI driver is built.

Dependencies/integration: intended for Device Tree systems with the K1 I2S controller, clocks, reset, and DMA channels.

Risks/test signals: compile-test should verify dependencies are sufficient on non-SpacemiT architectures, and runtime configs should ensure DMA_CMA is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spacemit/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spacemit/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/spacemit/Makefile

Purpose: builds the SpacemiT K1 I2S ASoC driver.

Important APIs/types: `snd-soc-k1-i2s-y := k1_i2s.o` and `obj-$(CONFIG_SND_SOC_K1_I2S) += snd-soc-k1-i2s.o`.

Control flow/state: no runtime state.

Dependencies/integration: ties the Kconfig symbol to the single driver source file.

Risks/test signals: verify module object naming matches packaging and modprobe expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spacemit/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spacemit/k1_i2s.c -->
# sources/distributed-fs/ceph-client/sound/soc/spacemit/k1_i2s.c

Purpose: ASoC CPU DAI driver for the SpacemiT K1 I2S/SSPA controller with DMAEngine PCM support.

Important APIs/functions: `spacemit_i2s_probe()` enables required clocks, maps registers, obtains an exclusive reset, derives playback/capture capability from `dma-names`, registers a dynamically cloned DAI, and registers DMAEngine PCM. `spacemit_i2s_init()` programs PSP frame format, FIFO thresholds, receive-without-transmit, and disables interrupts. DAI ops apply startup constraints based on I2S versus DSP_A/DSP_B, program sample width and DMA burst width, set BCLK/SSPA clock rates, set sysclk, configure frame-sync width/timing, refcount enable/disable triggers with `started_count`, and assert/deassert reset on DAI probe/remove.

Control flow/state: `struct spacemit_i2s_dev` persists MMIO, reset, clocks, DMA descriptors, supported stream directions, selected DAI format, and active stream count. Trigger refcounting lets playback/capture share the hardware enable bit.

Dependencies/integration: Device Tree compatible `spacemit,k1-i2s`, clocks `sysclk`, `bclk`, `sspa_bus`, `sspa`, reset controller, DMA channels named `tx`/`rx`, ASoC DAI format callbacks, and DMAEngine PCM.

Risks/test signals: `started_count` is not protected by a lock; simultaneous playback/capture trigger paths could race. DAI advertised rates include only 8/16/48 kHz while PCM hardware has a 192 kHz max constant, so constraints should be checked. Tests should cover tx-only, rx-only, full-duplex, I2S S16 stereo, DSP_A/B S32 mono, trigger refcounting, reset sequencing, clock rates, and missing DMA-name cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spacemit/k1_i2s.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/spear/Kconfig

Purpose: Kconfig menu for ST SPEAr ASoC support.

Important APIs/types: `SND_SPEAR_SOC` selects generic DMAEngine PCM and builds the shared PCM platform helper. `SND_SPEAR_SPDIF_OUT` and `SND_SPEAR_SPDIF_IN` are tristate symbols for the S/PDIF playback and capture interfaces.

Control flow/state: no runtime state. Symbols are minimal and likely selected by board/platform configuration rather than exposing detailed prompts here.

Dependencies/integration: supports legacy SPEAr platform-data based audio drivers.

Risks/test signals: build configurations should ensure S/PDIF drivers select or depend on `SND_SPEAR_SOC` where the shared PCM helper symbol is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/spear/Makefile

Purpose: maps SPEAr ASoC Kconfig symbols to module objects.

Important APIs/types: builds `spear_pcm.o` into `snd-soc-spear-pcm.o`, `spdif_in.o` into `snd-soc-spear-spdif-in.o`, and `spdif_out.o` into `snd-soc-spear-spdif-out.o`.

Control flow/state: no runtime state.

Dependencies/integration: links shared PCM support and S/PDIF interfaces according to Kconfig.

Risks/test signals: module build should verify S/PDIF objects resolve `devm_spear_pcm_platform_register()` from the shared PCM module.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in.c -->
# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in.c

Purpose: ASoC CPU DAI driver for SPEAr S/PDIF input/capture.

Important APIs/functions: probe maps MMIO, obtains FIFO IO resource, IRQ, clock, and platform data, initializes DMA parameters, requests IRQ, registers component/DAI, and registers the shared SPEAr DMAEngine PCM platform. `spdif_in_configure()` enables parity/status/user/valid/block capture and FIFO threshold. DAI ops save requested format, enable clock and hardware on trigger start, program 16-bit extraction versus IEC958 subframe mode, disable and optionally reset peripheral on stop, and mask IRQs on shutdown. IRQ handler logs FIFO/write/out-of-range errors and clears status.

Control flow/state: `struct spdif_in_dev` stores clock, platform DMA data, saved format, MMIO base, optional reset callback, IRQ, and DMAEngine config. Hardware is configured at trigger start and disabled at trigger stop.

Dependencies/integration: depends on legacy `spear_spdif_platform_data`, `spear_dma_data`, shared `spear_pcm` helper, platform clock, IRQ, and IO resources.

Risks/test signals: probe requires platform data and IORESOURCE_IO FIFO resource, so it is not DT-generic. IRQ clear writes zero to the IRQ register, matching this hardware contract but worth validating. Tests should cover S16 and IEC958 capture, start/stop/reset, IRQ error injection, missing platform data/resource failures, and DMA filter behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in_regs.h -->
# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in_regs.h

Purpose: register map and bit definitions for the SPEAr S/PDIF input controller.

Important APIs/types: defines control, IRQ mask/status, and lock-status offsets. Control bits cover parity/status/user/valid/block capture, sample mode, data swap/revert, extraction mode, enable, sample, and FIFO threshold. IRQ bits cover FIFO write error, empty FIFO read, FIFO full, and out-of-range.

Control flow/state: no code; values are consumed by `spdif_in.c` to program and diagnose hardware.

Dependencies/integration: private header for the SPEAr input driver.

Risks/test signals: incorrect bit definitions directly affect hardware programming. Tests should compare against the SoC reference manual and validate IRQ/status behavior on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_in_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out.c -->
# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out.c

Purpose: ASoC CPU DAI driver for SPEAr S/PDIF output/playback.

Important APIs/functions: probe maps MMIO, gets clock and platform data, initializes DMA parameters, registers component/DAI, and registers the shared SPEAr DMAEngine PCM platform. `spdif_out_configure()` resets the block, programs memory format, FIFO trigger, and hardware validity/user/channel/parity handling, then clears/disables interrupts. `spdif_out_hw_params()` chooses a core clock family based on sample rate and programs the divider. Trigger start selects audio-data or mute opmode, and stop selects off. `spdif_mute()` and DAI control callbacks expose an IEC958 playback switch. PM suspend/resume disables/enables the clock and restores configuration when running.

Control flow/state: `struct spdif_out_dev` stores clock, DMA params, saved rate/core frequency/mute, running flag, MMIO, and DMAEngine config. Saved params are used for resume and trigger/mute behavior.

Dependencies/integration: depends on legacy `spear_spdif_platform_data`, shared `spear_pcm`, platform clock, DMA filter data, and ASoC DAI controls.

Risks/test signals: probe dereferences platform data without a null check, unlike the input driver. `clk_set_rate()` return is ignored in `spdif_out_clock()`. Tests should cover all supported rate families, mute toggling while stopped/running, suspend/resume while running, missing platform data failure, DMA playback, and divider accuracy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out_regs.h -->
# sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out_regs.h

Purpose: register map and bit definitions for the SPEAr S/PDIF output controller.

Important APIs/types: defines reset, FIFO, interrupt status/clear/enable, control, channel status, pause/latency, frame length, and config offsets. Control bits cover opmode, normal state, divider, and sample-read fields. Config bits select memory format, validity/user/channel-status/parity sources, and FIFO DMA trigger thresholds.

Control flow/state: no runtime state; values are consumed by `spdif_out.c`.

Dependencies/integration: private hardware header for the SPEAr output driver.

Risks/test signals: divider mask/shift and opmode constants are critical for clocking and mute behavior. Tests should validate register writes against hardware documentation and observed S/PDIF output framing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spdif_out_regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.c

Purpose: shared SPEAr ASoC PCM DMAEngine registration helper.

Important APIs/functions: `devm_spear_pcm_platform_register()` copies a default `snd_dmaengine_pcm_config`, installs a legacy DMA filter callback, and registers DMAEngine PCM with `NO_DT` and `COMPAT` flags. The default hardware profile enables interleaved block-transfer mmap pause/resume with 16 KiB buffers and fixed 2 KiB periods.

Control flow/state: stateless after registration except for the caller-provided config object that is filled before `devm_snd_dmaengine_pcm_register()`.

Dependencies/integration: used by SPEAr S/PDIF input/output drivers with `sound/spear_dma.h` platform DMA data.

Risks/test signals: hard-coded period/buffer sizes may constrain modern use cases. Tests should verify DMA channel filtering, mmap playback/capture, pause/resume, and both S/PDIF drivers using independent config storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.h -->
# sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.h

Purpose: declares the shared SPEAr PCM platform registration helper.

Important APIs/types: `devm_spear_pcm_platform_register()` takes a device, mutable DMAEngine PCM config, and legacy DMA channel filter callback.

Control flow/state: no state; implementation fills the config and registers managed PCM resources.

Dependencies/integration: included by SPEAr S/PDIF drivers that need common PCM setup.

Risks/test signals: users must pass storage for `config` that remains valid for the managed PCM lifetime. Build tests should cover both input and output users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/spear/spear_pcm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/Kconfig -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/Kconfig

Purpose: Kconfig menu for Spreadtrum/Unisoc ASoC platform support.

Important APIs/types: `SND_SOC_SPRD` enables the SoC audio platform and selects compressed audio support. `SND_SOC_SPRD_MCDT` enables multi-channel data transfer support and depends on the base Spreadtrum ASoC platform.

Control flow/state: no runtime state.

Dependencies/integration: used by Spreadtrum PCM DMA/compress and MCDT source files in the same directory.

Risks/test signals: build tests should cover `SND_SOC_SPRD` with and without `SND_SOC_SPRD_MCDT`, including COMPILE_TEST on non-SPRD architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/sprd/Makefile

Purpose: builds Spreadtrum ASoC platform objects.

Important APIs/types: `snd-soc-sprd-platform-y` combines `sprd-pcm-dma.o` and `sprd-pcm-compress.o` under `CONFIG_SND_SOC_SPRD`; `sprd-mcdt.o` is built under `CONFIG_SND_SOC_SPRD_MCDT`.

Control flow/state: no runtime state.

Dependencies/integration: links PCM DMA, compressed PCM, and optional MCDT support according to the Kconfig menu.

Risks/test signals: object grouping means the base platform module always includes both DMA and compress support. Build tests should ensure symbols resolve when MCDT is disabled and enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/sprd/Makefile -->
