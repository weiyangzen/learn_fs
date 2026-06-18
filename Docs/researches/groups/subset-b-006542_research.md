# subset-b-006542 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-generic-dmaengine-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-generic-dmaengine-pcm.c

## Purpose
This file provides the generic ASoC platform component implementation for PCM devices backed by the Linux DMAEngine API. It bridges ALSA/ASoC PCM callbacks to DMAEngine helpers, registers a `snd_soc_component`, requests DMA channels from device tree or legacy filters, preallocates managed DMA buffers, and handles optional per-channel sample processing for copy-based access.

## Important APIs, Types, and Functions
The exported entry points are `snd_dmaengine_pcm_prepare_slave_config()`, `snd_dmaengine_pcm_register()`, and `snd_dmaengine_pcm_unregister()`. The runtime object is `struct dmaengine_pcm`, reached through `soc_component_to_pcm(component)`, with `config`, `flags`, and `chan[SNDRV_PCM_STREAM_*]`. `snd_dmaengine_pcm_prepare_slave_config()` converts ALSA hardware parameters to `struct dma_slave_config`, then overlays DAI DMA data from `snd_soc_dai_get_dma_data()`. It explicitly rejects multi-CPU links.

PCM component callbacks include `dmaengine_pcm_open()`, `dmaengine_pcm_close()`, `dmaengine_pcm_hw_params()`, `dmaengine_pcm_trigger()`, `dmaengine_pcm_pointer()`, `dmaengine_copy()`, `dmaengine_pcm_new()`, and `dmaengine_pcm_sync_stop()`. Two component driver tables exist: `dmaengine_pcm_component` for normal mmap/interleaved operation and `dmaengine_pcm_component_process` when `config->process` requires a `.copy` hook.

## Control Flow
Registration allocates `struct dmaengine_pcm`, installs a default config if none is supplied, requests OF DMA channels via `dmaengine_pcm_request_chan_of()`, chooses the component driver variant, initializes the component, and adds it to ASoC. PCM creation later calls `dmaengine_pcm_new()` for each stream: missing channels are requested by configured names, OF defaults (`tx`, `rx`, or `rx-tx` for half duplex), or the compatibility filter path. Open sets runtime hardware limits from either `config->pcm_hardware` or DAI DMA metadata, then opens the DMAEngine PCM helper. `hw_params` runs the configured `prepare_slave_config()` and calls `dmaengine_slave_config()`.

## State and Persistence
Persistent in-kernel state is the registered component plus requested DMA channels. The module parameter `prealloc_buffer_size_kbytes` defaults buffer preallocation to 512 KiB unless overridden by the config. `SND_DMAENGINE_PCM_FLAG_NO_RESIDUE` is set when DMA capabilities report descriptor-only residue or caps cannot be queried; pointer reporting then switches to period counting and exposes `SNDRV_PCM_INFO_BATCH`.

## Dependencies and Integration Points
The file depends on DMAEngine (`dma_request_chan`, `dma_get_slave_caps`, `dmaengine_slave_config`), ALSA DMAEngine PCM helpers, ASoC DAI DMA data, OF phandles/channel names, and ASoC component registration. Drivers integrate by calling `snd_dmaengine_pcm_register()` with `struct snd_dmaengine_pcm_config`, optional channel names, `compat_request_channel`, `prepare_slave_config`, `pcm_hardware`, and optional `process`.

## Risks and Test Signals
The largest behavioral risks are unsupported multi-CPU links, wrong DMA channel naming, half-duplex channel sharing, residue granularity assumptions, and callback ordering during error cleanup. `dmaengine_copy()` relies on channel-interleaved buffer offset math and must keep playback/capture copy ordering intact around `process()`. There is no local KUnit in this file; useful validation is boot/probe coverage for OF and legacy DMA paths, ALSA playback/capture smoke tests, residue/pointer tests on DMA engines with different granularity, and unregister/reprobe leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-generic-dmaengine-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-jack.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-jack.c

## Purpose
This file implements ASoC jack status reporting and GPIO-backed jack detection. It connects ALSA jack devices, ASoC DAPM pin power, notifier callbacks, optional voltage zones, and GPIO interrupt/debounce handling into one jack abstraction used by machine and codec drivers.

## Important APIs, Types, and Functions
The main exported APIs are `snd_soc_jack_report()`, `snd_soc_jack_add_zones()`, `snd_soc_jack_get_type()`, `snd_soc_jack_add_pins()`, `snd_soc_jack_notifier_register()`, `snd_soc_jack_notifier_unregister()`, `snd_soc_jack_add_gpios()`, `snd_soc_jack_add_gpiods()`, and `snd_soc_jack_free_gpios()`. `struct snd_soc_jack` owns status, a mutex, DAPM pins, zones, and a blocking notifier chain. `struct snd_soc_jack_pin` maps jack bits to DAPM pins. `struct snd_soc_jack_gpio` stores GPIO descriptor, debounce work, IRQ behavior, wakeup policy, and optional custom status callback.

## Control Flow
`snd_soc_jack_report()` is the central update path. It masks in new status bits, updates each configured DAPM pin, notifies registered listeners before DAPM sync, synchronizes DAPM if pins changed, then calls `snd_jack_report()` for userspace. `snd_soc_jack_add_pins()` validates pin names and masks, registers ALSA jack controls for pins, and replays the last status through `snd_soc_jack_report()`.

With GPIOLIB enabled, `snd_soc_jack_add_gpios()` allocates devres cleanup state, resolves GPIO descriptors, initializes delayed work, requests shared rising/falling IRQs, optionally enables wake, registers a PM notifier, exports the GPIO for diagnostics, and schedules initial detection after debounce. IRQs only queue delayed work; `gpio_work()` reads the line with `gpiod_get_value_cansleep()`, applies inversion or `jack_status_check()`, and reports the result.

## State and Persistence
Jack state lives in `jack->status`, the pin and zone lists, registered notifier blocks, delayed work items, IRQ registrations, and devres cleanup records. GPIO cleanup unregisters PM notifiers, frees IRQs, cancels delayed work synchronously, unexports GPIOs, drops descriptors, and clears the back pointer.

## Dependencies and Integration Points
The file integrates ALSA jack core (`snd_jack_report`, `snd_jack_add_new_kctl`), ASoC DAPM (`snd_soc_dapm_enable_pin`, `disable_pin`, `sync`), GPIO descriptors, IRQs, PM notifiers, workqueues, wakeup events, and tracepoints. Voltage-zone helpers let codec-specific ADC/micbias detection translate millivolt ranges into jack types.

## Risks and Test Signals
Important risks are calling `snd_soc_jack_report()` from atomic context despite its mutex and DAPM operations, missing debounce after resume, stale work during GPIO teardown, misuse of `devres_destroy()` when manually freeing, and notifier callbacks attempting recursive reporting. Test signals include GPIO insertion/removal IRQ tests, suspend/resume transition detection, inverted GPIO behavior, DAPM pin enablement, voltage-zone matching at boundaries, and devres/manual cleanup leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-jack.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-link.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-link.c

## Purpose
This file is a thin sequencing and rollback wrapper around machine-driver DAI link callbacks. It centralizes calls into `dai_link->init`, `exit`, PCM `ops`, compressed `compr_ops`, and `be_hw_params_fixup`, while tracking whether a callback was successfully entered so rollback paths do not call unmatched teardown hooks.

## Important APIs, Types, and Functions
The exported compressed-stream APIs are `snd_soc_link_compr_startup()`, `snd_soc_link_compr_shutdown()`, and `snd_soc_link_compr_set_params()`. PCM-side functions are used internally by ASoC core: `snd_soc_link_init()`, `snd_soc_link_exit()`, `snd_soc_link_be_hw_params_fixup()`, `snd_soc_link_startup()`, `snd_soc_link_shutdown()`, `snd_soc_link_prepare()`, `snd_soc_link_hw_params()`, `snd_soc_link_hw_free()`, and `snd_soc_link_trigger()`.

The file relies on marker fields in `struct snd_soc_pcm_runtime` such as `mark_startup`, `mark_hw_params`, `mark_trigger`, and `mark_compr_startup`. The local macros `soc_link_mark_push()`, `soc_link_mark_pop()`, and `soc_link_mark_match()` currently store one active stream pointer per callback class.

## Control Flow
For startup and hw_params, the wrapper calls the link callback if present and only records the marker on success. Shutdown and hw_free accept a `rollback` flag; when rollback is true, they return unless the matching marker was set for the same substream. Trigger handling maps start-like commands to forward callback execution plus marker push. Stop-like commands optionally check the marker during rollback, call the trigger callback, and pop a marker. Compressed startup/shutdown mirror the PCM startup/shutdown pattern.

## State and Persistence
No heap objects are allocated here. Persistent state is limited to runtime marker fields. These fields are reset during successful teardown and protect error unwind paths from invoking callbacks that were never completed.

## Dependencies and Integration Points
This wrapper is called by `soc-pcm.c` as part of open, close, hw_params, hw_free, prepare, trigger, and DPCM BE fixup. It integrates with machine driver callbacks in `struct snd_soc_ops` and `struct snd_soc_compr_ops`.

## Risks and Test Signals
The marker model assumes one marked substream per runtime field; future multi-substream or more complex rollback scenarios would need list-based tracking, which the comments already anticipate. A notable detail is that the stop branch in `snd_soc_link_trigger()` pops `startup` rather than `trigger`, which is worth preserving or reviewing against the surrounding rollback contract. Test signals should cover callback failure at each stage, rollback without prior success, trigger start failure followed by synthesized stop, compressed stream startup/shutdown rollback, and links with missing optional callbacks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-ops-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-ops-test.c

## Purpose
This KUnit file validates generic ASoC mixer control helpers from `soc-ops.c`, mainly `volsw` and `volsw_sx` info/get/put behavior. It supplies a fake component and cache-only regmap so conversion, masking, inversion, signed ranges, platform maximums, and stereo layouts can be tested without hardware.

## Important APIs, Types, and Functions
`enum soc_ops_test_control_layout` models single-register, double-shift, and double-register controls. `struct info_test_param` captures expected `snd_ctl_elem_info` output, and `struct access_test_param` captures a put/get round trip plus expected register values. Macros `ITEST()` and `ATEST()` make the large parameter tables compact.

The KUnit lifecycle functions are `soc_ops_test_init()` and `soc_ops_test_exit()`. The actual tests are `soc_ops_test_info()` and `soc_ops_test_access()`, with parameter generation through `KUNIT_ARRAY_PARAM()`.

## Control Flow
Initialization registers a KUnit device, creates a regmap with 32-bit native registers and flat cache, switches the regmap into cache-only mode, and embeds it in a fake `snd_soc_component`. Bus read/write callbacks intentionally fail if invoked, proving the tests use the cache path only. Info tests build a synthetic `snd_kcontrol`, call the selected info callback, and compare type, count, min, and max. Access tests initialize left and right registers, write ALSA control values through the selected `put`, verify register cache contents against masks, then read back through `get` and compare user-visible values.

## State and Persistence
State is per-test KUnit allocation: fake device, fake component, mutex, and cache-only regmap. The tested register state is reset for every parameterized case. No persistent kernel state is created outside the KUnit test lifetime.

## Dependencies and Integration Points
The test depends on KUnit, KUnit device helpers, regmap flat cache, ASoC component helpers, and the exported mixer callbacks from `soc-ops.c`. It is tightly aligned with the semantics of `struct soc_mixer_control`.

## Risks and Test Signals
The test table is broad for volume conversion but intentionally narrow for other `soc-ops.c` APIs: enum controls, bytes controls, XR/SX multi-register controls, volume limiting, and strobe helpers are not directly covered here. Strong signals include the boundary cases already present for negative minimums, `platform_max`, inverted ranges, same-register stereo shifts, separate-register stereo, and SX wraparound behavior. Future changes to mask calculation or signed conversion should update these parameter tables first.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-ops-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-ops.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-ops.c

## Purpose
This file provides generic ALSA control callbacks used by codec, component, and topology-defined ASoC mixer controls. It handles enum controls, integer/boolean volume controls, signed SX controls, byte-array controls, TLV bytes controls, signed multi-register controls, strobe controls, and runtime volume limiting.

## Important APIs, Types, and Functions
Exported enum helpers are `snd_soc_info_enum_double()`, `snd_soc_get_enum_double()`, and `snd_soc_put_enum_double()`. Volume helpers include `snd_soc_info_volsw()`, `snd_soc_info_volsw_sx()`, `snd_soc_get_volsw()`, `snd_soc_put_volsw()`, `snd_soc_get_volsw_sx()`, and `snd_soc_put_volsw_sx()`. Byte helpers are `snd_soc_bytes_info()`, `snd_soc_bytes_get()`, `snd_soc_bytes_put()`, `snd_soc_bytes_info_ext()`, and `snd_soc_bytes_tlv_callback()`. Additional exported helpers are `snd_soc_limit_volume()`, `snd_soc_info_xr_sx()`, `snd_soc_get_xr_sx()`, `snd_soc_put_xr_sx()`, `snd_soc_get_strobe()`, and `snd_soc_put_strobe()`.

Core private helpers include `soc_mixer_reg_to_ctl()`, `soc_mixer_ctl_to_reg()`, `soc_mixer_valid_ctl()`, `soc_mixer_mask()`, `soc_mixer_sx_mask()`, `soc_get_volsw()`, and `soc_put_volsw()`.

## Control Flow
Enum get reads one register, extracts left and optionally right fields, maps register values to enum items, and returns them to ALSA. Enum put validates item bounds, converts selected items to register values, builds a combined mask, and updates the component register.

Volume info computes ALSA type and range, treating one-bit controls as boolean unless the control name ends exactly in `" Volume"`. Volume get reads one or two registers, applies mask, sign extension or SX wrapping, min offset, clamp, and inversion. Volume put validates requested values against negative, platform max, and control max, converts to register fields, and updates either one combined register or two separate registers. `snd_soc_limit_volume()` finds a named kcontrol, lowers `platform_max`, and clips current hardware state through the control get/put callbacks.

Byte controls use raw regmap read/write and preserve masked bits in the first register-sized value. Extended bytes controls route TLV read/write operations to driver-supplied callbacks. XR/SX controls assemble or split a signed value across consecutive registers. Strobe put writes a bit high then low, or inverted low then high.

## State and Persistence
The file itself owns no global state. It mutates component registers through `snd_soc_component_read()` and `snd_soc_component_update_bits()`, regmap raw operations, and `platform_max` inside `struct soc_mixer_control`. Byte puts allocate a temporary DMA-capable copy with cleanup-managed `__free(kfree)`.

## Dependencies and Integration Points
These callbacks are used directly by static codec controls and indirectly by `soc-topology.c` when binding topology control IDs. They depend on ASoC component IO, regmap value widths/endian parsing, ALSA kcontrol ABI structures, and `struct soc_mixer_control`, `struct soc_enum`, `struct soc_bytes`, `struct soc_bytes_ext`, and `struct soc_mreg_control`.

## Risks and Test Signals
Critical risks are off-by-one masks, signed range wrapping, platform max clipping, stereo same-register versus separate-register mask handling, endian handling for masked bytes, and preserving change flags when the left channel changes but right-channel update fails. `soc-ops-test.c` provides strong coverage for `volsw` and `volsw_sx`; additional useful tests would cover bytes masks at 1/2/4-byte widths, enum value maps, XR/SX sign extension, strobe transitions, and `snd_soc_limit_volume()` clipping existing out-of-range state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-ops.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-pcm.c

## Purpose
This is the core ASoC PCM orchestration file. It creates ALSA PCM devices for DAI links, computes hardware constraints across CPU and codec DAIs, sequences component/link/DAI callbacks, manages DAPM stream events, and implements Dynamic PCM (DPCM) frontend/backend routing, state transitions, runtime updates, and debugfs state reporting.

## Important APIs, Types, and Functions
Externally visible functions include `snd_soc_runtime_action()`, `snd_soc_runtime_ignore_pmdown_time()`, `snd_soc_runtime_calc_hw()`, `snd_soc_dpcm_get_substream()`, `snd_soc_dpcm_runtime_update()`, `dpcm_be_dai_trigger()`, `widget_in_list()`, and `dpcm_end_walk_at_be()`. Internally, the non-DPCM PCM operation path is `soc_pcm_open()`, `soc_pcm_hw_params()`, `soc_pcm_prepare()`, `soc_pcm_trigger()`, `soc_pcm_hw_free()`, `soc_pcm_close()`, and `soc_pcm_pointer()`. DPCM uses `dpcm_fe_dai_open()`, `dpcm_fe_dai_hw_params()`, `dpcm_fe_dai_prepare()`, `dpcm_fe_dai_trigger()`, `dpcm_fe_dai_hw_free()`, and `dpcm_fe_dai_close()`.

Key state lives in `struct snd_soc_pcm_runtime`, `struct snd_soc_dpcm`, per-stream DPCM state (`state`, `runtime_update`, `trigger_pending`, `users`, `be_start`, `be_pause`, `fe_pause`, `hw_params`), and ALSA `struct snd_pcm_substream`.

## Control Flow
`soc_new_pcm()` determines playback/capture support, creates an ALSA PCM, installs either regular PCM ops or DPCM frontend ops, and attaches component callbacks like copy, mmap, ack, ioctl, and sync_stop. Regular open selects default pinctrl state, runtime-PM gets components, opens components/link/DAIs, computes compatible hardware from all participating DAIs, applies MSB and symmetry constraints, and activates runtime state. Hw_params applies symmetry, calls link, codec DAIs, CPU DAIs, and components, with TDM channel-mask fixups. Prepare starts DAPM and unmutes DAIs. Trigger selects link/component/DAI ordering from component or link policy and performs rollback on start failure. Close and hw_free reverse the setup and restore power state.

DPCM open discovers backend paths through DAPM, connects FE and BE `struct snd_soc_dpcm` links, opens BEs, opens the FE, and merges FE/BE hardware constraints as configured. DPCM runtime updates first prune old paths, then add new paths, starting or stopping BEs according to FE state. BE operations are guarded by state checks so shared BEs are not reconfigured while other FEs are running. Trigger code tracks shared BE start and pause reference counts and honors FE trigger ordering (`PRE` or `POST`).

## State and Persistence
Runtime state is protected by the ASoC DPCM mutex and, for trigger races, ALSA stream locks. DPCM connections persist in FE `be_clients` and BE `fe_clients` lists until pruned and disconnected. Debugfs exposes FE and BE DPCM state and hardware params for dynamic links. DAI symmetry parameters persist on DAIs while active and are cleared when inactive.

## Dependencies and Integration Points
This file integrates ALSA PCM core, ASoC components, DAIs, DAI links, DAPM, pinctrl, runtime PM, debugfs, and `soc-link.c`. It is also the central consumer of topology-created DAI links and dynamic routes.

## Risks and Test Signals
Main risks are DPCM shared-BE user count underflow/overflow, racey trigger_pending behavior, rollback asymmetry, invalid dynamic multi-CPU configurations, DAPM route changes while streams are active, and mismatched hardware constraints across CPU/codec DAIs. Test signals include normal PCM playback/capture, DPCM FE open with no backend route, route switching while active, shared BE with two FEs, pause-to-stop transitions, trigger rollback injection, suspend/resume, debugfs state inspection, and TDM channel-map cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-topology-test.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-topology-test.c

## Purpose
This KUnit file validates the ASoC topology loader and remover using small in-memory firmware blobs. It focuses on parameter validation, header validation, a minimal manifest, a minimal PCM topology, and repeated component/card reload scenarios.

## Important APIs, Types, and Functions
`struct kunit_soc_component` bundles a KUnit handle, expected loader result, `snd_soc_component`, `snd_soc_card`, and fake `struct firmware`. `d_probe()` calls `snd_soc_tplg_component_load()` during component probe and checks the expected return. `d_remove()` calls `snd_soc_tplg_component_remove()`.

The test defines a dummy DAI link and platform component, then two packed topology templates: `tplg_tmpl_empty` with a manifest header and manifest payload, and `tplg_tmpl_with_pcm` with a manifest plus one PCM object.

## Control Flow
Each test allocates a KUnit component wrapper, fills a fake card, optionally copies and mutates a topology template, registers the card and component, and relies on component probe to execute the topology load. Negative tests pass a null component, null firmware, bad magic, unsupported ABI, bad header size, or zero payload size. Positive tests load an empty manifest and a PCM topology. Reload tests repeat component registration/removal or card registration/removal 100 times to catch object cleanup problems.

## State and Persistence
State is scoped to KUnit allocations and the fake device registered in `snd_soc_tplg_test_init()`. The loader under test creates dynamic ASoC objects on the fake component/card; removal should clear them across repeated cycles. The global `test_dev` is reference-counted with `get_device()` and released in test exit.

## Dependencies and Integration Points
The test depends on KUnit, KUnit device helpers, ASoC card/component registration, `snd_soc_tplg_component_load()`, `snd_soc_tplg_component_remove()`, and topology UAPI structures. It indirectly tests PCM runtime addition for topology-created FE links.

## Risks and Test Signals
The tests cover important loader validation and lifecycle issues but only a narrow topology surface: no mixer, enum, bytes, widgets, DAPM graph, BE DAI, vendor blocks, bytes-ext ops, or backend link configuration. Strong signals are the bad-header tests and the 100-iteration reload loops, which are useful for dobj removal and stale runtime detection. Future topology changes should add malformed private-size, multi-header, widget/control, route, and backend-link cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-topology-test.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-topology.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-topology.c

## Purpose
This file implements the ASoC topology firmware loader and remover. It parses little-endian topology blobs in multiple passes, creates dynamic ALSA controls, DAPM widgets/routes, frontend DAIs and DAI links, configures backend DAIs and links, calls optional component-driver hooks for vendor data and custom initialization, and tears down dynamic objects in reverse pass order.

## Important APIs, Types, and Functions
The exported APIs are `snd_soc_tplg_component_load()`, `snd_soc_tplg_component_remove()`, and `snd_soc_tplg_widget_bind_event()`. The parser context is `struct soc_tplg`, containing firmware position, current header position, pass number, current index, component/card device, optional topology ops, custom kcontrol ops, and bytes-ext ops.

Important loader helpers include `soc_tplg_valid_header()`, `soc_tplg_process_headers()`, `soc_tplg_load_header()`, `soc_tplg_kcontrol_elems_load()`, `soc_tplg_dapm_widget_elems_load()`, `soc_tplg_dapm_graph_elems_load()`, `soc_tplg_pcm_elems_load()`, `soc_tplg_dai_elems_load()`, `soc_tplg_link_elems_load()`, and `soc_tplg_manifest_load()`. Object creators include `soc_tplg_control_dmixer_create()`, `soc_tplg_control_denum_create()`, `soc_tplg_control_dbytes_create()`, `soc_tplg_dapm_widget_create()`, `soc_tplg_dai_create()`, and `soc_tplg_fe_link_create()`.

## Control Flow
`snd_soc_tplg_component_load()` validates `comp`, `comp->card`, `comp->card->dev`, and firmware, initializes `struct soc_tplg`, then runs `soc_tplg_load()`. The parser loops through passes from manifest through vendor, controls, widgets, PCM/DAI, graph, BE DAI, and link configuration. For each pass it restarts at the beginning of firmware, validates every header, dispatches matching header types, and skips nonmatching types. After all passes, it completes DAPM and calls the component `complete` hook.

Control loading validates element counts and string lengths, allocates private control structures, binds IO handlers from component-supplied ops or built-in `io_ops`, creates TLV data, calls optional control-load hooks, registers kcontrols, and records dynamic objects on `comp->dobj_list`. Widget loading builds a DAPM template, parses embedded controls, lets the driver customize/ready the widget, creates it, and records its dobj. PCM loading creates a topology DAI plus a dynamic FE DAI link. Physical DAI and link sections configure already registered backend objects.

Removal walks passes in reverse, dispatching each dobj by type to remove controls, routes, widgets, DAIs, FE links, and backend-link dobj metadata.

## State and Persistence
Topology-created objects persist on the component `dobj_list` and through ASoC card/component structures. Most memory uses devm allocation against the card device; widget name strings are handed to DAPM ownership. Backend links are not topology-allocated, so removal resets only their dynamic-object metadata. If load fails, `snd_soc_tplg_component_load()` invokes component removal for cleanup.

## Dependencies and Integration Points
The file integrates firmware blobs, ALSA control core, ASoC component/card runtime, DAPM, DAI registration, dynamic PCM runtime creation, topology UAPI structures, built-in `soc-ops.c` callbacks, DAPM control callbacks, and optional `struct snd_soc_tplg_ops` driver hooks.

## Risks and Test Signals
Primary risks are malformed topology bounds, private-size cursor advancement, incomplete IO handler binding, duplicate or partially removed dobjs, backend link lifetime confusion, and mismatch between topology ABI sizes and kernel structures. `soc-topology-test.c` covers null inputs, bad headers, minimal PCM load, and reload loops. Additional high-value signals include fuzzed topology blobs, embedded widget controls, bytes-ext controls over 512 bytes, vendor blocks without callbacks, BE link configuration, deferred card instantiation, and failure injection in each driver hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-topology.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-usb.c -->
# sources/distributed-fs/ceph-client/sound/soc/soc-usb.c

## Purpose
This file provides a small ASoC/USB bridge for USB audio offload. It lets ASoC backend components register offload-capable USB ports, lets USB audio code discover the matching SoC context by device tree relationship, forwards connect/disconnect notifications, exposes private data lookup, checks supported USB formats, and creates a jack reporting offload availability.

## Important APIs, Types, and Functions
Exported APIs are `snd_soc_usb_setup_offload_jack()`, `snd_soc_usb_update_offload_route()`, `snd_soc_usb_find_priv_data()`, `snd_soc_usb_find_supported_format()`, `snd_soc_usb_allocate_port()`, `snd_soc_usb_free_port()`, `snd_soc_usb_add_port()`, `snd_soc_usb_remove_port()`, `snd_soc_usb_connect()`, and `snd_soc_usb_disconnect()`.

Global state is `usb_ctx_list`, protected by `ctx_mutex`. Lookup helpers are `snd_soc_find_phandle()`, `snd_soc_usb_ctx_lookup()`, and `snd_soc_find_usb_ctx()`.

## Control Flow
ASoC backend code allocates a `struct snd_soc_usb` with a component pointer and private data, fills callbacks as needed, and registers it through `snd_soc_usb_add_port()`. Registration appends the context to the global list under mutex and calls `snd_usb_rediscover_devices()` so existing USB devices can be matched.

USB-originated calls find a context by parsing the USB device's `usb-soc-be` phandle or, if no phandle is present, by matching the device node directly to a registered component's OF node. `snd_soc_usb_connect()` and `snd_soc_usb_disconnect()` invoke `connection_status_cb(ctx, sdev, true/false)` if present. Route queries invoke `update_offload_route_info()`. Private-data lookup returns `ctx->priv_data`. Format support delegates to `snd_usb_find_suppported_substream()`.

## State and Persistence
The only persistent state is the global list of registered USB offload contexts and each context's component/private-data/callback fields. List access is mutex-protected. `snd_soc_usb_free_port()` removes a port before freeing it; `snd_soc_usb_remove_port()` tolerates removal by scanning the list.

## Dependencies and Integration Points
The file integrates Open Firmware phandles, USB audio card helpers from `../usb/card.h`, ALSA jack creation (`SND_JACK_USB`), ASoC component jack setup, and backend-specific callback hooks in `struct snd_soc_usb`.

## Risks and Test Signals
Risks include stale context pointers if callbacks race with unregister, OF phandle mismatches, missing callbacks returning `-ENODEV`, and the misspelled external helper `snd_usb_find_suppported_substream()` being the required dependency. Test signals include registering/removing a port while USB devices are present, phandle and direct-node matching, connect/disconnect callback delivery, route kcontrol updates, format rejection for unsupported PCM params, and jack creation failure paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/soc-usb.c -->
