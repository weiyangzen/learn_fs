# sources/distributed-fs/ceph-client/sound/soc/qcom/qdsp6/q6asm.c

Purpose: `q6asm.c` implements the legacy APR-backed Q6 Audio Stream Manager service. It allocates ASM sessions, maps/unmaps shared DMA buffers, opens read/write streams, programs PCM and compressed codec format blocks, sends run/pause/flush/EOS/close commands, queues read/write buffers, and dispatches APR callbacks to client code.

Important APIs and types: `struct q6asm` stores the APR device, service API info, memory wait queue, session spinlock, and session table. `struct audio_client` represents one ASM session with callback, command lock, kref, playback/capture `audio_port_data`, command wait/result, perf mode, and device pointers. Packed structs model ASM command payloads for memory maps, open read/write, run, media formats, codec-specific format blocks, read/write buffers, and encoder config. Exported APIs are declared in `q6asm.h`.

Control flow: probe allocates service state and populates child devices. Clients allocate sessions via `q6asm_audio_client_alloc`, which stores the client in the session table at `session_id + 1`. Memory mapping allocates fragment descriptors, builds one contiguous shared-memory map region, waits for `ASM_CMDRSP_SHARED_MEM_MAP_REGIONS`, and stores the returned map handle. Open-write selects firmware decoder format from ALSA codec ID/profile; open-read selects PCM encoder format. Media-format helpers build and send codec payloads. Read/write async chooses the current buffer, builds an APR packet with buffer address/map handle/size/token, advances ring position, and sends without waiting.

Callbacks: service callbacks dispatch stream responses by destination session ID or memory-map responses by token session/direction. Stream callbacks translate APR basic result opcodes into client event constants, validate write/read done addresses in sync I/O mode, update atomic hardware pointers, and call the registered callback. Krefs protect sessions while callbacks run.

State and persistence: session table and map handles persist while clients are open. Buffer descriptors are per direction and freed on unmap. DSP session state is reset by close/flush commands, with `q6asm_reset_buf_state` resetting local ring indexes on flush. There is no persistent storage.

Dependencies and integration points: depends on APR, `q6core_get_svc_api_info`, q6dsp channel mapping, ALSA codec/compress IDs, and child platform devices such as `q6asm-dai`.

Risks: `q6asm_unmap_memory_regions` passes `port->buf[dir].phys` to `__q6asm_memory_unmap`, which is unused but suspicious for capture direction. Memory map currently always maps contiguous regions; non-contiguous support exists only in the internal helper. `q6asm_open_read` logs invalid format but still sends a packet with whatever `enc_cfg_id` remains. Callback address validation relies on token indexes from firmware. Error handling often converts DSP status to `-EINVAL`, losing detail.

Test signals: allocate/free all session IDs, map/unmap playback and capture buffers, open each supported codec/profile, send PCM/capture media formats, ring wrap for read/write, callback address validation, EOS/flush/close command responses, and unsupported firmware response handling.
