# subset-b-006510 research

Grouped research for Intel Atom SST and Intel AVS ASoC source files under `sources/distributed-fs/ceph-client`. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.c

## Purpose
This file implements the Merrifield/Baytrail Atom SST DPCM control plane for ASoC. It exposes DAPM widgets, routes, mixer controls, gain controls, algorithm byte controls, SSP slot maps, SSP format programming, and DSP scheduler control, then converts those ALSA/ASoC events into packed `snd_sst_bytes_v2` IPC payloads for the SST firmware.

## Important APIs, types, and functions
The central send path is `sst_fill_byte_control()`, `sst_fill_and_send_cmd_unlocked()`, and `sst_fill_and_send_cmd()`, which marshal firmware commands into the per-device byte stream and call `sst->ops->send_byte_stream()`. Slot routing is held in static `sst_ssp_tx_map[]` and `sst_ssp_rx_map[]` and exposed through `sst_slot_get()`, `sst_slot_put()`, and `sst_send_slot_map()`. Algorithm controls are implemented by `sst_algo_bytes_ctl_info()`, `sst_algo_control_get()`, `sst_algo_control_set()`, and `sst_send_algo_cmd()`. Gain controls are implemented by `sst_gain_ctl_info()`, `sst_gain_get()`, `sst_gain_put()`, `sst_send_gain_cmd()`, and `sst_set_pipe_gain()`.

DAPM event handlers include `sst_swm_mixer_event()`, `sst_set_be_modules()`, `sst_set_media_path()`, `sst_set_media_loop()`, and `sst_generic_modules_event()`. Public integration points used by the platform driver are `sst_handle_vb_timer()`, `sst_fill_ssp_slot()`, `sst_fill_ssp_config()`, `sst_fill_ssp_defaults()`, `send_ssp_cmd()`, `sst_send_pipe_gains()`, and `sst_dsp_init_v2_dpcm()`.

## Control flow
Component probe calls `sst_dsp_init_v2_dpcm()`, which allocates the shared byte-stream buffer, creates DAPM widgets and routes, initializes default cached gain values, registers gain, algorithm, and slot controls, and maps controls to their owning DAPM pipe widgets. Mixer and path widgets then push firmware commands when DAPM powers paths on or off. Control `.put()` handlers update cached values immediately, but only send firmware updates when their associated widget is powered.

Runtime audio paths start the DSP scheduler via `sst_handle_vb_timer()`, configure SSP defaults or caller-provided DAI format/TDM values, and send `SBA_HW_SET_SSP` for supported ports. DAPM path enables send media-path or media-loop commands, then replay cached gain and algorithm module parameters for the activated pipe. Mixer DAPM changes collect active input switches and send `SBA_SET_SWM` with up to `SST_CMD_SWM_MAX_INPUTS` resolved input IDs.

## State and persistence behavior
State is in-memory only. Gain values live in static `sst_gains[]`; algorithm payloads are devm-allocated and cached in each `sst_algo_control`; slot maps are static arrays shared across controls. DAPM widget power state controls whether cached values are merely stored or also forwarded to firmware. `sst_handle_vb_timer()` keeps a static `timer_usage` reference count and toggles firmware scheduler start/idle only at the first enable and last disable.

## Dependencies and integration points
The file depends on ASoC component, DAPM, DAI, kcontrol, TLV, and route APIs; on `sst-mfld-platform.h` for `struct sst_data` and the global `sst` DSP handle; and on `sst-atom-controls.h` for command layouts and helper macros. Its firmware-facing ABI is the packed `snd_sst_bytes_v2` byte-stream contract consumed by the low-level SST driver.

## Risks and edge cases
The file relies on many firmware-defined path IDs, command IDs, and packed structures. Control-to-widget mapping is name-prefix based, so renamed controls or widgets can silently stop replaying gain/algo settings. Slot maps are static global state, not per-card. `timer_usage` is also static and must stay balanced across errors and suspend/resume. `send_ssp_cmd()` only supports `ssp0-port` and `ssp2-port`; `ssp1-port` DAI activity will not program an SSP command through this helper. Firmware command length is capped by `SST_MAX_BIN_BYTES`.

## Test signals
Useful signals include control enumeration for gain/algo/slot controls, DAPM path enable/disable logs, correct `SBA_SET_SWM`, `SBA_SET_MEDIA_PATH`, `SBA_SET_MEDIA_LOOP_MAP`, `SBA_HW_SET_SSP`, and gain IPCs under dynamic debug, playback/capture through headset/deepbuffer/compress paths, mute/unmute replay through `mute_stream`, slot-map updates while the codec widget is powered, and suspend/resume with balanced DSP scheduler usage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.h

## Purpose
This header defines the Atom SST DPCM control ABI used between the ASoC control implementation and the SST firmware. It names firmware path IDs, mixer input bits, tasks, command IDs, module IDs, packed command payloads, SSP configuration values, DAPM widget macros, and ALSA kcontrol construction macros for gain, algorithm, and slot controls.

## Important APIs, types, and functions
The header defines mixer input constants such as `SST_IP_CODEC0`, `SST_IP_PCM0`, and `SST_IP_MEDIA*`, firmware path enums `sst_path_index`, `sst_swm_inputs`, and `sst_swm_outputs`, and IPC command metadata enums `sst_ipc_msg`, `sst_cmd_type`, `sst_task`, `sst_flag`, `sst_module_id`, and `sst_cmd`. Packed firmware payloads include `struct sst_destination_id`, `struct sst_dsp_header`, `struct sst_cmd_set_swm`, `struct sst_cmd_set_media_path`, `struct sst_cmd_set_speech_path`, `struct sst_cmd_set_gain_dual`, `struct sst_cmd_sba_hw_set_ssp`, and `struct sst_param_sba_ssp_slot_map`.

The ASoC modeling layer is built with macros such as `SST_AIF_IN`, `SST_AIF_OUT`, `SST_PATH_INPUT`, `SST_PATH_OUTPUT`, `SST_SWM_MIXER`, `SST_GAIN_KCONTROLS`, `SST_ALGO_KCONTROL_BYTES`, `SST_SSP_SLOT_CTL`, and `SST_SSP_MUX_CTL`. Shared runtime metadata is represented by `struct sst_ids`, `struct sst_gain_mixer_control`, `struct sst_gain_value`, `struct sst_algo_control`, `struct sst_enum`, `struct sst_ssp_config`, and `struct sst_ssp_cfg`. Public helper prototypes are `sst_fill_ssp_slot()`, `sst_fill_ssp_config()`, and `sst_fill_ssp_defaults()`.

## Control flow
The header has no executable control flow, but it determines how `sst-atom-controls.c` builds commands and ASoC graph objects. Widget macros attach `struct sst_ids` private data to DAPM widgets. Control macros attach private metadata that later lets get/put handlers locate cached values, firmware module IDs, pipe IDs, task IDs, and owning widgets.

## State and persistence behavior
No storage is allocated here. The structures define in-memory cached state and packed firmware-visible payloads used by implementation files. The default destination macros write sentinel location/module IDs for commands addressed to firmware default routing objects.

## Dependencies and integration points
It depends on `<sound/soc.h>` and `<sound/tlv.h>`. It is included by the Atom platform and controls files and acts as the shared contract between ASoC controls, DAI SSP configuration, and the low-level SST byte-stream IPC path.

## Risks and edge cases
Packed structures and bitfields must match firmware exactly. Changing path indices, module IDs, command IDs, or field widths can break DSP routing. The DAPM and kcontrol macros use compound literals for private data, so their lifetime relies on static initializer usage. Many constants encode firmware concepts that are not validated at compile time against firmware binaries.

## Test signals
Compile coverage catches macro/type breakage. Runtime signals include correct mixer control names, correct DAPM route creation, expected byte-stream payload lengths, working SSP slot maps, and firmware acceptance of gain, media-path, mixer, and SSP commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-atom-controls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-dsp.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-dsp.h

## Purpose
This header defines the Merrifield/Baytrail SST firmware IPC ABI: mailbox offsets, IPC message IDs, firmware and stream parameter layouts, timestamp structures, byte-stream control format, codec parameter unions, allocation payloads, and helper constants used by the ASoC platform and low-level SST driver.

## Important APIs, types, and functions
Important constants include mailbox/timestamp offsets (`SST_MAILBOX_SIZE`, `SST_MAILBOX_SEND`, `SST_TIME_STAMP_MRFLD`), IPC command IDs (`IPC_IA_ALLOC_STREAM_MRFLD`, `IPC_IA_START_STREAM_MRFLD`, `IPC_IA_DRAIN_STREAM_MRFLD`, `IPC_IA_SET_PARAMS`), asynchronous firmware IDs (`IPC_IA_FW_INIT_CMPLT_MRFLD`, `IPC_SST_PERIOD_ELAPSED_MRFLD`, `IPC_IA_BUF_UNDER_RUN_MRFLD`), and `SST_ASYNC_DRV_ID`.

The IPC headers are `struct ipc_dsp_hdr`, `union ipc_header_high`, `union ipc_header_mrfld`, and legacy `union ipc_header`. Firmware metadata and response layouts include `struct ipc_header_fw_init`, `struct snd_sst_fw_version`, and `struct sst_fw_build_info`. Stream configuration is expressed through `struct snd_sst_params`, `struct snd_sst_alloc_mrfld`, `struct snd_sst_alloc_params_ext`, `struct snd_sst_stream_params`, `union snd_sst_codec_params`, and codec-specific PCM/MP3/AAC/WMA structs. Runtime data exchange uses `struct snd_sst_tstamp`, `struct snd_sst_async_msg`, `struct snd_sst_runtime_params`, and `struct snd_sst_bytes_v2`.

## Control flow
The header does not execute code. At runtime, platform code fills `snd_sst_params`, low-level stream code converts it to `snd_sst_alloc_mrfld`, IPC helpers wrap payloads with `ipc_dsp_hdr` and `ipc_header_mrfld`, and interrupt handling decodes asynchronous message IDs and timestamp buffers according to these layouts.

## State and persistence behavior
The structures model transient mailbox and firmware state. Timestamp structures persist in shared mailbox memory per stream while a stream exists. `snd_sst_bytes_v2` carries cached ASoC controls from the platform side into one IPC transaction.

## Dependencies and integration points
This file is included by `sst-mfld-platform.h` and low-level SST implementation files. It is the binary ABI with SST firmware, so it integrates ALSA PCM/compress semantics with firmware allocation, drain, pause, resume, timestamp, byte-stream, and debug messages.

## Risks and edge cases
All mailbox payloads must remain 32-bit aligned as the header warns. Several structs are packed and include bitfields, so compiler/layout changes are high risk. Some codec fields are only partially populated by current callers. Mailbox sizes and scatter buffer counts are fixed; callers must not exceed `SST_MAILBOX_SIZE` or `MAX_NUM_SCATTER_BUFFERS`.

## Test signals
Validation includes firmware boot response decoding, PCM allocation, compressed MP3/AAC allocation, timestamp reads, byte-stream set/get controls, period elapsed and drain callbacks, async error logging, and negative tests for unsupported codecs, invalid stream IDs, and oversized byte-stream payloads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-dsp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-compress.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-compress.c

## Purpose
This file implements ALSA compressed-audio operations for the Atom SST ASoC platform. It adapts `snd_compr_stream` lifecycle, codec parameters, fragment callbacks, drain callbacks, timestamps, acknowledgements, and metadata operations to the low-level `compress_sst_ops` exported by the SST DSP driver.

## Important APIs, types, and functions
The exported object is `sst_platform_compress_ops`. Stream setup uses `sst_platform_compr_open()`, `sst_platform_compr_free()`, and `sst_platform_compr_set_params()`. Runtime control is handled by `sst_platform_compr_trigger()`, `sst_platform_compr_pointer()`, `sst_platform_compr_ack()`, `sst_platform_compr_set_metadata()`, `sst_platform_compr_get_caps()`, and `sst_platform_compr_get_codec_caps()`. Firmware callbacks are bridged through `sst_compr_fragment_elapsed()` and `sst_drain_notify()`.

## Control flow
Open allocates `struct sst_runtime_stream`, obtains the registered global `sst` DSP device, stores `sst->compr_ops`, powers on the LPE, and attaches runtime private data. `set_params` fills generic stream mapping via `sst_fill_stream_params()`, translates ALSA codec IDs for MP3 and AAC into SST codec parameters, sets ring buffer address/size and fragment size, installs fragment/drain callbacks, and calls `compr_ops->open()` to allocate a firmware stream ID. Trigger commands dispatch start, stop/drop, full drain, partial drain, pause, and pause release to the low-level driver. Pointer reads firmware timestamps and calculates the ring-buffer byte offset from `copied_total`.

## State and persistence behavior
Per-stream state is a heap-allocated `sst_runtime_stream` stored in `runtime->private_data`. It holds the firmware stream ID, cumulative `bytes_written`, and low-level ops pointer. No on-disk persistence exists. Power is reference-managed through the low-level driver on open/free.

## Dependencies and integration points
The file depends on ALSA compressed offload APIs, ASoC component compressed callbacks, the global `sst` registration from `sst-mfld-platform-pcm.c`, and the low-level compressed ops from `sst_drv_interface.c`. It uses `virt_to_phys()` on the compressed runtime buffer to provide firmware ring-buffer addresses.

## Risks and edge cases
Only MP3 and AAC are supported, and AAC accepts only ADTS and RAW stream formats. `sst_platform_compr_free()` powers down before closing the firmware stream, which depends on low-level power handling tolerating that order. Pointer offset calculation mutates a local copy of `copied_total` with `do_div()`. The code assumes a single contiguous compressed buffer and one scatter-gather entry.

## Test signals
Test MP3 and AAC open/set_params/start/stop, ADTS and RAW AAC formats, invalid codec rejection, fragment elapsed callbacks, drain and partial-drain notifications, metadata calls, timestamp progression, ack byte accounting, caps reporting, and cleanup after stream allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-compress.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-pcm.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-pcm.c

## Purpose
This file is the Atom SST ASoC platform/CPU-DAI driver for PCM and compressed audio integration. It registers the global DSP device handle used by the platform, maps front-end DAI streams to firmware stream IDs and pipe IDs, creates CPU DAIs for media, deepbuffer, compressed, and SSP backends, implements PCM component operations, and coordinates SSP/vb-timer power behavior around backend activity and system sleep.

## Important APIs, types, and functions
DSP registration is exposed through `sst_register_dsp()` and `sst_unregister_dsp()`, which manage the global `struct sst_device *sst`. Stream metadata is prepared by `sst_fill_stream_params()`, `sst_fill_pcm_params()`, `sst_fill_alloc_params()`, and `sst_platform_alloc_stream()`. PCM callbacks include `sst_media_open()`, `sst_media_close()`, `sst_media_prepare()`, `sst_soc_open()`, `sst_soc_trigger()`, `sst_soc_pointer()`, `sst_soc_delay()`, and `sst_soc_pcm_new()`.

Backend DAI control uses `sst_enable_ssp()`, `sst_be_hw_params()`, `sst_set_format()`, `sst_platform_set_ssp_slot()`, and `sst_disable_ssp()`, which call helpers implemented in `sst-atom-controls.c`. The component driver is `sst_soc_platform_drv`; the platform driver is `sst_platform_driver`. The DAI table `sst_platform_dai[]` defines `media-cpu-dai`, `deepbuffer-cpu-dai`, `compress-cpu-dai`, `ssp0-port`, `ssp1-port`, and `ssp2-port`.

## Control flow
Probe allocates `struct sst_data` and platform stream-map data, initializes the mutex, stores driver data, and registers the ASoC component plus DAIs. Component probe stores the card pointer and calls `sst_dsp_init_v2_dpcm()` to create the DAPM graph and controls. FE startup allocates `sst_runtime_stream`, takes a module reference on the low-level SST driver, powers up the DSP, and applies period/buffer constraints. Prepare either drops an already allocated stream or allocates and initializes a new one, including firmware PCM parameters and period callback registration. Trigger commands call low-level start/drop/pause/resume ops and update protected stream status.

Backend startup starts the firmware scheduler and fills SSP defaults when the DAI first becomes active. Hardware params sends SSP enable once active. Shutdown sends SSP disable and idles the scheduler when the backend no longer has active users. PM prepare suspends the card, powers it off, and idles active SSPs; complete restarts active SSPs and resumes the card.

## State and persistence behavior
Runtime stream state is heap-allocated per PCM open and stored in ALSA runtime private data. Global DSP registration persists in `sst` while the low-level driver is registered. `struct sst_data` stores the platform stream map, card pointer, command byte buffer pointer, and cached SSP command. No data is persisted outside kernel memory and device/firmware state.

## Dependencies and integration points
The file integrates ALSA PCM, compressed offload, ASoC component/DAI APIs, runtime PM through the low-level ops, firmware stream mappings from `asm/platform_sst_audio.h`, and control helpers from `sst-atom-controls.c`. It is the bridge between machine drivers and the low-level SST firmware driver.

## Risks and edge cases
Stream mapping only matches device number and direction, ignoring subdevice despite receiving it. `sst_register_dsp()` holds a module reference for the registered low-level device and users take additional references on open. The `prepare` path drops an existing stream and returns immediately, relying on a later prepare for reallocation. Backend behavior depends on `snd_soc_dai_active()` counts and only `send_ssp_cmd()` supports selected SSP names. Suspend prepare manually invokes ASoC suspend/poweroff and touches active DAIs, so ordering with the wider ASoC PM core is sensitive.

## Test signals
Test platform probe, component probe, DAI registration, PCM playback/capture/deepbuffer open/prepare/start/pause/resume/stop/close, compressed DAI creation, period elapsed callbacks, pointer and delay reads, managed DMA buffer sizing, SSP enable/disable for active backends, mute-stream gain updates, and suspend/resume with active and idle DAIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform-pcm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform.h

## Purpose
This header defines the public interface between the Atom SST ASoC platform driver, compressed-audio adapter, control implementation, and low-level SST DSP driver. It declares global registration objects, PCM limits, stream status enums, stream parameter structures, low-level operation tables, runtime stream state, device registration functions, and the platform private `struct sst_data`.

## Important APIs, types, and functions
The global integration points are `extern struct sst_device *sst`, `sst_register_dsp()`, and `sst_unregister_dsp()`. PCM/compress hardware limits include `SST_MAX_BUFFER`, `SST_MIN_PERIOD_BYTES`, and period count constraints. `struct pcm_stream_info` carries firmware stream ID, period callback, buffer pointer, delay, and sample rate. `struct sst_ops` and `struct compress_sst_ops` are the low-level driver callback contracts used by platform PCM and compressed operations.

Runtime and device state is represented by `struct sst_runtime_stream`, `struct sst_device`, and `struct sst_data`. Public helpers from other files include `sst_dsp_init_v2_dpcm()`, `sst_send_pipe_gains()`, `send_ssp_cmd()`, `sst_handle_vb_timer()`, `sst_set_stream_status()`, and `sst_fill_stream_params()`.

## Control flow
The header has no executable flow. At runtime, the low-level SST driver registers an `sst_device`; the ASoC platform stores its ops in per-stream runtime state and invokes them for PCM/compress operations. Control code uses `struct sst_data` for locking, byte-stream storage, and SSP command caching.

## State and persistence behavior
All defined state is in-memory runtime state. Stream status is protected by `status_lock` in `sst_runtime_stream`; control and SSP state is protected by `sst_data.lock`. No persistent filesystem state is defined.

## Dependencies and integration points
It includes `sst-mfld-dsp.h` and `sst-atom-controls.h`, making the firmware IPC ABI and DAPM/control ABI visible to platform files. It integrates with ALSA compressed APIs through `struct snd_compress_ops` and with low-level platform data from `struct sst_platform_data`.

## Risks and edge cases
The global `sst` pointer serializes all platform users onto one registered DSP. Operation table callbacks must be present for any path that invokes them; most callers do not defensively check all PCM callbacks. Buffer constants force a fixed 800 KiB min/max PCM buffer, which can expose firmware assumptions to user-space behavior.

## Test signals
Build tests catch callback signature drift. Runtime checks include successful DSP registration/unregistration, module reference balance, stream status transitions under concurrent callbacks, platform stream parameter filling, and both PCM and compressed paths using the same low-level DSP registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst-mfld-platform.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/Makefile

## Purpose
This Kbuild file defines the Atom HiFi2 SST low-level driver modules. It builds a shared core object from common IPC, stream, loader, interface, and helper sources, and builds separate PCI and ACPI enumeration modules.

## Important APIs, types, and functions
`snd-intel-sst-core-y` aggregates `sst.o`, `sst_ipc.o`, `sst_stream.o`, `sst_drv_interface.o`, `sst_loader.o`, and `sst_pvt.o`. `snd-intel-sst-pci-y` adds `sst_pci.o`, and `snd-intel-sst-acpi-y` adds `sst_acpi.o`. The build is controlled by `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM`, `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_PCI`, and `CONFIG_SND_SST_ATOM_HIFI2_PLATFORM_ACPI`.

## Control flow
There is no runtime control flow. At build time, Kbuild links the common implementation into `snd-intel-sst-core`, and conditionally builds bus-specific enumeration modules for PCI and ACPI. Runtime entry points come from the source files selected here.

## State and persistence behavior
The Makefile has no runtime state. Its only persistent behavior is the static object composition encoded for Kbuild.

## Dependencies and integration points
It depends on Linux Kbuild and the Kconfig symbols for Atom HiFi2 SST. The object split mirrors runtime responsibilities: `sst.o` core/PM/IRQ, `sst_ipc.o` IPC post/reply, `sst_stream.o` stream commands, `sst_loader.o` firmware load, `sst_pvt.o` helpers, and PCI/ACPI bus probes.

## Risks and edge cases
Missing an object produces unresolved symbols or incomplete driver behavior. Enabling only PCI or ACPI without the core symbol would omit shared implementation. Adding new common helpers requires updating `snd-intel-sst-core-y`.

## Test signals
Build with core only, PCI enabled, ACPI enabled, and both enabled. Verify generated modules link without unresolved symbols and expose expected PCI/ACPI aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.c

## Purpose
This is the common low-level Intel SST core for Atom HiFi2 platforms. It implements Merrifield-style interrupt handling, driver operation selection, context initialization and cleanup, asynchronous firmware request startup, sysfs firmware-version reporting, runtime/system PM, and DSP memory save/restore across suspend.

## Important APIs, types, and functions
Interrupt handling is split between `intel_sst_interrupt_mrfld()` and `intel_sst_irq_thread_mrfld()`. The Merrifield operation table `mrfld_ops` wires interrupt, reset, start, post-message, process-reply, save-context, allocate-stream, and post-download callbacks. Public lifecycle helpers are `sst_driver_ops()`, `sst_alloc_drv_context()`, `sst_context_init()`, `sst_context_cleanup()`, and `sst_configure_runtime_pm()`. PM paths are `intel_sst_runtime_suspend()`, `intel_sst_suspend()`, and `intel_sst_resume()`, exported through `intel_sst_pm`.

## Control flow
Bus-specific probe code allocates a context, fills platform data/resources, and calls `sst_context_init()`. Initialization selects operation callbacks, initializes locks/lists/workqueue, sets stream state, requests the threaded IRQ, masks default interrupts, adds a CPU latency QoS request, starts asynchronous firmware caching, creates the firmware-version sysfs group, and registers the DSP with the ASoC platform. Hard IRQ acknowledges done interrupts and queues pending IPC post work; busy interrupts copy large payloads from the mailbox, enqueue `ipc_post` objects on `rx_list`, clear DSP interrupt state, and wake the threaded handler. The thread drains `rx_list` and dispatches async process messages or command replies.

## State and persistence behavior
The `intel_sst_drv` context owns global firmware state, stream contexts, IPC queues, block waiters, memory mappings, workqueue, QoS request, and cached firmware. Firmware version is exposed through sysfs. Suspend can snapshot IRAM, DRAM, SRAM/mailbox, and DDR into `struct sst_fw_save`, then restore those memories and restart firmware on resume. Runtime suspend only prepares firmware for D3 and resets the DSP.

## Dependencies and integration points
The file depends on Linux IRQ, firmware, PM runtime, PM QoS, ACPI, sysfs, ASoC, and the platform registration API in `sst-mfld-platform.h`. It coordinates helper implementations in `sst_ipc.c`, `sst_loader.c`, `sst_stream.c`, `sst_pvt.c`, and bus probes.

## Risks and edge cases
The interrupt path must handle invalid mailbox sizes and allocation failure in atomic context. `sst_context_init()` requests firmware asynchronously before actual runtime load, so callers must tolerate firmware not being cached yet. Suspend rejects running streams and optionally frees streams when platform data says streams are lost. Memory snapshot sizes use base/end fields and must match mapped ranges. Error handling around sysfs group creation removes a group that may not have been created.

## Test signals
Probe logs, IRQ registration, firmware async request, sysfs `firmware_version`, IPC done/busy interrupt behavior, runtime autosuspend, system suspend/resume with idle streams, stream reallocation after resume on Baytrail, and negative tests for missing firmware, IRQ failures, mailbox-size corruption, and active stream suspend rejection are high-value signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.h

## Purpose
This private header defines the low-level Intel SST driver model: register offsets, firmware state values, stream states, firmware binary layout, IPC wait blocks, stream contexts, memory-copy descriptors, module/library metadata, platform context, hardware operation callbacks, and cross-file function prototypes.

## Important APIs, types, and functions
Key hardware constants include `SST_CSR`, `SST_ISRX`, `SST_IMRX`, `SST_IPCX`, `SST_IPCD`, `MRFLD_FW_VIRTUAL_BASE`, and firmware context sizes. State enums are `sst_states`, `sst_stream_states`, `sst_ram_type`, and `sst_lib_dwnld_status`. IPC synchronization uses `struct sst_block`; per-stream state uses `struct stream_info`; firmware parsing uses `struct sst_fw_header`, `struct fw_module_header`, and `struct fw_block_info`; copy operations use `struct sst_memcpy_list`.

`struct intel_sst_drv` is the central context, owning mapped memories, lists, workqueue, stream array, locks, platform data, firmware cache, QoS, IPC register offsets, library memory manager, and suspend snapshot. `struct intel_sst_ops` is the platform-specific operation table. The header declares the full cross-file API for stream commands, IPC posting, firmware loading, block waits, pvt-id allocation, stream lookup, context lifecycle, PM helpers, and MMIO read/write helpers.

## Control flow
No code runs in this header, but all low-level source files implement functions declared here against the same context. Bus probes allocate and initialize `intel_sst_drv`; firmware loader populates copy lists; IPC code posts/wakes blocks; stream code mutates `streams[]`; PM code saves/restores firmware memories.

## State and persistence behavior
All persistent runtime state is represented in `intel_sst_drv` and `stream_info`. Firmware cache `fw_in_mem` and copy lists survive across runtime power cycles. `fw_save` temporarily persists memory images across system suspend. No data is written to disk.

## Dependencies and integration points
It depends on the Linux firmware API and on platform structures from `asm/platform_sst_audio.h` through implementation files. It is the contract connecting bus enumeration, firmware loading, IPC, stream control, and ASoC platform registration.

## Risks and edge cases
Many fields are shared across IRQ, workqueue, PM, and ALSA callbacks, so lock discipline is critical. Stream array index 0 is reserved. Firmware file/block layouts are trusted by the loader after signature and size checks. `pvt_id` uses a bitset with a small maximum and can exhaust under many simultaneous blocking IPCs.

## Test signals
Build coverage plus runtime coverage of all declared paths: firmware parse/load, IPC block timeout/wakeup, stream allocation/free, PM context save/restore, bus probe/remove, and MMIO helper access on target hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_acpi.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_acpi.c

## Purpose
This file provides ACPI enumeration for the Atom SST LPE driver on Baytrail, Baytrail-CR, Cherrytrail/Braswell, and special `LPE0F28` systems. It selects the SST DSP driver when appropriate, matches a machine driver, installs platform data/resource descriptors, creates companion platform devices, maps ACPI resources into the shared SST context, and starts common SST initialization.

## Important APIs, types, and functions
Platform descriptors include `byt_fwparse_info`, `byt_ipc_info`, `byt_lib_dnld_info`, `byt_rvp_res_info`, `bytcr_res_info`, `lpe8086_res_info`, `byt_rvp_platform_data`, and `chv_platform_data`. Resource mapping is implemented by `sst_platform_get_resources()`. Bus lifecycle is `sst_acpi_probe()` and `sst_acpi_remove()`, registered through `sst_acpi_driver` with ACPI IDs `LPE0F28`, `80860F28`, and `808622A8`.

## Control flow
Probe validates ACPI match, consults `snd_intel_acpi_dsp_driver_probe()` to avoid binding when another DSP driver is selected, finds a matching ASoC machine, chooses Baytrail or Cherrytrail platform data, handles `LPE0F28` resource quirks, parses the ACPI HID as a device ID for normal IDs, and switches Baytrail-CR to a different IRQ resource index. It registers the SST platform component device and the machine device, fills firmware name from the machine data, maps IRAM, DRAM, SHIM, mailbox, DDR, and IRQ resources, calls `sst_context_init()`, enables runtime PM, and stores the context on the platform device.

## State and persistence behavior
Resource descriptors are static, with one mutable pointer in Baytrail platform data adjusted for Baytrail-CR or `LPE0F28`. Runtime state is held in `intel_sst_drv` and platform devices. No persistent storage is written.

## Dependencies and integration points
The file integrates ACPI, platform-device registration, Intel DSP selection, SOF/SST machine-match tables, Baytrail/Cherrytrail quirks, and common SST lifecycle helpers. It passes machine data to board drivers and `sst_platform_info` to the common SST core.

## Risks and edge cases
The static `byt_rvp_platform_data.res_info` is modified based on the probed system, which is acceptable for one device but fragile if multiple variants were present. `LPE0F28` mutates a resource range in place to synthesize an LPE base range. The code registers the platform and machine devices before resource mapping and context init; failures after registration may leave cleanup to device management outside this function.

## Test signals
Test ACPI match on `80860F28`, `808622A8`, Baytrail-CR IRQ index selection, `LPE0F28` resource patching, machine-driver discovery, firmware-name propagation, all ioremap failures, IRQ lookup, runtime PM enablement, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_drv_interface.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_drv_interface.c

## Purpose
This file exposes the low-level SST DSP services to the ASoC platform through `struct sst_ops` and `struct compress_sst_ops`. It translates PCM/compressed open, close, start, stop, pause, drain, timestamp, byte-stream, metadata, capability, and power requests into common SST firmware operations and registers the resulting `sst_device` with the platform driver.

## Important APIs, types, and functions
PCM-facing helpers include `sst_open_pcm_stream()`, `sst_close_pcm_stream()`, `sst_stream_init()`, `sst_stream_start()`, `sst_stream_drop()`, `sst_stream_pause()`, `sst_stream_resume()`, `sst_read_timestamp()`, and `sst_send_byte_stream()`. Compressed-facing helpers include `sst_cdev_open()`, `sst_cdev_close()`, `sst_cdev_stream_start()`, `sst_cdev_stream_drop()`, `sst_cdev_stream_drain()`, `sst_cdev_tstamp()`, `sst_cdev_ack()`, `sst_cdev_caps()`, `sst_cdev_codec_caps()`, and `sst_cdev_set_metadata()`. `sst_power_control()` handles runtime PM and firmware load-on-demand. `sst_register()` and `sst_unregister()` bridge to `sst_register_dsp()` and `sst_unregister_dsp()`.

## Control flow
The platform powers on the DSP through `sst_power_control(true)`. If runtime PM resumes the device from reset and this is the first user, firmware is loaded. PCM open allocates a firmware stream using `sst_get_stream()`, while stream init installs PCM period callbacks and substream pointers. Trigger paths update stream status and send firmware start/drop/pause/resume commands. Timestamp reads copy firmware timestamp memory and convert ring/hardware counters into ALSA pointer and delay values. Compressed open allocates a stream and stores fragment/drain callbacks; ack updates cumulative bytes in the firmware timestamp area; drain is asynchronous and completes through the callback.

## State and persistence behavior
The file mutates `ctx->streams[]`: status, callbacks, substream pointers, cumulative bytes, channel count, pipe ID, and task ID. `ctx->stream_cnt` tracks PCM streams. The static `sst_dsp_device` stores callback tables and a current device pointer for registration. Capabilities are static for MP3 and AAC.

## Dependencies and integration points
It depends on runtime PM, PM QoS, ALSA PCM/compress APIs, firmware stream helpers in `sst_stream.c`, IPC helpers in `sst_pvt.c`, and global platform registration in `sst-mfld-platform-pcm.c`. It is the main boundary consumed by the ASoC platform and compressed layer.

## Risks and edge cases
`sst_power_control()` uses runtime PM usage count to decide when to load firmware, which is sensitive to reference balance. PCM `sst_stream_start()` returns success when firmware is not running, masking some state races. Timestamp math assumes firmware counters are coherent and uses 24-bit sample width for compressed IO frames. `sst_cdev_close()` does not runtime-put directly; power down is done by the platform compressed free path.

## Test signals
Test firmware load on first power-up, PCM open/init/start/drop/pause/resume/close, compressed MP3/AAC open/start/drain/ack/tstamp/close, byte-stream control commands, caps output, timestamp pointer/delay correctness, runtime PM reference balance, and error paths for invalid stream IDs or reset firmware state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_drv_interface.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_ipc.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_ipc.c

## Purpose
This file implements Merrifield-style SST IPC posting, interrupt acknowledgement, synchronous wait-block matching, firmware-init processing, asynchronous firmware notifications, and command reply processing.

## Important APIs, types, and functions
Wait-block management is `sst_create_block()`, `sst_wake_up_block()`, and `sst_free_block()`. Host-to-DSP posting is `sst_post_message_mrfld()`, with deferred queue support through the context `ipc_dispatch_list`. Interrupt completion is handled by `intel_sst_clear_intr_mrfld()`. Firmware async processing is split across `process_fw_init()` and `process_fw_async_msg()`. Replies are decoded by `sst_process_reply_mrfld()`.

## Control flow
Synchronous callers create an `sst_block`, post an IPC, and sleep on the shared waitqueue. When a DSP reply arrives, `sst_process_reply_mrfld()` matches by IPC message ID and private driver ID, stores result/data in the block, and wakes the waiter. `sst_post_message_mrfld()` either busy-waits for a free IPCX register for synchronous sends or pulls the next queued dispatch-list message when the done interrupt/workqueue path indicates the DSP is ready. Large messages copy mailbox payload data before writing the IPC header.

Async firmware messages use driver ID zero. Period elapsed messages locate the stream by firmware pipe ID and call PCM and compressed callbacks unless the stream has been dropped back to init state. Drain messages call the compressed drain callback. Firmware init complete stores version/build information and releases the firmware-download waiter. Async error and underrun messages are logged.

## State and persistence behavior
Blocks live on `ctx->block_list` until matched, timed out, or freed. Posted messages are transient heap allocations. Firmware version persists in `ctx->fw_version`. The code mutates stream callbacks indirectly through async notifications but does not own stream allocation.

## Dependencies and integration points
It depends on shim/MMIO helpers from `sst_pvt.c`, IPC structures from `sst-mfld-dsp.h`, stream lookup from `sst_pvt.c`, and stream callbacks installed by `sst_drv_interface.c`. It is invoked from the top/bottom IRQ paths in `sst.c`.

## Risks and edge cases
Large mailbox payload size validation is done in the IRQ path, but this file trusts `msg_low` when duplicating reply payloads. `sst_post_message_mrfld()` frees messages even on posting failure. Block matching logs missing blocks only at debug level, which avoids log spam but can hide protocol mismatch. Period elapsed depends on unique pipe IDs in `streams[]`.

## Test signals
Test blocking IPC success, blocking IPC timeout, queued nonblocking IPC dispatch after done interrupt, large and short replies, firmware init complete, period elapsed callbacks, drain callbacks, buffer underrun logs, firmware async errors, and malformed/unmatched replies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_ipc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_loader.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_loader.c

## Purpose
This file controls SST DSP reset/start and firmware loading. It parses Intel SST firmware containers, builds a list of memory-copy operations for IRAM/DRAM/DDR blocks, caches firmware in host memory, transfers parsed blocks to DSP memory, writes Merrifield DCCM configuration, starts the DSP, and waits for firmware initialization.

## Important APIs, types, and functions
MMIO copy helpers are `memcpy32_toio()` and `memcpy32_fromio()`. DSP control is `intel_sst_reset_dsp_mrfld()` and `sst_start_mrfld()`. Firmware validation/parsing is performed by `sst_validate_fw_image()`, `sst_parse_module_memcpy()`, and `sst_parse_fw_memcpy()`. Copy-list management is `sst_fill_memcpy_list()`, `sst_do_memcpy()`, and `sst_memcpy_free_resources()`. Firmware cache/load entry points are `sst_firmware_load_cb()`, `sst_request_fw()`, `sst_post_download_mrfld()`, and `sst_load_fw()`.

## Control flow
Firmware can be requested asynchronously during context init or synchronously on first runtime power-up if not already cached. The loader validates `$SST` signature and file size, iterates module headers and block headers, skips custom-info blocks, and records IO copies for IRAM, DRAM, or DDR destinations. `sst_load_fw()` requires the device in reset, creates a firmware-download block, raises CPU latency QoS, resets the DSP, copies all firmware blocks, writes DDR base/BSS reset data into DCCM, starts the DSP, waits for firmware init completion, restores QoS, frees the block, optionally restores DSP context, and marks firmware running.

## State and persistence behavior
Cached firmware bytes live in `ctx->fw_in_mem`; parsed copy operations live in `ctx->memcpy_list`; both persist until context cleanup. Firmware load mutates DSP IRAM/DRAM/DDR and `ctx->sst_state`. No filesystem writes occur.

## Dependencies and integration points
It depends on the Linux firmware loader, QoS APIs, MMIO helpers, IPC block waits from `sst_pvt.c`, firmware init wakeup from `sst_ipc.c`, and platform memory ranges in `intel_sst_drv`.

## Risks and edge cases
Firmware parsing validates top-level signature/size but otherwise trusts module sizes and block offsets. `sst_load_fw()` logs success even when `ret_val` is an error after the restore label. `sst_start_mrfld()` contains an unusual debug string. Copy sizes are divided by four, so non-32-bit-aligned firmware blocks would be truncated by copy helpers. Multiple cache parses can append duplicate copy-list entries if not guarded by state.

## Test signals
Test missing firmware, invalid signature/size, valid firmware parse, IRAM/DRAM/DDR block copies, custom-info skip, DSP reset/start register writes, firmware init timeout, QoS update/restore, DCCM DDR-base write, and repeated runtime power cycles using cached firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_loader.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pci.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pci.c

## Purpose
This file provides legacy PCI enumeration for the Intel SST LPE driver on Merrifield/Tangier-style devices. It maps PCI BAR resources, validates relocated DDR/IMR firmware base expectations, initializes the common SST context, and registers runtime PM for PCI-bound hardware.

## Important APIs, types, and functions
Resource mapping is implemented by `sst_platform_get_resources()`. PCI lifecycle is `intel_sst_probe()` and `intel_sst_remove()`, registered through `sst_driver` and the `intel_sst_ids` PCI table. It uses `relocate_imr_addr_mrfld()` to compare the PCI DDR base against platform library metadata.

## Control flow
Probe allocates `intel_sst_drv`, stores platform data from `pci->dev.platform_data`, records the IRQ and firmware filename, calls `sst_context_init()`, enables the PCI function, stores a PCI reference, maps DDR/SHIM/mailbox/IRAM/DRAM resources, stores driver data, and configures runtime PM. Remove calls common cleanup, releases the PCI reference, and clears driver data.

## State and persistence behavior
The file creates no persistent state beyond fields in `intel_sst_drv` and the PCI driver-data pointer. PCI-managed region and ioremap resources are tied to the PCI device lifetime.

## Dependencies and integration points
It depends on PCI core APIs, platform data supplied to the PCI device, common SST context helpers, and firmware/library metadata from `asm/platform_sst_audio.h`. Runtime PM callbacks are provided by `intel_sst_pm`.

## Risks and edge cases
The probe calls `sst_context_init()` before enabling the PCI device and before mapping resources, but common context init requests IRQ and can rely on mapped `shim` fields, making ordering especially sensitive for this legacy path. DDR mapping and base validation only apply to `PCI_DEVICE_ID_INTEL_SST_TNG`. Missing `lib_info` or relocated base mismatch fails probe.

## Test signals
Test PCI probe/remove on supported Tangier hardware, BAR request/mapping failures, DDR base relocation validation, firmware filename selection, IRQ handling after resource mapping, runtime PM enablement, and cleanup after partial probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pvt.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pvt.c

## Purpose
This file contains private helper routines for SST MMIO access, firmware-state updates, IPC wait timeouts, IPC message/block allocation, generic IPC construction, runtime PM put, header filling, private ID allocation, stream validation/lookup, IMR address relocation, and queued IPC dispatch.

## Important APIs, types, and functions
MMIO helpers are `sst_shim_write()`, `sst_shim_read()`, `sst_reg_read64()`, `sst_shim_write64()`, and `sst_shim_read64()`. Synchronization helpers are `sst_set_fw_state_locked()`, `sst_wait_timeout()`, `sst_create_ipc_msg()`, `sst_create_block_and_ipc_msg()`, and `sst_assign_pvt_id()`. Message construction is handled by `sst_prepare_and_post_msg()`, `sst_fill_header_mrfld()`, and `sst_fill_header_dsp()`. Stream helpers are `sst_clean_stream()`, `sst_validate_strid()`, `get_stream_info()`, and `get_stream_id_mrfld()`. `relocate_imr_addr_mrfld()` maps physical DDR base into the firmware virtual IMR window.

## Control flow
Most firmware commands call `sst_prepare_and_post_msg()`: allocate a private ID, optionally create a wait block, create an IPC message, fill the host and DSP headers, copy payload data, post synchronously or queue asynchronously, wait for response when requested, duplicate returned data for the caller, free the block, and clear the private-ID bit. `sst_wait_timeout()` waits up to `SST_BLOCK_TIMEOUT`; on timeout it marks firmware reset and returns `-EBUSY`.

## State and persistence behavior
The helper mutates `ctx->sst_state`, `ctx->pvt_id`, `ctx->ipc_dispatch_list`, stream status fields, and runtime PM usage through `pm_runtime_put_autosuspend()`. Message and block allocations are transient.

## Dependencies and integration points
It is shared by loader, IPC, stream, interface, PCI, and PM code. It depends on waitqueues, spinlocks, runtime PM, firmware IPC structures, and MMIO accessors.

## Risks and edge cases
`sst_prepare_and_post_msg()` assumes large messages have allocated mailbox data before copying DSP headers. If message allocation succeeds but block allocation fails, the large-message mailbox buffer is not separately freed in the error path. Private IDs are limited by `SST_MAX_BLOCKS` and use bit operations on `volatile long unsigned pvt_id`. Timeouts forcibly set firmware reset state, affecting unrelated users.

## Test signals
Test IPC construction for large/short, sync/async, response/no-response combinations; private ID exhaustion; wait timeout; stream ID validation; pipe-to-stream lookup; IMR relocation math; runtime PM put errors; and dispatch-list posting while IPC is busy/free.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_pvt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_stream.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_stream.c

## Purpose
This file implements firmware stream allocation and stream-control IPCs for Merrifield-style SST: allocate/reallocate, start, byte-stream set/get, pause, resume, drop, drain, and free. It owns the translation from `snd_sst_params` into the firmware `snd_sst_alloc_mrfld` payload cached per stream.

## Important APIs, types, and functions
The allocation path is `sst_alloc_stream_mrfld()` and `sst_realloc_stream()`. Runtime command APIs are `sst_start_stream()`, `sst_pause_stream()`, `sst_resume_stream()`, `sst_drop_stream()`, `sst_drain_stream()`, and `sst_free_stream()`. Generic control-byte IPCs are sent through `sst_send_byte_stream_mrfld()`.

## Control flow
Allocation stores operation, codec type, scatter/ring buffer address and size, fragment size, codec params, channel map, pipe ID, task ID, channel count, and timestamp address in `stream_info`, then calls `sst_realloc_stream()`. Reallocation sends `IPC_IA_ALLOC_STREAM_MRFLD` and inspects the returned allocation response; `SST_ERR_STREAM_IN_USE` triggers a firmware free attempt. Start requires `STREAM_RUNNING` state and sends `IPC_IA_START_STREAM_MRFLD`. Pause/resume validate state, send blocking firmware commands, and update `status`/`prev`; resume has special handling for streams recreated after suspend. Drop resets the stream to init state and sends a nonblocking drop. Drain sends a nonblocking drain and relies on async drain notifications. Free sends `IPC_IA_FREE_STREAM_MRFLD`, then cleans host stream state.

## State and persistence behavior
Each stream's cached allocation payload persists in `ctx->streams[str_id].alloc_param`, enabling resume-time reallocation. `status`, `prev`, `resume_status`, `resume_prev`, `pipe_id`, `task_id`, `num_ch`, and cumulative bytes are mutated by these commands. Byte-stream commands use transient IPC messages and optional wait blocks.

## Dependencies and integration points
It depends on `sst_prepare_and_post_msg()`, `sst_send_byte_stream_mrfld()` consumers in the ASoC control layer, stream parameter helpers from `sst_drv_interface.c`, firmware timestamp offsets, and platform LPE viewpoint settings.

## Risks and edge cases
State transitions are partly protected by stream mutexes and partly direct assignments. `sst_start_stream()` rejects if the caller did not pre-set status to running. Drop is sent without waiting for a response. Byte-stream get copies back `bytes->len` from block data without checking reply size. Timestamp address calculation differs depending on `lpe_viewpt_rqd`.

## Test signals
Test PCM and compressed allocation, firmware allocation failure, stream-in-use recovery, channel maps for mono/stereo/multichannel, start state validation, pause/resume from running and init, recreated-stream resume cases, drop without response, drain callback delivery, free after reset, and byte-stream set/get controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/atom/sst/sst_stream.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/Makefile -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/Makefile

## Purpose
This Kbuild file defines the Intel AVS ASoC driver module and board subdirectory integration. It aggregates the generic AVS core, IPC, topology, path, PCM, loader, board-selection, control, sysfs, platform-specific DSP operations, trace support, and optional debugfs/probe support.

## Important APIs, types, and functions
`snd-soc-avs-y` includes common objects `dsp.o`, `ipc.o`, `messages.o`, `utils.o`, `core.o`, `loader.o`, `topology.o`, `path.o`, `pcm.o`, `board_selection.o`, `control.o`, and `sysfs.o`; CLDMA support `cldma.o`; platform variants `skl.o`, `apl.o`, `cnl.o`, `icl.o`, `tgl.o`, `mtl.o`, `lnl.o`, and `ptl.o`; and `trace.o`. `CFLAGS_trace.o := -I$(src)` supports `define_trace.h` include resolution. When `CONFIG_DEBUG_FS` is set, `probes.o` and `debugfs.o` are added. `obj-$(CONFIG_SND_SOC_INTEL_AVS)` builds `snd-soc-avs.o`, and `obj-$(CONFIG_SND_SOC) += boards/` enters machine support.

## Control flow
There is no runtime control flow. Build-time composition determines which platform-specific `avs_dsp_ops` objects and optional debug interfaces are linked into the AVS module.

## State and persistence behavior
The file has no runtime state. Its persistent effect is the Kbuild object graph.

## Dependencies and integration points
It depends on Kbuild, `CONFIG_SND_SOC_INTEL_AVS`, `CONFIG_DEBUG_FS`, and `CONFIG_SND_SOC`. The object list must stay aligned with prototypes in `avs.h` and with PCI platform descriptors in `core.c`.

## Risks and edge cases
Omitting a platform object breaks PCI IDs that reference its operation table. Omitting `trace.o` breaks tracepoint definitions; the special include flag is required for trace header generation. Debugfs objects must stay conditional on `CONFIG_DEBUG_FS`.

## Test signals
Build with AVS built-in and module, with and without debugfs, and with board support enabled. Check for unresolved symbols from platform operation tables, trace definitions, and debugfs/probe functions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/apl.c -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/apl.c

## Purpose
This file implements Apollo Lake/Goldmont-class platform-specific AVS DSP operations. It handles IPC interrupt recognition, debug-log enablement, log buffer draining, firmware coredump collection, and D0ix low-power policy for cAVS 1.5/1.8 style firmware.

## Important APIs, types, and functions
`avs_apl_dsp_interrupt()` checks `AVS_ADSP_REG_ADSPIS` and dispatches IPC interrupts to `avs_skl_ipc_interrupt()`. Under debugfs, `avs_apl_enable_logs()` builds `avs_apl_log_state_info` and sends `avs_ipc_set_enable_logs()`. Log handling is `avs_apl_log_buffer_status()` and `avs_apl_wait_log_entry()`. Crash collection is `avs_apl_coredump()`, using firmware register windows and log payload buffers. Power policy is `avs_apl_lp_streaming()`, `avs_apl_d0ix_toggle()`, and `avs_apl_set_d0ix()`. The exported operation table is `avs_apl_dsp_ops`.

## Control flow
On interrupt, the handler reads ADSPIS, ignores invalid `UINT_MAX` reads, and services IPC when the IPC bit is set. Log-buffer notifications read firmware log layout, optionally dump wrapped and linear payload regions to the tracing FIFO, and always advance the firmware-visible read pointer. Coredump captures the firmware register window, optionally drains pre-stack logs, waits up to 10 ms for stack-dump log entries, copies wrapped log payload data until the requested stack size is gathered, updates read pointers, and submits the dump through `dev_coredumpv()`.

D0ix policy wakes unconditionally when requested. When considering sleep, it permits D0ix if no paths are active or if every gateway copier in every active path has `lp_buffer_alloc` set. `avs_apl_set_d0ix()` tells firmware whether D0ix is being entered with active low-power streaming.

## State and persistence behavior
This file does not own long-lived state, but it reads and updates firmware log-buffer read pointers, consumes trace data into AVS logging infrastructure, and walks `adev->path_list` under `path_list_lock`. Coredumps are handed to the kernel devcoredump facility.

## Dependencies and integration points
It depends on HD-audio extended register access, AVS messages, path/topology models, log-buffer helpers, debugfs logging infrastructure, devcoredump, and generic HDA firmware load operations. Its operation table is referenced by AVS platform descriptors for APL/GLK-class devices.

## Risks and edge cases
Log pointer handling must handle wraparound correctly and avoid reading stale data. Coredump stack collection may be incomplete if stack entries do not arrive before timeout, but register data is still dumped. D0ix traversal assumes copier modules with gateway attributes are represented in active paths and that `lp_buffer_alloc` correctly models low-power buffer placement. `resource_mask` validation in log enablement depends on `fls_long()` versus actual DSP core count.

## Test signals
Test IPC interrupt recognition, log enable/disable per core, log buffer wraparound draining, behavior with no log consumer, coredump with and without stack dump, coredump timeout, D0ix allow/deny for no paths, all-LP gateways, and any non-LP gateway, plus firmware return-code conversion through `AVS_IPC_RET()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/apl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/avs.h -->
# sources/distributed-fs/ceph-client/sound/soc/intel/avs/avs.h

## Purpose
This is the main private header for the Intel AVS ASoC driver. It defines platform operation tables, platform descriptors, core driver state, IPC message/context structures, platform attributes, helper macros, and cross-file prototypes for DSP control, IPC, firmware resources, firmware loading, component registration, board registration, topology parsing, debug logging, D0ix, and sysfs integration.

## Important APIs, types, and functions
`struct avs_dsp_ops` abstracts per-platform DSP operations such as core power/reset/stall, interrupt handling, firmware/library loading, log handling, coredump, D0ix policy, and log enablement. `struct avs_spec` describes a platform by name, minimum firmware version, boot core mask, attributes, SRAM windows, HIPCI register layout, and operation table. Platform attributes include `AVS_PLATATTR_CLDMA`, `IMR`, `ACE`, and `ALTHDA`.

`struct avs_dev` is the central runtime object and embeds `struct hda_bus`. It owns DSP BAR mapping, spec pointer, IPC context, firmware/hardware/module configuration, module instance ID allocators, pipeline ID allocator, loaded firmware list, core reference counts, library names, L1SEN counter, firmware-ready completion, probe work, component/path lists and locks, trace state, and optional debugfs/probe fields. `struct avs_ipc_msg` and `struct avs_ipc` model request/reply payloads, completions, serialization, recovery, and D0ix state. `AVS_IPC_RET()` converts positive firmware error codes to `-EREMOTEIO`.

## Control flow
The header itself does not execute code. PCI core code selects an `avs_spec`, generic code calls `avs_dsp_op()` for platform-specific operations, IPC code fills `avs_ipc_msg` and uses `avs_ipc` completions, loader code manages firmware entries, topology/path code allocates modules and pipelines, and PCM/control code registers ASoC components and paths.

## State and persistence behavior
All AVS runtime state is in `avs_dev` and `avs_ipc`. Firmware list entries hold requested firmware objects until released. Module and pipeline IDA pools persist while topology paths exist. D0ix and recovery flags persist in the IPC context. Debug trace buffers are in-memory only, except coredumps emitted through kernel devcoredump.

## Dependencies and integration points
The header depends on Linux device, firmware, kfifo, debugfs, HD-audio, and ASoC component APIs plus local `messages.h` and `registers.h`. It is included by most AVS implementation files and defines the internal ABI for the module.

## Risks and edge cases
Because this header centralizes cross-file contracts, signature drift affects many objects in `Makefile`. `avs_dsp_op()` assumes the platform operation pointer exists. `to_avs_dev()` assumes device driver data is an HD-audio bus. IPC callers must consistently apply `AVS_IPC_RET()` after consuming firmware error codes. Optional debugfs fields must only be used under `CONFIG_DEBUG_FS`.

## Test signals
Compile all AVS objects and platform variants. Runtime signals include PCI platform descriptor selection, firmware boot, IPC request/reply completions, recovery and D0ix state transitions, module/pipeline ID allocation/free, board/component registration, trace/debugfs behavior when enabled, and disabled-debugfs builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/intel/avs/avs.h -->
