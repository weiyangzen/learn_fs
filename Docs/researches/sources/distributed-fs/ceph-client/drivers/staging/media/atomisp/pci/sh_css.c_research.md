# sources/distributed-fs/ceph-client/drivers/staging/media/atomisp/pci/sh_css.c

## Purpose
`sh_css.c` is the central host-side controller for Intel AtomISP Camera Imaging ISP Subsystem (CSS) streams. It loads CSS firmware, initializes the SP/ISP-facing runtime, creates and destroys streams and pipes, selects firmware binaries for preview/video/capture/YUV post-processing modes, builds host pipeline stages, maps queues, manages buffer enqueue/dequeue, decodes events, configures input-system paths for ISP2400 and ISP2401, and preserves enough stream state for suspend/resume style save/restore.

## Important APIs, Types, And Data
- Global CSS state is kept in `struct sh_css my_css`, including pipe slots, active pipes, IRQ type, MIPI buffer sizing, continuous-capture defaults, and flags such as `stop_copy_preview`.
- Save/restore state is modeled by `enum ia_sh_css_modes`, `struct sh_css_stream_seed`, and `struct sh_css_save my_css_save`; seeds retain stream config, pipe configs, original handles, loaded firmware/environment copies, MMU base, and IRQ type.
- Host/SP buffer bookkeeping uses `struct sh_css_hmm_buffer_record hmm_buffer_record[]` to associate queued HMM vbuf handles with buffer type and original host kernel pointer until dequeue validation releases them.
- Initialization/public runtime APIs include `ia_css_load_firmware()`, `ia_css_unload_firmware()`, `ia_css_init()`, `ia_css_uninit()`, `ia_css_start_sp()`, `ia_css_stop_sp()`, `ia_css_enable_isys_event_queue()`, `ia_css_irq_translate()`, and `ia_css_irq_enable()`.
- Pipe APIs include `ia_css_pipe_config_defaults()`, `ia_css_pipe_extra_config_defaults()`, `ia_css_pipe_create()`, `ia_css_pipe_create_extra()`, `ia_css_pipe_destroy()`, `ia_css_pipe_get_info()`, `ia_css_pipe_override_frame_format()`, `ia_css_pipe_map_queue()`, `ia_css_pipe_get_pipeline()`, `ia_css_pipe_get_pipe_num()`, and `ia_css_pipe_get_isp_pipe_version()`.
- Stream APIs include `ia_css_stream_config_defaults()`, `ia_css_stream_create()`, `ia_css_stream_destroy()`, `ia_css_stream_start()`, `ia_css_stream_stop()`, `ia_css_stream_has_stopped()`, `ia_css_stream_unload()`, `ia_css_stream_get_info()`, FIFO input helpers, continuous capture helpers, and raw-buffer locking/unlocking helpers.
- Buffer/event APIs include `ia_css_pipe_enqueue_buffer()`, `ia_css_pipe_dequeue_buffer()`, `ia_css_dequeue_psys_event()`, `ia_css_dequeue_isys_event()`, `ia_css_stream_capture_frame()`, and `ia_css_stream_capture()`.
- Binary-loading helpers choose ISP firmware binaries by pipe mode: preview (`load_preview_binaries()`), video (`load_video_binaries()`), capture variants (`load_capture_binaries()`, `load_primary_binaries()`, `load_advanced_binaries()`, `load_low_light_binaries()`, `load_bayer_isp_binaries()`), copy (`load_copy_binaries()`), and YUVPP (`load_yuvpp_binaries()`).
- Pipeline construction helpers build stage graphs for SP execution: `create_host_pipeline_structure()`, `create_host_pipeline()`, `create_host_preview_pipeline()`, `create_host_video_pipeline()`, `create_host_regular_capture_pipeline()`, `create_host_isyscopy_capture_pipeline()`, `create_host_yuvpp_pipeline()`, and `create_host_copy_pipeline()`.

## Control Flow
Firmware is first loaded through `ia_css_load_firmware()`, which resets `my_css` when the flush callback changes, loads firmware blobs, and initializes binary metadata. `ia_css_init()` then initializes pipe/pipeline/queue maps, hardware access, MMU base, GPIO flash strobe state, interrupt routing, resource manager, refcounts, parameter subsystem, SP firmware control config, DMA burst size, input system, and default GDC LUTs.

Pipes are created independently with `ia_css_pipe_create_extra()`. That path allocates a pipe, assigns a unique `pipe_num` in `my_css.all_pipes`, copies pipe and extra config, derives DVS delay, initializes optional YUV/Bayer downscale frame info, configures output and viewfinder frame metadata, and leaves binary loading until stream creation.

Streams are created by `ia_css_stream_create()`. It validates inputs and metadata, allocates the stream and pipe array, adjusts ISP2401 online/buffered-sensor mode semantics, initializes continuous raw buffer counts, configures old input receiver state or PRBS state, attaches pipes to the stream, initializes ISP parameters, handles sensor binning, creates internal copy pipes for continuous preview/video, validates effective resolutions, loads binaries for each pipe, fills `ia_css_pipe_info`, maps SP threads and buffer queues, creates empty host pipeline structures, and records a save/restore seed while in working mode.

Starting a stream with `ia_css_stream_start()` creates full host pipeline stages, registers ISP2401 CSI RX streams, configures MIPI size checks for ISP2400 buffered-sensor mode, programs the input network for ISP2400 or ISP2401, then calls `sh_css_pipe_start()`. Pipe start dispatches to preview/video/capture/YUVPP start functions, refreshes ISP parameters unless the SP does raw copy, dumps the debug graph, and sends `IA_CSS_PSYS_SW_EVENT_START_STREAM` to the appropriate SP thread(s), including copy/capture companion threads for continuous modes.

Stopping is split: `ia_css_stream_stop()` requests pipeline stop and clears ISP2400 MIPI size checks, while `ia_css_stream_destroy()` unmaps queues/threads, destroys ISP2401 virtual input streams, unregisters CSI RX streams, frees MIPI buffers for buffered-sensor mode, unloads binaries, detaches pipes from the stream, and removes save/restore seeds. `ia_css_stream_unload()` layers stream destroy plus pipe destroy for saved stream seeds.

## Pipeline And Binary Selection
Preview selects a preview binary, optional viewfinder post-processing binary, and sometimes an ISP copy binary depending on online/continuous mode and ISP generation. It may retry preview binary selection with YUV-line viewfinder output when VF post-processing is needed.

Video selects a video binary, optional cascaded YUV scaler binaries, optional VF post-processing binary, optional copy binary on ISP2400 offline/non-continuous flows, delay frames, and TNR frames. It computes invalid frame count from DVS delay and doubles it when viewfinder output also consumes delayed frames.

Capture dispatches by capture mode. RAW capture uses copy binaries or SP copy for binary/JPEG-style output; BAYER uses pre-DE; PRIMARY builds one or more primary stages plus optional capture post-processing/LDC/YUV scaler/VF post-processing; ADVANCED and LOW_LIGHT build pre/anr-or-gdc/post chains plus optional capture post-processing and copy. Capture mode determines whether viewfinder is legal and whether input must be raw.

YUVPP can add an ISP copy stage, cascaded YUV scaler stages, multiple output stages, and per-output VF post-processing. ISP2401 avoids copy except for specific YUV422 input cases, while ISP2400 generally needs copy.

## Input System, Queues, And Events
ISP2400 input setup converts stream format to MIPI format, programs the SP input circuit, configures the input formatter for online/continuous/copy cases, and configures PRBS sync generation when needed.

ISP2401 input setup translates stream config into `ia_css_isys_descr_t` descriptors, including input port ID/type, CSI/PRBS attributes, metadata format/stride/alignment, compression, packed raw setting, linked stream ID, and output-port attributes from the first binary for online flows. It then creates/calculates virtual input system streams under the SP pipeline input terminal.

`ia_css_pipe_map_queue()` maps dynamic buffer queues per SP thread and pipe kind. It conditionally maps input queues, output/VF queues, metadata, parameter queues, 3A stats, DIS stats, and multiple output-stage queues for YUVPP.

`ia_css_pipe_enqueue_buffer()` converts host buffers into `struct sh_css_hmm_buffer` payloads, allocates an HMM vbuf, stores payload into HMM, enqueues it to the SP buffer queue, records the vbuf/type/kernel pointer in `hmm_buffer_record`, and notifies the SP with `IA_CSS_PSYS_SW_EVENT_BUFFER_ENQUEUED`. `ia_css_pipe_dequeue_buffer()` reverses that path, validates the dequeued HMM address against the record table, releases the vbuf, copies exposure/config/timing metadata back into host frame/stat/metadata objects, marks invalid startup frames, and signals `BUFFER_DEQUEUED`.

`ia_css_dequeue_psys_event()` decodes 4-byte SP event payloads into host `ia_css_event` values, handles two-payload timer events, maps pipe numbers back through `find_pipe_by_num()`, redirects frame-tagged events to the capture pipe in continuous capture, and resolves acceleration firmware handles. `ia_css_dequeue_isys_event()` decodes input-system EOF events.

## State And Persistence
Most persistent runtime state is in global `my_css`, per-stream `struct ia_css_stream`, per-pipe `struct ia_css_pipe`, per-pipeline stage lists, resource-manager vbuf pools, HMM allocations, SP DMEM control variables, and hardware registers. `my_css_save` persists MMU base, IRQ type, driver environment, loaded firmware pointer, and stream seeds across power-management-style close/reopen flows.

Stream creation stores seed entries only when `my_css_save.mode == sh_css_mode_working`; destruction removes those seeds. In non-working modes, stream creation can immediately destroy the temporary stream after recreating handles. The file also stores MIPI frame sizes/counts in `my_css`, raw continuous buffers and metadata buffers in pipes, TNR/delay frames in video settings, and loaded binary state inside each pipe settings union.

SP state is initialized in `ia_css_start_sp()` by starting ISP firmware, waiting for `IA_CSS_SP_SW_INITIALIZED`, initializing host/SP control variables, setting up queues, and initializing HMM buffer records. `ia_css_stop_sp()` sends terminate, marks SP stopped, waits for SP/ISP idle, uninitializes HMM records, and clears pending parameter sets.

## Dependencies And Integration Points
This file is tightly coupled to almost every AtomISP CSS subsystem: firmware loading (`sh_css_firmware`, `ia_css_binary`), SP control (`ia_css_spctrl`, `sh_css_sp`, `sh_css_sp_group`), input system (`ia_css_isys`, `ia_css_ifmtr`, CSI RX helpers), pipeline and stage descriptors (`ia_css_pipeline`, `ia_css_pipe_*desc`, `ia_css_pipe_*stagedesc`), frame/metadata allocation (`ia_css_frame`, metadata helpers), resource manager and HMM (`ia_css_rmgr`, `hmm`), parameter/refcount subsystems (`sh_css_params`, `ia_css_refcount`), hardware accessors for MMU/GPIO/DMA/IRQ/SP/ISP, and debugging/metrics/event helpers.

It is also the primary integration layer between public `ia_css_*` APIs used by the AtomISP driver and the private SP/ISP firmware contract. Several comments require host enums and SP enums/event masks to remain synchronized, and queue/event IDs must match SP-side expectations.

## Risks
- The file mixes public API behavior, hardware programming, firmware protocol, queue lifecycle, memory allocation, and save/restore state, so regressions can cross subsystem boundaries quickly.
- ISP2400 versus ISP2401 conditionals are pervasive. Incorrect generation gating can program the wrong input system, copy path, MIPI frames, DMA burst length, queue mapping, or online/buffered-sensor semantics.
- Many paths allocate multi-stage scaler descriptors, binary arrays, delay/TNR frames, MIPI frames, metadata buffers, and HMM vbuf records; partial failure cleanup is inconsistent in places and can leak or leave stale stage state.
- `hmm_buffer_record` is a fixed global table with linear lookup and no visible locking in this file. Queue pressure, concurrent stream access, or missing dequeue paths can exhaust records or validate the wrong lifetime assumptions.
- Several functions rely on `assert()` for invariants while still dereferencing values afterward; production builds without assertions may expose null or out-of-range behavior.
- SP event decoding depends on hard-coded payload byte layouts and synchronized host/SP enum ordering. Firmware drift can silently misclassify events or map them to destroyed pipes.
- Continuous capture creates hidden copy/capture pipe relationships and reuses continuous raw buffers across pipes; mistakes in buffer counts, thread mapping, or stop/destroy ordering can strand buffers or start wrong SP threads.
- Some comments call out temporary hacks and hard-coded knowledge in VF post-processing, YUV scaler cascades, RX configuration, and SkyCam/legacy cases; these are high-risk areas for format or resolution changes.
- Stream destroy for ISP2401 reuses loop variable names in nested loops, making control flow brittle and worth extra review when modifying virtual input stream cleanup.

## Test Signals
- Firmware lifecycle: load/unload, `ia_css_init()`/`ia_css_uninit()`, SP start/stop timeout handling, repeated start/stop cycles, and idle checks on both ISP2400 and ISP2401.
- Stream lifecycle: create/start/stop/destroy/unload for preview, video, capture RAW/BAYER/PRIMARY/ADVANCED/LOW_LIGHT, copy-only, and YUVPP, including multi-pipe and continuous capture cases.
- Input modes: memory, sensor, buffered sensor, PRBS, online/offline, packed raw, metadata-enabled streams, compressed CSI2, and each CSI port/lane count.
- Format coverage: copy output verification for YUV420/YUV422/RGB/RAW/BINARY inputs, JPEG/binary copy sizing, `NV12_TILEY` override, raw bit-depth propagation, and viewfinder enable/disable combinations.
- Pipeline validation: expected stage counts/order for copy, preview+VFPP, video+TNR+DVS+YUV scaler, capture primary/LDC/capture_pp/scaler/VFPP, advanced/low-light chains, and YUVPP multi-output cascades.
- Queue and buffer tests: enqueue/dequeue every dynamic buffer type, invalid/null buffers, SP-not-running `-EBUSY`, HMM record exhaustion, stale HMM address validation, invalid startup frame countdown, metadata and timing propagation.
- Event tests: PSYS output/VF/statistics/pipeline/tag/timer/warning/assert events, ISYS EOF events, destroyed-pipe races returning `-EBUSY`, and acceleration-stage firmware-handle resolution.
- Resource cleanup: fault-injection on allocation and `ia_css_binary_find()` failure paths, repeated stream create-destroy without output frames, MIPI frame cleanup, YUV scaler descriptor cleanup, TNR/delay frame freeing, and HMM vbuf release on stop.
