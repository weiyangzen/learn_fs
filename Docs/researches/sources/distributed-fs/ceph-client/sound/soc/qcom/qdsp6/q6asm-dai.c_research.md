# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm-dai.c

Purpose: `q6asm-dai.c` is the ALSA SoC frontend DAI component for the legacy Q6 Audio Stream Manager. It exposes up to eight multimedia PCM frontends and compressed playback, creates ASM audio clients, maps DMA buffers, opens ASM streams, registers routes through `q6routing`, queues buffers, and translates ASM callbacks into ALSA notifications.

Important APIs and types: `struct q6asm_dai_rtd` is per-stream state: PCM/compress stream, codec, DMA buffer, spinlock, physical address with optional SID, buffer/period sizing, byte counters, queue pointer, source bitmask, ASM audio client, stream IDs, session ID, state, gapless metadata, and drain flags. `q6asm_fe_dai_component` defines PCM and compress callbacks plus DAPM widgets for multimedia DL/UL paths. `Q6ASM_FEDAI_DRIVER` builds DAI templates; `of_q6asm_parse_dai_data` chooses enabled directions and compress capability from DT children.

Control flow: PCM `open` allocates runtime state, creates an ASM audio client, sets hardware constraints, and stores the physical DMA address. `prepare` remaps buffers, opens write/read stream, registers the route, sends PCM media format or capture encoder config, queues capture reads, and marks the stream running. `trigger` sends run, EOS, or pause commands. Playback `ack` queues writes for newly available periods. Close sends close, unmaps memory, frees the client, closes routing, and frees state.

Compressed control flow: `compr_open` allocates a large DMA ring and ASM client. `set_params` opens the decoder stream, routes it, sends codec-specific format blocks for FLAC/WMA/ALAC/APE or opens MP3, maps fragments, and marks running. `copy` writes user data into the ring and kicks the DSP when empty. Callback handling supports gapless next-track by toggling stream IDs 1 and 2, setting initial/trailing silence, using last-buffer flags, and notifying drain completion.

State and persistence: all state is per-open runtime; the only persistent component data is the parsed DAI table and SID. Routing state persists until explicit `q6routing_stream_close`. Compressed counters are protected by a spinlock, while route/client lifetime is managed by close/free paths.

Dependencies and integration points: this file depends on `q6asm.h`, `q6routing.h`, ALSA PCM/compress APIs, DMA mapping, DT child nodes, and q6dsp errno. It is the legacy frontend counterpart to the APM frontend.

Risks: `q6asm_dai_hw_params` lacks a default error for unsupported formats, leaving bits-per-sample unchanged. Several error paths free the audio client but may not close routing if routing opened later. `q6asm_dai_compr_free` frees DMA pages only inside the audio_client branch. Playback `ack` has the same appl_ptr wrap risk as APM. The gapless next-track path is complex and sensitive to metadata ordering.

Test signals: DT parsing for directions/compress DAIs, PCM open/prepare/trigger/ack/pointer/close, capture read requeueing, compressed MP3/FLAC/WMA/ALAC/APE setup, next-track and partial drain, route open/close pairing, and fault injection for map/open/format failures.
