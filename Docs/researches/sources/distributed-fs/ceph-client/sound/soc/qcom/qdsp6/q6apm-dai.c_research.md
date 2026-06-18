# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6apm-dai.c

Purpose: `q6apm-dai.c` is the ALSA SoC frontend DAI component for AudioReach APM graphs. It exposes PCM and compressed playback interfaces, maps ALSA buffers into DSP shared memory, programs graph media formats, queues period buffers, and translates graph callbacks into ALSA period/compress notifications.

Important APIs and types: `struct q6apm_dai_rtd` is per-stream runtime state with substream/compress stream, codec params, DMA buffer, physical address with optional SID bits, PCM size/count/periods, byte counters, queue pointer, state, graph pointer, spinlock, and drain flags. `q6apm_fe_dai_component` registers component callbacks: `open`, `close`, `prepare`, `pcm_new`, `pcm_free`, `hw_params`, `pointer`, `trigger`, `ack`, and compress ops. `q6apm_compr_caps` describes compressed capabilities; supported compressed codecs are MP3, AAC, FLAC, and raw OPUS.

Control flow: PCM `open` allocates runtime state, opens the APM graph keyed by CPU DAI ID, applies hardware constraints, and derives the physical address from the fixed DMA buffer plus optional IOMMU SID. `pcm_new` allocates fixed DMA buffers and maps the whole max buffer with `q6apm_map_memory_fixed_region`. `prepare` sets shared-memory and PCM media format, allocates period fragments, prepares and starts the graph, and queues capture reads. Playback `ack` queues writes for newly advanced ALSA periods. Callback paths update ALSA via `snd_pcm_period_elapsed`.

Compressed control flow: `compr_open` allocates a coherent DMA buffer, opens a playback graph, and enables the placeholder decoder. `set_params` sets the real decoder module ID, sends media format, maps fragments, prepares and starts the graph, or for next-track updates sends compressed params only. `copy` writes user data into a ring buffer and kicks the DSP if no data is in flight. Write-done callbacks advance `copied_total`, queue more bytes, and send EOS on drain.

State and persistence: all stream state is per-open and freed on close/free. DSP memory maps persist for the PCM lifetime and are unmapped by `pcm_free`; compressed maps are released in `compr_free`. Byte counters and queue pointers are protected by spinlock for compress paths but PCM `queue_ptr` arithmetic depends on ALSA callback ordering.

Dependencies and integration points: this file depends on `q6apm.h`, AudioReach helpers, ALSA PCM/compress APIs, DMA mapping, and DT IOMMU SID parsing. It integrates frontend CPU DAIs with AudioReach graphs created by `q6apm.c`.

Risks: `q6apm_dai_compr_open` leaks the graph/runtime state if `snd_dma_alloc_pages` fails after graph open. `q6apm_dai_close` assumes `runtime->private_data` and `graph` are valid. Playback `ack` computes available periods by simple subtraction of appl_ptr and queue_ptr without wrap handling. Compress get-codec-caps only fills MP3 despite advertising other codecs. Errors from some async writes and EOS sends are ignored.

Test signals: exercise PCM playback/capture open, prepare, start, stop, pointer, and close; verify fixed-buffer map/unmap pairing; test compressed set_params/copy/drain/partial-drain/next-track; inject graph command failures and DMA allocation failures; validate IOMMU SID address composition.
