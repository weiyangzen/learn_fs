# sources/distributed-fs/ceph-client/sound/soc/sof/amd/acp-pcm.c

Purpose: AMD ACP PCM callbacks for SOF streams: open/close, hardware params, and pointer reporting.

Important APIs/types/functions: `acp_pcm_open()` allocates an inactive `acp_dsp_stream` and stores it in ALSA runtime private data. `acp_pcm_hw_params()` configures stream PTEs, fills SOF platform stream params with physical stream offset/tag, enables continuous position updates, and writes buffer size into scratch. `acp_pcm_pointer()` reads `sof_ipc_stream_posn` and returns ALSA frames. `acp_pcm_close()` releases the stream.

Control flow: open selects a stream tag via `acp_dsp_stream_get()`. hw_params derives page count from DMA bytes and calls `acp_dsp_stream_config()`, then communicates stream tag and physical address to firmware. Pointer lookup finds the SOF PCM by DAI runtime, reads position data through IPC mailbox helpers, updates cached position, and converts host bytes to frames.

State and persistence: per-runtime private data points to a stream from `adata->stream_buf`. Scratch memory receives per-stream buffer sizes. Cached positions live in `snd_sof_pcm_stream`.

Dependencies and integration points: ALSA PCM runtime, SOF PCM lookup, ACP stream PTE helper, SOF IPC position offsets, and firmware stream box layout.

Risks: pointer returns 0 on lookup/read failure, which can hide errors but avoids crashing the PCM engine. Stream allocation has only eight slots shared with trace/probes. Buffer size scratch indexing assumes tags are 1-based and within `ACP_MAX_STREAM`.

Test signals: PCM open/hw_params/close sequences, playback/capture position accuracy, and stream exhaustion tests.
