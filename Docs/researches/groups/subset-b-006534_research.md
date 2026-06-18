# subset-b-006534 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.c

Purpose: `q6afe.c` implements the legacy APR-backed Qualcomm QDSP6 Audio Front End service driver. It owns AFE port objects, maps source-tree port indexes to DSP AFE port IDs, sends configuration/start/stop/clock messages to the DSP, and exposes helper APIs used by backend DAI drivers for HDMI/DP, Slimbus, MI2S, TDM, codec DMA, and USB audio paths.

Important APIs and types: `struct q6afe` stores the APR device, service API info, command wait state, lock, and live port list. `struct q6afe_port` stores one configured DSP port, including wait queue, token, DSP ID, config union, optional TDM slot map, result, kref, and list node. The large `port_maps[]` table is the persistent in-memory mapping from LPASS/DT port IDs to DSP AFE port IDs and RX/TX direction metadata. Exported APIs include `q6afe_get_port_id`, `q6afe_port_get_from_id`, `q6afe_port_put`, `q6afe_port_start`, `q6afe_port_stop`, `q6afe_*_port_prepare`, `q6afe_port_set_sysclk`, `q6afe_set_lpass_clock`, `q6afe_vote_lpass_core_hw`, and `q6afe_unvote_lpass_core_hw`.

Control flow: probe allocates `q6afe`, initializes wait queues, locks, and the port list, then populates child devices. Callers obtain ports with `q6afe_port_get_from_id`, which validates the index, chooses a parameter ID based on the DSP port range, allocates a kref-managed port, and adds it to `port_list`. Prepare functions fill the cached packed DSP config. Start first sends `AFE_PORT_CMD_SET_PARAM_V2` with the cached config, optionally sends TDM slot mapping, then sends `AFE_PORT_CMD_DEVICE_START`; stop sends `AFE_PORT_CMD_DEVICE_STOP`. `afe_apr_send_pkt` serializes commands through `afe->lock`, sends the APR packet, and waits up to `TIMEOUT_MS` for `q6afe_callback` to fill the matching result.

State and persistence: all state is runtime kernel memory. Port lifetimes are tracked by krefs, with callback lookup temporarily taking a reference to avoid freeing while a response is being handled. DSP-side memory is not persisted; clock and port configuration must be resent after port creation/start. TDM slot mapping is heap-allocated in the port and freed with the port.

Dependencies and integration points: the driver depends on APR, `q6core_get_svc_api_info`, ALSA SoC types, dt-bindings for q6afe ports, and q6dsp errno definitions. It is the service layer below `q6afe-dai`/LPASS DAI users and below common clock providers that call into `q6afe_set_lpass_clock`.

Risks: command matching uses shared result fields and serialized command locking, so missing callbacks cause 3-second stalls. `q6afe_usb_port_prepare` stores only sample rate/channels/bit width before sending extra USB LPCM/service-interval params, so unset `endian` or `service_interval` fields remain zero unless higher layers fill them. `q6afe_tdm_port_prepare` silently returns if slot-map allocation fails, leaving `q6afe_port_start` to start without slot mapping. Port-map correctness is critical; a wrong token or cfg type sends valid-looking commands to the wrong DSP endpoint.

Test signals: probe should create child devices for `qcom,q6afe`. Port tests should cover valid/invalid IDs, I2S SD-line masks, TDM slot maps, start/stop timeout/error responses, clock enable/disable paths, USB parameter programming, and kref behavior when callbacks race with port release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.h

Purpose: `q6afe.h` is the public interface for the legacy Q6 AFE service. It defines LPASS clock IDs, port limits, channel-map constants, and per-transport configuration structs consumed by `q6afe.c` and DAI drivers.

Important APIs and types: key structs are `q6afe_hdmi_cfg`, `q6afe_slim_cfg`, `q6afe_i2s_cfg`, `q6afe_tdm_cfg`, `q6afe_cdc_dma_cfg`, `q6afe_usb_cfg`, and the aggregate `q6afe_port_config`. The opaque `struct q6afe_port` enforces use through helper functions. Exported declarations cover port acquisition/lifetime, start/stop, virtual-to-DSP port lookup, transport-specific prepare helpers, `q6afe_port_set_sysclk`, global clock setting, codec DMA/TDM preparation, USB device-token programming, and LPASS core vote/unvote.

Control flow: users include this header, call `q6afe_port_get_from_id`, fill one of the transport config structs, call the matching prepare routine, optionally configure clocks or USB device tokens, start the port, then stop and put it. The header does not execute logic but establishes the required order and data contracts for `q6afe.c`.

State and persistence: no state is stored here. The constants are ABI-like DSP command values and must remain stable relative to firmware expectations. Config structs are copied by callers into the runtime port object.

Dependencies and integration points: the header includes `../common.h` for `LPASS_MAX_PORT` and channel/port definitions. It integrates backend DAI implementations with AFE service internals while hiding `struct q6afe_port` fields.

Risks: several clock ID ranges overlap by design, notably PCM/TDM IDs, so callers must pass the correct semantic clock and transport. Channel-map size is fixed at eight, and unsupported layouts require validation before reaching firmware. Changing struct field widths or constant values breaks packed messages built in `q6afe.c`.

Test signals: compile coverage from all AFE DAI users is the primary signal. Runtime tests should verify each declared helper is exported by `q6afe.c` and that expected clock IDs produce firmware-visible clock commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6afe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-dai.c

Purpose: `q6apm-dai.c` is the ALSA SoC frontend DAI component for AudioReach APM graphs. It exposes PCM and compressed playback interfaces, maps ALSA buffers into DSP shared memory, programs graph media formats, queues period buffers, and translates graph callbacks into ALSA period/compress notifications.

Important APIs and types: `struct q6apm_dai_rtd` is per-stream runtime state with substream/compress stream, codec params, DMA buffer, physical address with optional SID bits, PCM size/count/periods, byte counters, queue pointer, state, graph pointer, spinlock, and drain flags. `q6apm_fe_dai_component` registers component callbacks: `open`, `close`, `prepare`, `pcm_new`, `pcm_free`, `hw_params`, `pointer`, `trigger`, `ack`, and compress ops. `q6apm_compr_caps` describes compressed capabilities; supported compressed codecs are MP3, AAC, FLAC, and raw OPUS.

Control flow: PCM `open` allocates runtime state, opens the APM graph keyed by CPU DAI ID, applies hardware constraints, and derives the physical address from the fixed DMA buffer plus optional IOMMU SID. `pcm_new` allocates fixed DMA buffers and maps the whole max buffer with `q6apm_map_memory_fixed_region`. `prepare` sets shared-memory and PCM media format, allocates period fragments, prepares and starts the graph, and queues capture reads. Playback `ack` queues writes for newly advanced ALSA periods. Callback paths update ALSA via `snd_pcm_period_elapsed`.

Compressed control flow: `compr_open` allocates a coherent DMA buffer, opens a playback graph, and enables the placeholder decoder. `set_params` sets the real decoder module ID, sends media format, maps fragments, prepares and starts the graph, or for next-track updates sends compressed params only. `copy` writes user data into a ring buffer and kicks the DSP if no data is in flight. Write-done callbacks advance `copied_total`, queue more bytes, and send EOS on drain.

State and persistence: all stream state is per-open and freed on close/free. DSP memory maps persist for the PCM lifetime and are unmapped by `pcm_free`; compressed maps are released in `compr_free`. Byte counters and queue pointers are protected by spinlock for compress paths but PCM `queue_ptr` arithmetic depends on ALSA callback ordering.

Dependencies and integration points: this file depends on `q6apm.h`, AudioReach helpers, ALSA PCM/compress APIs, DMA mapping, and DT IOMMU SID parsing. It integrates frontend CPU DAIs with AudioReach graphs created by `q6apm.c`.

Risks: `q6apm_dai_compr_open` leaks the graph/runtime state if `snd_dma_alloc_pages` fails after graph open. `q6apm_dai_close` assumes `runtime->private_data` and `graph` are valid. Playback `ack` computes available periods by simple subtraction of appl_ptr and queue_ptr without wrap handling. Compress get-codec-caps only fills MP3 despite advertising other codecs. Errors from some async writes and EOS sends are ignored.

Test signals: exercise PCM playback/capture open, prepare, start, stop, pointer, and close; verify fixed-buffer map/unmap pairing; test compressed set_params/copy/drain/partial-drain/next-track; inject graph command failures and DMA allocation failures; validate IOMMU SID address composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-lpass-dais.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-lpass-dais.c

Purpose: `q6apm-lpass-dais.c` registers AudioReach backend LPASS DAIs. It binds the common LPASS port table to APM graph operations and supplies DAI ops for DMA, I2S, and HDMI/DisplayPort backends.

Important APIs and types: `struct q6apm_lpass_dai_data` keeps one graph pointer, started flag, and `audioreach_module_config` per `APM_PORT_MAX` port. DAI ops are `q6dma_ops`, `q6i2s_ops`, and `q6hdmi_ops`, all sharing startup/prepare/shutdown/trigger behavior with format-specific `hw_params`, channel-map, or set-fmt callbacks.

Control flow: probe allocates the state object, fills `q6dsp_audio_port_dai_driver_config` with APM-specific ops, asks `q6dsp_audio_ports_set_config` for the full DAI table, then registers the component with `.of_xlate_dai_name`. Capture graphs are opened in `startup`; playback graphs are opened in `prepare` to satisfy the source-before-sink graph sequencing comment. `prepare` stops any already-started graph, sets module direction, applies PCM media format to graph modules, and sends graph prepare. `trigger` starts the graph on START/RESUME/PAUSE_RELEASE if not already started. `shutdown` stops and closes the graph.

State and persistence: graph pointers and module configs are runtime component state indexed by DAI ID. `is_port_started` prevents duplicate graph starts. Channel maps and display-port indexes persist between hw_params/set_channel_map and prepare.

Dependencies and integration points: this layer depends on the common LPASS port table in `q6dsp-lpass-ports.c`, AudioReach graph APIs from `q6apm.c`, and `q6dsp-common` channel allocation. It is selected by the `qcom,q6apm-lpass-dais` compatible.

Risks: arrays are indexed directly by `dai->id`, so DT/table IDs must be less than `APM_PORT_MAX`. HDMI `hw_params` uses the maximum channel interval rather than the exact selected channel count. Several operations assume `graph[dai->id]` is non-null; unusual trigger ordering can crash. Stop errors in prepare are not checked.

Test signals: validate all backend DAI IDs translate to names and ops, capture and playback graph open ordering, channel-map validation for DMA TX/RX sets, HDMI channel allocation, repeated prepare/start/stop/shutdown cycles, and invalid DAI ID rejection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-lpass-dais.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.c

Purpose: `q6apm.c` implements the GPR-backed AudioReach Audio Process Manager service. It loads topology-derived graph packets, manages graph reference counts, sends graph lifecycle commands, maps shared memory, sends media-format and decoder parameters, and dispatches graph data callbacks to ALSA-facing clients.

Important APIs and types: `struct q6apm` holds the GPR device, global command result/wait state, mutexes, service state, widget list, and IDRs for graphs, graph infos, subgraphs, containers, and modules. `struct audioreach_graph` is a cached graph packet plus refcount and topology info. `struct q6apm_graph` is the public per-client graph handle with GPR port, callbacks, shared-memory endpoint IID, rx/tx buffer data, command wait, and topology info. Exported APIs cover graph open/close/prepare/start/stop/flush, memory map/unmap, fragment allocation, read/write, media format, decoder controls, module lookup, APM readiness, and hardware pointer reads.

Control flow: probe initializes IDRs, registers the ASoC component, loads topology through `audioreach_tplg_init`, and populates child devices. Opening a graph looks up or creates an `audioreach_graph`, allocates and sends a graph-open packet, allocates a client `q6apm_graph`, finds the shared-memory endpoint IID by direction, and allocates a GPR port with `graph_callback`. Lifecycle calls build APM subgraph-list management packets and wait synchronously via `audioreach_send_cmd_sync`. Data write/read functions choose the next ring fragment, fill a shared-memory endpoint packet, advance `dsp_buf`, and send through the graph GPR port.

State and persistence: graph topology data is held in IDRs for the life of the APM device. Cached graph packets are shared by kref and closed only when the last client releases them. `start_count` allows multiple clients to share a graph start, but it is not protected by its own lock. Memory-map handles are stored in `audioreach_graph_info` and reused until explicit unmap. Buffer fragments and hardware pointers are per graph handle.

Dependencies and integration points: the file is built around `audioreach.h`, GPR/APR transport, ALSA topology, and `q6apm.h`. Frontend and backend DAI drivers consume its exports. Firmware callback opcodes update memory-map handles and deliver period completions.

Risks: `q6apm_get_audioreach_graph` sends graph-open with response opcode zero and does not check the return. `q6apm_graph_start/stop` mutate `start_count` without locking and stop can underflow if calls are unbalanced. `q6apm_map_memory_fixed_region` returns success if a handle already exists, even if the new physical region differs. Callback token indexing assumes tokens are valid buffer indexes. Close sets `ar_graph` NULL before freeing the GPR port, so late callbacks are dropped but still rely on graph object lifetime.

Test signals: topology loading, graph sharing/refcount, lifecycle command ordering, memory map handle updates, data write/read ring wrapping, callback address validation, decoder module ID setup for supported codecs, and error injection for missing modules or GPR timeouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.h

Purpose: `q6apm.h` is the exported interface and core data model for AudioReach APM graph clients. It defines channel constants, callback events, graph/session limits, shared-memory buffer records, and public graph APIs.

Important APIs and types: `struct q6apm` mirrors the service state used by `q6apm.c`. `struct audio_buffer` is a physical address/size pair. `struct audioreach_graph_data` stores fragment arrays, period count, next DSP buffer index, and atomic hardware pointer. `struct audioreach_graph` caches topology graph state and refcount. `struct q6apm_graph` is the per-client handle used by DAI code. Public functions include graph lifecycle, media format for PCM and shared memory endpoints, read/write, fixed-region memory map/unmap, fragment allocation/free, synchronous command send, module lookup, ADSP/APM readiness, compressed decoder controls, and hardware pointer query.

Control flow: callers open a graph by topology graph ID and direction, configure media formats, map memory, allocate fragments, prepare/start, exchange read/write buffers, stop/flush, then close and unmap/free resources. The callback typedef `q6apm_cb` allows lower-level graph events to be translated into ALSA notifications.

State and persistence: the header exposes enough struct fields for cooperating in-tree drivers to read graph IDs, buffer data, and topology info directly. That speeds integration but increases coupling: external users can observe or mutate state that `q6apm.c` expects to own.

Dependencies and integration points: includes Linux kernel primitives, ALSA SoC, APR/GPR support, `../common.h`, and `audioreach.h`. It is consumed by APM frontend, LPASS backend, and clock/port integration code.

Risks: ABI is not stable for external modules because structs are public and lack accessors. `APM_PORT_MAX` depends on `LPASS_MAX_PORT`; any DT/table mismatch can produce out-of-bounds indexing in users. Direction conventions are ALSA `SNDRV_PCM_STREAM_*` values and must match the rx/tx naming used inside `q6apm.c`.

Test signals: compile all users after field changes, verify event constants match callback dispatch, and exercise both playback/capture directions to confirm shared-memory endpoint selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm-dai.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm-dai.c

Purpose: `q6asm-dai.c` is the ALSA SoC frontend DAI component for the legacy Q6 Audio Stream Manager. It exposes up to eight multimedia PCM frontends and compressed playback, creates ASM audio clients, maps DMA buffers, opens ASM streams, registers routes through `q6routing`, queues buffers, and translates ASM callbacks into ALSA notifications.

Important APIs and types: `struct q6asm_dai_rtd` is per-stream state: PCM/compress stream, codec, DMA buffer, spinlock, physical address with optional SID, buffer/period sizing, byte counters, queue pointer, source bitmask, ASM audio client, stream IDs, session ID, state, gapless metadata, and drain flags. `q6asm_fe_dai_component` defines PCM and compress callbacks plus DAPM widgets for multimedia DL/UL paths. `Q6ASM_FEDAI_DRIVER` builds DAI templates; `of_q6asm_parse_dai_data` chooses enabled directions and compress capability from DT children.

Control flow: PCM `open` allocates runtime state, creates an ASM audio client, sets hardware constraints, and stores the physical DMA address. `prepare` remaps buffers, opens write/read stream, registers the route, sends PCM media format or capture encoder config, queues capture reads, and marks the stream running. `trigger` sends run, EOS, or pause commands. Playback `ack` queues writes for newly available periods. Close sends close, unmaps memory, frees the client, closes routing, and frees state.

Compressed control flow: `compr_open` allocates a large DMA ring and ASM client. `set_params` opens the decoder stream, routes it, sends codec-specific format blocks for FLAC/WMA/ALAC/APE or opens MP3, maps fragments, and marks running. `copy` writes user data into the ring and kicks the DSP when empty. Callback handling supports gapless next-track by toggling stream IDs 1 and 2, setting initial/trailing silence, using last-buffer flags, and notifying drain completion.

State and persistence: all state is per-open runtime; the only persistent component data is the parsed DAI table and SID. Routing state persists until explicit `q6routing_stream_close`. Compressed counters are protected by a spinlock, while route/client lifetime is managed by close/free paths.

Dependencies and integration points: this file depends on `q6asm.h`, `q6routing.h`, ALSA PCM/compress APIs, DMA mapping, DT child nodes, and q6dsp errno. It is the legacy frontend counterpart to the APM frontend.

Risks: `q6asm_dai_hw_params` lacks a default error for unsupported formats, leaving bits-per-sample unchanged. Several error paths free the audio client but may not close routing if routing opened later. `q6asm_dai_compr_free` frees DMA pages only inside the audio_client branch. Playback `ack` has the same appl_ptr wrap risk as APM. The gapless next-track path is complex and sensitive to metadata ordering.

Test signals: DT parsing for directions/compress DAIs, PCM open/prepare/trigger/ack/pointer/close, capture read requeueing, compressed MP3/FLAC/WMA/ALAC/APE setup, next-track and partial drain, route open/close pairing, and fault injection for map/open/format failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm-dai.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.c

Purpose: `q6asm.c` implements the legacy APR-backed Q6 Audio Stream Manager service. It allocates ASM sessions, maps/unmaps shared DMA buffers, opens read/write streams, programs PCM and compressed codec format blocks, sends run/pause/flush/EOS/close commands, queues read/write buffers, and dispatches APR callbacks to client code.

Important APIs and types: `struct q6asm` stores the APR device, service API info, memory wait queue, session spinlock, and session table. `struct audio_client` represents one ASM session with callback, command lock, kref, playback/capture `audio_port_data`, command wait/result, perf mode, and device pointers. Packed structs model ASM command payloads for memory maps, open read/write, run, media formats, codec-specific format blocks, read/write buffers, and encoder config. Exported APIs are declared in `q6asm.h`.

Control flow: probe allocates service state and populates child devices. Clients allocate sessions via `q6asm_audio_client_alloc`, which stores the client in the session table at `session_id + 1`. Memory mapping allocates fragment descriptors, builds one contiguous shared-memory map region, waits for `ASM_CMDRSP_SHARED_MEM_MAP_REGIONS`, and stores the returned map handle. Open-write selects firmware decoder format from ALSA codec ID/profile; open-read selects PCM encoder format. Media-format helpers build and send codec payloads. Read/write async chooses the current buffer, builds an APR packet with buffer address/map handle/size/token, advances ring position, and sends without waiting.

Callbacks: service callbacks dispatch stream responses by destination session ID or memory-map responses by token session/direction. Stream callbacks translate APR basic result opcodes into client event constants, validate write/read done addresses in sync I/O mode, update atomic hardware pointers, and call the registered callback. Krefs protect sessions while callbacks run.

State and persistence: session table and map handles persist while clients are open. Buffer descriptors are per direction and freed on unmap. DSP session state is reset by close/flush commands, with `q6asm_reset_buf_state` resetting local ring indexes on flush. There is no persistent storage.

Dependencies and integration points: depends on APR, `q6core_get_svc_api_info`, q6dsp channel mapping, ALSA codec/compress IDs, and child platform devices such as `q6asm-dai`.

Risks: `q6asm_unmap_memory_regions` passes `port->buf[dir].phys` to `__q6asm_memory_unmap`, which is unused but suspicious for capture direction. Memory map currently always maps contiguous regions; non-contiguous support exists only in the internal helper. `q6asm_open_read` logs invalid format but still sends a packet with whatever `enc_cfg_id` remains. Callback address validation relies on token indexes from firmware. Error handling often converts DSP status to `-EINVAL`, losing detail.

Test signals: allocate/free all session IDs, map/unmap playback and capture buffers, open each supported codec/profile, send PCM/capture media formats, ring wrap for read/write, callback address validation, EOS/flush/close command responses, and unsupported firmware response handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.h

Purpose: `q6asm.h` is the public interface to the legacy Q6 ASM service. It defines client event constants, simple command IDs, token masks, performance modes, codec parameter structs, and exported session/buffer/stream operations.

Important APIs and types: event macros pair high-level commands with callback events such as pause, flush, EOS, close, run done, write done, and read done. Codec structs `q6asm_flac_cfg`, `q6asm_wma_cfg`, `q6asm_alac_cfg`, and `q6asm_ape_cfg` carry ALSA compress parameters into packed ASM format blocks. The opaque `struct audio_client` is created with `q6asm_audio_client_alloc` and freed with `q6asm_audio_client_free`. Exports cover open read/write, media-format programming, silence removal, run/run_nowait, generic commands, memory map/unmap, async read/write, session ID, and hardware pointer.

Control flow: a caller allocates an audio client, maps memory, opens a stream, sends format/config commands, runs, queues reads/writes, reacts to callbacks, then stops/closes, unmaps, and frees the client. The header separates blocking command APIs from `*_nowait` variants.

State and persistence: no state is stored in the header. Constants such as `ASM_WRITE_TOKEN_*` encode the token layout used by both DAI code and callback parsing, so they are part of the in-kernel contract.

Dependencies and integration points: includes `q6dsp-common.h` for channel constants and `PCM_MAX_NUM_CHANNEL`. Used by `q6asm.c` and the legacy frontend DAI. ALSA codec IDs passed to these functions come from UAPI headers.

Risks: stream IDs, session IDs, and direction values are plain integers; misuse can address the wrong ASM stream. Codec structs must match firmware expectations but are not self-validating. `FORMAT_LINEAR_PCM` duplicates a constant also used in APM headers.

Test signals: compile all ASM users after API changes, verify callback event values match `q6asm.c`, and run playback/capture/compress paths for every exported operation order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.c

Purpose: `q6core.c` implements the APR Q6 core/AVCS service helper. It detects whether ADSP is ready and retrieves service API versions for other QDSP6 audio services.

Important APIs and types: `struct q6core` holds the APR device, wait queue, AVCS state, lock, response flags, version response buffers, feature-support booleans, and request state. Exported APIs are `q6core_is_adsp_ready` and `q6core_get_svc_api_info`. Internal payload types model old `AVCS_GET_VERSIONS` and newer framework-version responses.

Control flow: callbacks handle basic unsupported responses, framework-version responses, legacy version responses, and ADSP state responses, then wake waiters. `q6core_get_svc_api_info` lazily requests framework versions, falls back to legacy service versions if unsupported, caches the result, and searches for the requested service ID. `q6core_is_adsp_ready` loops for up to 3000 ms, sending get-state probes with 100 ms waits; if firmware does not support the command, it assumes ADSP is up.

State and persistence: `g_core` is a singleton set at probe and cleared on remove. Version responses are duplicated into heap memory and reused after the first request. Support booleans determine fallback behavior.

Dependencies and integration points: depends on APR, q6dsp errno for `ADSP_EUNSUPPORTED`, and DT compatible `qcom,q6core`. Other services call it during probe to fill service API info or to gate readiness.

Risks: if `g_core` or `ainfo` is missing, `q6core_get_svc_api_info` returns 0 without filling info, which can look like success. The readiness loop does not sleep beyond wait time and may issue repeated commands quickly. Version response allocation uses GFP_ATOMIC in callback and can fail under pressure, causing request errors.

Test signals: unsupported command fallback, framework-vs-legacy version lookup, absent service ID returning `-ENOTSUPP`, ADSP ready timeout, singleton probe/remove cleanup, and allocation-failure callback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.h

Purpose: `q6core.h` exposes the small public contract for Q6 core service readiness and service-version lookup.

Important APIs and types: `struct q6core_svc_api_info` carries service ID version data as `service_id`, `api_version`, and `api_branch_version`. `q6core_is_adsp_ready` returns whether the ADSP/Q6 service is considered ready. `q6core_get_svc_api_info` fills API version fields for a service ID.

Control flow: service drivers call these helpers during probe before constructing service-specific command behavior. The header itself has no implementation state.

State and persistence: no local state. Returned data is derived from the singleton `q6core` cache in `q6core.c`.

Dependencies and integration points: consumed by `q6afe.c` and `q6asm.c`, and potentially other QDSP6 services that need firmware API version information.

Risks: callers must handle the implementation's ambiguous zero return when core state is missing. Header users need Linux integer types in scope through transitive includes.

Test signals: compile users and verify service API info is filled for known service IDs on hardware or mocked APR responses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.c

Purpose: `q6dsp-common.c` provides shared audio channel helper functions used by QDSP6 drivers.

Important APIs and types: `q6dsp_map_channels` fills an eight-entry PCM channel map for 1, 2, 3, 4, 5, 6, or 8 channels using QDSP6 channel position constants. `q6dsp_get_channel_allocation` returns HDMI CEA-861-E channel allocation values for 2 through 8 channels.

Control flow: both functions are simple switch tables. Unsupported channel counts return `-EINVAL`. `q6dsp_map_channels` clears the map before filling supported entries.

State and persistence: no state. Outputs are caller-provided arrays or return values.

Dependencies and integration points: exports are used by ASM media-format setup and APM/HDMI DAI setup. The implementation depends on constants from `q6dsp-common.h` and Linux errno/string helpers.

Risks: 7-channel PCM mapping is unsupported while HDMI allocation accepts 7 channels. The 6/8-channel map orders LFE before FC, matching this DSP expectation but potentially surprising to generic ALSA users. HDMI allocation table is fixed to the comment's CEA mapping and does not include every possible speaker layout.

Test signals: unit-style tests for every supported channel count, unsupported channel counts, zeroed trailing channel map entries, and expected HDMI allocation bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.h

Purpose: `q6dsp-common.h` defines shared PCM channel constants and declares common helper functions for QDSP6 audio drivers.

Important APIs and types: `PCM_MAX_NUM_CHANNEL` is 8. Channel constants define null, front left/right/center, left/right surround, LFE, center surround, left/right back, and top surround positions. Function declarations are `q6dsp_map_channels` and `q6dsp_get_channel_allocation`.

Control flow: callers use constants in media-format structs and call helpers for default channel mapping or HDMI channel allocation.

State and persistence: no state.

Dependencies and integration points: included by `q6asm.h`, `q6dsp-common.c`, APM LPASS DAI code, and any driver that needs shared QDSP6 channel positions.

Risks: constants overlap semantically with similar definitions in `q6apm.h`, creating drift risk. The helper prototype fixes the channel map array to eight entries.

Test signals: compile all includes and verify constants remain aligned with firmware and APM/ASM media-format users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-errno.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-errno.h

Purpose: `q6dsp-errno.h` defines firmware ADSP error/status codes used by QDSP6 audio service drivers.

Important APIs and types: it provides numeric `ADSP_E*` macros for OK, failed, bad param, unsupported, version mismatch, unexpected, panic, resource, handle, already, not ready, pending, busy, aborted, preempted, continue, immediate, not implemented, need more, no memory, and not exist.

Control flow: service callbacks compare firmware status fields to these constants, especially `ADSP_EUNSUPPORTED` in q6core fallback logic.

State and persistence: no state; constants are firmware protocol values.

Dependencies and integration points: included by q6core, q6afe, q6asm, and DAI code for interpreting DSP response status. These values bridge APR/GPR payloads to Linux errno handling.

Risks: many drivers collapse nonzero ADSP status to `-EINVAL`, so preserving distinct constants here does not automatically preserve diagnostic fidelity. Any value change would break protocol decoding.

Test signals: compile coverage and mocked DSP responses for unsupported, busy, bad param, and no-memory statuses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-errno.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.c

Purpose: `q6dsp-lpass-clocks.c` adapts QDSP6 LPASS clock and hardware-block vote operations into the Linux common clock framework.

Important APIs and types: `struct q6dsp_clk` wraps one clock hardware object with QDSP6 clock ID, attributes, cached rate, vote handle, and device. `struct q6dsp_cc` stores the provider, clock array, and `q6dsp_clk_desc`. Clock ops are split between rate-bearing clocks (`clk_q6dsp_ops`) that call `lpass_set_clk` on prepare/unprepare and vote-only clocks (`clk_vote_q6dsp_ops`) that call `lpass_vote_clk`/`lpass_unvote_clk`. The exported entry is `q6dsp_clock_dev_probe`.

Control flow: probe reads the match-data descriptor, allocates provider state, creates a `clk_hw` for each descriptor entry, chooses ops based on whether an initial rate is nonzero, registers each clock, and adds an OF clock provider. OF lookup validates index and attribute arguments, stores the requested attribute in the clock, and returns its `clk_hw`.

State and persistence: cached rate and last-requested attributes live in `struct q6dsp_clk`. Vote handles are stored after prepare and reused for unprepare. Registered clocks persist for the platform device lifetime through devm allocations.

Dependencies and integration points: descriptors come from platform-specific drivers using `q6dsp-lpass-clocks.h`. Function pointers usually target AFE/APM clock/vote helpers. The OF provider expects two-cell clock specifiers: clock index and attribute.

Risks: `clk_q6dsp_determine_rate` returns 0 without constraining `req`, so consumers may believe any rate is acceptable. Attribute is mutable per OF lookup on a shared clock object; multiple consumers with different attributes can race or override each other. `Q6DSP_MAX_CLK_ID` must cover all descriptor `clk_id` values.

Test signals: register descriptors with valid/invalid IDs, prepare/unprepare rate clocks and vote clocks, set/recalc rate, OF lookup with invalid attribute, and multi-consumer attribute behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.h -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.h

Purpose: `q6dsp-lpass-clocks.h` defines descriptor structures for registering QDSP6 LPASS clocks with the common helper in `q6dsp-lpass-clocks.c`.

Important APIs and types: `struct q6dsp_clk_init` describes one clock: Linux provider index, firmware QDSP6 clock ID or hardware block ID, name, and optional default rate. `Q6DSP_VOTE_CLK` builds a vote-only descriptor with no rate. `struct q6dsp_clk_desc` contains the descriptor array, count, and function pointers for setting, voting, and unvoting LPASS clocks. `q6dsp_clock_dev_probe` is declared for reuse by platform drivers.

Control flow: platform drivers provide a `q6dsp_clk_desc` as OF match data and call `q6dsp_clock_dev_probe` from their probe function.

State and persistence: no state in the header; descriptors are usually static const data in platform-specific code.

Dependencies and integration points: depends on platform devices and callback implementations from AFE/APM service layers. Consumers use OF clock specifiers resolved by the C file.

Risks: function pointer contracts are not type-rich enough to distinguish rate clocks from vote-only clocks; descriptor rate zero is the discriminator. Bad `clk_id` values fail later at probe or lookup.

Test signals: compile descriptor users, probe with mixed rate/vote clocks, and confirm callbacks are invoked with expected IDs and attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-clocks.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-ports.c -->
# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-ports.c

Purpose: `q6dsp-lpass-ports.c` provides the common ALSA SoC DAI driver table for QDSP6 LPASS ports and helpers to assign backend-specific DAI ops. It is shared by AudioReach/APM and other LPASS DAI drivers.

Important APIs and types: macros build repeated DAI descriptors for TDM playback/capture, codec DMA RX/TX, DisplayPort RX, and MI2S RX/TX. `q6dsp_audio_fe_dais[]` is the central static table covering USB, HDMI, Slimbus 0-6, primary through senary MI2S, LPI MI2S, primary through quinary TDM slots, DP RX 0-7, WSA/VA/RX/TX codec DMA ports. Exported helpers are `q6dsp_audio_ports_of_xlate_dai_name` and `q6dsp_audio_ports_set_config`.

Control flow: platform DAI probes call `q6dsp_audio_ports_set_config` with a config struct holding ops pointers. The helper walks the static table and assigns ops by ID range: HDMI/DP, Slimbus, MI2S/LPI MI2S, TDM, codec DMA, and USB. It returns the table pointer and count. Device-tree DAI name translation calls `q6dsp_audio_ports_of_xlate_dai_name`, scans the table by ID, and returns the matching name.

State and persistence: the DAI table is static mutable global state because ops pointers are patched in place. Once configured, all users see the same ops assignments. There is no per-device copy in this helper.

Dependencies and integration points: depends on ALSA SoC DAI structs, PCM rate/format flags, q6afe dt-bindings for port IDs, and the companion header defining the config struct. APM LPASS DAIs consume it directly.

Risks: because the table is global and mutable, two different platform drivers using different ops configs could overwrite each other. ID range matching must stay aligned with dt-bindings; adding new ports outside existing ranges will silently leave ops unset. `DISPLAY_PORT_RX` and `DISPLAY_PORT_RX_0` naming/range handling must match binding IDs.

Test signals: verify every table entry gets non-null ops for the intended backend, OF xlate returns correct names for all IDs, unsupported IDs return `-EINVAL`, and global table behavior is safe when multiple compatible drivers probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6dsp-lpass-ports.c -->
